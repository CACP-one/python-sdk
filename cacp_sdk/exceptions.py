"""
CACP SDK Exceptions

Defines all custom exceptions used throughout the SDK.
"""

from typing import Optional, Dict, Any


class CacpError(Exception):
    """Base exception for all CACP SDK errors."""

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[dict] = None,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
        self.request_id = request_id

    def __str__(self) -> str:
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message


# Authentication Errors (5000-5099)
class AuthenticationError(CacpError):
    """Raised when authentication fails."""

    def __init__(
        self,
        message: str = "Authentication failed",
        code: Optional[str] = "AUTH_ERROR",
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(message, code, request_id=request_id)


class InvalidCredentialsError(AuthenticationError):
    """Raised when credentials are invalid (5001, 5002)."""

    def __init__(
        self,
        message: str = "Invalid credentials",
        code: Optional[int] = None,
    ) -> None:
        super().__init__(message, code or "INVALID_CREDENTIALS")
        self.broker_code = code


class MissingOrganizationError(AuthenticationError):
    """Raised when organization context is missing (5003, 5004)."""

    def __init__(
        self,
        message: str = "Missing organization context",
        code: Optional[int] = None,
    ) -> None:
        super().__init__(message, code or "MISSING_ORGANIZATION")
        self.broker_code = code


class AccountDisabledError(AuthenticationError):
    """Raised when account is disabled (5005)."""

    def __init__(
        self,
        message: str = "Account disabled",
        code: Optional[int] = None,
    ) -> None:
        super().__init__(message, code or "ACCOUNT_DISABLED")
        self.broker_code = code


class InvalidTokenError(AuthenticationError):
    """Raised when token is invalid (5006)."""

    def __init__(
        self,
        message: str = "Invalid token",
        code: Optional[int] = None,
    ) -> None:
        super().__init__(message, code or "INVALID_TOKEN")
        self.broker_code = code


# Rate Limit & Quota Errors (6000-6099)
class RateLimitError(CacpError):
    """Raised when rate limit is exceeded (6001)."""

    def __init__(
        self,
        retry_after: Optional[float] = None,
        message: str = "Rate limit exceeded",
        code: Optional[int] = None,
        request_id: Optional[str] = None,
    ) -> None:
        self.retry_after = retry_after
        self.broker_code = code
        msg = f"{message}. Retry after {retry_after} seconds" if retry_after else message
        super().__init__(msg, code or "RATE_LIMIT_EXCEEDED", request_id=request_id)


class QuotaExceededError(CacpError):
    """Raised when quota is exceeded (6002)."""

    def __init__(
        self,
        message: str = "Quota exceeded",
        code: Optional[int] = None,
    ) -> None:
        super().__init__(message, code or "QUOTA_EXCEEDED")
        self.broker_code = code


# Group Errors (7000-7099)
class GroupError(CacpError):
    """Raised when a group operation fails."""

    def __init__(
        self,
        message: str,
        group_id: Optional[str] = None,
        code: Optional[str] = "GROUP_ERROR",
    ) -> None:
        self.group_id = group_id
        super().__init__(message, code)


class GroupNotFoundError(GroupError):
    """Raised when a group is not found (7002)."""

    def __init__(
        self,
        group_id: str,
        message: Optional[str] = None,
        code: Optional[int] = None,
    ) -> None:
        self.group_id = group_id
        self.broker_code = code
        super().__init__(
            message or f"Group not found: {group_id}",
            group_id,
            code or "GROUP_NOT_FOUND",
        )


class AgentNotInGroupError(GroupError):
    """Raised when agent is not in group (7003)."""

    def __init__(
        self,
        group_id: str,
        agent_id: str,
        message: Optional[str] = None,
        code: Optional[int] = None,
    ) -> None:
        self.group_id = group_id
        self.agent_id = agent_id
        self.broker_code = code
        super().__init__(
            message or f"Agent {agent_id} not in group {group_id}",
            group_id,
            code or "AGENT_NOT_IN_GROUP",
        )


class InsufficientFundsError(GroupError):
    """Raised when funds are insufficient (7001)."""

    def __init__(
        self,
        message: str = "Insufficient funds",
        code: Optional[int] = None,
    ) -> None:
        self.broker_code = code
        super().__init__(message, code or "INSUFFICIENT_FUNDS")


class DuplicateGroupError(GroupError):
    """Raised when group already exists (7006)."""

    def __init__(
        self,
        group_name: str,
        message: Optional[str] = None,
        code: Optional[int] = None,
    ) -> None:
        self.group_name = group_name
        self.broker_code = code
        super().__init__(
            message or f"Group already exists: {group_name}",
            code or "DUPLICATE_GROUP",
        )


class AgentAlreadyInGroupError(GroupError):
    """Raised when agent is already in group (7007)."""

    def __init__(
        self,
        group_id: str,
        agent_id: str,
        message: Optional[str] = None,
        code: Optional[int] = None,
    ) -> None:
        self.group_id = group_id
        self.agent_id = agent_id
        self.broker_code = code
        super().__init__(
            message or f"Agent {agent_id} already in group {group_id}",
            group_id,
            code or "AGENT_ALREADY_IN_GROUP",
        )


class CannotRemoveLastAgentError(GroupError):
    """Raised when cannot remove last agent from group (7008)."""

    def __init__(
        self,
        group_id: str,
        message: Optional[str] = None,
        code: Optional[int] = None,
    ) -> None:
        self.group_id = group_id
        self.broker_code = code
        super().__init__(
            message or f"Cannot remove last agent from group {group_id}",
            group_id,
            code or "CANNOT_REMOVE_LAST_AGENT",
        )


# Agent Errors (2000-2099)
class AgentNotFoundError(CacpError):
    """Raised when an agent is not found (2001)."""

    def __init__(
        self,
        agent_id: str,
        message: Optional[str] = None,
        code: Optional[int] = None,
    ) -> None:
        self.agent_id = agent_id
        self.broker_code = code
        super().__init__(
            message or f"Agent not found: {agent_id}",
            code or "AGENT_NOT_FOUND",
        )


class NoMatchingAgentsError(CacpError):
    """Raised when no agents match the criteria (2008)."""

    def __init__(
        self,
        message: str = "No matching agents",
        code: Optional[int] = None,
    ) -> None:
        self.broker_code = code
        super().__init__(message, code or "NO_MATCHING_AGENTS")


# Message Errors (3000-3099)
class MessageError(CacpError):
    """Raised when a message operation fails."""

    def __init__(
        self,
        message: str,
        message_id: Optional[str] = None,
        code: Optional[str] = "MESSAGE_ERROR",
    ) -> None:
        self.message_id = message_id
        super().__init__(message, code)


class ValidationError(CacpError):
    """Raised when validation fails (3001, 3002)."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        code: Optional[int] = None,
        request_id: Optional[str] = None,
    ) -> None:
        self.field = field
        self.broker_code = code
        super().__init__(message, code or "VALIDATION_ERROR", request_id=request_id)


# Task Errors (6000-6099 - but task-specific)
class TaskNotFoundError(CacpError):
    """Raised when a task is not found."""

    def __init__(
        self,
        task_id: str,
        message: Optional[str] = None,
    ) -> None:
        self.task_id = task_id
        super().__init__(
            message or f"Task not found: {task_id}",
            code="TASK_NOT_FOUND",
        )


class TaskStateError(CacpError):
    """Raised when a task operation cannot be performed due to state."""

    def __init__(
        self,
        message: str,
        task_id: Optional[str] = None,
        current_status: Optional[str] = None,
    ) -> None:
        self.task_id = task_id
        self.current_status = current_status
        msg = message
        if task_id and current_status:
            msg = f"{message} (task_id: {task_id}, status: {current_status})"
        super().__init__(msg, code="TASK_STATE_ERROR")


class DuplicateTaskError(CacpError):
    """Raised when task ID already exists (2009)."""

    def __init__(
        self,
        task_id: str,
        message: Optional[str] = None,
        code: Optional[int] = None,
    ) -> None:
        self.task_id = task_id
        self.broker_code = code
        super().__init__(
            message or f"Task already exists: {task_id}",
            code or "DUPLICATE_TASK",
        )


class TaskError(CacpError):
    """Raised when a task operation fails."""

    def __init__(
        self,
        message: str,
        task_id: Optional[str] = None,
        code: Optional[str] = "TASK_ERROR",
    ) -> None:
        self.task_id = task_id
        super().__init__(message, code)


# Permission Errors (4000-4099)
class PermissionError(CacpError):
    """Raised when user has insufficient permissions (4003)."""

    def __init__(
        self,
        message: str = "Insufficient permissions",
        code: Optional[int] = None,
    ) -> None:
        self.broker_code = code
        super().__init__(message, code or "PERMISSION_ERROR")


class AuthenticationRequiredError(CacpError):
    """Raised when authentication is required (4001)."""

    def __init__(
        self,
        message: str = "Authentication required",
        code: Optional[int] = None,
    ) -> None:
        self.broker_code = code
        super().__init__(message, code or "AUTHENTICATION_REQUIRED")


class RpcNotFoundError(CacpError):
    """Raised when RPC request is not found (4004)."""

    def __init__(
        self,
        message: str = "RPC request not found",
        code: Optional[int] = None,
    ) -> None:
        self.broker_code = code
        super().__init__(message, code or "RPC_NOT_FOUND")


# Connection & General Errors
class ConnectionError(CacpError):
    """Raised when a connection error occurs."""

    def __init__(
        self,
        message: str = "Connection error",
        code: Optional[str] = "CONNECTION_ERROR",
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(message, code, request_id=request_id)


class TimeoutError(CacpError):
    """Raised when an operation times out."""

    def __init__(
        self,
        operation: str,
        timeout: Optional[float] = None,
        request_id: Optional[str] = None,
    ) -> None:
        self.operation = operation
        self.timeout = timeout
        message = f"Operation timed out: {operation}"
        if timeout:
            message += f" (after {timeout}s)"
        super().__init__(message, code="TIMEOUT", request_id=request_id)


class WebSocketError(CacpError):
    """Raised when a WebSocket error occurs."""

    def __init__(
        self,
        message: str,
        code: Optional[str] = "WEBSOCKET_ERROR",
    ) -> None:
        super().__init__(message, code)


class RpcError(CacpError):
    """Raised when an RPC call fails."""

    def __init__(
        self,
        message: str,
        method: Optional[str] = None,
        rpc_code: Optional[int] = None,
    ) -> None:
        self.method = method
        self.rpc_code = rpc_code
        super().__init__(message, code="RPC_ERROR")


class NotFoundError(CacpError):
    """Raised when a resource is not found."""

    def __init__(
        self,
        resource: str,
        resource_id: Optional[str] = None,
        message: Optional[str] = None,
    ) -> None:
        self.resource = resource
        self.resource_id = resource_id
        msg = message or f"{resource} not found"
        if resource_id:
            msg = f"{resource} not found: {resource_id}"
        super().__init__(msg, code="NOT_FOUND")


class MemberError(CacpError):
    """Raised when a group member operation fails."""

    def __init__(
        self,
        message: str,
        group_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        code: Optional[str] = "MEMBER_ERROR",
    ) -> None:
        self.group_id = group_id
        self.agent_id = agent_id
        super().__init__(message, code)


# Error Code Mapping
ERROR_CODE_MAP: Dict[int, type] = {
    # Authentication Errors (5000-5099)
    5001: InvalidCredentialsError,
    5002: InvalidCredentialsError,
    5003: MissingOrganizationError,
    5004: MissingOrganizationError,
    5005: AccountDisabledError,
    5006: InvalidTokenError,
    
    # Rate Limit & Quota Errors (6000-6099)
    6001: RateLimitError,
    6002: QuotaExceededError,
    
    # Group Errors (7000-7099)
    7001: InsufficientFundsError,
    7002: GroupNotFoundError,
    7003: AgentNotInGroupError,
    7006: DuplicateGroupError,
    7007: AgentAlreadyInGroupError,
    7008: CannotRemoveLastAgentError,
    
    # Agent Errors (2000-2099)
    2001: AgentNotFoundError,
    2008: NoMatchingAgentsError,
    2009: DuplicateTaskError,
    
    # Validation Errors (3000-3099)
    3001: ValidationError,
    3002: ValidationError,
    
    # Permission Errors (4000-4099)
    4001: AuthenticationRequiredError,
    4003: PermissionError,
    4004: RpcNotFoundError,
}


def raise_for_error(response: Dict[str, Any], request_id: Optional[str] = None) -> None:
    """
    Raise the appropriate exception based on broker error code.
    
    Args:
        response: Response dict from broker, expected to have 'error' key
                  with 'code' and 'message' fields.
        request_id: Optional request ID for tracking.
    
    Raises:
        CacpError: Appropriate exception based on error code.
    
    Example:
        >>> response = {"error": {"code": 2001, "message": "Agent not found"}}
        >>> raise_for_error(response)
        AgentNotFoundError: Agent not found
    """
    error = response.get("error", {})
    code = error.get("code")
    message = error.get("message", "Unknown error")
    
    if not code:
        raise CacpError(message, request_id=request_id)
    
    exc_class = ERROR_CODE_MAP.get(code, CacpError)
    
    # Prepare kwargs based on exception type
    kwargs: Dict[str, Any] = {"message": message, "code": code, "request_id": request_id}
    
    # Add type-specific parameters
    if exc_class == AgentNotFoundError:
        kwargs["agent_id"] = error.get("agent_id", "")
    elif exc_class == GroupNotFoundError:
        kwargs["group_id"] = error.get("group_id", "")
    elif exc_class == TaskNotFoundError:
        kwargs["task_id"] = error.get("task_id", "")
    elif exc_class == RateLimitError:
        kwargs["retry_after"] = error.get("retry_after")
    elif exc_class in (AgentNotInGroupError, AgentAlreadyInGroupError):
        kwargs["group_id"] = error.get("group_id", "")
        kwargs["agent_id"] = error.get("agent_id", "")
    elif exc_class == DuplicateGroupError:
        kwargs["group_name"] = error.get("group_name", "")
    elif exc_class == CannotRemoveLastAgentError:
        kwargs["group_id"] = error.get("group_id", "")
    elif exc_class == DuplicateTaskError:
        kwargs["task_id"] = error.get("task_id", "")
    
    raise exc_class(**kwargs)