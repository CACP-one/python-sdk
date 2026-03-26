"""
CACP SDK Main Client

The main async client for interacting with CACP.
"""

import asyncio
import json
import logging
import uuid
from typing import Any, Callable, Dict, Optional, TypeVar, Union

import httpx

from cacp_sdk.agents import AgentsAPI
from cacp_sdk.api_keys import APIKeysAPI
from cacp_sdk.auth import AuthAPI
from cacp_sdk.config import Config
from cacp_sdk.exceptions import (
    AuthenticationError,
    CacpError,
    ConnectionError,
    RateLimitError,
    TimeoutError,
    ValidationError,
    raise_for_error,
)
from cacp_sdk.groups import GroupsAPI
from cacp_sdk.messaging import MessagingAPI
from cacp_sdk.models import ErrorResponse
from cacp_sdk.tasks import TasksAPI
from cacp_sdk.websocket import WebSocketClient

T = TypeVar("T")

logger = logging.getLogger(__name__)


class CacpClient:
    """
    Main async client for CACP.

    This client provides access to all CACP APIs including:
    - Agent management (registration, discovery, health)
    - Messaging (send, receive, RPC)
    - Tasks (long-running asynchronous operations)
    - Groups (agent teams)
    - WebSocket real-time communication

    Example:
        ```python
        async with CacpClient(base_url="http://localhost:4001", api_key="key") as client:
            agent = await client.agents.register(
                name="my-agent",
                capabilities=["chat"]
            )
        ```
    """

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        jwt_token: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        logger: Optional[logging.Logger] = None,
        on_request: Optional[Callable[[str, str, Dict[str, Any]], None]] = None,
        on_response: Optional[Callable[[str, int, Dict[str, Any]], None]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the CACP client.

        Args:
            base_url: The base URL of the CACP API
            api_key: API key for authentication
            jwt_token: JWT token for authentication (alternative to api_key)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Initial retry delay in seconds
            logger: Custom logger for SDK operations
            on_request: Callback invoked before each request (method, path, headers)
            on_response: Callback invoked after each response (path, status, response)
            **kwargs: Additional configuration options
        """
        self._config = Config(
            base_url=base_url,
            api_key=api_key,
            jwt_token=jwt_token,
            timeout=timeout,
            max_retries=max_retries,
            retry_delay=retry_delay,
            logger=logger,
            on_request=on_request,
            on_response=on_response,
            **kwargs,
        )

        self._http_client: Optional[httpx.AsyncClient] = None
        self._websocket_client: Optional[WebSocketClient] = None

        # Initialize API modules
        self._agents: Optional[AgentsAPI] = None
        self._messaging: Optional[MessagingAPI] = None
        self._tasks: Optional[TasksAPI] = None
        self._groups: Optional[GroupsAPI] = None
        self._auth: Optional[AuthAPI] = None
        self._api_keys: Optional[APIKeysAPI] = None

    @property
    def config(self) -> Config:
        """Get the client configuration."""
        return self._config

    @property
    def agents(self) -> AgentsAPI:
        """Get the agents API module."""
        if self._agents is None:
            self._agents = AgentsAPI(self)
        return self._agents

    @property
    def messaging(self) -> MessagingAPI:
        """Get the messaging API module."""
        if self._messaging is None:
            self._messaging = MessagingAPI(self)
        return self._messaging

    @property
    def tasks(self) -> TasksAPI:
        """Get the tasks API module."""
        if self._tasks is None:
            self._tasks = TasksAPI(self)
        return self._tasks

    @property
    def groups(self) -> GroupsAPI:
        """Get the groups API module."""
        if self._groups is None:
            self._groups = GroupsAPI(self)
        return self._groups

    @property
    def auth(self) -> AuthAPI:
        """Get the auth API module."""
        if self._auth is None:
            self._auth = AuthAPI(self)
        return self._auth

    @property
    def api_keys(self) -> APIKeysAPI:
        """Get the API keys management module."""
        if self._api_keys is None:
            self._api_keys = APIKeysAPI(self)
        return self._api_keys

    @property
    def websocket(self) -> WebSocketClient:
        """Get the WebSocket client."""
        if self._websocket_client is None:
            self._websocket_client = WebSocketClient(self)
        return self._websocket_client

    async def __aenter__(self) -> "CacpClient":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def connect(self) -> None:
        """Initialize the HTTP client connection."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                base_url=self._config.api_base_url,
                timeout=httpx.Timeout(self._config.timeout),
                limits=httpx.Limits(max_connections=self._config.connection_pool_size),
                headers=self._get_default_headers(),
                verify=self._config.verify_ssl,
            )

    async def close(self) -> None:
        """Close the HTTP client connection."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

        if self._websocket_client:
            await self._websocket_client.close()
            self._websocket_client = None

    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for all requests."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": self._config.user_agent,
        }
        headers.update(self._config.get_auth_headers())
        return headers

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the CACP API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            path: API endpoint path
            params: Query parameters
            json_data: JSON body data
            data: Raw body data
            headers: Additional headers
            timeout: Request timeout override
            request_id: Unique request ID for tracking

        Returns:
            Parsed JSON response

        Raises:
            AuthenticationError: If authentication fails
            ValidationError: If request validation fails
            RateLimitError: If rate limit is exceeded
            ConnectionError: If connection fails
            TimeoutError: If request times out
            CacpError: For other API errors
        """
        if self._http_client is None:
            await self.connect()

        # Generate request ID if not provided
        if request_id is None:
            request_id = str(uuid.uuid4())

        request_headers = {"X-Request-ID": request_id}
        if headers:
            request_headers.update(headers)

        request_timeout = timeout or self._config.timeout

        # Call on_request callback
        if self._config.on_request:
            try:
                self._config.on_request(method, path, request_headers)
            except Exception as e:
                if self._config.logger:
                    self._config.logger.warning(f"on_request callback failed: {e}")

        # Log request
        if self._config.logger:
            self._config.logger.debug(
                f"Request: {method} {path} (ID: {request_id})"
            )

        last_error: Optional[Exception] = None
        response_data: Optional[Dict[str, Any]] = None

        for attempt in range(1, self._config.max_retries + 1):
            try:
                response = await self._http_client.request(
                    method=method,
                    url=path,
                    params=params,
                    json=json_data,
                    content=data if isinstance(data, (str, bytes)) else None,
                    headers=request_headers,
                    timeout=request_timeout,
                )

                # Parse response
                response_data = self._parse_response(response)

                # Call on_response callback
                if self._config.on_response:
                    try:
                        self._config.on_response(path, response.status_code, response_data)
                    except Exception as e:
                        if self._config.logger:
                            self._config.logger.warning(f"on_response callback failed: {e}")

                # Log response
                if self._config.logger:
                    self._config.logger.debug(
                        f"Response: {response.status_code} for {method} {path} (ID: {request_id})"
                    )

                # Handle successful response
                if response.status_code < 400:
                    return response_data

                # Handle error responses
                await self._handle_error_response(response, attempt, request_id)

            except httpx.TimeoutException as e:
                last_error = TimeoutError(
                    operation=f"{method} {path}",
                    timeout=request_timeout,
                    request_id=request_id,
                )
                if self._config.logger:
                    self._config.logger.warning(
                        f"Request timeout (attempt {attempt}/{self._config.max_retries}): {path} (ID: {request_id})"
                    )

            except httpx.ConnectError as e:
                last_error = ConnectionError(
                    f"Failed to connect to {self._config.base_url}: {str(e)}",
                    request_id=request_id,
                )
                if self._config.logger:
                    self._config.logger.warning(
                        f"Connection error (attempt {attempt}/{self._config.max_retries}): {e} (ID: {request_id})"
                    )

            except httpx.HTTPStatusError as e:
                await self._handle_error_response(e.response, attempt, request_id)

            # Wait before retry
            if attempt < self._config.max_retries:
                delay = self._config.retry_delay * (2 ** (attempt - 1))
                await asyncio.sleep(delay)

        # All retries exhausted
        if last_error:
            raise last_error
        raise ConnectionError(f"Failed to complete request: {method} {path}", request_id=request_id)

    def _parse_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Parse the HTTP response."""
        if not response.content:
            return {}

        try:
            return response.json()
        except json.JSONDecodeError:
            return {"data": response.text}

    async def _handle_error_response(
        self,
        response: httpx.Response,
        attempt: int,
        request_id: Optional[str] = None,
    ) -> None:
        """Handle HTTP error responses."""
        status_code = response.status_code

        # Parse error body
        try:
            error_data = response.json()
        except (json.JSONDecodeError, ValueError):
            error_data = {}

        # Try to use broker error code mapping first
        if error_data and "error" in error_data:
            try:
                raise_for_error(error_data, request_id=request_id)
            except CacpError:
                # Re-raise mapped errors
                raise
            except KeyError:
                # No broker error code, fall through to HTTP status handling
                pass

        # Get error message and details for fallback handling
        error_obj = error_data.get("error", {})
        error_message = error_obj.get("message", response.text) if isinstance(error_obj, dict) else error_data.get("error", response.text)
        error_details = error_data.get("details") if isinstance(error_data, dict) else None
        error_code = error_obj.get("code") if isinstance(error_obj, dict) else None

        # Log error
        if self._config.logger:
            self._config.logger.error(
                f"Error response: {status_code} - {error_message} (ID: {request_id}, code: {error_code})"
            )

        # Authentication errors (HTTP 401)
        if status_code == 401:
            raise AuthenticationError(
                message=error_message or "Authentication failed",
                code=error_code,
                request_id=request_id,
            )

        # Validation errors (HTTP 400)
        if status_code == 400:
            raise ValidationError(
                message=error_message,
                field=error_obj.get("field") if isinstance(error_obj, dict) and error_details else None,
                code=error_code,
                request_id=request_id,
            )

        # Rate limiting (HTTP 429)
        if status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                retry_after=float(retry_after) if retry_after else None,
                message=error_message,
                request_id=request_id,
            )

        # Not found (HTTP 404)
        if status_code == 404:
            raise CacpError(
                message=error_message or "Resource not found",
                code=error_code or "NOT_FOUND",
                details=error_details,
                request_id=request_id,
            )

        # Server errors - may be retryable
        if status_code >= 500:
            if attempt < self._config.max_retries:
                return  # Allow retry
            raise CacpError(
                message=error_message or f"Server error: {status_code}",
                code=error_code or "SERVER_ERROR",
                details=error_details,
                request_id=request_id,
            )

        # Other client errors
        raise CacpError(
            message=error_message,
            code=error_code or f"HTTP_{status_code}",
            details=error_details,
            request_id=request_id,
        )

    # Convenience methods
    async def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a GET request."""
        return await self.request("GET", path, params=params, **kwargs)

    async def post(
        self,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a POST request."""
        return await self.request("POST", path, json_data=json_data, **kwargs)

    async def put(
        self,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a PUT request."""
        return await self.request("PUT", path, json_data=json_data, **kwargs)

    async def patch(
        self,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a PATCH request."""
        return await self.request("PATCH", path, json_data=json_data, **kwargs)

    async def delete(
        self,
        path: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a DELETE request."""
        return await self.request("DELETE", path, **kwargs)
