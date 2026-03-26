"""Tests for the Tasks API."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from cacp_sdk import (
    CacpClient,
    CacpError,
    Task,
    TaskCreate,
    TaskListOptions,
    TaskList,
    TaskStatus,
    TaskNotFoundError,
    TaskStateError,
)


class TestTasksAPI:
    """Tests for TasksAPI."""

    @pytest.mark.asyncio
    async def test_create_task(self) -> None:
        """Test creating a new task."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.json.return_value = {
                "task_id": "task_abc123",
                "task_type": "data-processing",
                "status": "pending",
                "priority": "normal",
                "payload": {"data_source": "s3://bucket/data.csv"},
                "retry_count": 0,
                "max_retries": 3,
                "created_at": datetime.now().isoformat(),
            }
            mock_client.request = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            async with CacpClient(base_url="http://localhost:4001", api_key="key") as client:
                task = await client.tasks.create(
                    task_type="data-processing",
                    payload={"data_source": "s3://bucket/data.csv"},
                    priority="normal",
                )

            assert task.id == "task_abc123"
            assert task.task_type == "data-processing"
            assert task.status == TaskStatus.PENDING

    @pytest.mark.asyncio
    async def test_create_task_with_schedule(self) -> None:
        """Test creating a scheduled task."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.json.return_value = {
                "task_id": "task_def456",
                "task_type": "scheduled-job",
                "status": "pending",
                "priority": "high",
                "retry_count": 0,
                "max_retries": 5,
                "created_at": datetime.now().isoformat(),
                "scheduled_at": datetime.now().isoformat(),
            }
            mock_client.request = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            scheduled_at = datetime.now()
            async with CacpClient(base_url="http://localhost:4001", api_key="key") as client:
                task = await client.tasks.create(
                    task_type="scheduled-job",
                    priority="high",
                    max_retries=5,
                    scheduled_at=scheduled_at,
                )

            assert task.id == "task_def456"
            assert task.max_retries == 5
            assert task.priority == "high"

    @pytest.mark.asyncio
    async def test_list_tasks(self) -> None:
        """Test listing tasks with filters."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "tasks": [
                    {
                        "task_id": "task_1",
                        "task_type": "data-processing",
                        "status": "running",
                        "priority": "normal",
                        "retry_count": 0,
                        "max_retries": 3,
                        "created_at": datetime.now().isoformat(),
                    },
                    {
                        "task_id": "task_2",
                        "task_type": "analysis",
                        "status": "running",
                        "priority": "normal",
                        "retry_count": 1,
                        "max_retries": 3,
                        "created_at": datetime.now().isoformat(),
                    },
                ],
                "count": 2,
            }
            mock_client.request = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            async with CacpClient(base_url="http://localhost:4001", api_key="key") as client:
                tasks = await client.tasks.list(
                    status=TaskStatus.RUNNING,
                    limit=10,
                )

            assert len(tasks.tasks) == 2
            assert tasks.total == 2
            assert all(task.status == TaskStatus.RUNNING for task in tasks.tasks)

    @pytest.mark.asyncio
    async def test_list_tasks_with_filters(self) -> None:
        """Test listing tasks with multiple filters."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "tasks": [
                    {
                        "task_id": "task_1",
                        "task_type": "data-processing",
                        "status": "failed",
                        "priority": "high",
                        "sender_agent_id": "agent_abc",
                        "retry_count": 3,
                        "max_retries": 3,
                        "created_at": datetime.now().isoformat(),
                    },
                ],
                "count": 1,
            }
            mock_client.request = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            async with CacpClient(base_url="http://localhost:4001", api_key="key") as client:
                tasks = await client.tasks.list(
                    status=TaskStatus.FAILED,
                    task_type="data-processing",
                    sender_agent_id="agent_abc",
                    priority="high",
                )

            assert len(tasks.tasks) == 1
            assert tasks.tasks[0].priority == "high"
            assert tasks.tasks[0].sender_agent_id == "agent_abc"

    @pytest.mark.asyncio
    async def test_get_task(self) -> None:
        """Test getting a task by ID."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "task_id": "task_xyz789",
                "task_type": "data-processing",
                "status": "running",
                "priority": "normal",
                "payload": {"data_source": "s3://bucket/data.csv"},
                "result": None,
                "error_message": None,
                "retry_count": 1,
                "max_retries": 3,
                "created_at": datetime.now().isoformat(),
                "started_at": datetime.now().isoformat(),
            }
            mock_client.request = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            async with CacpClient(base_url="http://localhost:4001", api_key="key") as client:
                task = await client.tasks.get("task_xyz789")

            assert task.id == "task_xyz789"
            assert task.status == TaskStatus.RUNNING
            assert task.retry_count == 1

    @pytest.mark.asyncio
    async def test_get_task_not_found(self) -> None:
        """Test getting a non-existent task."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.json.return_value = {
                "error": {"code": 6002, "message": "Task not found"}
            }
            mock_response.headers = {}
            mock_client.request = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            async with CacpClient(base_url="http://localhost:4001", api_key="key") as client:
                with pytest.raises(CacpError) as exc_info:
                    await client.tasks.get("nonexistent_task")

    @pytest.mark.asyncio
    async def test_cancel_task(self) -> None:
        """Test cancelling a task."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "task_id": "task_xyz789",
                "task_type": "data-processing",
                "status": "cancelled",
                "priority": "normal",
                "retry_count": 1,
                "max_retries": 3,
                "created_at": datetime.now().isoformat(),
                "cancelled_at": datetime.now().isoformat(),
            }
            mock_client.request = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            async with CacpClient(base_url="http://localhost:4001", api_key="key") as client:
                task = await client.tasks.cancel("task_xyz789")

            assert task.status == TaskStatus.CANCELLED

    @pytest.mark.asyncio
    async def test_cancel_completed_task(self) -> None:
        """Test cancelling a completed task (should fail)."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_response.json.return_value = {
                "error": {"code": 6004, "message": "Cannot cancel a completed task"}
            }
            mock_response.headers = {}
            mock_client.request = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            async with CacpClient(base_url="http://localhost:4001", api_key="key") as client:
                with pytest.raises(CacpError):
                    await client.tasks.cancel("completed_task")

    @pytest.mark.asyncio
    async def test_retry_task(self) -> None:
        """Test retrying a failed task."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "task_id": "task_xyz789",
                "task_type": "data-processing",
                "status": "queued",
                "priority": "normal",
                "retry_count": 2,
                "max_retries": 3,
                "created_at": datetime.now().isoformat(),
            }
            mock_client.request = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            async with CacpClient(base_url="http://localhost:4001", api_key="key") as client:
                task = await client.tasks.retry("task_xyz789")

            assert task.status == TaskStatus.QUEUED
            assert task.retry_count == 2

    @pytest.mark.asyncio
    async def test_retry_non_retryable_task(self) -> None:
        """Test retrying a task that cannot be retried."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_response.json.return_value = {
                "error": {"code": 6006, "message": "Task cannot be retried"}
            }
            mock_response.headers = {}
            mock_client.request = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            async with CacpClient(base_url="http://localhost:4001", api_key="key") as client:
                with pytest.raises(CacpError):
                    await client.tasks.retry("running_task")

    @pytest.mark.asyncio
    async def test_tasks_api_lazy_init(self) -> None:
        """Test that tasks API is lazily initialized."""
        client = CacpClient(base_url="http://localhost:4001", api_key="key")

        assert client._tasks is None
        tasks_api = client.tasks
        assert client._tasks is tasks_api
        assert client.tasks is tasks_api  # Returns same instance


class TestTaskModels:
    """Tests for Task models."""

    def test_task_status_enum(self) -> None:
        """Test TaskStatus enum values."""
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.QUEUED.value == "queued"
        assert TaskStatus.RUNNING.value == "running"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.CANCELLED.value == "cancelled"

    def test_task_model_from_dict(self) -> None:
        """Test creating Task model from dict."""
        task_data = {
            "task_id": "task_123",
            "task_type": "data-processing",
            "status": "running",
            "priority": "high",
            "payload": {"data": "value"},
            "retry_count": 1,
            "max_retries": 3,
            "created_at": datetime.now().isoformat(),
        }
        task = Task(**task_data)

        assert task.id == "task_123"
        assert task.task_type == "data-processing"
        assert task.status == TaskStatus.RUNNING

    def test_task_create_model(self) -> None:
        """Test TaskCreate model validation."""
        task_create = TaskCreate(
            task_type="data-processing",
            payload={"source": "file.csv"},
            priority="high",
            max_retries=5,
        )

        assert task_create.task_type == "data-processing"
        assert task_create.priority == "high"
        assert task_create.max_retries == 5

    def test_task_list_options_model(self) -> None:
        """Test TaskListOptions model."""
        options = TaskListOptions(
            status=TaskStatus.RUNNING,
            task_type="analysis",
            limit=50,
            offset=10,
        )

        assert options.status == TaskStatus.RUNNING
        assert options.task_type == "analysis"
        assert options.limit == 50
        assert options.offset == 10

    def test_task_list_model(self) -> None:
        """Test TaskList model."""
        task_list = TaskList(
            tasks=[
                Task(
                    task_id="task_1",
                    task_type="test",
                    status=TaskStatus.COMPLETED,
                    priority="normal",
                    created_at=datetime.now(),
                )
            ],
            total=1,
            limit=10,
            offset=0,
        )

        assert len(task_list.tasks) == 1
        assert task_list.total == 1