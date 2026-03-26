"""
WebSocket Real-Time Communication Example

This example demonstrates real-time messaging via WebSocket.
"""

import asyncio
import os

from cacp_sdk import CacpClient


async def message_handler(message: dict) -> None:
    """Handle incoming WebSocket messages."""
    msg_type = message.get("type", "unknown")
    print(f"  📩 Received [{msg_type}]: {message.get('content', message)}")


async def main() -> None:
    base_url = os.getenv("CACP_URL", "http://localhost:4001")
    api_key = os.getenv("CACP_API_KEY", "your-api-key")

    async with CacpClient(base_url=base_url, api_key=api_key) as client:
        # Register an agent
        print("Registering agent...")
        agent = await client.agents.register(
            name="websocket-demo-agent",
            capabilities=["real-time", "chat"],
        )
        print(f"Agent: {agent.id}")

        # Connect WebSocket
        print("\nConnecting WebSocket...")
        async with client.websocket.connect() as ws:
            print("✓ WebSocket connected")

            # Register message handler
            ws.on_message(message_handler)

            # Subscribe to messages for our agent
            print(f"\nSubscribing to messages for agent {agent.id}...")
            await ws.subscribe(agent.id)
            print("✓ Subscribed")

            # Send a message through WebSocket
            print("\nSending message via WebSocket...")
            await ws.send(
                to_agent=agent.id,  # Send to self for demo
                content={"text": "Hello via WebSocket!"},
                message_type="message",
                from_agent=agent.id,
            )
            print("✓ Message sent")

            # Listen for messages for a short time
            print("\nListening for messages (5 seconds)...")
            try:
                async with asyncio.timeout(5):
                    async for message in ws.messages():
                        print(f"  📩 Message: {message}")
            except asyncio.TimeoutError:
                print("✓ Listen timeout reached")

            # Unsubscribe
            print("\nUnsubscribing...")
            await ws.unsubscribe(agent.id)
            print("✓ Unsubscribed")

        print("\nWebSocket closed")

        # Clean up
        print("\nCleaning up...")
        await client.agents.delete(agent.id)
        print("✓ Done")


if __name__ == "__main__":
    asyncio.run(main())
