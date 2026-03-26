"""
Tests for WebSocket client.
"""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cacp_sdk import CacpClient
from cacp_sdk.websocket import WebSocketClient
from cacp_sdk.exceptions import WebSocketError, ConnectionError


class TestWebSocketClient:
    """Tests for WebSocketClient class."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return CacpClient(base_url="http://localhost:4001", api_key="test-key")

    @pytest.fixture
    def ws_client(self, client):
        """Create a WebSocket client."""
        return WebSocketClient(client)

    def test_is_connected_initially_false(self, ws_client):
        """Test that isConnected is initially False."""
        assert ws_client.is_connected is False

    @pytest.mark.asyncio
    async def test_connect_success(self, ws_client):
        """Test successful WebSocket connection."""
        mock_ws = AsyncMock()
        mock_ws.__aiter__ = MagicMock(return_value=iter([]))

        with patch('websockets.connect', new_callable=AsyncMock) as mock_connect:
            mock_connect.return_value = mock_ws

            await ws_client.connect()

            assert ws_client.is_connected is True
            mock_connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_already_connected(self, ws_client):
        """Test connecting when already connected."""
        ws_client._connected = True
        ws_client._ws = AsyncMock()

        with patch('websockets.connect', new_callable=AsyncMock) as mock_connect:
            await ws_client.connect()

            mock_connect.assert_not_called()

    @pytest.mark.asyncio
    async def test_close(self, ws_client):
        """Test closing WebSocket connection."""
        mock_ws = AsyncMock()
        ws_client._ws = mock_ws
        ws_client._connected = True

        await ws_client.close()

        mock_ws.close.assert_called_once()
        assert ws_client.is_connected is False

    @pytest.mark.asyncio
    async def test_close_when_not_connected(self, ws_client):
        """Test closing when not connected."""
        await ws_client.close()  # Should not raise

    @pytest.mark.asyncio
    async def test_subscribe_not_connected(self, ws_client):
        """Test subscribing when not connected raises error."""
        with pytest.raises(WebSocketError, match="not connected"):
            await ws_client.subscribe("agent-123")

    @pytest.mark.asyncio
    async def test_subscribe_success(self, ws_client):
        """Test successful subscription."""
        mock_ws = AsyncMock()
        ws_client._ws = mock_ws
        ws_client._connected = True

        await ws_client.subscribe("agent-123")

        # Check that the subscription was added
        assert "agent-123" in ws_client._subscriptions

    @pytest.mark.asyncio
    async def test_unsubscribe_not_connected(self, ws_client):
        """Test unsubscribing when not connected does nothing."""
        ws_client._subscriptions["agent-123"] = True

        await ws_client.unsubscribe("agent-123")

        # Should not raise, subscription remains since not connected
        assert "agent-123" in ws_client._subscriptions

    @pytest.mark.asyncio
    async def test_unsubscribe_success(self, ws_client):
        """Test successful unsubscription."""
        mock_ws = AsyncMock()
        ws_client._ws = mock_ws
        ws_client._connected = True
        ws_client._subscriptions["agent-123"] = True

        await ws_client.unsubscribe("agent-123")

        assert "agent-123" not in ws_client._subscriptions

    @pytest.mark.asyncio
    async def test_send_not_connected(self, ws_client):
        """Test sending when not connected raises error."""
        with pytest.raises(WebSocketError, match="not connected"):
            await ws_client.send(
                to_agent="agent-456",
                content={"message": "hello"}
            )

    @pytest.mark.asyncio
    async def test_send_success(self, ws_client):
        """Test successful message send."""
        mock_ws = AsyncMock()
        ws_client._ws = mock_ws
        ws_client._connected = True

        await ws_client.send(
            to_agent="agent-456",
            content={"message": "hello"},
            message_type="message"
        )

        mock_ws.send.assert_called_once()
        sent_data = json.loads(mock_ws.send.call_args[0][0])
        assert sent_data["type"] == "message"
        assert sent_data["to_agent"] == "agent-456"
        assert sent_data["content"] == {"message": "hello"}

    @pytest.mark.asyncio
    async def test_send_rpc_not_connected(self, ws_client):
        """Test sending RPC when not connected raises error."""
        with pytest.raises(WebSocketError, match="not connected"):
            await ws_client.send_rpc(
                to_agent="agent-456",
                method="calculate",
                params={"a": 1, "b": 2}
            )

    @pytest.mark.asyncio
    async def test_send_rpc_success(self, ws_client):
        """Test successful RPC send."""
        mock_ws = AsyncMock()
        ws_client._ws = mock_ws
        ws_client._connected = True

        await ws_client.send_rpc(
            to_agent="agent-456",
            method="calculate",
            params={"a": 1, "b": 2},
            request_id="req-123"
        )

        mock_ws.send.assert_called_once()
        sent_data = json.loads(mock_ws.send.call_args[0][0])
        assert sent_data["type"] == "rpc"
        assert sent_data["to_agent"] == "agent-456"
        assert sent_data["method"] == "calculate"
        assert sent_data["params"] == {"a": 1, "b": 2}
        assert sent_data["request_id"] == "req-123"

    @pytest.mark.asyncio
    async def test_send_response_not_connected(self, ws_client):
        """Test sending response when not connected raises error."""
        with pytest.raises(WebSocketError, match="not connected"):
            await ws_client.send_response(
                to_agent="agent-456",
                request_id="req-123",
                result={"sum": 3}
            )

    @pytest.mark.asyncio
    async def test_send_response_success(self, ws_client):
        """Test successful response send."""
        mock_ws = AsyncMock()
        ws_client._ws = mock_ws
        ws_client._connected = True

        await ws_client.send_response(
            to_agent="agent-456",
            request_id="req-123",
            result={"sum": 3}
        )

        mock_ws.send.assert_called_once()
        sent_data = json.loads(mock_ws.send.call_args[0][0])
        assert sent_data["type"] == "rpc_response"
        assert sent_data["to_agent"] == "agent-456"
        assert sent_data["request_id"] == "req-123"
        assert sent_data["result"] == {"sum": 3}

    @pytest.mark.asyncio
    async def test_send_response_with_error(self, ws_client):
        """Test sending error response."""
        mock_ws = AsyncMock()
        ws_client._ws = mock_ws
        ws_client._connected = True

        await ws_client.send_response(
            to_agent="agent-456",
            request_id="req-123",
            error={"code": 400, "message": "Invalid params"}
        )

        mock_ws.send.assert_called_once()
        sent_data = json.loads(mock_ws.send.call_args[0][0])
        assert sent_data["error"] == {"code": 400, "message": "Invalid params"}

    def test_on_message(self, ws_client):
        """Test adding message handler."""
        handler = MagicMock()
        ws_client.on_message(handler)

        assert handler in ws_client._message_handlers

    @pytest.mark.asyncio
    async def test_context_manager(self, client):
        """Test using WebSocket as async context manager."""
        mock_ws = AsyncMock()
        mock_ws.__aiter__ = MagicMock(return_value=iter([]))

        with patch('websockets.connect', new_callable=AsyncMock) as mock_connect:
            mock_connect.return_value = mock_ws

            async with client.websocket as ws:
                assert ws.is_connected is True

            assert ws.is_connected is False
