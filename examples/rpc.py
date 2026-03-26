"""
RPC Example

This example demonstrates RPC-style calls between agents.
"""

import asyncio
import os

from cacp_sdk import CacpClient, RpcError, TimeoutError


async def main() -> None:
    base_url = os.getenv("CACP_URL", "http://localhost:4001")
    api_key = os.getenv("CACP_API_KEY", "your-api-key")

    async with CacpClient(base_url=base_url, api_key=api_key) as client:
        # Register a calculator agent (simulated)
        print("Registering calculator agent...")
        calculator = await client.agents.register(
            name="calculator-agent",
            description="Performs basic math operations",
            capabilities=["math", "calculation", "rpc"],
            metadata={"operations": ["add", "subtract", "multiply", "divide"]},
        )
        print(f"Calculator agent: {calculator.id}")

        # Make an RPC call
        print("\nMaking RPC call: add(10, 20)...")
        try:
            response = await client.messaging.rpc_call(
                to_agent=calculator.id,
                method="add",
                params={"a": 10, "b": 20},
                timeout=30.0,
            )

            print(f"✓ RPC Response:")
            print(f"  Request ID: {response.id}")
            print(f"  Result: {response.result}")
            print(f"  From: {response.from_agent}")
            if response.execution_time:
                print(f"  Execution time: {response.execution_time:.3f}s")

        except TimeoutError as e:
            print(f"✗ RPC call timed out: {e}")
            print("  (This is expected if no agent is listening)")

        except RpcError as e:
            print(f"✗ RPC call failed: {e}")
            print(f"  Method: {e.method}")
            print(f"  Code: {e.rpc_code}")

        # Another RPC example
        print("\nMaking RPC call: multiply(5, 7)...")
        try:
            response = await client.messaging.rpc_call(
                to_agent=calculator.id,
                method="multiply",
                params={"a": 5, "b": 7},
            )
            print(f"✓ Result: {response.result}")

        except (TimeoutError, RpcError) as e:
            print(f"✗ Error: {e}")

        # Clean up
        print("\nCleaning up...")
        await client.agents.delete(calculator.id)
        print("✓ Done")


if __name__ == "__main__":
    asyncio.run(main())
