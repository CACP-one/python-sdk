"""Tests for data models."""

import pytest
from datetime import datetime

from cacp_sdk.models import (
    Agent,
    AgentStatus,
    AgentRegistration,
    Message,
    MessageStatus,
    MessageType,
    RpcRequest,
    RpcResponse,
)


class TestAgentModels:
    """Tests for Agent-related models."""

    def test_agent_model(self) -> None:
        """Test Agent model creation."""
        agent = Agent(
            id="agent_123",
            name="test-agent",
            description="A test agent",
            capabilities=["chat", "code"],
            status=AgentStatus.ONLINE,
            metadata={"version": "1.0"},
        )

        assert agent.id == "agent_123"
        assert agent.name == "test-agent"
        assert agent.status == AgentStatus.ONLINE
        assert "chat" in agent.capabilities

    def test_agent_registration_model(self) -> None:
        """Test AgentRegistration model."""
        registration = AgentRegistration(
            name="new-agent",
            description="A new agent",
            capabilities=["test"],
            metadata={"key": "value"},
        )

        assert registration.name == "new-agent"
        assert registration.capabilities == ["test"]

    def test_agent_status_enum(self) -> None:
        """Test AgentStatus enum values."""
        assert AgentStatus.ONLINE.value == "online"
        assert AgentStatus.OFFLINE.value == "offline"
        assert AgentStatus.DEGRADED.value == "degraded"
        assert AgentStatus.ERROR.value == "error"


class TestMessageModels:
    """Tests for Message-related models."""

    def test_message_model(self) -> None:
        """Test Message model creation."""
        message = Message(
            id="msg_123",
            from_agent="agent_1",
            to_agent="agent_2",
            content={"text": "Hello"},
            message_type=MessageType.MESSAGE,
            status=MessageStatus.PENDING,
        )

        assert message.id == "msg_123"
        assert message.from_agent == "agent_1"
        assert message.to_agent == "agent_2"
        assert message.content == {"text": "Hello"}

    def test_message_type_enum(self) -> None:
        """Test MessageType enum values."""
        assert MessageType.MESSAGE.value == "message"
        assert MessageType.REQUEST.value == "request"
        assert MessageType.RESPONSE.value == "response"
        assert MessageType.RPC.value == "rpc"

    def test_message_status_enum(self) -> None:
        """Test MessageStatus enum values."""
        assert MessageStatus.PENDING.value == "pending"
        assert MessageStatus.DELIVERED.value == "delivered"
        assert MessageStatus.COMPLETED.value == "completed"
        assert MessageStatus.FAILED.value == "failed"


class TestRpcModels:
    """Tests for RPC-related models."""

    def test_rpc_request_model(self) -> None:
        """Test RpcRequest model."""
        request = RpcRequest(
            to_agent="agent_123",
            method="calculate",
            params={"a": 1, "b": 2},
            timeout=30.0,
        )

        assert request.to_agent == "agent_123"
        assert request.method == "calculate"
        assert request.params == {"a": 1, "b": 2}
        assert request.timeout == 30.0

    def test_rpc_response_model(self) -> None:
        """Test RpcResponse model."""
        response = RpcResponse(
            id="rpc_123",
            from_agent="agent_456",
            result={"sum": 3},
            execution_time=0.05,
        )

        assert response.id == "rpc_123"
        assert response.result == {"sum": 3}
        assert response.error is None

    def test_rpc_response_with_error(self) -> None:
        """Test RpcResponse model with error."""
        response = RpcResponse(
            id="rpc_123",
            from_agent="agent_456",
            error={"code": 500, "message": "Internal error"},
        )

        assert response.error is not None
        assert response.error["code"] == 500
        assert response.result is None
