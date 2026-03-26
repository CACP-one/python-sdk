"""
CACP SDK Groups API

Agent group/team management operations.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from cacp_sdk.client import CacpClient


class GroupMember(BaseModel):
    """Represents a member of a group."""

    agent_id: str = Field(..., alias="agent_id", description="Agent ID")
    role: str = Field(default="member", description="Member role (leader, member)")
    joined_at: datetime = Field(..., description="When the agent joined the group")

    model_config = {"populate_by_name": True}


class Group(BaseModel):
    """Represents an agent group."""

    id: str = Field(..., alias="group_id", description="Unique group identifier")
    name: str = Field(..., description="Group name")
    description: Optional[str] = Field(None, description="Group description")
    leader_agent_id: Optional[str] = Field(None, description="Leader agent ID")
    capabilities: List[str] = Field(default_factory=list, description="Aggregated capabilities")
    members: List[GroupMember] = Field(default_factory=list, description="Group members")
    member_count: int = Field(0, description="Number of members")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    organization_id: Optional[str] = Field(None, description="Organization ID")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = {"populate_by_name": True}


class GroupCreate(BaseModel):
    """Request model for creating a group."""

    name: str = Field(..., min_length=1, max_length=255, description="Group name")
    description: Optional[str] = Field(None, max_length=2000, description="Group description")
    leader_agent_id: Optional[str] = Field(None, description="Leader agent ID")
    capabilities: List[str] = Field(default_factory=list, description="Group capabilities")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class GroupUpdate(BaseModel):
    """Request model for updating a group."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    leader_agent_id: Optional[str] = None
    capabilities: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class GroupList(BaseModel):
    """Paginated list of groups."""

    groups: List[Group] = Field(default_factory=list)
    total: int = Field(0, description="Total number of groups")
    limit: int = Field(100, description="Page size")
    offset: int = Field(0, description="Page offset")


class MemberAdd(BaseModel):
    """Request model for adding a member to a group."""

    agent_id: str = Field(..., description="Agent ID to add")
    role: str = Field(default="member", description="Member role")


class BroadcastResult(BaseModel):
    """Result of broadcasting a message to a group."""

    status: str = Field(..., description="Broadcast status")
    group_id: str = Field(..., description="Group ID")
    recipients: List[str] = Field(default_factory=list, description="Recipient agent IDs")
    recipient_count: int = Field(0, description="Number of recipients")


class GroupsAPI:
    """
    API for group management operations.

    Provides methods for:
    - Creating and managing agent groups/teams
    - Adding and removing group members
    - Broadcasting messages to all members
    - Managing group capabilities and metadata
    """

    def __init__(self, client: "CacpClient") -> None:
        """Initialize the groups API."""
        self._client = client

    async def create(
        self,
        name: str,
        description: Optional[str] = None,
        leader_agent_id: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Group:
        """
        Create a new group.

        Args:
            name: Group name
            description: Group description
            leader_agent_id: Leader agent ID
            capabilities: Group capabilities
            metadata: Additional metadata

        Returns:
            The created Group object

        Example:
            ```python
            group = await client.groups.create(
                name="research-team",
                description="Research and analysis agents",
                capabilities=["research", "analysis", "writing"]
            )
            print(f"Created group: {group.id}")
            ```
        """
        create_data = {
            "name": name,
            "description": description,
            "leader_agent_id": leader_agent_id,
            "capabilities": capabilities or [],
            "metadata": metadata or {},
        }

        response = await self._client.post("/v1/groups", json_data=create_data)
        return Group(**response)

    async def list(self, limit: int = 100, offset: int = 0) -> GroupList:
        """
        List all groups.

        Args:
            limit: Maximum number of results
            offset: Result offset for pagination

        Returns:
            Paginated list of groups

        Example:
            ```python
            groups = await client.groups.list()
            print(f"Found {len(groups.groups)} groups")
            ```
        """
        params = {"limit": limit, "offset": offset}
        response = await self._client.get("/v1/groups", params=params)

        groups = [Group(**group_data) for group_data in response.get("groups", [])]
        return GroupList(
            groups=groups,
            total=response.get("count", len(groups)),
            limit=limit,
            offset=offset,
        )

    async def get(self, group_id: str) -> Group:
        """
        Get a group by ID (including members).

        Args:
            group_id: The unique group identifier

        Returns:
            The Group object with members

        Raises:
            GroupNotFoundError: If the group doesn't exist

        Example:
            ```python
            group = await client.groups.get("research-team")
            print(f"Group has {group.member_count} members")
            ```
        """
        response = await self._client.get(f"/v1/groups/{group_id}")
        return Group(**response)

    async def update(
        self,
        group_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        leader_agent_id: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Group:
        """
        Update an existing group.

        Args:
            group_id: The group to update
            name: New name (optional)
            description: New description (optional)
            leader_agent_id: New leader agent ID (optional)
            capabilities: Updated capabilities list (optional)
            metadata: Updated or additional metadata (optional)

        Returns:
            The updated Group object

        Example:
            ```python
            group = await client.groups.update(
                "research-team",
                description="Updated team description",
                capabilities=["research", "analysis", "writing", "data-science"]
            )
            ```
        """
        update_data = {
            "name": name,
            "description": description,
            "leader_agent_id": leader_agent_id,
            "capabilities": capabilities,
            "metadata": metadata,
        }

        update_data = {k: v for k, v in update_data.items() if v is not None}

        response = await self._client.put(f"/v1/groups/{group_id}", json_data=update_data)
        return Group(**response)

    async def delete(self, group_id: str) -> None:
        """
        Delete a group.

        Args:
            group_id: The group to delete

        Example:
            ```python
            await client.groups.delete("research-team")
            print("Group deleted")
            ```
        """
        await self._client.delete(f"/v1/groups/{group_id}")

    async def add_member(
        self,
        group_id: str,
        agent_id: str,
        role: str = "member",
    ) -> GroupMember:
        """
        Add a member to a group.

        Args:
            group_id: The group to add the member to
            agent_id: The agent to add
            role: Member role (leader, member)

        Returns:
            The added GroupMember object

        Raises:
            GroupNotFoundError: If the group doesn't exist
            MemberError: If the agent cannot be added

        Example:
            ```python
            member = await client.groups.add_member(
                "research-team",
                agent_id="agent_abc123",
                role="member"
            )
            print(f"Added {member.agent_id} to group")
            ```
        """
        add_data = {"agent_id": agent_id, "role": role}
        response = await self._client.post(
            f"/v1/groups/{group_id}/members",
            json_data=add_data,
        )
        return GroupMember(**response)

    async def remove_member(self, group_id: str, agent_id: str) -> None:
        """
        Remove a member from a group.

        Args:
            group_id: The group to remove the member from
            agent_id: The agent to remove

        Example:
            ```python
            await client.groups.remove_member("research-team", agent_id="agent_abc123")
            print("Member removed from group")
            ```
        """
        await self._client.delete(f"/v1/groups/{group_id}/members/{agent_id}")

    async def broadcast(
        self,
        group_id: str,
        message: Dict[str, Any],
        exclude_sender: bool = True,
    ) -> BroadcastResult:
        """
        Broadcast a message to all members of a group.

        Args:
            group_id: The group to broadcast to
            message: Message to broadcast
            exclude_sender: Whether to exclude the sender from recipients

        Returns:
            Broadcast result with recipient information

        Raises:
            GroupNotFoundError: If the group doesn't exist
            MemberError: If no online members exist

        Example:
            ```python
            result = await client.groups.broadcast(
                "research-team",
                message={"type": "announcement", "content": "Team meeting at 3 PM"}
            )
            print(f"Message sent to {result.recipient_count} members")
            ```
        """
        broadcast_data = {
            "message": message,
            "exclude_sender": exclude_sender,
        }
        response = await self._client.post(
            f"/v1/groups/{group_id}/message",
            json_data=broadcast_data,
        )
        return BroadcastResult(**response)