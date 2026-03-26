"""
Synchronous CACP Client Wrapper

Provides a synchronous interface to the async CACP client,
enabling use in scripts, CLI tools, and legacy applications.
"""

import asyncio
from typing import Any, Dict, List, Optional

from cacp_sdk.agents import AgentsAPI
from cacp_sdk.api_keys import APIKeysAPI
from cacp_sdk.auth import AuthAPI
from cacp_sdk.client import CacpClient
from cacp_sdk.groups import GroupsAPI, Group, GroupMember, BroadcastResult
from cacp_sdk.messaging import MessagingAPI
from cacp_sdk.models import Agent, Message
from cacp_sdk.tasks import TasksAPI, Task


class SyncAgentsAPI:
    """Synchronous wrapper for Agents API."""

    def __init__(self, async_api: AgentsAPI):
        self._async_api = async_api

    def register(
        self,
        name: str,
        capabilities: List[str],
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Agent:
        return asyncio.run(
            self._async_api.register(
                name=name,
                capabilities=capabilities,
                description=description,
                metadata=metadata,
            )
        )

    def list(self, limit: int = 100, offset: int = 0) -> List[Agent]:
        return asyncio.run(self._async_api.list(limit=limit, offset=offset))

    def get(self, agent_id: str) -> Agent:
        return asyncio.run(self._async_api.get(agent_id))

    def update(
        self,
        agent_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Agent:
        return asyncio.run(
            self._async_api.update(
                agent_id=agent_id,
                name=name,
                description=description,
                capabilities=capabilities,
                metadata=metadata,
            )
        )

    def delete(self, agent_id: str) -> None:
        return asyncio.run(self._async_api.delete(agent_id))

    def query_by_capability(
        self, capabilities: List[str], limit: int = 100, offset: int = 0
    ) -> List[Agent]:
        return asyncio.run(
            self._async_api.query_by_capability(
                capabilities=capabilities, limit=limit, offset=offset
            )
        )

    def health_check(self, agent_id: str) -> Dict[str, Any]:
        return asyncio.run(self._async_api.health_check(agent_id))

    def discover(
        self,
        query: str,
        threshold: float = 0.7,
        limit: int = 10,
    ) -> List[Agent]:
        return asyncio.run(
            self._async_api.discover(
                query=query,
                threshold=threshold,
                limit=limit,
            )
        )


class SyncMessagingAPI:
    """Synchronous wrapper for Messaging API."""

    def __init__(self, async_api: MessagingAPI):
        self._async_api = async_api

    def send(
        self,
        to: str,
        content: Any,
        message_type: Optional[str] = None,
        correlation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Message:
        return asyncio.run(
            self._async_api.send(
                to=to,
                content=content,
                message_type=message_type,
                correlation_id=correlation_id,
                metadata=metadata,
            )
        )

    def send_rpc(
        self,
        to: str,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: float = 30.0,
    ) -> Any:
        return asyncio.run(
            self._async_api.send_rpc(
                to=to,
                method=method,
                params=params,
                timeout=timeout,
            )
        )

    def get(self, message_id: str) -> Message:
        return asyncio.run(self._async_api.get(message_id))

    def list(
        self,
        limit: int = 100,
        offset: int = 0,
        message_type: Optional[str] = None,
        before: Optional[str] = None,
        after: Optional[str] = None,
    ) -> List[Message]:
        return asyncio.run(
            self._async_api.list(
                limit=limit,
                offset=offset,
                message_type=message_type,
                before=before,
                after=after,
            )
        )

    def get_sent_by_agent(self, agent_id: str, limit: int = 100, offset: int = 0) -> List[Message]:
        return asyncio.run(
            self._async_api.get_sent_by_agent(agent_id=agent_id, limit=limit, offset=offset)
        )

    def get_sent_to_agent(self, agent_id: str, limit: int = 100, offset: int = 0) -> List[Message]:
        return asyncio.run(
            self._async_api.get_sent_to_agent(agent_id=agent_id, limit=limit, offset=offset)
        )


class SyncTasksAPI:
    """Synchronous wrapper for Tasks API."""

    def __init__(self, async_api: TasksAPI):
        self._async_api = async_api

    def create(
        self,
        task_type: str,
        input_data: Dict[str, Any],
        timeout: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Task:
        return asyncio.run(
            self._async_api.create(
                task_type=task_type,
                input_data=input_data,
                timeout=timeout,
                metadata=metadata,
            )
        )

    def get(self, task_id: str) -> Task:
        return asyncio.run(self._async_api.get(task_id))

    def list(
        self,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Task]:
        return asyncio.run(self._async_api.list(status=status, limit=limit, offset=offset))

    def cancel(self, task_id: str) -> Task:
        return asyncio.run(self._async_api.cancel(task_id))

    def wait_for_completion(
        self, task_id: str, timeout: float = 60.0, poll_interval: float = 1.0
    ) -> Task:
        return asyncio.run(
            self._async_api.wait_for_completion(
                task_id=task_id,
                timeout=timeout,
                poll_interval=poll_interval,
            )
        )


class SyncGroupsAPI:
    """Synchronous wrapper for Groups API."""

    def __init__(self, async_api: GroupsAPI):
        self._async_api = async_api

    def create(self, name: str, description: Optional[str] = None) -> Group:
        return asyncio.run(self._async_api.create(name=name, description=description))

    def get(self, group_id: str) -> Group:
        return asyncio.run(self._async_api.get(group_id))

    def list(self, limit: int = 100, offset: int = 0) -> List[Group]:
        return asyncio.run(self._async_api.list(limit=limit, offset=offset))

    def update(
        self,
        group_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Group:
        return asyncio.run(
            self._async_api.update(
                group_id=group_id,
                name=name,
                description=description,
            )
        )

    def delete(self, group_id: str) -> None:
        return asyncio.run(self._async_api.delete(group_id))

    def add_member(self, group_id: str, agent_id: str, role: str = "member") -> "GroupMember":
        return asyncio.run(
            self._async_api.add_member(group_id=group_id, agent_id=agent_id, role=role)
        )

    def remove_member(self, group_id: str, agent_id: str) -> None:
        return asyncio.run(self._async_api.remove_member(group_id=group_id, agent_id=agent_id))

    def broadcast(
        self, group_id: str, message: Dict[str, Any], exclude_sender: bool = True
    ) -> "BroadcastResult":
        return asyncio.run(
            self._async_api.broadcast(
                group_id=group_id, message=message, exclude_sender=exclude_sender
            )
        )


class SyncAuthAPI:
    """Synchronous wrapper for Auth API."""

    def __init__(self, async_api: AuthAPI):
        self._async_api = async_api

    def register(
        self,
        email: str,
        password: str,
        user_name: str,
        organization_name: str,
    ):
        from cacp_sdk.auth import AuthRegisterResponse
        result = asyncio.run(
            self._async_api.register(
                email=email,
                password=password,
                user_name=user_name,
                organization_name=organization_name,
            )
        )
        return result

    def login(self, email: str, password: str):
        from cacp_sdk.auth import AuthLoginResponse
        result = asyncio.run(
            self._async_api.login(email=email, password=password)
        )
        return result

    def get_token(self, api_key: str):
        from cacp_sdk.auth import AuthTokenResponse
        result = asyncio.run(
            self._async_api.get_token(api_key=api_key)
        )
        return result

    def refresh_token(self):
        from cacp_sdk.auth import AuthRefreshResponse
        result = asyncio.run(self._async_api.refresh_token())
        return result


class SyncAPIKeysAPI:
    """Synchronous wrapper for API Keys API."""

    def __init__(self, async_api: APIKeysAPI):
        self._async_api = async_api

    def create(
        self,
        name: Optional[str] = None,
        scopes: Optional[List[str]] = None,
        expires_in_days: Optional[int] = None,
    ):
        from cacp_sdk.api_keys import APIKeyCreated
        result = asyncio.run(
            self._async_api.create(
                name=name,
                scopes=scopes,
                expires_in_days=expires_in_days,
            )
        )
        return result

    def list(self):
        from cacp_sdk.api_keys import APIKeyListResponse
        result = asyncio.run(self._async_api.list())
        return result

    def get(self, key_id: str):
        from cacp_sdk.api_keys import APIKey
        result = asyncio.run(self._async_api.get(key_id=key_id))
        return result

    def delete(self, key_id: str) -> None:
        return asyncio.run(self._async_api.delete(key_id=key_id))


class SyncCacpClient:
    """
    Synchronous wrapper around the async CacpClient.

    This class provides a blocking/synchronous interface to the CACP SDK,
    making it easier to use in scripts, CLI tools, and other non-async contexts.

    Example:
        ```python
        with SyncCacpClient(base_url="http://localhost:4001", api_key="key") as client:
            agent = client.agents.register(
                name="my-agent",
                capabilities=["chat"]
            )
            print(f"Registered agent: {agent.id}")
        ```
    """

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        jwt_token: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the synchronous CACP client.

        Args:
            base_url: The base URL of the CACP API
            api_key: API key for authentication
            jwt_token: JWT token for authentication (alternative to api_key)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Initial retry delay in seconds
            **kwargs: Additional configuration options
        """
        self._async_client = CacpClient(
            base_url=base_url,
            api_key=api_key,
            jwt_token=jwt_token,
            timeout=timeout,
            max_retries=max_retries,
            retry_delay=retry_delay,
            **kwargs,
        )
        self._connected = False
        self._agents: Optional[SyncAgentsAPI] = None
        self._messaging: Optional[SyncMessagingAPI] = None
        self._tasks: Optional[SyncTasksAPI] = None
        self._groups: Optional[SyncGroupsAPI] = None
        self._auth: Optional[SyncAuthAPI] = None
        self._api_keys: Optional[SyncAPIKeysAPI] = None

    @property
    def config(self) -> Any:
        """Get the client configuration."""
        return self._async_client.config

    @property
    def agents(self) -> SyncAgentsAPI:
        """Get the synchronous agents API module."""
        if self._agents is None:
            self._agents = SyncAgentsAPI(self._async_client.agents)
        return self._agents

    @property
    def messaging(self) -> SyncMessagingAPI:
        """Get the synchronous messaging API module."""
        if self._messaging is None:
            self._messaging = SyncMessagingAPI(self._async_client.messaging)
        return self._messaging

    @property
    def tasks(self) -> SyncTasksAPI:
        """Get the synchronous tasks API module."""
        if self._tasks is None:
            self._tasks = SyncTasksAPI(self._async_client.tasks)
        return self._tasks

    @property
    def groups(self) -> SyncGroupsAPI:
        """Get the synchronous groups API module."""
        if self._groups is None:
            self._groups = SyncGroupsAPI(self._async_client.groups)
        return self._groups

    @property
    def auth(self) -> SyncAuthAPI:
        """Get the synchronous auth API module."""
        if self._auth is None:
            self._auth = SyncAuthAPI(self._async_client.auth)
        return self._auth

    @property
    def api_keys(self) -> SyncAPIKeysAPI:
        """Get the synchronous API keys module."""
        if self._api_keys is None:
            self._api_keys = SyncAPIKeysAPI(self._async_client.api_keys)
        return self._api_keys

    def __enter__(self) -> "SyncCacpClient":
        """Context manager entry - connects to the server."""
        if not self._connected:
            asyncio.run(self._async_client.connect())
            self._connected = True
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit - closes the connection."""
        if self._connected:
            asyncio.run(self._async_client.close())
            self._connected = False

    def connect(self) -> None:
        """Manually connect to the server."""
        if not self._connected:
            asyncio.run(self._async_client.connect())
            self._connected = True

    def close(self) -> None:
        """Manually close the connection."""
        if self._connected:
            asyncio.run(self._async_client.close())
            self._connected = False

    def __del__(self) -> None:
        """Cleanup when object is garbage collected."""
        if self._connected:
            try:
                self.close()
            except Exception:
                pass
