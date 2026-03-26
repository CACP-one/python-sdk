"""
CACP Python SDK

Official Python SDK for CACP - the universal messaging and RPC layer
for AI agent interoperability.
"""

from cacp_sdk.client import CacpClient
from cacp_sdk.exceptions import (
    CacpError,
    AuthenticationError,
    AgentNotFoundError,
    NotFoundError,
    MessageError,
    ConnectionError,
    RateLimitError,
    ValidationError,
    TimeoutError,
    WebSocketError,
    RpcError,
    TaskError,
    TaskNotFoundError,
    TaskStateError,
    GroupNotFoundError,
    GroupError,
    MemberError,
    InvalidCredentialsError,
    MissingOrganizationError,
    AccountDisabledError,
    InvalidTokenError,
    QuotaExceededError,
    AgentNotInGroupError,
    InsufficientFundsError,
    DuplicateGroupError,
    AgentAlreadyInGroupError,
    CannotRemoveLastAgentError,
    NoMatchingAgentsError,
    DuplicateTaskError,
    PermissionError,
    AuthenticationRequiredError,
    RpcNotFoundError,
    raise_for_error,
)
from cacp_sdk.groups import (
    GroupsAPI,
    Group,
    GroupCreate,
    GroupUpdate,
    GroupMember,
    GroupList,
    BroadcastResult,
)
from cacp_sdk.auth import (
    AuthAPI,
    User,
    Organization,
    AuthRegisterResponse,
    AuthLoginResponse,
    AuthTokenResponse,
    AuthRefreshResponse,
)
from cacp_sdk.api_keys import (
    APIKeysAPI,
    APIKey,
    APIKeyCreated,
    APIKeyListResponse,
)
from cacp_sdk.models import (
    Agent,
    Message,
    MessageStatus,
    RpcRequest,
    RpcResponse,
    AgentStatus,
    MessageType,
)
from cacp_sdk.tasks import (
    TasksAPI,
    Task,
    TaskCreate,
    TaskListOptions,
    TaskList,
    TaskStatus,
)
from cacp_sdk.phoenix_channel import (
    PhoenixChannelClient,
    PhoenixChannel,
    PhoenixMessage,
)
from cacp_sdk.sync_client import (
    SyncCacpClient,
    SyncAgentsAPI,
    SyncMessagingAPI,
    SyncTasksAPI,
    SyncGroupsAPI,
    SyncAuthAPI,
    SyncAPIKeysAPI,
)

__version__ = "0.1.0"
__author__ = "CACP Team"
__all__ = [
    # Version
    "__version__",
    # Client
    "CacpClient",
    # Exceptions
    "CacpError",
    "AuthenticationError",
    "AgentNotFoundError",
    "NotFoundError",
    "MessageError",
    "ConnectionError",
    "RateLimitError",
    "ValidationError",
    "TimeoutError",
    "WebSocketError",
    "RpcError",
    "TaskError",
    "TaskNotFoundError",
    "TaskStateError",
    "GroupNotFoundError",
    "GroupError",
    "MemberError",
    "InvalidCredentialsError",
    "MissingOrganizationError",
    "AccountDisabledError",
    "InvalidTokenError",
    "QuotaExceededError",
    "AgentNotInGroupError",
    "InsufficientFundsError",
    "DuplicateGroupError",
    "AgentAlreadyInGroupError",
    "CannotRemoveLastAgentError",
    "NoMatchingAgentsError",
    "DuplicateTaskError",
    "PermissionError",
    "AuthenticationRequiredError",
    "RpcNotFoundError",
    "raise_for_error",
    # Models
    "Agent",
    "Message",
    "MessageStatus",
    "RpcRequest",
    "RpcResponse",
    "AgentStatus",
    "MessageType",
    # Tasks
    "TasksAPI",
    "Task",
    "TaskCreate",
    "TaskListOptions",
    "TaskList",
    "TaskStatus",
    # Groups
    "GroupsAPI",
    "Group",
    "GroupCreate",
    "GroupUpdate",
    "GroupMember",
    "GroupList",
    "BroadcastResult",
    # Auth
    "AuthAPI",
    "User",
    "Organization",
    "AuthRegisterResponse",
    "AuthLoginResponse",
    "AuthTokenResponse",
    "AuthRefreshResponse",
    # API Keys
    "APIKeysAPI",
    "APIKey",
    "APIKeyCreated",
    "APIKeyListResponse",
    # Phoenix Channels
    "PhoenixChannelClient",
    "PhoenixChannel",
    "PhoenixMessage",
    # Sync Client
    "SyncCacpClient",
    "SyncAgentsAPI",
    "SyncMessagingAPI",
    "SyncTasksAPI",
    "SyncGroupsAPI",
    "SyncAuthAPI",
    "SyncAPIKeysAPI",
]
