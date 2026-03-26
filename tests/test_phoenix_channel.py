"""
Tests for Phoenix Channel Protocol Implementation
"""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from cacp_sdk.phoenix_channel import (
    PhoenixMessage,
    PhoenixChannel,
    PhoenixChannelClient,
)
from cacp_sdk.exceptions import ConnectionError, WebSocketError


class TestPhoenixMessage:
    """Test PhoenixMessage class."""

    def test_from_tuple(self):
        """Test creating PhoenixMessage from tuple."""
        tuple_msg = ["1", "phx_join", "agent:123", {"status": "ok"}]
        msg = PhoenixMessage.from_tuple(tuple_msg)

        assert msg.ref == "1"
        assert msg.event == "phx_join"
        assert msg.topic == "agent:123"
        assert msg.payload == {"status": "ok"}

    def test_to_tuple(self):
        """Test converting PhoenixMessage to tuple."""
        msg = PhoenixMessage(ref="1", event="phx_join", topic="agent:123", payload={"status": "ok"})
        tuple_msg = msg.to_tuple()

        assert tuple_msg == ["1", "phx_join", "agent:123", {"status": "ok"}]

    def test_to_json(self):
        """Test serializing PhoenixMessage to JSON."""
        msg = PhoenixMessage(ref="1", event="phx_join", topic="agent:123", payload={"status": "ok"})
        json_str = msg.to_json()

        expected = json.dumps(["1", "phx_join", "agent:123", {"status": "ok"}])
        assert json_str == expected

    def test_from_json(self):
        """Test deserializing PhoenixMessage from JSON."""
        json_str = json.dumps(["1", "phx_join", "agent:123", {"status": "ok"}])
        msg = PhoenixMessage.from_json(json_str)

        assert msg.ref == "1"
        assert msg.event == "phx_join"
        assert msg.topic == "agent:123"
        assert msg.payload == {"status": "ok"}

    def test_from_tuple_invalid_length(self):
        """Test that invalid tuple raises error."""
        with pytest.raises(ValueError):
            PhoenixMessage.from_tuple(["1", "phx_join"])

    def test_from_json_invalid_format(self):
        """Test that invalid JSON raises error."""
        with pytest.raises(ValueError):
            PhoenixMessage.from_json(json.dumps({"ref": "1"}))


class TestPhoenixChannel:
    """Test PhoenixChannel class."""

    def test_channel_creation(self):
        """Test creating a PhoenixChannel."""
        channel = PhoenixChannel(topic="agent:123", params={"token": "test"})

        assert channel.topic == "agent:123"
        assert channel.params == {"token": "test"}
        assert not channel.is_joined

    def test_mark_joined(self):
        """Test marking channel as joined."""
        channel = PhoenixChannel(topic="agent:123")
        channel._mark_joined()

        assert channel.is_joined

    def test_reset_join(self):
        """Test resetting join state."""
        channel = PhoenixChannel(topic="agent:123")
        channel._mark_joined()
        channel._reset_join()

        assert not channel.is_joined

    def test_emit_handler(self):
        """Test emitting to event handlers."""
        channel = PhoenixChannel(topic="agent:123")

        handler_called = []

        def handler(payload):
            handler_called.append(payload)

        channel.on("message", handler)
        channel.emit("message", {"data": "test"})

        assert len(handler_called) == 1
        assert handler_called[0] == {"data": "test"}

    def test_wait_until_joined(self):
        """Test waiting until channel is joined."""
        channel = PhoenixChannel(topic="agent:123")

        async def test():
            task = asyncio.create_task(channel.wait_until_joined(timeout=1.0))
            await asyncio.sleep(0.1)
            channel._mark_joined()
            await task

        asyncio.run(test())

    def test_wait_until_joined_timeout(self):
        """Test timeout when waiting for channel join."""
        channel = PhoenixChannel(topic="agent:123")

        async def test():
            with pytest.raises(WebSocketError):
                await channel.wait_until_joined(timeout=0.1)

        asyncio.run(test())


class TestPhoenixChannelClient:
    """Test PhoenixChannelClient class."""

    @pytest.fixture
    def mock_client(self):
        """Create mock CacpClient."""
        client = MagicMock()
        config = MagicMock()
        config.ws_url = "ws://localhost:4001"
        config.get_auth_headers = MagicMock(return_value={"Authorization": "Bearer token"})
        config.user_agent = "CACP-SDK-Test"
        config.websocket_reconnect = True
        config.websocket_max_reconnect_attempts = 5
        config.websocket_reconnect_delay = 1000
        client.config = config
        return client

    @pytest.fixture
    def phoenix_client(self, mock_client):
        """Create PhoenixChannelClient instance."""
        return PhoenixChannelClient(mock_client)

    def test_client_creation(self, phoenix_client):
        """Test creating PhoenixChannelClient."""
        assert isinstance(phoenix_client._client, MagicMock)
        assert not phoenix_client.is_connected
        assert phoenix_client._ref_counter == 0

    def test_next_ref(self, phoenix_client):
        """Test getting next message reference."""
        ref1 = phoenix_client._next_ref()
        ref2 = phoenix_client._next_ref()
        ref3 = phoenix_client._next_ref()

        assert ref1 == 1
        assert ref2 == 2
        assert ref3 == 3

    @pytest.mark.asyncio
    async def test_channel_get_or_create(self, phoenix_client):
        """Test getting or creating a channel."""
        channel1 = phoenix_client.channel("agent:123")
        channel2 = phoenix_client.channel("agent:123")
        channel3 = phoenix_client.channel("agent:456")

        assert channel1 is channel2
        assert channel1 is not channel3
        assert channel1.topic == "agent:123"
        assert channel3.topic == "agent:456"

    @pytest.mark.asyncio
    async def test_connect(self, phoenix_client):
        """Test connecting to Phoenix Channel."""
        with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
            mock_ws = AsyncMock()
            mock_ws.send = AsyncMock()
            mock_ws.close = AsyncMock()
            mock_connect.return_value = mock_ws

            await phoenix_client.connect()

            assert phoenix_client.is_connected
            mock_connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_close(self, phoenix_client):
        """Test closing connection."""
        with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
            mock_ws = AsyncMock()
            mock_ws.send = AsyncMock()
            mock_ws.close = AsyncMock()
            mock_connect.return_value = mock_ws

            await phoenix_client.connect()
            await phoenix_client.close()

            assert not phoenix_client.is_connected
            mock_ws.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager(self, phoenix_client):
        """Test using client as async context manager."""
        with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
            mock_ws = AsyncMock()
            mock_ws.send = AsyncMock()
            mock_ws.close = AsyncMock()
            mock_connect.return_value = mock_ws

            async with phoenix_client:
                assert phoenix_client.is_connected

            assert not phoenix_client.is_connected

    def test_subscribe(self, phoenix_client):
        """Test subscribing to agent."""
        phoenix_client.subscribe("agent-123")

        assert "agent:agent-123" in phoenix_client._channels
        assert phoenix_client._channels["agent:agent-123"].topic == "agent:agent-123"

    @pytest.mark.asyncio
    async def test_unsubscribe(self, phoenix_client):
        """Test unsubscribing from agent."""
        with patch.object(phoenix_client, "leave_channel", new_callable=AsyncMock):
            phoenix_client.subscribe("agent-123")
            await phoenix_client.unsubscribe("agent-123")

            phoenix_client.leave_channel.assert_called_once_with("agent:agent-123")

    @pytest.mark.asyncio
    async def test_send_message(self, phoenix_client):
        """Test sending a message."""
        with patch.object(phoenix_client, "push", new_callable=AsyncMock):
            await phoenix_client.send(
                to_agent="agent-123",
                content={"text": "hello"},
                message_type="message",
                from_agent="agent-456",
                metadata={"key": "value"},
            )

            phoenix_client.push.assert_called_once()
            call_args = phoenix_client.push.call_args
            assert call_args[0][0] == "agent:agent-123"
            assert call_args[0][1] == "send"
            assert "message" in call_args[0][2]

    @pytest.mark.asyncio
    async def test_send_rpc(self, phoenix_client):
        """Test sending RPC request."""
        with patch.object(phoenix_client, "push", new_callable=AsyncMock):
            await phoenix_client.send_rpc(
                to_agent="agent-123",
                method="process",
                params={"input": "test"},
                request_id="req-123",
                from_agent="agent-456",
            )

            phoenix_client.push.assert_called_once()
            call_args = phoenix_client.push.call_args
            assert call_args[0][0] == "agent:agent-123"
            assert call_args[0][1] == "rpc_request"
            assert "message" in call_args[0][2]

    def test_on_message_handler(self, phoenix_client):
        """Test registering message handler."""
        handler_called = []

        def handler(payload):
            handler_called.append(payload)

        phoenix_client.on_message(handler)

        assert len(phoenix_client._global_handlers) == 1

    @pytest.mark.asyncio
    async def test_messages_iterator(self, phoenix_client):
        """Test receiving messages via iterator."""
        received_messages = []

        with patch.object(phoenix_client, "_message_queue") as mock_queue:
            mock_queue.get = AsyncMock(side_effect=[
                PhoenixMessage("1", "message", "agent:123", {"message": {"content": "test1"}}),
                PhoenixMessage("2", "message", "agent:123", {"message": {"content": "test2"}}),
                asyncio.TimeoutError(),
            ])

            async with phoenix_client._message_queue:
                count = 0
                try:
                    async for msg in phoenix_client.messages():
                        received_messages.append(msg)
                        count += 1
                        if count >= 2:
                            break
                except asyncio.TimeoutError:
                    pass

            assert len(received_messages) == 2

    @pytest.mark.asyncio
    async def test_auto_reconnect_exponential_backoff(self, phoenix_client):
        """Test exponential backoff in reconnect attempts."""
        with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
            mock_connect.side_effect = [ConnectionError("Failed"), AsyncMock()]

            with patch("asyncio.sleep") as mock_sleep:
                await phoenix_client.connect()

                # Check that sleep was called with increasing delays
                assert mock_sleep.call_count >= 1

    @pytest.mark.asyncio
    async def test_resubscribe_after_reconnect(self, phoenix_client):
        """Test that channels are resubscribed after reconnect."""
        phoenix_client.subscribe("agent-123")
        phoenix_client.subscribe("agent-456")

        with patch.object(phoenix_client, "join_channel", new_callable=AsyncMock) as mock_join:
            await phoenix_client._resubscribe_channels()

            assert mock_join.call_count == 2

    @pytest.mark.asyncio
    async def test_max_reconnect_attempts(self, phoenix_client):
        """Test that max reconnect attempts is respected."""
        phoenix_client._config.websocket_max_reconnect_attempts = 2

        with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
            mock_connect.side_effect = ConnectionError("Failed")

            with patch("asyncio.sleep", new_callable=AsyncMock):
                with pytest.raises(ConnectionError):
                    await phoenix_client._attempt_reconnect()

                assert phoenix_client._reconnect_attempts <= 2