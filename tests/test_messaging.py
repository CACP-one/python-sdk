"""Tests for the messaging API."""

import json

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from cacp_sdk import CacpClient
from cacp_sdk.models import Message, MessageStatus, MessageType


class TestMessagingAPI:
    """Tests for MessagingAPI."""

    @pytest.mark.asyncio
    async def test_send_message(self) -> None:
        """Test sending a message."""
        mock_response = {
            "id": "msg_123",
            "to_agent": "agent_456",
            "content": {"text": "Hello"},
            "message_type": "message",
            "status": "pending",
            "priority": "normal",
            "metadata": {},
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_resp = MagicMock()
            mock_resp.status_code = 201
            mock_resp.json.return_value = mock_response
            mock_resp.content = json.dumps(mock_response).encode()
            mock_client.request = AsyncMock(return_value=mock_resp)
            mock_client.aclose = AsyncMock()
            mock_client_class.return_value = mock_client

            async with CacpClient(base_url="http://localhost:4001", api_key="key") as client:
                await client.connect()
                client._http_client.request = AsyncMock(return_value=mock_resp)
                message = await client.messaging.send(
                    to_agent="agent_456",
                    content={"text": "Hello"},
                )

            assert message.id == "msg_123"
            assert message.to_agent == "agent_456"
            assert message.status == MessageStatus.PENDING

    @pytest.mark.asyncio
    async def test_get_message(self) -> None:
        """Test getting a message by ID."""
        mock_response = {
            "id": "msg_123",
            "to_agent": "agent_456",
            "from_agent": "agent_789",
            "content": {"text": "Hello"},
            "message_type": "message",
            "status": "delivered",
            "priority": "normal",
            "metadata": {},
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = mock_response
            mock_resp.content = json.dumps(mock_response).encode()
            mock_client.request = AsyncMock(return_value=mock_resp)
            mock_client.aclose = AsyncMock()
            mock_client_class.return_value = mock_client

            async with CacpClient(base_url="http://localhost:4001", api_key="key") as client:
                await client.connect()
                client._http_client.request = AsyncMock(return_value=mock_resp)
                message = await client.messaging.get("msg_123")

            assert message.id == "msg_123"
            assert message.status == MessageStatus.DELIVERED

    @pytest.mark.asyncio
    async def test_rpc_call(self) -> None:
        """Test RPC call."""
        mock_response = {
            "id": "rpc_123",
            "from_agent": "agent_456",
            "result": {"sum": 30},
            "error": None,
            "execution_time": 0.05,
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = mock_response
            mock_resp.content = json.dumps(mock_response).encode()
            mock_client.request = AsyncMock(return_value=mock_resp)
            mock_client.aclose = AsyncMock()
            mock_client_class.return_value = mock_client

            async with CacpClient(base_url="http://localhost:4001", api_key="key") as client:
                await client.connect()
                client._http_client.request = AsyncMock(return_value=mock_resp)
                response = await client.messaging.rpc_call(
                    to_agent="agent_456",
                    method="add",
                    params={"a": 10, "b": 20},
                )

            assert response.id == "rpc_123"
            assert response.result == {"sum": 30}

    @pytest.mark.asyncio
    async def test_broadcast(self) -> None:
        """Test broadcasting a message."""
        mock_response = {
            "messages": [
                {
                    "id": "msg_1",
                    "to_agent": "agent_1",
                    "content": {"event": "test"},
                    "message_type": "broadcast",
                    "status": "pending",
                    "priority": "normal",
                    "metadata": {},
                },
                {
                    "id": "msg_2",
                    "to_agent": "agent_2",
                    "content": {"event": "test"},
                    "message_type": "broadcast",
                    "status": "pending",
                    "priority": "normal",
                    "metadata": {},
                },
            ]
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = mock_response
            mock_resp.content = json.dumps(mock_response).encode()
            mock_client.request = AsyncMock(return_value=mock_resp)
            mock_client.aclose = AsyncMock()
            mock_client_class.return_value = mock_client

            async with CacpClient(base_url="http://localhost:4001", api_key="key") as client:
                await client.connect()
                client._http_client.request = AsyncMock(return_value=mock_resp)
                messages = await client.messaging.broadcast(
                    content={"event": "test"},
                )

            assert len(messages) == 2
            assert messages[0].message_type == MessageType.BROADCAST
