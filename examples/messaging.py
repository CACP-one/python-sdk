"""
Messaging Example

This example demonstrates how to send messages between agents.
"""

import asyncio
import os

from cacp_sdk import CacpClient


async def main() -> None:
    base_url = os.getenv("CACP_URL", "http://localhost:4001")
    api_key = os.getenv("CACP_API_KEY", "your-api-key")

    async with CacpClient(base_url=base_url, api_key=api_key) as client:
        # Register two agents
        print("Registering agents...")
        sender = await client.agents.register(
            name="sender-agent",
            capabilities=["send-messages"],
        )
        receiver = await client.agents.register(
            name="receiver-agent",
            capabilities=["receive-messages", "process-data"],
        )

        print(f"Sender: {sender.id}")
        print(f"Receiver: {receiver.id}")

        # Send a message
        print("\nSending message...")
        message = await client.messaging.send(
            to_agent=receiver.id,
            content={
                "text": "Hello from sender!",
                "data": {"value": 42},
            },
            message_type="request",
            priority="normal",
        )

        print(f"✓ Message sent: {message.id}")
        print(f"  Status: {message.status}")

        # Check message status
        print("\nChecking message status...")
        status = await client.messaging.get_status(message.id)
        print(f"  Current status: {status}")

        # Wait for completion
        print("\nWaiting for message completion...")
        try:
            completed = await client.messaging.wait_for_completion(
                message.id,
                timeout=30.0,
            )
            print(f"✓ Message completed: {completed.status}")
        except Exception as e:
            print(f"Message did not complete: {e}")

        # Broadcast a message
        print("\nBroadcasting message to all agents...")
        broadcast_messages = await client.messaging.broadcast(
            content={"event": "system_notification", "message": "Test broadcast"},
        )
        print(f"✓ Broadcast sent to {len(broadcast_messages)} agents")

        # Clean up
        print("\nCleaning up...")
        await client.agents.delete(sender.id)
        await client.agents.delete(receiver.id)
        print("✓ Done")


if __name__ == "__main__":
    asyncio.run(main())
