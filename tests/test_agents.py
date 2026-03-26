"""Tests for the agents API."""

import json

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from cacp_sdk import CacpClient
from cacp_sdk.models import Agent, AgentStatus, AgentList


class TestAgentsAPI:
    """Tests for AgentsAPI."""

    @pytest.mark.asyncio
    async def test_register_agent(self) -> None:
        """Test agent registration."""
        mock_response = {
            "id": "agent_123",
            "name": "test-agent",
            "description": "Test agent",
            "capabilities": ["chat", "code"],
            "status": "offline",
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
                agent = await client.agents.register(
                    name="test-agent",
                    description="Test agent",
                    capabilities=["chat", "code"],
                )

            assert agent.id == "agent_123"
            assert agent.name == "test-agent"
            assert "chat" in agent.capabilities

    @pytest.mark.asyncio
    async def test_get_agent(self) -> None:
        """Test getting an agent by ID."""
        mock_response = {
            "id": "agent_123",
            "name": "test-agent",
            "description": "Test agent",
            "capabilities": ["chat"],
            "status": "online",
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
                agent = await client.agents.get("agent_123")

            assert agent.id == "agent_123"
            assert agent.status == AgentStatus.ONLINE

    @pytest.mark.asyncio
    async def test_list_agents(self) -> None:
        """Test listing agents."""
        mock_response = {
            "agents": [
                {"id": "agent_1", "name": "agent-1", "capabilities": [], "status": "online", "metadata": {}},
                {"id": "agent_2", "name": "agent-2", "capabilities": [], "status": "offline", "metadata": {}},
            ],
            "total": 2,
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
                result = await client.agents.list()

            assert result.total == 2
            assert len(result.agents) == 2

    @pytest.mark.asyncio
    async def test_query_by_capability(self) -> None:
        """Test querying agents by capability."""
        mock_response = {
            "agents": [
                {
                    "id": "agent_1",
                    "name": "code-agent",
                    "capabilities": ["code-generation", "python"],
                    "status": "online",
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
                agents = await client.agents.query_by_capability(
                    capabilities=["code-generation"],
                    match_all=False,
                )

            assert len(agents) == 1
            assert "code-generation" in agents[0].capabilities

    @pytest.mark.asyncio
    async def test_delete_agent(self) -> None:
        """Test deleting an agent."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_resp = MagicMock()
            mock_resp.status_code = 204
            mock_resp.json.return_value = {}
            mock_resp.content = b""
            mock_client.request = AsyncMock(return_value=mock_resp)
            mock_client.aclose = AsyncMock()
            mock_client_class.return_value = mock_client

            async with CacpClient(base_url="http://localhost:4001", api_key="key") as client:
                await client.connect()
                client._http_client.request = AsyncMock(return_value=mock_resp)
                await client.agents.delete("agent_123")

            # Should not raise an exception

    @pytest.mark.asyncio
    async def test_get_health(self) -> None:
        """Test getting agent health status."""
        mock_response = {
            "agent_id": "agent_123",
            "status": "online",
            "health_score": 95.5,
            "metrics": [
                {
                    "agent_id": "agent_123",
                    "metric_name": "response_time",
                    "value": 0.05,
                    "unit": "seconds",
                    "timestamp": "2024-01-01T00:00:00Z",
                }
            ],
            "last_check": "2024-01-01T00:00:00Z",
            "issues": [],
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
                health = await client.agents.get_health("agent_123")

            assert health.agent_id == "agent_123"
            assert health.status == AgentStatus.ONLINE
            assert health.health_score == 95.5
            assert len(health.metrics) == 1
            assert health.metrics[0].metric_name == "response_time"

    @pytest.mark.asyncio
    async def test_set_status(self) -> None:
        """Test setting agent status."""
        mock_response = {
            "id": "agent_123",
            "name": "test-agent",
            "capabilities": ["chat"],
            "status": "maintenance",
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
                agent = await client.agents.set_status("agent_123", "maintenance")

            assert agent.status == AgentStatus.MAINTENANCE

    @pytest.mark.asyncio
    async def test_heartbeat(self) -> None:
        """Test sending a heartbeat."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {}
            mock_resp.content = b""
            mock_client.request = AsyncMock(return_value=mock_resp)
            mock_client.aclose = AsyncMock()
            mock_client_class.return_value = mock_client

            async with CacpClient(base_url="http://localhost:4001", api_key="key") as client:
                await client.connect()
                client._http_client.request = AsyncMock(return_value=mock_resp)
                await client.agents.heartbeat("agent_123")

            # Should not raise an exception
