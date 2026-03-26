"""
Basic Agent Registration Example

This example demonstrates how to register an agent with CACP.
"""

import asyncio
import os

from cacp_sdk import CacpClient


async def main() -> None:
    # Initialize the client
    base_url = os.getenv("CACP_URL", "http://localhost:4001")
    api_key = os.getenv("CACP_API_KEY", "your-api-key")

    async with CacpClient(base_url=base_url, api_key=api_key) as client:
        # Register a new agent
        print("Registering agent...")
        agent = await client.agents.register(
            name="example-assistant",
            description="A helpful AI assistant example",
            capabilities=["chat", "question-answering", "general-knowledge"],
            metadata={
                "model": "gpt-4",
                "version": "1.0.0",
                "owner": "example-team",
            },
        )

        print(f"✓ Agent registered successfully!")
        print(f"  ID: {agent.id}")
        print(f"  Name: {agent.name}")
        print(f"  Status: {agent.status}")
        print(f"  Capabilities: {agent.capabilities}")

        # List all agents
        print("\nListing all agents...")
        agent_list = await client.agents.list(limit=10)

        print(f"Found {agent_list.total} agents:")
        for a in agent_list.agents:
            print(f"  - {a.name} ({a.status})")

        # Query agents by capability
        print("\nQuerying agents with 'chat' capability...")
        chat_agents = await client.agents.query_by_capability(
            capabilities=["chat"],
            match_all=False,
        )

        print(f"Found {len(chat_agents)} agents with 'chat' capability:")
        for a in chat_agents:
            print(f"  - {a.name}")

        # Clean up - delete the agent
        print(f"\nDeleting agent {agent.id}...")
        await client.agents.delete(agent.id)
        print("✓ Agent deleted")


if __name__ == "__main__":
    asyncio.run(main())
