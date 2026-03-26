"""
Tests for error code mapping
"""

import pytest

from cacp_sdk.exceptions import (
    CacpError,
    InvalidCredentialsError,
    MissingOrganizationError,
    AccountDisabledError,
    InvalidTokenError,
    RateLimitError,
    QuotaExceededError,
    GroupNotFoundError,
    AgentNotInGroupError,
    InsufficientFundsError,
    DuplicateGroupError,
    AgentAlreadyInGroupError,
    CannotRemoveLastAgentError,
    AgentNotFoundError,
    NoMatchingAgentsError,
    ValidationError,
    DuplicateTaskError,
    PermissionError,
    AuthenticationRequiredError,
    RpcNotFoundError,
    raise_for_error,
)


class TestErrorCodeMapping:
    """Tests for broker error code mapping."""

    def test_invalid_credentials_5001(self):
        """Test error code 5001 maps to InvalidCredentialsError."""
        response = {
            "error": {
                "code": 5001,
                "message": "Invalid email or password"
            }
        }
        with pytest.raises(InvalidCredentialsError) as exc_info:
            raise_for_error(response)
        assert "Invalid email or password" in str(exc_info.value)
        assert exc_info.value.broker_code == 5001

    def test_invalid_credentials_5002(self):
        """Test error code 5002 maps to InvalidCredentialsError."""
        response = {
            "error": {
                "code": 5002,
                "message": "Invalid API key"
            }
        }
        with pytest.raises(InvalidCredentialsError) as exc_info:
            raise_for_error(response)
        assert "Invalid API key" in str(exc_info.value)

    def test_missing_organization_5003(self):
        """Test error code 5003 maps to MissingOrganizationError."""
        response = {
            "error": {
                "code": 5003,
                "message": "Missing organization context"
            }
        }
        with pytest.raises(MissingOrganizationError) as exc_info:
            raise_for_error(response)
        assert exc_info.value.broker_code == 5003

    def test_account_disabled_5005(self):
        """Test error code 5005 maps to AccountDisabledError."""
        response = {
            "error": {
                "code": 5005,
                "message": "Account disabled"
            }
        }
        with pytest.raises(AccountDisabledError) as exc_info:
            raise_for_error(response)
        assert exc_info.value.broker_code == 5005

    def test_rate_limit_6001(self):
        """Test error code 6001 maps to RateLimitError."""
        response = {
            "error": {
                "code": 6001,
                "message": "Rate limit exceeded",
                "retry_after": 30
            }
        }
        with pytest.raises(RateLimitError) as exc_info:
            raise_for_error(response)
        assert exc_info.value.retry_after == 30

    def test_quota_exceeded_6002(self):
        """Test error code 6002 maps to QuotaExceededError."""
        response = {
            "error": {
                "code": 6002,
                "message": "Quota exceeded"
            }
        }
        with pytest.raises(QuotaExceededError) as exc_info:
            raise_for_error(response)
        assert exc_info.value.broker_code == 6002

    def test_insufficient_funds_7001(self):
        """Test error code 7001 maps to InsufficientFundsError."""
        response = {
            "error": {
                "code": 7001,
                "message": "Insufficient funds"
            }
        }
        with pytest.raises(InsufficientFundsError) as exc_info:
            raise_for_error(response)
        assert exc_info.value.broker_code == 7001

    def test_group_not_found_7002(self):
        """Test error code 7002 maps to GroupNotFoundError."""
        response = {
            "error": {
                "code": 7002,
                "message": "Group not found",
                "group_id": "group-123"
            }
        }
        with pytest.raises(GroupNotFoundError) as exc_info:
            raise_for_error(response)
        assert exc_info.value.group_id == "group-123"

    def test_agent_not_in_group_7003(self):
        """Test error code 7003 maps to AgentNotInGroupError."""
        response = {
            "error": {
                "code": 7003,
                "message": "Agent not in group",
                "group_id": "group-123",
                "agent_id": "agent-456"
            }
        }
        with pytest.raises(AgentNotInGroupError) as exc_info:
            raise_for_error(response)
        assert exc_info.value.group_id == "group-123"
        assert exc_info.value.agent_id == "agent-456"

    def test_duplicate_group_7006(self):
        """Test error code 7006 maps to DuplicateGroupError."""
        response = {
            "error": {
                "code": 7006,
                "message": "Duplicate group",
                "group_name": "my-group"
            }
        }
        with pytest.raises(DuplicateGroupError) as exc_info:
            raise_for_error(response)
        assert exc_info.value.group_name == "my-group"

    def test_agent_already_in_group_7007(self):
        """Test error code 7007 maps to AgentAlreadyInGroupError."""
        response = {
            "error": {
                "code": 7007,
                "message": "Agent already in group",
                "group_id": "group-123",
                "agent_id": "agent-456"
            }
        }
        with pytest.raises(AgentAlreadyInGroupError) as exc_info:
            raise_for_error(response)
        assert exc_info.value.group_id == "group-123"
        assert exc_info.value.agent_id == "agent-456"

    def test_cannot_remove_last_agent_7008(self):
        """Test error code 7008 maps to CannotRemoveLastAgentError."""
        response = {
            "error": {
                "code": 7008,
                "message": "Cannot remove last agent",
                "group_id": "group-123"
            }
        }
        with pytest.raises(CannotRemoveLastAgentError) as exc_info:
            raise_for_error(response)
        assert exc_info.value.group_id == "group-123"

    def test_agent_not_found_2001(self):
        """Test error code 2001 maps to AgentNotFoundError."""
        response = {
            "error": {
                "code": 2001,
                "message": "Agent not found",
                "agent_id": "agent-123"
            }
        }
        with pytest.raises(AgentNotFoundError) as exc_info:
            raise_for_error(response)
        assert exc_info.value.agent_id == "agent-123"

    def test_no_matching_agents_2008(self):
        """Test error code 2008 maps to NoMatchingAgentsError."""
        response = {
            "error": {
                "code": 2008,
                "message": "No matching agents"
            }
        }
        with pytest.raises(NoMatchingAgentsError) as exc_info:
            raise_for_error(response)
        assert exc_info.value.broker_code == 2008

    def test_duplicate_task_2009(self):
        """Test error code 2009 maps to DuplicateTaskError."""
        response = {
            "error": {
                "code": 2009,
                "message": "Duplicate task ID",
                "task_id": "task-123"
            }
        }
        with pytest.raises(DuplicateTaskError) as exc_info:
            raise_for_error(response)
        assert exc_info.value.task_id == "task-123"

    def test_validation_error_3001(self):
        """Test error code 3001 maps to ValidationError."""
        response = {
            "error": {
                "code": 3001,
                "message": "Invalid request payload"
            }
        }
        with pytest.raises(ValidationError) as exc_info:
            raise_for_error(response)
        assert exc_info.value.broker_code == 3001

    def test_validation_error_3002(self):
        """Test error code 3002 maps to ValidationError."""
        response = {
            "error": {
                "code": 3002,
                "message": "Missing required fields"
            }
        }
        with pytest.raises(ValidationError) as exc_info:
            raise_for_error(response)
        assert exc_info.value.broker_code == 3002

    def test_authentication_required_4001(self):
        """Test error code 4001 maps to AuthenticationRequiredError."""
        response = {
            "error": {
                "code": 4001,
                "message": "Authentication required"
            }
        }
        with pytest.raises(AuthenticationRequiredError) as exc_info:
            raise_for_error(response)
        assert exc_info.value.broker_code == 4001

    def test_permission_error_4003(self):
        """Test error code 4003 maps to PermissionError."""
        response = {
            "error": {
                "code": 4003,
                "message": "Insufficient permissions"
            }
        }
        with pytest.raises(PermissionError) as exc_info:
            raise_for_error(response)
        assert exc_info.value.broker_code == 4003

    def test_rpc_not_found_4004(self):
        """Test error code 4004 maps to RpcNotFoundError."""
        response = {
            "error": {
                "code": 4004,
                "message": "RPC request not found"
            }
        }
        with pytest.raises(RpcNotFoundError) as exc_info:
            raise_for_error(response)
        assert exc_info.value.broker_code == 4004

    def test_unknown_error_code(self):
        """Test unknown error code maps to generic CacpError."""
        response = {
            "error": {
                "code": 9999,
                "message": "Unknown error"
            }
        }
        with pytest.raises(CacpError) as exc_info:
            raise_for_error(response)
        assert not isinstance(exc_info.value, AgentNotFoundError)
        assert isinstance(exc_info.value, CacpError)

    def test_missing_error_code(self):
        """Test missing error code maps to generic CacpError."""
        response = {
            "error": {
                "message": "Error without code"
            }
        }
        with pytest.raises(CacpError) as exc_info:
            raise_for_error(response)
        assert "Error without code" in str(exc_info.value)

    def test_malformed_response(self):
        """Test malformed response without error key."""
        response = {"data": "some data"}
        with pytest.raises(CacpError) as exc_info:
            raise_for_error(response)
        assert "Unknown error" in str(exc_info.value)