"""
Phoenix Channel Protocol Implementation

Implements Phoenix Channels WebSocket protocol for CACP WebSocket communication.
Message format: [ref, event, topic, payload]
"""

import asyncio
import json
import logging
import uuid
from typing import TYPE_CHECKING, Any, AsyncIterator, Callable, Dict, List, Optional

import websockets
from websockets.client import WebSocketClientProtocol

from cacp_sdk.exceptions import ConnectionError, WebSocketError

if TYPE_CHECKING:
    from cacp_sdk.client import CacpClient

logger = logging.getLogger(__name__)


class PhoenixMessage:
    """Represents a Phoenix Channel message in tuple format [ref, event, topic, payload]."""

    def __init__(self, ref: str, event: str, topic: str, payload: Optional[Dict[str, Any]] = None):
        self.ref = ref
        self.event = event
        self.topic = topic
        self.payload = payload or {}

    @classmethod
    def from_tuple(cls, message: List[Any]) -> "PhoenixMessage":
        """Create a PhoenixMessage from a tuple [ref, event, topic, payload]."""
        if len(message) < 4:
            raise ValueError(f"Invalid Phoenix message tuple: {message}")
        payload = message[3] if len(message) > 3 else {}
        return cls(ref=str(message[0]), event=str(message[1]), topic=str(message[2]), payload=payload)

    def to_tuple(self) -> List[Any]:
        """Convert to tuple format [ref, event, topic, payload]."""
        return [self.ref, self.event, self.topic, self.payload]

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_tuple())

    @classmethod
    def from_json(cls, json_str: str) -> "PhoenixMessage":
        """Deserialize from JSON string."""
        message = json.loads(json_str)
        if not isinstance(message, list):
            raise ValueError("Phoenix message must be a list")
        return cls.from_tuple(message)


class PhoenixChannel:
    """Represents a Phoenix Channel.Each channel is subscribed to a topic."""

    def __init__(self, topic: str, params: Optional[Dict[str, Any]] = None):
        self.topic = topic
        self.params = params or {}
        self._joined = False
        self._join_event = asyncio.Event()
        self._message_handlers: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}

    @property
    def is_joined(self) -> bool:
        return self._joined

    def on(self, event: str, handler: Callable[[Dict[str, Any]], None]) -> None:
        """Register a handler for a specific event."""
        if event not in self._message_handlers:
            self._message_handlers[event] = []
        self._message_handlers[event].append(handler)

    def emit(self, event: str, payload: Optional[Dict[str, Any]] = None) -> None:
        """Emit an event to registered handlers."""
        if event in self._message_handlers:
            for handler in self._message_handlers[event]:
                try:
                    handler(payload or {})
                except Exception as e:
                    logger.error(f"Error in event handler for {event}: {e}")

    async def wait_until_joined(self, timeout: float = 5.0) -> None:
        """Wait until the channel is joined."""
        try:
            await asyncio.wait_for(self._join_event.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            raise WebSocketError(f"Timeout waiting to join channel: {self.topic}")

    def _mark_joined(self) -> None:
        """Mark the channel as joined."""
        self._joined = True
        self._join_event.set()

    def _reset_join(self) -> None:
        """Reset join state for reconnection."""
        self._joined = False
        self._join_event.clear()


class PhoenixChannelClient:
    """
    Phoenix Channels WebSocket client implementation.

    Implements the Phoenix Channel protocol:
    - Message format: [ref, event, topic, payload]
    - Heartbeat: phx_reply to "phoenix" topic every 30s
    - Channel join: phx_join event
    - Auto-reconnect with exponential backoff
    """

    def __init__(self, client: "CacpClient") -> None:
        self._client = client
        self._config = client.config

        self._ws: Optional[WebSocketClientProtocol] = None
        self._connected = False
        self._reconnect_attempts = 0

        self._message_queue: asyncio.Queue[PhoenixMessage] = asyncio.Queue()
        self._receive_task: Optional[asyncio.Task[None]] = None
        self._heartbeat_task: Optional[asyncio.Task[None]] = None

        self._ref_counter = 0
        self._channels: Dict[str, PhoenixChannel] = {}
        self._global_handlers: List[Callable[[PhoenixMessage], None]] = []

        self._pending_requests: Dict[str, asyncio.Future] = {}

    @property
    def is_connected(self) -> bool:
        return self._connected and self._ws is not None

    async def connect(self) -> "PhoenixChannelClient":
        if self.is_connected:
            return self

        ws_url = f"{self._config.ws_url}/websocket?vsn=2.0.0"

        headers = self._config.get_auth_headers()
        headers["User-Agent"] = self._config.user_agent

        try:
            self._ws = await websockets.connect(
                ws_url,
                extra_headers=headers,
                ping_interval=None,
                ping_timeout=None,
                close_timeout=5,
            )

            self._connected = True
            self._reconnect_attempts = 0

            self._receive_task = asyncio.create_task(self._receive_loop())
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

            logger.info(f"Phoenix Channel connected to {ws_url}")

            await self._resubscribe_channels()

            return self

        except Exception as e:
            self._connected = False
            raise ConnectionError(f"Failed to connect Phoenix Channel: {e}")

    async def close(self) -> None:
        if not self._connected:
            return

        self._connected = False

        if self._receive_task:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass
            self._receive_task = None

        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
            self._heartbeat_task = None

        for channel in list(self._channels.values()):
            await self._leave_channel(channel.topic)

        if self._ws:
            try:
                await self._ws.close()
            except Exception:
                pass
            self._ws = None

        logger.info("Phoenix Channel disconnected")

    async def __aenter__(self) -> "PhoenixChannelClient":
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()

    def channel(self, topic: str, params: Optional[Dict[str, Any]] = None) -> PhoenixChannel:
        """Get or create a channel for the given topic."""
        if topic in self._channels:
            return self._channels[topic]

        channel = PhoenixChannel(topic, params)
        self._channels[topic] = channel
        return channel

    async def join_channel(self, topic: str, params: Optional[Dict[str, Any]] = None) -> PhoenixChannel:
        """Join a Phoenix channel."""
        channel = self.channel(topic, params)

        if channel.is_joined:
            return channel

        message = PhoenixMessage(
            ref=self._next_ref(),
            event="phx_join",
            topic=topic,
            payload=params or {}
        )

        future: asyncio.Future[Dict[str, Any]] = asyncio.Future()
        self._pending_requests[message.ref] = future

        await self._send(message)

        try:
            response = await asyncio.wait_for(future, timeout=5.0)
            if response.get("status") != "ok":
                self._pending_requests.pop(message.ref, None)
                raise WebSocketError(f"Failed to join channel {topic}: {response}")
        except asyncio.TimeoutError:
            self._pending_requests.pop(message.ref, None)
            raise WebSocketError(f"Timeout joining channel {topic}")

        channel._mark_joined()
        logger.info(f"Joined channel: {topic}")

        return channel

    async def leave_channel(self, topic: str) -> None:
        """Leave a Phoenix channel."""
        if topic not in self._channels:
            return

        channel = self._channels[topic]

        if not channel.is_joined:
            return

        message = PhoenixMessage(
            ref=self._next_ref(),
            event="phx_leave",
            topic=topic,
            payload={}
        )

        try:
            await self._send(message)
        except Exception as e:
            logger.warning(f"Error sending leave for channel {topic}: {e}")

        channel._reset_join()
        logger.info(f"Left channel: {topic}")

    async def push(self, topic: str, event: str, payload: Optional[Dict[str, Any]] = None) -> None:
        """Push an event to a channel."""
        message = PhoenixMessage(
            ref=self._next_ref(),
            event=event,
            topic=topic,
            payload=payload or {}
        )

        await self._send(message)

    async def request(
        self,
        topic: str,
        event: str,
        payload: Optional[Dict[str, Any]] = None,
        timeout: float = 5.0
    ) -> Dict[str, Any]:
        """Send a request and wait for response."""
        message = PhoenixMessage(
            ref=self._next_ref(),
            event=event,
            topic=topic,
            payload=payload or {}
        )

        future: asyncio.Future[Dict[str, Any]] = asyncio.Future()
        self._pending_requests[message.ref] = future

        await self._send(message)

        try:
            response = await asyncio.wait_for(future, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            self._pending_requests.pop(message.ref, None)
            raise WebSocketError(f"Timeout waiting for response to {event} on {topic}")
        finally:
            self._pending_requests.pop(message.ref, None)

    def subscribe(self, agent_id: str) -> None:
        """Subscribe to messages for an agent (backward compatibility)."""
        topic = f"agent:{agent_id}"
        self.channel(topic)

    async def unsubscribe(self, agent_id: str) -> None:
        """Unsubscribe from messages for an agent."""
        topic = f"agent:{agent_id}"
        await self.leave_channel(topic)

    async def send(
        self,
        to_agent: str,
        content: Dict[str, Any],
        message_type: str = "message",
        from_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Send a message through WebSocket (backward compatibility)."""
        topic = f"agent:{to_agent}"

        payload = {
            "message": {
                "content": content,
                "message_type": message_type,
            }
        }

        if from_agent:
            payload["message"]["sender"] = {"agent_id": from_agent}
        if metadata:
            payload["message"]["metadata"] = metadata

        await self.push(topic, "send", payload)

    async def send_rpc(
        self,
        to_agent: str,
        method: str,
        params: Dict[str, Any],
        request_id: Optional[str] = None,
        from_agent: Optional[str] = None,
    ) -> None:
        """Send an RPC request through WebSocket."""
        topic = f"agent:{to_agent}"

        payload = {
            "message": {
                "method": method,
                "params": params,
            }
        }

        if request_id:
            payload["message"]["correlation_id"] = request_id
        if from_agent:
            payload["message"]["sender"] = {"agent_id": from_agent}

        await self.push(topic, "rpc_request", payload)

    def on_message(self, handler: Callable[[Dict[str, Any]], None]) -> None:
        """Register a global message handler."""
        self._global_handlers.append(handler)

    async def messages(self) -> AsyncIterator[Dict[str, Any]]:
        """Async iterator for receiving messages."""
        while self.is_connected:
            try:
                phx_message = await asyncio.wait_for(self._message_queue.get(), timeout=1.0)

                if phx_message.event in ["message", "rpc_response", "rpc_error"]:
                    payload = phx_message.payload
                    message = payload.get("message", payload)

                    yield message
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error getting message from queue: {e}")
                break

    async def _send(self, message: PhoenixMessage) -> None:
        """Send a Phoenix message."""
        if not self._ws:
            raise WebSocketError("WebSocket not connected")

        try:
            await self._ws.send(message.to_json())
            logger.debug(f"Sent: {message.event} on {message.topic}")
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            self._connected = False
            raise WebSocketError(f"Failed to send message: {e}")

    async def _receive_loop(self) -> None:
        """Background task to receive and process messages."""
        if not self._ws:
            return

        try:
            async for raw_message in self._ws:
                try:
                    phx_message = PhoenixMessage.from_json(raw_message)
                    await self._handle_message(phx_message)
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"Invalid message received: {e}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

        except websockets.ConnectionClosed as e:
            logger.info(f"Connection closed: {e}")
            self._connected = False

            if self._config.websocket_reconnect:
                await self._attempt_reconnect()

        except Exception as e:
            logger.error(f"Error in receive loop: {e}")
            self._connected = False

    async def _handle_message(self, message: PhoenixMessage) -> None:
        """Handle an incoming Phoenix message."""
        logger.debug(f"Received: {message.event} on {message.topic}")

        if message.event == "phx_reply":
            await self._handle_reply(message)
        elif message.event == "phx_error":
            await self._handle_error(message)
        elif message.event == "phx_close":
            logger.warning(f"Channel closed: {message.topic}")
            if message.topic in self._channels:
                self._channels[message.topic]._reset_join()
        else:
            await self._message_queue.put(message)

        channel = self._channels.get(message.topic)
        if channel:
            channel.emit(message.event, message.payload)

        for handler in self._global_handlers:
            try:
                handler(message.payload)
            except Exception as e:
                logger.error(f"Error in global message handler: {e}")

    async def _handle_reply(self, message: PhoenixMessage) -> None:
        """Handle a phx_reply message."""
        message_ref = message.ref

        if message_ref in self._pending_requests:
            future = self._pending_requests[message_ref]
            if not future.done():
                future.set_result(message.payload)

    async def _handle_error(self, message: PhoenixMessage) -> None:
        """Handle a phx_error message."""
        message_ref = message.ref

        if message_ref in self._pending_requests:
            future = self._pending_requests[message_ref]
            if not future.done():
                future.set_exception(WebSocketError(f"Phoenix error: {message.payload}"))

    async def _heartbeat_loop(self) -> None:
        """Send Phoenix heartbeats every 30s."""
        while self.is_connected:
            try:
                await asyncio.sleep(30)

                if not self.is_connected or not self._ws:
                    break

                message = PhoenixMessage(
                    ref=str(self._next_ref()),
                    event="heartbeat",
                    topic="phoenix",
                    payload={}
                )

                await self._send(message)
                logger.debug("Sent Phoenix heartbeat")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.debug(f"Heartbeat error: {e}")
                break

    def _next_ref(self) -> int:
        """Get next message reference."""
        self._ref_counter += 1
        return self._ref_counter

    async def _attempt_reconnect(self) -> None:
        """Attempt to reconnect with exponential backoff."""
        max_attempts = self._config.websocket_max_reconnect_attempts
        delay = self._config.websocket_reconnect_delay

        while self._reconnect_attempts < max_attempts:
            self._reconnect_attempts += 1
            logger.info(f"Attempting reconnect ({self._reconnect_attempts}/{max_attempts})")

            try:
                await asyncio.sleep(delay * (2 ** (self._reconnect_attempts - 1)))

                for channel in self._channels.values():
                    channel._reset_join()

                await self.connect()
                logger.info("Reconnected successfully")
                return
            except Exception as e:
                logger.warning(f"Reconnect attempt failed: {e}")

        logger.error("Max reconnect attempts reached")
        raise ConnectionError("WebSocket connection lost and reconnect failed")

    async def _resubscribe_channels(self) -> None:
        """Resubscribe to all channels after reconnect."""
        for topic, channel in list(self._channels.items()):
            try:
                await self.join_channel(topic, channel.params)
            except Exception as e:
                logger.warning(f"Failed to resubscribe to {topic}: {e}")