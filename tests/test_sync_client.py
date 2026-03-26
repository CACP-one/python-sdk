"""
Tests for Synchronous CACP Client
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

from cacp_sdk.sync_client import (
    SyncCacpClient,
    SyncAgentsAPI,
    SyncMessagingAPI,
    SyncTasksAPI,
    SyncGroupsAPI,
)
from cacp_sdk.models import Agent, Message, MessageType, MessageStatus
from cacp_sdk.tasks import Task
from cacp_sdk.groups import Group


class TestSyncAgentsAPI:
    """Tests for SyncAgentsAPI wrapper."""

    @pytest.fixture
    def mock_async_agents_api(self):
        api = Mock()
        api.register = AsyncMock()
        api.list = AsyncMock()
        api.get = AsyncMock()
        api.update = AsyncMock()
        api.delete = AsyncMock()
        api.query_by_capability = AsyncMock()
        api.health_check = AsyncMock()
        return api

    @pytest.fixture
    def sync_agents(self, mock_async_agents_api):
        return SyncAgentsAPI(mock_async_agents_api)

    def test_register(self, sync_agents, mock_async_agents_api):
        mock_agent = Agent(
            id="agent-123",
            name="Test Agent",
            capabilities=["test"],
            description="A test agent",
            metadata={},
            status="online",
        )
        mock_async_agents_api.register.return_value = mock_agent

        result = sync_agents.register(
            name="Test Agent",
            capabilities=["test"],
            description="A test agent",
            metadata={},
        )

        assert isinstance(result, Agent)
        assert result.id == "agent-123"
        mock_async_agents_api.register.assert_called_once()

    def test_list(self, sync_agents, mock_async_agents_api):
        mock_agents = [Mock(id=idx) for idx in range(3)]
        mock_async_agents_api.list.return_value = mock_agents

        result = sync_agents.list(limit=100, offset=0)

        assert len(result) == 3
        mock_async_agents_api.list.assert_called_once_with(limit=100, offset=0)

    def test_get(self, sync_agents, mock_async_agents_api):
        mock_agent = Mock(id="agent-123")
        mock_async_agents_api.get.return_value = mock_agent

        result = sync_agents.get("agent-123")

        assert result.id == "agent-123"
        mock_async_agents_api.get.assert_called_once_with("agent-123")

    def test_update(self, sync_agents, mock_async_agents_api):
        mock_agent = Mock(id="agent-123")
        mock_async_agents_api.update.return_value = mock_agent

        result = sync_agents.update("agent-123", name="Updated Name")

        assert result.id == "agent-123"
        mock_async_agents_api.update.assert_called_once_with(
            agent_id="agent-123",
            name="Updated Name",
            description=None,
            capabilities=None,
            metadata=None,
        )

    def test_query_by_capability(self, sync_agents, mock_async_agents_api):
        mock_agents = [Mock(id=idx) for idx in range(2)]
        mock_async_agents_api.query_by_capability.return_value = mock_agents

        result = sync_agents.query_by_capability(["test"], limit=10)

        assert len(result) == 2
        mock_async_agents_api.query_by_capability.assert_called_once()

    def test_health_check(self, sync_agents, mock_async_agents_api):
        mock_health = {"status": "healthy", "last_seen": "2024-01-01"}
        mock_async_agents_api.health_check.return_value = mock_health

        result = sync_agents.health_check("agent-123")

        assert result["status"] == "healthy"
        mock_async_agents_api.health_check.assert_called_once_with("agent-123")


class TestSyncMessagingAPI:
    """Tests for SyncMessagingAPI wrapper."""

    @pytest.fixture
    def mock_async_messaging_api(self):
        api = Mock()
        api.send = AsyncMock()
        api.send_rpc = AsyncMock()
        api.get = AsyncMock()
        api.list = AsyncMock()
        api.get_sent_by_agent = AsyncMock()
        api.get_sent_to_agent = AsyncMock()
        return api

    @pytest.fixture
    def sync_messaging(self, mock_async_messaging_api):
        return SyncMessagingAPI(mock_async_messaging_api)

    def test_send(self, sync_messaging, mock_async_messaging_api):
        mock_message = Mock(id="msg-123")
        mock_async_messaging_api.send.return_value = mock_message

        result = sync_messaging.send(to="agent-456", content="Hello")

        assert result.id == "msg-123"
        mock_async_messaging_api.send.assert_called_once()

    def test_send_rpc(self, sync_messaging, mock_async_messaging_api):
        mock_response = {"result": "success"}
        mock_async_messaging_api.send_rpc.return_value = mock_response

        result = sync_messaging.send_rpc(to="agent-456", method="test_method")

        assert result["result"] == "success"
        mock_async_messaging_api.send_rpc.assert_called_once_with(
            to="agent-456", method="test_method", params=None, timeout=30.0
        )

    def test_get(self, sync_messaging, mock_async_messaging_api):
        mock_message = Mock(id="msg-123")
        mock_async_messaging_api.get.return_value = mock_message

        result = sync_messaging.get("msg-123")

        assert result.id == "msg-123"
        mock_async_messaging_api.get.assert_called_once_with("msg-123")

    def test_list(self, sync_messaging, mock_async_messaging_api):
        mock_messages = [Mock(id=idx) for idx in range(3)]
        mock_async_messaging_api.list.return_value = mock_messages

        result = sync_messaging.list(limit=10)

        assert len(result) == 3
        mock_async_messaging_api.list.assert_called_once_with(
            limit=10, offset=0, message_type=None, before=None, after=None
        )


class TestSyncTasksAPI:
    """Tests for SyncTasksAPI wrapper."""

    @pytest.fixture
    def mock_async_tasks_api(self):
        api = Mock()
        api.create = AsyncMock()
        api.get = AsyncMock()
        api.list = AsyncMock()
        api.cancel = AsyncMock()
        api.wait_for_completion = AsyncMock()
        return api

    @pytest.fixture
    def sync_tasks(self, mock_async_tasks_api):
        return SyncTasksAPI(mock_async_tasks_api)

    def test_create(self, sync_tasks, mock_async_tasks_api):
        mock_task = Task(
            id="task-123",
            task_type="test_type",
            status="pending",
            payload={"key": "value"},
            created_at=datetime.now(),
        )
        mock_async_tasks_api.create.return_value = mock_task

        result = sync_tasks.create(
            task_type="test_type",
            input_data={"key": "value"},
        )

        assert isinstance(result, Task)
        assert result.id == "task-123"
        mock_async_tasks_api.create.assert_called_once()

    def test_get(self, sync_tasks, mock_async_tasks_api):
        mock_task = Mock(id="task-123")
        mock_async_tasks_api.get.return_value = mock_task

        result = sync_tasks.get("task-123")

        assert result.id == "task-123"
        mock_async_tasks_api.get.assert_called_once_with("task-123")

    def test_list(self, sync_tasks, mock_async_tasks_api):
        mock_tasks = [Mock(id=idx) for idx in range(2)]
        mock_async_tasks_api.list.return_value = mock_tasks

        result = sync_tasks.list(status="pending")

        assert len(result) == 2
        mock_async_tasks_api.list.assert_called_once_with(status="pending", limit=100, offset=0)

    def test_cancel(self, sync_tasks, mock_async_tasks_api):
        mock_task = Mock(id="task-123", status="cancelled")
        mock_async_tasks_api.cancel.return_value = mock_task

        result = sync_tasks.cancel("task-123")

        assert result.status == "cancelled"
        mock_async_tasks_api.cancel.assert_called_once_with("task-123")

    def test_wait_for_completion(self, sync_tasks, mock_async_tasks_api):
        mock_task = Task(
            id="task-123",
            task_type="test_type",
            status="completed",
            payload={},
            result={"output": "done"},
            created_at=datetime.now(),
        )
        mock_async_tasks_api.wait_for_completion.return_value = mock_task

        result = sync_tasks.wait_for_completion("task-123")

        assert result.status == "completed"
        assert result.result == {"output": "done"}
        mock_async_tasks_api.wait_for_completion.assert_called_once()


class TestSyncGroupsAPI:
    """Tests for SyncGroupsAPI wrapper."""

    @pytest.fixture
    def mock_async_groups_api(self):
        api = Mock()
        api.create = AsyncMock()
        api.get = AsyncMock()
        api.list = AsyncMock()
        api.update = AsyncMock()
        api.delete = AsyncMock()
        api.add_member = AsyncMock()
        api.remove_member = AsyncMock()
        api.broadcast = AsyncMock()
        return api

    @pytest.fixture
    def sync_groups(self, mock_async_groups_api):
        return SyncGroupsAPI(mock_async_groups_api)

    def test_create(self, sync_groups, mock_async_groups_api):
        mock_group = Group(id="group-123", name="Test Group")
        mock_async_groups_api.create.return_value = mock_group

        result = sync_groups.create(name="Test Group")

        assert isinstance(result, Group)
        assert result.id == "group-123"
        mock_async_groups_api.create.assert_called_once()

    def test_get(self, sync_groups, mock_async_groups_api):
        mock_group = Mock(id="group-123")
        mock_async_groups_api.get.return_value = mock_group

        result = sync_groups.get("group-123")

        assert result.id == "group-123"
        mock_async_groups_api.get.assert_called_once_with("group-123")

    def test_list(self, sync_groups, mock_async_groups_api):
        mock_groups = [Mock(id=idx) for idx in range(2)]
        mock_async_groups_api.list.return_value = mock_groups

        result = sync_groups.list()

        assert len(result) == 2
        mock_async_groups_api.list.assert_called_once_with(limit=100, offset=0)

    def test_add_member(self, sync_groups, mock_async_groups_api):
        mock_member = Mock(agent_id="agent-456", role="member")
        mock_async_groups_api.add_member.return_value = mock_member

        result = sync_groups.add_member("group-123", "agent-456")

        assert result.agent_id == "agent-456"
        mock_async_groups_api.add_member.assert_called_once_with(
            group_id="group-123", agent_id="agent-456", role="member"
        )

    def test_remove_member(self, sync_groups, mock_async_groups_api):
        mock_async_groups_api.remove_member.return_value = None

        result = sync_groups.remove_member("group-123", "agent-456")

        assert result is None
        mock_async_groups_api.remove_member.assert_called_once_with(
            group_id="group-123", agent_id="agent-456"
        )


class TestSyncCacpClient:
    """Tests for SyncCacpClient main class."""

    @pytest.fixture
    def mock_async_client(self):
        client = Mock()
        client.connect = AsyncMock()
        client.close = AsyncMock()
        client.config = Mock()
        return client

    @pytest.fixture
    def sync_client(self, mock_async_client):
        with patch("cacp_sdk.sync_client.CacpClient", return_value=mock_async_client):
            return SyncCacpClient(base_url="http://localhost:4001", api_key="test_key")

    def test_initialization(self, sync_client):
        assert sync_client._connected is False
        assert sync_client._agents is None
        assert sync_client._messaging is None

    def test_context_manager(self, sync_client, mock_async_client):
        with sync_client:
            assert sync_client._connected is True
            mock_async_client.connect.assert_called_once()

        assert sync_client._connected is False
        mock_async_client.close.assert_called_once()

    def test_manual_connect_close(self, sync_client, mock_async_client):
        sync_client.connect()
        assert sync_client._connected is True
        mock_async_client.connect.assert_called_once()

        sync_client.close()
        assert sync_client._connected is False
        mock_async_client.close.assert_called_once()

    def test_agents_property(self, sync_client, mock_async_client):
        agents_api = sync_client.agents
        assert isinstance(agents_api, SyncAgentsAPI)
        assert sync_client._agents is agents_api

        second_call = sync_client.agents
        assert second_call is agents_api

    def test_messaging_property(self, sync_client, mock_async_client):
        messaging_api = sync_client.messaging
        assert isinstance(messaging_api, SyncMessagingAPI)
        assert sync_client._messaging is messaging_api

    def test_tasks_property(self, sync_client, mock_async_client):
        tasks_api = sync_client.tasks
        assert isinstance(tasks_api, SyncTasksAPI)
        assert sync_client._tasks is tasks_api

    def test_groups_property(self, sync_client, mock_async_client):
        groups_api = sync_client.groups
        assert isinstance(groups_api, SyncGroupsAPI)
        assert sync_client._groups is groups_api

    def test_config_property(self, sync_client):
        config = sync_client.config
        assert config is sync_client._async_client.config


class TestSyncVsAsyncConsistency:
    """Tests comparing sync and async results."""

    def test_sync_async_same_result_register(self):
        async def async_register(**kwargs):
            return Agent(
                id="agent-123",
                name="Test",
                capabilities=["test"],
                description="",
                metadata={},
                status="online",
            )

        mock_api = Mock()
        mock_api.register = AsyncMock(side_effect=async_register)

        sync_api = SyncAgentsAPI(mock_api)
        result = sync_api.register(name="Test", capabilities=["test"])

        assert result.id == "agent-123"
        assert result.name == "Test"

    def test_sync_async_same_result_send(self):
        async def async_send(**kwargs):
            return Message(
                id="msg-123",
                from_agent="agent-1",
                to_agent="agent-2",
                content={"text": "Hello"},
                message_type=MessageType.MESSAGE,
                status=MessageStatus.DELIVERED,
                created_at=datetime.now(),
            )

        mock_api = Mock()
        mock_api.send = AsyncMock(side_effect=async_send)

        sync_api = SyncMessagingAPI(mock_api)
        result = sync_api.send(to="agent-2", content={"text": "Hello"})

        assert result.id == "msg-123"

    def test_multiple_sync_calls(self):
        counter = [0]

        async def async_increment(**kwargs):
            counter[0] += 1
            return [Mock(id=f"agent-{counter[0]}")]

        mock_api = Mock()
        mock_api.list = AsyncMock(side_effect=async_increment)

        sync_api = SyncAgentsAPI(mock_api)
        result1 = sync_api.list()
        result2 = sync_api.list()

        assert len(result1) == 1
        assert len(result2) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
