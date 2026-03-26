"""
CACP SDK Agents API

Agent management and discovery operations.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from cacp_sdk.models import (
    Agent,
    AgentList,
    AgentRegistration,
    AgentUpdate,
    CapabilityQuery,
    HealthStatus,
    SemanticSearchQuery,
)

if TYPE_CHECKING:
    from cacp_sdk.client import CacpClient


class AgentsAPI:
    """
    API for agent management operations.

    Provides methods for:
    - Registering and unregistering agents
    - Discovering agents by capability
    - Semantic search for agents
    - Agent health monitoring
    """

    def __init__(self, client: "CacpClient") -> None:
        """Initialize the agents API."""
        self._client = client

    async def register(
        self,
        name: str,
        capabilities: List[str],
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Agent:
        """
        Register a new agent with the broker.

        Args:
            name: Unique name for the agent
            capabilities: List of capabilities the agent provides
            description: Human-readable description
            metadata: Additional metadata (model, version, etc.)

        Returns:
            The registered Agent object

        Example:
            ```python
            agent = await client.agents.register(
                name="code-assistant",
                description="Helps with code generation",
                capabilities=["code-generation", "python", "javascript"],
                metadata={"model": "gpt-4", "version": "2.0"}
            )
            print(f"Registered: {agent.id}")
            ```
        """
        registration = AgentRegistration(
            name=name,
            description=description,
            capabilities=capabilities,
            metadata=metadata,
        )

        response = await self._client.post(
            "/v1/agents",
            json_data=registration.model_dump(exclude_none=True),
        )

        return Agent(**response)

    async def get(self, agent_id: str) -> Agent:
        """
        Get an agent by ID.

        Args:
            agent_id: The unique agent identifier

        Returns:
            The Agent object

        Raises:
            AgentNotFoundError: If the agent doesn't exist
        """
        response = await self._client.get(f"/v1/agents/{agent_id}")
        return Agent(**response)

    async def list(
        self,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> AgentList:
        """
        List all registered agents.

        Args:
            status: Filter by agent status (online, offline, etc.)
            limit: Maximum number of results
            offset: Result offset for pagination

        Returns:
            Paginated list of agents
        """
        params: Dict[str, Any] = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status

        response = await self._client.get("/v1/agents", params=params)

        agents = [Agent(**agent_data) for agent_data in response.get("agents", [])]
        return AgentList(
            agents=agents,
            total=response.get("total", len(agents)),
            limit=limit,
            offset=offset,
        )

    async def update(
        self,
        agent_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        status: Optional[str] = None,
    ) -> Agent:
        """
        Update an existing agent.

        Args:
            agent_id: The agent to update
            name: New name (optional)
            description: New description (optional)
            capabilities: New capabilities list (optional)
            metadata: New or updated metadata (optional)
            status: New status (optional)

        Returns:
            The updated Agent object
        """
        update_data = AgentUpdate(
            name=name,
            description=description,
            capabilities=capabilities,
            metadata=metadata,
            status=status,
        )

        response = await self._client.patch(
            f"/v1/agents/{agent_id}",
            json_data=update_data.model_dump(exclude_none=True),
        )

        return Agent(**response)

    async def delete(self, agent_id: str) -> None:
        """
        Delete an agent from the broker.

        Args:
            agent_id: The agent to delete
        """
        await self._client.delete(f"/v1/agents/{agent_id}")

    async def query_by_capability(
        self,
        capabilities: List[str],
        match_all: bool = False,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[Agent]:
        """
        Find agents by their capabilities.

        Args:
            capabilities: List of capabilities to search for
            match_all: If True, agent must have ALL capabilities (AND).
                      If False, agent needs ANY capability (OR).
            status: Filter by agent status
            limit: Maximum number of results

        Returns:
            List of matching agents

        Example:
            ```python
            # Find agents with Python OR JavaScript capability
            agents = await client.agents.query_by_capability(
                capabilities=["python", "javascript"],
                match_all=False
            )

            # Find agents with BOTH code-generation AND testing capabilities
            agents = await client.agents.query_by_capability(
                capabilities=["code-generation", "testing"],
                match_all=True
            )
            ```
        """
        query = CapabilityQuery(
            capabilities=capabilities,
            match_all=match_all,
            status=status,
            limit=limit,
        )

        response = await self._client.get(
            "/v1/agents/query",
            params=query.model_dump(exclude_none=True),
        )

        return [Agent(**agent_data) for agent_data in response.get("agents", [])]

    async def semantic_search(
        self,
        query: str,
        limit: int = 10,
        threshold: float = 0.5,
    ) -> List[Agent]:
        """
        Find agents using natural language semantic search.

        Uses embeddings to find agents whose capabilities or descriptions
        semantically match the query.

        Args:
            query: Natural language query describing what you need
            limit: Maximum number of results
            threshold: Minimum similarity score (0.0 to 1.0)

        Returns:
            List of matching agents with similarity scores

        Example:
            ```python
            agents = await client.agents.semantic_search(
                query="I need help analyzing sales data and creating charts",
                limit=5
            )
            for agent in agents:
                print(f"{agent.name}: {agent.match_score}")
            ```
        """
        search_query = SemanticSearchQuery(
            query=query,
            limit=limit,
            threshold=threshold,
        )

        response = await self._client.post(
            "/v1/agents/semantic-search",
            json_data=search_query.model_dump(),
        )

        return [Agent(**agent_data) for agent_data in response.get("agents", [])]

    async def get_health(self, agent_id: str) -> HealthStatus:
        """
        Get the health status of an agent.

        Args:
            agent_id: The agent to check

        Returns:
            Health status including metrics and issues
        """
        response = await self._client.get(f"/v1/agents/{agent_id}/health")
        return HealthStatus(**response)

    async def set_status(
        self,
        agent_id: str,
        status: str,
    ) -> Agent:
        """
        Set the status of an agent.

        Args:
            agent_id: The agent to update
            status: New status (online, offline, maintenance, etc.)

        Returns:
            The updated Agent object
        """
        return await self.update(agent_id, status=status)

    async def heartbeat(self, agent_id: str) -> None:
        """
        Send a heartbeat to indicate the agent is still alive.

        This updates the agent's last_seen_at timestamp.

        Args:
            agent_id: The agent sending the heartbeat
        """
        await self._client.post(f"/v1/agents/{agent_id}/heartbeat")

    async def discover(
        self,
        query: str,
        threshold: float = 0.7,
        limit: int = 10,
    ) -> List[Agent]:
        """
        Discover agents using natural language semantic search.

        Uses embeddings to find agents whose capabilities or descriptions
        semantically match the query. This is powered by AI-based semantic
        matching.

        Args:
            query: Natural language query describing what you need
            threshold: Minimum similarity score (0.0 to 1.0, default: 0.7)
            limit: Maximum number of results (default: 10)

        Returns:
            List of matching agents with similarity scores

        Raises:
            CacpError: If semantic matching is not configured (missing API key)

        Example:
            ```python
            agents = await client.agents.discover(
                query="I need an agent that can help with data analysis and visualization",
                threshold=0.6,
                limit=5
            )
            for agent in agents:
                print(f"{agent.name}: score={agent.match_score}")
            ```
        """
        response = await self._client.post(
            "/v1/agents/discover",
            json_data={
                "query": query,
                "threshold": threshold,
                "limit": limit,
            },
        )

        return [Agent(**agent_data) for agent_data in response.get("agents", [])]
