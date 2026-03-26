"""
CACP SDK Tasks API

Task management for long-running asynchronous operations.
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from cacp_sdk.client import CacpClient


class TaskStatus(str, Enum):
    """Task status enumeration."""

    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task(BaseModel):
    """Represents a task."""

    id: str = Field(..., alias="task_id", description="Unique task identifier")
    task_type: str = Field(..., description="Type of the task")
    status: TaskStatus = Field(..., description="Current task status")
    priority: str = Field("normal", description="Task priority (low, normal, high, urgent)")
    sender_agent_id: Optional[str] = Field(None, description="Sender agent ID")
    recipient_agent_id: Optional[str] = Field(None, description="Recipient agent ID")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Task payload")
    result: Optional[Dict[str, Any]] = Field(None, description="Task result if completed")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    retry_count: int = Field(0, description="Number of retry attempts")
    max_retries: int = Field(3, description="Maximum retry attempts")
    created_at: datetime = Field(..., description="Creation timestamp")
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled execution time")
    started_at: Optional[datetime] = Field(None, description="Execution start time")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": "task_xyz789",
                    "task_type": "data-processing",
                    "status": "running",
                    "priority": "high",
                    "sender_agent_id": "agent_abc123",
                    "recipient_agent_id": "agent_def456",
                    "payload": {"data_source": "s3://bucket/data.csv"},
                    "retry_count": 0,
                    "max_retries": 3,
                }
            ]
        },
    }


class TaskCreate(BaseModel):
    """Request model for creating a task."""

    task_type: str = Field(..., min_length=1, description="Type of task to create")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Task payload")
    priority: str = Field("normal", description="Task priority")
    recipient_agent_id: Optional[str] = Field(None, description="Target agent ID")
    scheduled_at: Optional[datetime] = Field(None, description="Schedule for later execution")
    max_retries: int = Field(3, ge=0, le=10, description="Maximum retry attempts")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class TaskListOptions(BaseModel):
    """Options for listing tasks."""

    status: Optional[TaskStatus] = Field(None, description="Filter by status")
    task_type: Optional[str] = Field(None, description="Filter by task type")
    sender_agent_id: Optional[str] = Field(None, description="Filter by sender agent")
    recipient_agent_id: Optional[str] = Field(None, description="Filter by recipient agent")
    priority: Optional[str] = Field(None, description="Filter by priority")
    limit: int = Field(100, ge=1, le=1000, description="Maximum results")
    offset: int = Field(0, ge=0, description="Result offset")


class TaskList(BaseModel):
    """Paginated list of tasks."""

    tasks: List[Task] = Field(default_factory=list)
    total: int = Field(0, description="Total number of tasks")
    limit: int = Field(100, description="Page size")
    offset: int = Field(0, description="Page offset")


class TasksAPI:
    """
    API for task management operations.

    Provides methods for:
    - Creating and managing long-running asynchronous tasks
    - Monitoring task status and results
    - Cancelling and retrying failed tasks
    - Listing and filtering tasks
    """

    def __init__(self, client: "CacpClient") -> None:
        """Initialize the tasks API."""
        self._client = client

    async def create(
        self,
        task_type: str,
        payload: Optional[Dict[str, Any]] = None,
        priority: str = "normal",
        recipient_agent_id: Optional[str] = None,
        scheduled_at: Optional[datetime] = None,
        max_retries: int = 3,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Task:
        """
        Create a new task.

        Args:
            task_type: Type of task to create
            payload: Task payload data
            priority: Task priority (low, normal, high, urgent)
            recipient_agent_id: Target agent ID (optional)
            scheduled_at: Schedule for later execution
            max_retries: Maximum retry attempts
            metadata: Additional metadata

        Returns:
            The created Task object

        Raises:
            TaskError: If task creation fails
            ValidationError: If parameters are invalid

        Example:
            ```python
            task = await client.tasks.create(
                task_type="data-processing",
                payload={"data_source": "s3://bucket/data.csv"},
                priority="high"
            )
            print(f"Created task: {task.id}")
            ```
        """
        create_data = {
            "task_type": task_type,
            "payload": payload or {},
            "priority": priority,
            "recipient_agent_id": recipient_agent_id,
            "max_retries": max_retries,
        }

        if scheduled_at:
            create_data["scheduled_at"] = scheduled_at.isoformat()

        if metadata:
            create_data["metadata"] = metadata

        response = await self._client.post("/v1/tasks", json_data=create_data)
        return Task(**response)

    async def list(
        self,
        status: Optional[TaskStatus] = None,
        task_type: Optional[str] = None,
        sender_agent_id: Optional[str] = None,
        recipient_agent_id: Optional[str] = None,
        priority: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> TaskList:
        """
        List tasks with optional filters.

        Args:
            status: Filter by task status
            task_type: Filter by task type
            sender_agent_id: Filter by sender agent
            recipient_agent_id: Filter by recipient agent
            priority: Filter by priority
            limit: Maximum number of results
            offset: Result offset for pagination

        Returns:
            Paginated list of tasks

        Example:
            ```python
            tasks = await client.tasks.list(
                status=TaskStatus.RUNNING,
                limit=10
            )
            print(f"Found {len(tasks.tasks)} running tasks")
            ```
        """
        params: Dict[str, Any] = {"limit": limit, "offset": offset}

        if status:
            params["status"] = status.value
        if task_type:
            params["task_type"] = task_type
        if sender_agent_id:
            params["sender_agent_id"] = sender_agent_id
        if recipient_agent_id:
            params["recipient_agent_id"] = recipient_agent_id
        if priority:
            params["priority"] = priority

        response = await self._client.get("/v1/tasks", params=params)

        tasks = [Task(**task_data) for task_data in response.get("tasks", [])]
        return TaskList(
            tasks=tasks,
            total=response.get("count", len(tasks)),
            limit=limit,
            offset=offset,
        )

    async def get(self, task_id: str) -> Task:
        """
        Get a task by ID.

        Args:
            task_id: The unique task identifier

        Returns:
            The Task object

        Raises:
            TaskNotFoundError: If the task doesn't exist

        Example:
            ```python
            task = await client.tasks.get("task_xyz789")
            print(f"Task status: {task.status}")
            ```
        """
        response = await self._client.get(f"/v1/tasks/{task_id}")
        return Task(**response)

    async def cancel(self, task_id: str) -> Task:
        """
        Cancel a task.

        Args:
            task_id: The task to cancel

        Returns:
            The updated Task object

        Raises:
            TaskNotFoundError: If the task doesn't exist
            TaskStateError: If the task is in a terminal state

        Example:
            ```python
            task = await client.tasks.cancel("task_xyz789")
            print(f"Task cancelled: {task.status}")
            ```
        """
        response = await self._client.post(f"/v1/tasks/{task_id}/cancel")
        return Task(**response)

    async def retry(self, task_id: str) -> Task:
        """
        Retry a failed task.

        Args:
            task_id: The task to retry

        Returns:
            The updated Task object

        Raises:
            TaskNotFoundError: If the task doesn't exist
            TaskStateError: If the task cannot be retried

        Example:
            ```python
            task = await client.tasks.retry("task_xyz789")
            print(f"Retrying task, attempt {task.retry_count + 1}")
            ```
        """
        response = await self._client.post(f"/v1/tasks/{task_id}/retry")
        return Task(**response)