"""
CACP SDK Messaging API

Message sending, receiving, and RPC operations.
"""

import asyncio
import time
import uuid
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from cacp_sdk.exceptions import MessageError, RpcError, TimeoutError
from cacp_sdk.models import (
    BroadcastMessage,
    Message,
    MessageSend,
    MessageStatus,
    MessageType,
    RpcRequest,
    RpcResponse,
)

if TYPE_CHECKING:
    from cacp_sdk.client import CacpClient


class MessagingAPI:
    """
    API for messaging operations.

    Provides methods for:
    - Sending messages between agents
    - RPC-style calls with responses
    - Broadcasting messages
    - Message status tracking
    """

    def __init__(self, client: "CacpClient") -> None:
        """Initialize the messaging API."""
        self._client = client

    async def send(
        self,
        to_agent: str,
        content: Dict[str, Any],
        message_type: str = "message",
        priority: str = "normal",
        metadata: Optional[Dict[str, Any]] = None,
        ttl: Optional[int] = None,
    ) -> Message:
        """
        Send a message to another agent.

        Args:
            to_agent: Recipient agent ID
            content: Message content (any JSON-serializable dict)
            message_type: Type of message (message, request, notification)
            priority: Message priority (low, normal, high, urgent)
            metadata: Additional metadata
            ttl: Time-to-live in seconds

        Returns:
            The sent Message object with ID and status

        Example:
            ```python
            message = await client.messaging.send(
                to_agent="data-processor",
                content={"action": "analyze", "data": [1, 2, 3]},
                message_type="request",
                priority="high"
            )
            print(f"Sent message: {message.id}")
            ```
        """
        message_data = MessageSend(
            to_agent=to_agent,
            content=content,
            message_type=MessageType(message_type),
            priority=priority,
            metadata=metadata,
            ttl=ttl,
        )

        response = await self._client.post(
            "/v1/messages",
            json_data=message_data.model_dump(exclude_none=True),
        )

        return Message(**response)

    async def get(self, message_id: str) -> Message:
        """
        Get a message by ID.

        Args:
            message_id: The unique message identifier

        Returns:
            The Message object with current status
        """
        response = await self._client.get(f"/v1/messages/{message_id}")
        return Message(**response)

    async def get_status(self, message_id: str) -> MessageStatus:
        """
        Get the status of a message.

        Args:
            message_id: The message to check

        Returns:
            Current message status
        """
        message = await self.get(message_id)
        return message.status

    async def wait_for_completion(
        self,
        message_id: str,
        timeout: float = 60.0,
        poll_interval: float = 1.0,
    ) -> Message:
        """
        Wait for a message to complete.

        Polls the message status until it reaches a terminal state
        (completed, failed, or timeout).

        Args:
            message_id: The message to wait for
            timeout: Maximum time to wait in seconds
            poll_interval: Time between status checks

        Returns:
            The completed Message object

        Raises:
            TimeoutError: If the wait times out
            MessageError: If the message fails
        """
        start_time = time.monotonic()

        while True:
            message = await self.get(message_id)

            if message.status == MessageStatus.COMPLETED:
                return message

            if message.status == MessageStatus.FAILED:
                raise MessageError(
                    message=message.error or "Message failed",
                    message_id=message_id,
                )

            if message.status == MessageStatus.TIMEOUT:
                raise TimeoutError(
                    operation=f"wait_for_message({message_id})",
                    timeout=timeout,
                )

            elapsed = time.monotonic() - start_time
            if elapsed >= timeout:
                raise TimeoutError(
                    operation=f"wait_for_message({message_id})",
                    timeout=timeout,
                )

            await asyncio.sleep(poll_interval)

    async def rpc_call(
        self,
        to_agent: str,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: float = 30.0,
    ) -> RpcResponse:
        """
        Make an RPC call to another agent.

        Sends a request and waits for a response. This is a blocking call
        that waits for the remote agent to process the request and respond.

        Args:
            to_agent: Target agent ID
            method: Method name to call on the remote agent
            params: Parameters to pass to the method
            timeout: Maximum time to wait for response

        Returns:
            The RPC response with result or error

        Raises:
            TimeoutError: If the call times out
            RpcError: If the remote agent returns an error

        Example:
            ```python
            response = await client.messaging.rpc_call(
                to_agent="calculator-agent",
                method="add",
                params={"a": 10, "b": 20}
            )
            print(f"Result: {response.result}")  # 30
            ```
        """
        request_id = str(uuid.uuid4())

        rpc_request = RpcRequest(
            to_agent=to_agent,
            method=method,
            params=params or {},
            timeout=timeout,
            id=request_id,
        )

        # Send the RPC request
        response = await self._client.post(
            "/v1/messages/rpc",
            json_data=rpc_request.model_dump(exclude_none=True),
            timeout=timeout + 5.0,  # Extra buffer for network
        )

        # Parse the response
        rpc_response = RpcResponse(**response)

        if rpc_response.error:
            raise RpcError(
                message=rpc_response.error.get("message", "RPC call failed"),
                method=method,
                rpc_code=rpc_response.error.get("code"),
            )

        return rpc_response

    async def broadcast(
        self,
        content: Dict[str, Any],
        message_type: str = "broadcast",
        capability_filter: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Message]:
        """
        Broadcast a message to all agents or agents with specific capabilities.

        Args:
            content: Message content
            message_type: Type of broadcast message
            capability_filter: Only send to agents with these capabilities
            metadata: Additional metadata

        Returns:
            List of sent messages (one per recipient)

        Example:
            ```python
            # Broadcast to all agents
            messages = await client.messaging.broadcast(
                content={"event": "system_shutdown", "in": 300}
            )

            # Broadcast only to agents with "notifications" capability
            messages = await client.messaging.broadcast(
                content={"alert": "High CPU usage detected"},
                capability_filter=["notifications"]
            )
            ```
        """
        broadcast_data = BroadcastMessage(
            content=content,
            message_type=MessageType(message_type),
            capability_filter=capability_filter,
            metadata=metadata,
        )

        response = await self._client.post(
            "/v1/messages/broadcast",
            json_data=broadcast_data.model_dump(exclude_none=True),
        )

        return [Message(**msg_data) for msg_data in response.get("messages", [])]

    async def cancel(self, message_id: str) -> None:
        """
        Cancel a pending message.

        Args:
            message_id: The message to cancel

        Note:
            Only messages that haven't been delivered can be cancelled.
        """
        await self._client.delete(f"/v1/messages/{message_id}")

    async def retry(self, message_id: str) -> Message:
        """
        Retry a failed message.

        Args:
            message_id: The failed message to retry

        Returns:
            The new Message object
        """
        response = await self._client.post(f"/v1/messages/{message_id}/retry")
        return Message(**response)
