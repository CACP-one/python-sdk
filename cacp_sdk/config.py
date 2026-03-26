"""
CACP SDK Configuration

Configuration management for the SDK client.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional
import logging


@dataclass
class Config:
    """SDK configuration settings."""

    base_url: str
    api_key: Optional[str] = None
    jwt_token: Optional[str] = None
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_multiplier: float = 2.0
    max_retry_delay: float = 30.0
    connection_pool_size: int = 10
    websocket_reconnect: bool = True
    websocket_reconnect_delay: float = 5.0
    websocket_max_reconnect_attempts: int = 5
    user_agent: str = "cacp-sdk-python/0.1.0"
    verify_ssl: bool = True
    logger: Optional[logging.Logger] = None
    on_request: Optional[Callable[[str, str, Dict[str, Any]], None]] = None
    on_response: Optional[Callable[[str, int, Dict[str, Any]], None]] = None

    @property
    def api_base_url(self) -> str:
        """Get the API base URL."""
        return self.base_url.rstrip("/")

    @property
    def ws_url(self) -> str:
        """Get the WebSocket URL derived from base_url."""
        url = self.base_url.rstrip("/")
        if url.startswith("https://"):
            return url.replace("https://", "wss://")
        elif url.startswith("http://"):
            return url.replace("http://", "ws://")
        return url

    def get_auth_headers(self) -> dict:
        """Get authentication headers based on configured credentials."""
        headers = {}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        elif self.jwt_token:
            headers["Authorization"] = f"Bearer {self.jwt_token}"
        return headers


@dataclass
class RetryConfig:
    """Retry configuration for failed requests."""

    max_retries: int = 3
    retry_delay: float = 1.0
    retry_multiplier: float = 2.0
    max_retry_delay: float = 30.0
    retryable_status_codes: set = field(
        default_factory=lambda: {408, 429, 500, 502, 503, 504}
    )

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for a given retry attempt with exponential backoff."""
        delay = self.retry_delay * (self.retry_multiplier ** (attempt - 1))
        return min(delay, self.max_retry_delay)

    def should_retry(self, status_code: int, attempt: int) -> bool:
        """Determine if a request should be retried."""
        return attempt < self.max_retries and status_code in self.retryable_status_codes
