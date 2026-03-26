"""
CACP SDK Data Models

Pydantic models for request/response data structures.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    """Agent status enumeration."""

    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class MessageType(str, Enum):
    """Message type enumeration."""

    MESSAGE = "message"
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    BROADCAST = "broadcast"
    RPC = "rpc"


class MessageStatus(str, Enum):
    """Message status enumeration."""

    PENDING = "pending"
    DELIVERED = "delivered"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class Agent(BaseModel):
    """Represents a registered agent."""

    id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., description="Agent name")
    description: Optional[str] = Field(None, description="Agent description")
    capabilities: List[str] = Field(default_factory=list, description="Agent capabilities")
    status: AgentStatus = Field(AgentStatus.OFFLINE, description="Current agent status")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Agent metadata")
    organization_id: Optional[str] = Field(None, description="Organization ID")
    created_at: Optional[datetime] = Field(None, description="Registration timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    last_seen_at: Optional[datetime] = Field(None, description="Last activity timestamp")

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": "agent_abc123",
                    "name": "Code Assistant",
                    "description": "Helps with code generation and review",
                    "capabilities": ["code-generation", "code-review", "python", "javascript"],
                    "status": "online",
                    "metadata": {"model": "gpt-4", "version": "2.0"},
                }
            ]
        },
    }


class AgentRegistration(BaseModel):
    """Request model for agent registration."""

    name: str = Field(..., min_length=1, max_length=255, description="Agent name")
    description: Optional[str] = Field(None, max_length=2000, description="Agent description")
    capabilities: List[str] = Field(default_factory=list, description="Agent capabilities")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Agent metadata")


class AgentUpdate(BaseModel):
    """Request model for agent update."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    capabilities: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    status: Optional[AgentStatus] = None


class Message(BaseModel):
    """Represents a message between agents."""

    id: str = Field(..., description="Unique message identifier")
    from_agent: Optional[str] = Field(None, description="Sender agent ID")
    to_agent: Optional[str] = Field(None, description="Recipient agent ID")
    content: Dict[str, Any] = Field(..., description="Message content")
    message_type: MessageType = Field(MessageType.MESSAGE, description="Message type")
    status: MessageStatus = Field(MessageStatus.PENDING, description="Message status")
    priority: str = Field("normal", description="Message priority")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Message metadata")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    delivered_at: Optional[datetime] = Field(None, description="Delivery timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    error: Optional[str] = Field(None, description="Error message if failed")

    model_config = {
        "populate_by_name": True,
    }


class MessageSend(BaseModel):
    """Request model for sending a message."""

    to_agent: str = Field(..., description="Recipient agent ID")
    content: Dict[str, Any] = Field(..., description="Message content")
    message_type: MessageType = Field(MessageType.MESSAGE, description="Message type")
    priority: str = Field("normal", description="Message priority (low, normal, high, urgent)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Message metadata")
    ttl: Optional[int] = Field(None, description="Time-to-live in seconds")


class BroadcastMessage(BaseModel):
    """Request model for broadcasting a message."""

    content: Dict[str, Any] = Field(..., description="Message content")
    message_type: MessageType = Field(MessageType.BROADCAST, description="Message type")
    capability_filter: Optional[List[str]] = Field(None, description="Filter by capabilities")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Message metadata")


class RpcRequest(BaseModel):
    """RPC request model."""

    to_agent: str = Field(..., description="Target agent ID")
    method: str = Field(..., description="Method to call")
    params: Dict[str, Any] = Field(default_factory=dict, description="Method parameters")
    timeout: float = Field(30.0, description="Timeout in seconds")
    id: Optional[str] = Field(None, description="Request ID for correlation")


class RpcResponse(BaseModel):
    """RPC response model."""

    id: str = Field(..., description="Request ID for correlation")
    result: Optional[Any] = Field(None, description="Result of the RPC call")
    error: Optional[Dict[str, Any]] = Field(None, description="Error if call failed")
    from_agent: str = Field(..., description="Agent that responded")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")


class CapabilityQuery(BaseModel):
    """Request model for capability-based agent query."""

    capabilities: List[str] = Field(..., min_length=1, description="Capabilities to search for")
    match_all: bool = Field(False, description="Match all capabilities (AND) vs any (OR)")
    status: Optional[AgentStatus] = Field(None, description="Filter by status")
    limit: int = Field(100, ge=1, le=1000, description="Maximum results")
    offset: int = Field(0, ge=0, description="Result offset")


class SemanticSearchQuery(BaseModel):
    """Request model for semantic agent search."""

    query: str = Field(..., min_length=1, description="Natural language query")
    limit: int = Field(10, ge=1, le=100, description="Maximum results")
    threshold: float = Field(0.5, ge=0.0, le=1.0, description="Minimum similarity threshold")


class AgentList(BaseModel):
    """Paginated list of agents."""

    agents: List[Agent] = Field(default_factory=list)
    total: int = Field(0, description="Total number of agents")
    limit: int = Field(100, description="Page size")
    offset: int = Field(0, description="Page offset")


class HealthMetric(BaseModel):
    """Agent health metric."""

    agent_id: str = Field(..., description="Agent ID")
    metric_name: str = Field(..., description="Metric name")
    value: float = Field(..., description="Metric value")
    unit: Optional[str] = Field(None, description="Metric unit")
    timestamp: datetime = Field(..., description="Measurement timestamp")


class HealthStatus(BaseModel):
    """Agent health status."""

    agent_id: str = Field(..., description="Agent ID")
    status: AgentStatus = Field(..., description="Current status")
    health_score: float = Field(..., ge=0.0, le=100.0, description="Health score (0-100)")
    metrics: List[HealthMetric] = Field(default_factory=list, description="Health metrics")
    last_check: datetime = Field(..., description="Last health check timestamp")
    issues: List[str] = Field(default_factory=list, description="Current issues")


class WebSocketMessage(BaseModel):
    """WebSocket message model."""

    type: str = Field(..., description="Message type")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Message payload")
    timestamp: Optional[datetime] = Field(None, description="Message timestamp")


class ErrorResponse(BaseModel):
    """API error response."""

    error: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
