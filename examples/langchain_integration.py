"""
LangChain Integration Example

This example shows how to use CACP agents as LangChain tools.
"""

import asyncio
import os
from typing import Optional

from cacp_sdk import CacpClient


class CacpAgentTool:
    """
    A LangChain-compatible tool that uses CACP agents.

    This allows you to use any CACP-registered agent as a tool
    in your LangChain workflows.
    """

    def __init__(
        self,
        client: CacpClient,
        capability: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ):
        """
        Initialize the tool.

        Args:
            client: CACP client
            capability: Capability to search for when invoking the tool
            name: Tool name (defaults to capability name)
            description: Tool description
        """
        self._client = client
        self._capability = capability
        self.name = name or f"cacp_{capability.replace('-', '_')}"
        self.description = description or f"CACP agent with {capability} capability"

    async def arun(self, input: str, **kwargs) -> str:
        """
        Run the tool asynchronously.

        Args:
            input: Input to send to the agent

        Returns:
            Agent response
        """
        # Find an agent with the required capability
        agents = await self._client.agents.query_by_capability(
            capabilities=[self._capability],
            match_all=False,
        )

        if not agents:
            return f"No agent found with capability: {self._capability}"

        # Use the first available agent
        agent = agents[0]

        # Make an RPC call
        try:
            response = await self._client.messaging.rpc_call(
                to_agent=agent.id,
                method="process",
                params={"input": input, **kwargs},
                timeout=60.0,
            )
            return str(response.result)
        except Exception as e:
            return f"Error calling agent: {e}"

    def run(self, input: str, **kwargs) -> str:
        """Synchronous wrapper for arun."""
        return asyncio.run(self.arun(input, **kwargs))


async def main() -> None:
    base_url = os.getenv("CACP_URL", "http://localhost:4001")
    api_key = os.getenv("CACP_API_KEY", "your-api-key")

    async with CacpClient(base_url=base_url, api_key=api_key) as client:
        # Register a sample agent
        print("Registering code-assistant agent...")
        code_agent = await client.agents.register(
            name="code-assistant",
            description="Helps with code generation and debugging",
            capabilities=["code-generation", "python", "javascript"],
        )
        print(f"✓ Registered: {code_agent.id}")

        # Create a LangChain-compatible tool
        code_tool = CacpAgentTool(
            client=client,
            capability="code-generation",
            name="code_generator",
            description="Generates code based on natural language descriptions",
        )

        print(f"\nTool created: {code_tool.name}")
        print(f"Description: {code_tool.description}")

        # Use the tool
        print("\nUsing tool to generate code...")
        result = await code_tool.arun("Write a Python function to calculate fibonacci")
        print(f"Result: {result}")

        # Example: Using multiple tools
        print("\n\nCreating multiple tools...")

        tools = [
            CacpAgentTool(client, "code-generation", name="code_gen"),
            CacpAgentTool(client, "data-analysis", name="data_analyst"),
            CacpAgentTool(client, "visualization", name="visualizer"),
        ]

        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")

        # Clean up
        print("\nCleaning up...")
        await client.agents.delete(code_agent.id)
        print("✓ Done")


if __name__ == "__main__":
    asyncio.run(main())
