"""
Semantic Search Example

This example demonstrates finding agents using natural language queries.
"""

import asyncio
import os

from cacp_sdk import CacpClient


async def main() -> None:
    base_url = os.getenv("CACP_URL", "http://localhost:4001")
    api_key = os.getenv("CACP_API_KEY", "your-api-key")

    async with CacpClient(base_url=base_url, api_key=api_key) as client:
        # Register some agents with different capabilities
        print("Registering agents...")

        agents = []
        agent_configs = [
            {
                "name": "code-assistant",
                "description": "Helps with code generation, debugging, and code review",
                "capabilities": ["code-generation", "debugging", "code-review"],
            },
            {
                "name": "data-analyst",
                "description": "Analyzes data, creates visualizations, and generates reports",
                "capabilities": ["data-analysis", "visualization", "reporting"],
            },
            {
                "name": "customer-support",
                "description": "Handles customer inquiries, support tickets, and FAQs",
                "capabilities": ["customer-support", "ticketing", "faq"],
            },
        ]

        for config in agent_configs:
            agent = await client.agents.register(**config)
            agents.append(agent)
            print(f"  ✓ Registered: {agent.name}")

        # Perform semantic searches
        queries = [
            "I need help writing Python code",
            "Analyze my sales data and create charts",
            "Help me respond to customer complaints",
            "Debug my application",
        ]

        print("\nPerforming semantic searches...")
        for query in queries:
            print(f"\nQuery: '{query}'")

            results = await client.agents.semantic_search(
                query=query,
                limit=3,
                threshold=0.3,
            )

            if results:
                print("  Results:")
                for agent in results:
                    score = getattr(agent, "match_score", "N/A")
                    print(f"    - {agent.name} (score: {score})")
                    print(f"      {agent.description}")
            else:
                print("  No matching agents found")

        # Capability-based query
        print("\n\nCapability-based query: agents with 'code-generation' OR 'debugging'")
        results = await client.agents.query_by_capability(
            capabilities=["code-generation", "debugging"],
            match_all=False,
        )

        print(f"  Found {len(results)} agents:")
        for agent in results:
            print(f"    - {agent.name}: {agent.capabilities}")

        # Clean up
        print("\nCleaning up...")
        for agent in agents:
            await client.agents.delete(agent.id)
        print("✓ Done")


if __name__ == "__main__":
    asyncio.run(main())
