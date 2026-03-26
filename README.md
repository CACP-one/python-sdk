# CACP Python SDK

Official Python SDK for [CACP](https://cacp.io) - the universal messaging and RPC layer for AI agent interoperability.

CACP enables AI agents built on different frameworks (LangChain, AutoGen, CrewAI, Vertex AI, Claude Agents, etc.) to communicate using a single open standard protocol.

## Features

- ✅ **Complete API Coverage** - All broker endpoints (Agents, Messaging, Tasks, Groups, Auth, API Keys)
- 🔄 **Async & Sync Clients** - Both async (`CacpClient`) and synchronous (`SyncCacpClient`) options
- 🌐 **WebSocket Support** - Real-time communication using Phoenix Channels protocol
- 🔐 **Flexible Authentication** - API keys and JWT token support with user registration
- 📦 **Type Safety** - Full type hints and Pydantic models
- 🛡️ **Error Handling** - Comprehensive error classes with broker error codes (1001-6002)
- 🔄 **Auto Retry** - Configurable retry logic with exponential backoff
- 📊 **Rate Limiting** - Built-in rate limit handling
- 🔍 **Semantic Discovery** - Natural language agent discovery
- 👥 **Team Management** - Groups API for agent teams
- 📋 **Task Tracking** - Long-running asynchronous task management
- 🎯 **Framework Integrations** - Works seamlessly with LangChain, AutoGen, and CrewAI

## Installation

```bash
pip install cacp-sdk
```

**Minimum Python version:** 3.9+

**Requirements:**
- `httpx>=0.25.0` - HTTP client
- `websockets>=12.0` - WebSocket support
- `pydantic>=2.0.0` - Data validation

## Quick Start

### Async Client (Recommended)

```python
import asyncio
from cacp_sdk import CacpClient

async def main():
    # Initialize client with API key
    async with CacpClient(
        base_url="http://localhost:4001",
        api_key="your-api-key"
    ) as client:
        # Register an agent
        agent = await client.agents.register(
            name="my-agent",
            capabilities=["chat", "analysis"],
            metadata={"version": "1.0.0"}
        )
        print(f"✓ Registered agent: {agent.agent_id}")

        # Send a message
        message = await client.messaging.send(
            sender_id=agent.agent_id,
            recipient_id="other-agent-id",
            message_type="chat",
            payload={"text": "Hello, world!"}
        )
        print(f"✓ Sent message: {message.message_id}")

asyncio.run(main())
```

### Synchronous Client (For Scripts/CLIs)

```python
from cacp_sdk import SyncCacpClient

# Initialize sync client
with SyncCacpClient(
    base_url="http://localhost:4001",
    api_key="your-api-key"
) as client:
    # All the same methods, but blocking (no await needed)
    agent = client.agents.register(
        name="my-agent",
        capabilities=["chat"]
    )
    print(f"✓ Registered agent: {agent.agent_id}")
```

## Authentication

### Using API Key (Recommended for Services)

```python
from cacp_sdk import CacpClient

client = CacpClient(
    base_url="http://localhost:4001",
    api_key="your-api-key-here"
)
```

### Using JWT Token (For Users)

```python
from cacp_sdk import CacpClient

client = CacpClient(
    base_url="http://localhost:4001",
    jwt_token="your-jwt-token-here"
)
```

### User Registration & Login

```python
from cacp_sdk import CacpClient

client = CacpClient(base_url="http://localhost:4001")

# Register a new user
response = await client.auth.register(
    user_name="john_doe",
    email="john@example.com",
    password="secure-password"
)
print(f"✓ User registered: {response.user.user_id}")

# Login to get JWT token
login_response = await client.auth.login(
    email="john@example.com",
    password="secure-password"
)
print(f"✓ JWT token: {login_response.access_token}")

# Use the token
authenticated_client = CacpClient(
    base_url="http://localhost:4001",
    jwt_token=login_response.access_token
)

# Refresh token when expired
refresh_response = await client.auth.refresh_token(
    refresh_token=login_response.refresh_token
)
```

## API Modules

### 1. Agents API

Manage agent registration, discovery, and health.

```python
# Register an agent
agent = await client.agents.register(
    name="analysis-agent",
    capabilities=["analysis", "reporting", "financial"],
    metadata={
        "version": "1.0.0",
        "description": "Financial analysis agent",
        "model": "gpt-4"
    }
)

# List all agents
agents = await client.agents.list()
for agent in agents.agents:
    print(f"{agent.name}: {agent.capabilities}")

# Get agent by ID
agent = await client.agents.get(agent_id="agent-123")

# Update agent
updated = await client.agents.update(
    agent_id="agent-123",
    capabilities=["analysis", "reporting", "visualization"]
)

# Delete agent
await client.agents.delete(agent_id="agent-123")

# Query agents by capability
agents = await client.agents.query("financial")

# Semantic agent discovery (NEW!)
discovered = await client.agents.discover(
    query="Find agents that can analyze financial data and generate reports",
    limit=5
)
for agent in discovered.agents:
    print(f"✓ Found: {agent.name}")
    print(f"  Capabilities: {', '.join(agent.capabilities)}")
    print(f"  Match score: {agent.match_score}")
```

### 2. Messaging API

Send and receive messages between agents.

```python
# Send a message
message = await client.messaging.send(
    sender_id="agent-123",
    recipient_id="agent-456",
    message_type="task",
    payload={
        "task_id": "task-789",
        "description": "Analyze Q4 financial data",
        "data": {
            "dataset": "q4_data.csv",
            "metrics": ["revenue", "profit", "growth"]
        }
    }
)
print(f"✓ Message sent: {message.message_id}")

# RPC call (method invocation)
response = await client.messaging.rpc_call(
    sender_id="agent-123",
    recipient_id="agent-456",
    method="process_data",
    params={"input": "some data"},
    timeout=30.0
)
print(f"✓ RPC response: {response.result}")

# Get message status
status = await client.messaging.get_status(message_id="msg-123")
print(f"Status: {status.status}")

# Get message details
message = await client.messaging.get(message_id="msg-123")
```

### 3. Tasks API (NEW!)

Manage long-running asynchronous tasks.

```python
# Create a task
task = await client.tasks.create(
    agent_id="agent-123",
    operation="data-analysis",
    input_data={
        "dataset": "financial_data.csv",
        "analysis_type": "time_series"
    },
    metadata={"priority": "high"}
)
print(f"✓ Task created: {task.task_id}")

# List tasks
tasks = await client.tasks.list(agent_id="agent-123", status="running")

# Get task details
task = await client.tasks.get(task_id="task-123")
print(f"Task status: {task.status}")

# Cancel a task
await client.tasks.cancel(task_id="task-123")

# Retry a failed task
task = await client.tasks.retry(task_id="task-123")

# Poll task status
while task.status in ["pending", "running"]:
    task = await client.tasks.get(task_id=task.task_id)
    await asyncio.sleep(1)
print(f"✓ Task completed: {task.status}, output: {task.output}")
```

### 4. Groups API (NEW!)

Manage agent groups for team communication and broadcasting.

```python
# Create a group
group = await client.groups.create(
    name="data-science-team",
    description="Team for data science tasks"
)
print(f"✓ Group created: {group.id}")

# Add members to group
await client.groups.add_member(
    group_id="group-123",
    agent_id="agent-456"
)
await client.groups.add_member(group_id="group-123", agent_id="agent-789")

# List groups
groups = await client.groups.list()
for group in groups.groups:
    print(f"{group.name}: {len(group.members)} members")

# Get group details
group = await client.groups.get(group_id="group-123")

# Update group
updated = await client.groups.update(
    group_id="group-123",
    description="Updated description"
)

# Broadcast message to group
result = await client.groups.broadcast(
    group_id="group-123",
    sender_id="agent-123",
    message_type="task",
    payload={"task": "Please analyze Q4 data"}
)
print(f"✓ Broadcast to {len(result.delivered_to)} agents")

# Remove member from group
await client.groups.remove_member(
    group_id="group-123",
    agent_id="agent-456"
)

# Delete group
await client.groups.delete(group_id="group-123")
```

### 5. API Keys API (NEW!)

Manage API keys for your account.

```python
# Create an API key
key_response = await client.api_keys.create(
    name="production-key",
    scopes=["agents:read", "agents:write", "messaging:send"]
)
api_key = key_response.api_key
print(f"✓ API key created: {key_response.key_id}")
print(f"  Key (save this!): {api_key}")

# List API keys
keys = await client.api_keys.list()
for key in keys.api_keys:
    print(f"{key.name}: {key.key_id}")

# Get API key details
key = await client.api_keys.get(key_id="key-123")

# Delete an API key
await client.api_keys.delete(key_id="key-123")
```

### 6. WebSocket Support

Real-time communication using Phoenix Channels protocol.

```python
import asyncio
from cacp_sdk import CacpClient

async def websocket_example():
    async with CacpClient(
        base_url="http://localhost:4001",
        jwt_token="your-jwt-token"
    ) as client:
        # Connect to WebSocket
        await client.websocket.connect()

        # Join agent channel
        await client.websocket.join_agent_channel(agent_id="agent-123")

        # Define message handler
        async def handle_message(message):
            print(f"📨 Received: {message.payload}")
            if message.event == "message":
                # Handle incoming messages
                pass
            elif message.event == "rpc_response":
                # Handle RPC responses
                pass

        # Subscribe to messages
        await client.websocket.subscribe(handle_message)

        # Send message via WebSocket
        await client.websocket.send(
            recipient_id="agent-456",
            message_type="chat",
            payload={"text": "Hello via WebSocket!"}
        )

        # Keep connection alive
        await asyncio.sleep(60)

        # Disconnect
        await client.websocket.close()

asyncio.run(websocket_example())
```

## Complete Tutorial: Building a Multi-Agent System

Let's build a complete multi-agent system with agent teams, tasks, and real-time communication.

```python
import asyncio
from cacp_sdk import CacpClient

async def build_multi_agent_system():
    async with CacpClient(
        base_url="http://localhost:4001",
        api_key="your-api-key"
    ) as client:

        # ========================================
        # Step 1: Register specialized agents
        # ========================================
        print("Step 1: Registering agents...")

        data_agent = await client.agents.register(
            name="data-analyst",
            capabilities=["data-analysis", "statistics", "visualization"],
            metadata={"specialty": "financial data"}
        )
        print(f"  ✓ Registered: {data_agent.name}")

        report_agent = await client.agents.register(
            name="report-writer",
            capabilities=["writing", "reporting", "formatting"],
            metadata={"specialty": "business reports"}
        )
        print(f"  ✓ Registered: {report_agent.name}")

        # ========================================
        # Step 2: Create an agent team (group)
        # ========================================
        print("\nStep 2: Creating agent team...")

        team = await client.groups.create(
            name="financial-analysis-team",
            description="Team for financial data analysis and reporting"
        )
        print(f"  ✓ Created group: {team.id}")

        await client.groups.add_member(team.id, data_agent.agent_id)
        await client.groups.add_member(team.id, report_agent.agent_id)
        print(f"  ✓ Added 2 members to team")

        # ========================================
        # Step 3: Create background tasks
        # ========================================
        print("\nStep 3: Creating tasks...")

        analysis_task = await client.tasks.create(
            agent_id=data_agent.agent_id,
            operation="analyze_financial_data",
            input_data={
                "dataset": "q4_2024.csv",
                "metrics": ["revenue", "profit", "growth"]
            },
            metadata={"priority": "high"}
        )
        print(f"  ✓ Created analysis task: {analysis_task.task_id}")

        # ========================================
        # Step 4: Broadcast work to team
        # ========================================
        print("\nStep 4: Broadcasting task to team...")

        result = await client.groups.broadcast(
            group_id=team.id,
            sender_id=data_agent.agent_id,
            message_type="task",
            payload={
                "action": "prepare_report",
                "data": analysis_task.task_id
            }
        )
        print(f"  ✓ Broadcast to {len(result.delivered_to)} agents")

        # ========================================
        # Step 5: Monitor task completion
        # ========================================
        print("\nStep 5: Monitoring task completion...")

        while analysis_task.status in ["pending", "running"]:
            analysis_task = await client.tasks.get(task_id=analysis_task.task_id)
            await asyncio.sleep(1)

        if analysis_task.status == "completed":
            print(f"  ✓ Task completed successfully")
            print(f"  Output: {analysis_task.output}")
        else:
            print(f"  ✗ Task failed: {analysis_task.error}")

        # ========================================
        # Step 6: Semantic discovery for help
        # ========================================
        print("\nStep 6: Discovering agents for next task...")

        discovered = await client.agents.discover(
            query="Find agents that can create charts and visualize data",
            limit=3
        )

        print(f"  Found {len(discovered.agents)} agents:")
        for agent in discovered.agents:
            print(f"    - {agent.name} (score: {agent.match_score:.2f})")

        # ========================================
        # Step 7: Cleanup
        # ========================================
        print("\nStep 7: Cleaning up...")

        await client.groups.delete(team.id)
        await client.agents.delete(data_agent.agent_id)
        await client.agents.delete(report_agent.agent_id)
        print("  ✓ Cleanup complete")

asyncio.run(build_multi_agent_system())
```

## Configuration

### Basic Configuration

```python
from cacp_sdk import CacpClient

client = CacpClient(
    base_url="http://localhost:4001",
    api_key="your-api-key",
    timeout=30.0,          # Request timeout in seconds
    max_retries=3,         # Maximum retry attempts
    retry_delay=1.0,       # Initial retry delay in seconds
)
```

### Custom Logger

```python
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("cacp_sdk")

client = CacpClient(
    base_url="http://localhost:4001",
    api_key="your-api-key",
    logger=logger
)
```

### Request/Response Callbacks

```python
def on_request(method: str, path: str, headers: dict):
    print(f"→ Request: {method} {path}")
    print(f"  Request ID: {headers.get('X-Request-ID')}")

def on_response(path: str, status: int, response: dict):
    print(f"← Response: {status} for {path}")

client = CacpClient(
    base_url="http://localhost:4001",
    api_key="your-api-key",
    on_request=on_request,
    on_response=on_response
)
```

## Error Handling

Comprehensive error handling with specific error types:

```python
from cacp_sdk import (
    CacpError,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    TimeoutError,
    AgentNotFoundError,
    MessageError,
    TaskNotFoundError,
    GroupNotFoundError,
    InvalidCredentialsError,
    QuotaExceededError,
    RpcNotFoundError
)

try:
    agent = await client.agents.get(agent_id="non-existent")
except AgentNotFoundError as e:
    print(f"✗ Agent not found: {e.message}")
    print(f"  Error code: {e.code}")
    print(f"  Request ID: {e.request_id}")

except RateLimitError as e:
    print(f"✗ Rate limited, retry after {e.retry_after} seconds")

except AuthenticationError as e:
    print(f"✗ Authentication failed: {e.message}")

except InvalidCredentialsError as e:
    print(f"✗ Invalid credentials: {e.message}")

except QuotaExceededError as e:
    print(f"✗ Quota exceeded: {e.message}")

except CacpError as e:
    print(f"✗ CACP error: {e.message} (code: {e.code})")
```

### Common Error Codes

| Error Code | Error Type | Description |
|------------|------------|-------------|
| 1001 | InvalidCredentialsError | Invalid credentials |
| 1002 | AccountDisabledError | Account disabled |
| 1003 | InvalidTokenError | Invalid token |
| 1004 | QuotaExceededError | Quota exceeded |
| 2001 | AgentNotFoundError | Agent not found |
| 2002 | DuplicateAgentError | Agent already exists |
| 2003 | AgentNotInGroupError | Agent not in group |
| 3001 | MessageNotFoundError | Message not found |
| 3002 | MessageError | Invalid message format |
| 5001 | ValidationError | Validation error |
| 5002 | RateLimitError | Rate limit exceeded |
| 6001 | TaskNotFoundError | Task not found |
| 6002 | TaskStateError | Invalid task operation |
| 7001 | GroupNotFoundError | Group not found |

## Framework Integrations

### LangChain Integration

```python
from langchain.agents import AgentExecutor
from langchain.tools import Tool
from cacp_sdk import CacpClient

class CacpAgentTool:
    """Use CACP agents as LangChain tools."""

    def __init__(self, client: CacpClient, capability: str):
        self.client = client
        self.capability = capability

    async def run(self, input: str) -> str:
        # Discover agents by capability
        agents = await self.client.agents.query(self.capability)
        if not agents.agents:
            return f"No agent found with capability: {self.capability}"

        # Send RPC call
        response = await self.client.messaging.rpc_call(
            sender_id="my-agent",
            recipient_id=agents.agents[0].agent_id,
            method="process",
            params={"input": input}
        )
        return response.result

# Use in LangChain
client = CacpClient(base_url="http://localhost:4001", api_key="key")
code_tool = Tool(
    name="code-generator",
    description="Generate Python code",
    func=CacpAgentTool(client, "code-generation").run
)
```

### AutoGen Integration

```python
import autogen
from cacp_sdk import CacpClient

class CacpRemoteAgent(autogen.ConversableAgent):
    """AutoGen agent that communicates via CACP."""

    def __init__(self, client: CacpClient, remote_agent_id: str, **kwargs):
        super().__init__(**kwargs)
        self.client = client
        self.remote_agent_id = remote_agent_id

    async def generate_reply_messages(self, messages, **kwargs):
        last_message = messages[-1]["content"]

        response = await self.client.messaging.rpc_call(
            sender_id="my-agent",
            recipient_id=self.remote_agent_id,
            method="chat",
            params={"message": last_message}
        )
        return [autogen.AssistantMessage(content=response.result)]
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=cacp_sdk --cov-report=html

# Type checking
mypy cacp_sdk

# Linting
ruff check cacp_sdk

# Formatting
black cacp_sdk

# Watch mode
pytest-watch
```

## Links

- 📚 [Documentation](https://docs.cacp.io)
- 🐙 [GitHub Repository](https://github.com/cacp/cacp)
- 📖 [Protocol Specification](https://github.com/cacp/cacp/blob/main/spec/README.md)
- 🐛 [Issue Tracker](https://github.com/cacp/cacp/issues)
- 💬 [Discord Community](https://discord.gg/cacp)

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

For questions and support:
- 📧 Email: support@cacp.io
- 💬 Discord: https://discord.gg/cacp
- 📖 Docs: https://docs.cacp.io