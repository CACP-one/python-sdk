"""Tests for the main client."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from cacp_sdk import CacpClient, CacpError, AuthenticationError
from cacp_sdk.models import Agent, AgentStatus


class TestCacpClient:
    """Tests for CacpClient."""

    def test_client_initialization(self) -> None:
        """Test client initialization with various options."""
        client = CacpClient(
            base_url="http://localhost:4001",
            api_key="test-key",
            timeout=60.0,
            max_retries=5,
        )

        assert client.config.base_url == "http://localhost:4001"
        assert client.config.api_key == "test-key"
        assert client.config.timeout == 60.0
        assert client.config.max_retries == 5

    def test_client_with_jwt(self) -> None:
        """Test client initialization with JWT token."""
        client = CacpClient(
            base_url="http://localhost:4001",
            jwt_token="test-jwt-token",
        )

        assert client.config.jwt_token == "test-jwt-token"
        headers = client.config.get_auth_headers()
        assert headers["Authorization"] == "Bearer test-jwt-token"

    def test_ws_url_conversion(self) -> None:
        """Test WebSocket URL conversion from HTTP URL."""
        client_https = CacpClient(base_url="https://api.cacp.io")
        assert client_https.config.ws_url == "wss://api.cacp.io"

        client_http = CacpClient(base_url="http://localhost:4001")
        assert client_http.config.ws_url == "ws://localhost:4001"

    @pytest.mark.asyncio
    async def test_context_manager(self) -> None:
        """Test async context manager usage."""
        async with CacpClient(base_url="http://localhost:4001", api_key="key") as client:
            assert client._http_client is not None

        # Client should be closed after context exit
        assert client._http_client is None

    @pytest.mark.asyncio
    async def test_agents_api_lazy_init(self) -> None:
        """Test that agents API is lazily initialized."""
        client = CacpClient(base_url="http://localhost:4001", api_key="key")

        assert client._agents is None
        agents_api = client.agents
        assert client._agents is agents_api

    @pytest.mark.asyncio
    async def test_messaging_api_lazy_init(self) -> None:
        """Test that messaging API is lazily initialized."""
        client = CacpClient(base_url="http://localhost:4001", api_key="key")

        assert client._messaging is None
        messaging_api = client.messaging
        assert client._messaging is messaging_api


class TestClientRequests:
    """Tests for HTTP request handling."""

    @pytest.mark.asyncio
    async def test_successful_request(self) -> None:
        """Test successful HTTP request."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"id": "test-id", "name": "test"}
            mock_response.content = b'{"id": "test-id", "name": "test"}'
            mock_client.request = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            async with CacpClient(base_url="http://localhost:4001", api_key="key") as client:
                result = await client.get("/v1/test")

            assert result["id"] == "test-id"

    @pytest.mark.asyncio
    async def test_authentication_error(self) -> None:
        """Test authentication error handling."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.json.return_value = {"error": "Invalid API key"}
            mock_response.headers = {}
            mock_client.request = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            async with CacpClient(base_url="http://localhost:4001", api_key="invalid") as client:
                with pytest.raises(AuthenticationError):
                    await client.get("/v1/protected")

    @pytest.mark.asyncio
    async def test_not_found_error(self) -> None:
        """Test 404 error handling."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.json.return_value = {"error": "Agent not found"}
            mock_response.headers = {}
            mock_client.request = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            async with CacpClient(base_url="http://localhost:4001", api_key="key") as client:
                with pytest.raises(CacpError) as exc_info:
                    await client.get("/v1/agents/nonexistent")

                assert exc_info.value.code == "NOT_FOUND"
