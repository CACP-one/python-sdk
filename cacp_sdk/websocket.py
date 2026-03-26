"""
CACP SDK WebSocket Client

Real-time bidirectional communication via WebSocket.
"""

import asyncio
import logging
from typing import TYPE_CHECKING, Any, AsyncIterator, Callable, Dict, Optional

from cacp_sdk.exceptions import ConnectionError, WebSocketError
from cacp_sdk.phoenix_channel import PhoenixChannelClient

if TYPE_CHECKING:
    from cacp_sdk.client import CacpClient

logger = logging.getLogger(__name__)


class WebSocketClient:
    """
    WebSocket client for real-time communication.

    Provides:
    - Connection management with auto-reconnect
    - Message subscription
    - Bidirectional messaging
    - Phoenix Channels protocol support
    """

    def __init__(self, client: "CacpClient") -> None:
        """Initialize the WebSocket client."""
        self._client = client
        self._config = client.config
        self._phoenix_client = PhoenixChannelClient(client)

    @property
    def is_connected(self) -> bool:
        """Check if WebSocket is connected."""
        return self._phoenix_client.is_connected

    @property
    def phoenix_client(self) -> PhoenixChannelClient:
        """Get the underlying PhoenixChannelClient."""
        return self._phoenix_client

    async def connect(self) -> "WebSocketClient":
        """
        Connect to the WebSocket endpoint.

        Returns:
            Self for chaining

        Raises:
            ConnectionError: If connection fails
        """
        await self._phoenix_client.connect()
        return self

    async def close(self) -> None:
        """Close the WebSocket connection."""
        await self._phoenix_client.close()

    async def __aenter__(self) -> "WebSocketClient":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def subscribe(self, agent_id: str) -> None:
        """
        Subscribe to messages for an agent.

        Args:
            agent_id: The agent to receive messages for

        Raises:
            WebSocketError: If not connected
        """
        self._phoenix_client.subscribe(agent_id)
        logger.debug(f"Subscribed to messages for agent: {agent_id}")

    async def unsubscribe(self, agent_id: str) -> None:
        """
        Unsubscribe from messages for an agent.

        Args:
            agent_id: The agent to stop receiving messages for
        """
        await self._phoenix_client.unsubscribe(agent_id)
        logger.debug(f"Unsubscribed from messages for agent: {agent_id}")

    async def send(
        self,
        to_agent: str,
        content: Dict[str, Any],
        message_type: str = "message",
        from_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Send a message through WebSocket.

        Args:
            to_agent: Recipient agent ID
            content: Message content
            message_type: Type of message
            from_agent: Sender agent ID (optional)
            metadata: Additional metadata
        """
        await self._phoenix_client.send(
            to_agent=to_agent,
            content=content,
            message_type=message_type,
            from_agent=from_agent,
            metadata=metadata,
        )

    async def send_rpc(
        self,
        to_agent: str,
        method: str,
        params: Dict[str, Any],
        request_id: Optional[str] = None,
        from_agent: Optional[str] = None,
    ) -> None:
        """
        Send an RPC request through WebSocket.

        Args:
            to_agent: Target agent ID
            method: Method to call
            params: Method parameters
            request_id: Request ID for correlation
            from_agent: Sender agent ID
        """
        await self._phoenix_client.send_rpc(
            to_agent=to_agent,
            method=method,
            params=params,
            request_id=request_id,
            from_agent=from_agent,
        )

    async def send_response(
        self,
        to_agent: str,
        request_id: str,
        result: Any = None,
        error: Optional[Dict[str, Any]] = None,
        from_agent: Optional[str] = None,
    ) -> None:
        """
        Send an RPC response through WebSocket.

        Args:
            to_agent: Target agent ID
            request_id: Original request ID
            result: Result data
            error: Error data if failed
            from_agent: Sender agent ID
        """
        topic = f"agent:{to_agent}"

        payload: Dict[str, Any] = {
            "request_id": request_id,
        }

        if result is not None:
            payload["result"] = result
        if error:
            payload["error"] = error

        await self._phoenix_client.push(topic, "rpc_response", payload)

    def on_message(self, handler: Callable[[Dict[str, Any]], None]) -> None:
        """
        Register a message handler.

        Args:
            handler: Function to call for each received message
        """
        self._phoenix_client.on_message(handler)

    async def messages(self) -> AsyncIterator[Dict[str, Any]]:
        """
        Async iterator for receiving messages.

        Yields:
            Message dictionaries as they arrive

        Example:
            ```python
            async with client.websocket.connect() as ws:
                await ws.subscribe(agent_id="my-agent")

                async for message in ws.messages():
                    print(f"Received: {message}")
                    # Handle message...
            ```
        """
        async for message in self._phoenix_client.messages():
            yield message