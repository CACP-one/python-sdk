# CACP Python SDK

Official Python SDK for [CACP](https://cacp.io) - the universal messaging and RPC layer for AI agent interoperability.

## Installation

```bash
pip install cacp-sdk
```

## Quick Start

### Initialize the Client

```python
from cacp_sdk import CacpClient

# Initialize with API key
client = CacpClient(
    base_url="https://api.cacp.io",
    api_key="your-api-key"
)

# Or with JWT token
client = CacpClient(
    base_url="https://api.cacp.io",
    jwt_token="your-jwt-token"
)
```

### Register an Agent

```python
import asyncio
from cacp_sdk import CacpClient

async def main():
    async with CacpClient(base_url="http://localhost:4001", api_key="your-key") as client:
        # Register a new agent
        agent = await client.agents.register(
            name="my-assistant",
            description="A helpful AI assistant",
            capabilities=["chat", "code-generation", "analysis"],
            metadata={"model": "gpt-4", "version": "1.0"}
        )
        print(f"Registered agent: {agent.id}")

asyncio.run(main())
```

### Send Messages

```python
# Send a direct message
message = await client.messaging.send(
    to_agent="target-agent-id",
    content={"text": "Hello from Python SDK!"},
    message_type="request"
)
print(f"Message sent: {message.id}")

# Send with RPC pattern
response = await client.messaging.rpc_call(
    to_agent="target-agent-id",
    method="process_data",
    params={"input": "some data"},
    timeout=30.0
)
print(f"RPC response: {response}")
```

### WebSocket Real-Time Communication

```python
async with client.websocket.connect() as ws:
    # Subscribe to messages
    await ws.subscribe(agent_id="my-agent-id")
    
    # Listen for messages
    async for message in ws.messages():
        print(f"Received: {message}")
        
        # Send a response
        await ws.send(
            to_agent=message.from_agent,
            content={"response": "Got it!"}
        )
```

### Query Agents by Capability

```python
# Find agents with specific capabilities
agents = await client.agents.query_by_capability(
    capabilities=["code-generation", "python"]
)

for agent in agents:
    print(f"Found: {agent.name} - {agent.capabilities}")
```

### Semantic Search

```python
# Find agents using natural language
agents = await client.agents.semantic_search(
    query="I need an agent that can help with data analysis and visualization"
)

for agent in agents:
    print(f"Match: {agent.name} (score: {agent.match_score})")
```

## Features

- **Async-first design** - Built on `httpx` and `websockets` for high-performance async operations
- **Type hints** - Full type annotations for IDE autocomplete and type checking
- **Automatic retries** - Configurable retry logic with exponential backoff
- **Connection pooling** - Efficient HTTP connection management
- **WebSocket support** - Real-time bidirectional communication
- **Comprehensive error handling** - Structured exceptions for all error cases
- **Observability** - Built-in logging, request ID tracking, and callback hooks
- **Synchronous client** - Blocking client wrapper for scripts and CLIs
- **Broker-aligned error codes** - Direct mapping to broker error codes (2001-7008)

## API Reference

### Client

```python
CacpClient(
    base_url: str,                    # Broker API URL
    api_key: str | None = None,       # API key for authentication
    jwt_token: str | None = None,     # JWT token for authentication
    timeout: float = 30.0,            # Request timeout in seconds
    max_retries: int = 3,             # Maximum retry attempts
    retry_delay: float = 1.0,         # Initial retry delay in seconds
    logger: logging.Logger = None,    # Custom logger for SDK operations
    on_request: Callable = None,      # Callback invoked before each request
    on_response: Callable = None,     # Callback invoked after each response
)
```

### Agents API

```python
# Register a new agent
await client.agents.register(
    name: str,
    description: str,
    capabilities: list[str],
    metadata: dict | None = None,
)

# Get agent by ID
await client.agents.get(agent_id: str)

# List all agents
await client.agents.list(
    status: str | None = None,
    limit: int = 100,
    offset: int = 0,
)

# Update agent
await client.agents.update(
    agent_id: str,
    name: str | None = None,
    description: str | None = None,
    capabilities: list[str] | None = None,
    metadata: dict | None = None,
)

# Delete agent
await client.agents.delete(agent_id: str)

# Query by capability
await client.agents.query_by_capability(
    capabilities: list[str],
    match_all: bool = False,
)

# Semantic search
await client.agents.semantic_search(
    query: str,
    limit: int = 10,
)
```

### Messaging API

```python
# Send a message
await client.messaging.send(
    to_agent: str,
    content: dict,
    message_type: str = "message",
    priority: str = "normal",
    metadata: dict | None = None,
)

# Get message status
await client.messaging.get(message_id: str)

# RPC call with response
await client.messaging.rpc_call(
    to_agent: str,
    method: str,
    params: dict,
    timeout: float = 30.0,
)

# Broadcast to all agents
await client.messaging.broadcast(
    content: dict,
    message_type: str = "message",
)
```

### WebSocket API

```python
# Connect
async with client.websocket.connect() as ws:
    # Subscribe to messages for an agent
    await ws.subscribe(agent_id: str)
    
    # Unsubscribe
    await ws.unsubscribe(agent_id: str)
    
    # Send message
    await ws.send(
        to_agent: str,
        content: dict,
        message_type: str = "message",
    )
    
    # Receive messages
    async for message in ws.messages():
        handle_message(message)
```

## Error Handling

```python
from cacp_sdk import (
    CacpError,
    AuthenticationError,
    AgentNotFoundError,
    MessageError,
    ConnectionError,
    RateLimitError,
)

try:
    agent = await client.agents.get("non-existent-id")
except AgentNotFoundError:
    print("Agent not found")
except AuthenticationError:
    print("Invalid credentials")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except CacpError as e:
    print(f"Error: {e.message} (code: {e.code})")
```

## Observability

### Logging

The SDK provides built-in logging for all HTTP requests and responses:

```python
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create client with custom logger
logger = logging.getLogger("cacp")
client = CacpClient(
    base_url="http://localhost:4001",
    api_key="your-key",
    logger=logger
)
```

### Request/Response Callbacks

Monitor all requests and responses with callbacks:

```python
def log_request(method: str, path: str, headers: dict) -> None:
    print(f"Request: {method} {path}")
    print(f"Request ID: {headers.get('X-Request-ID')}")

def log_response(path: str, status: int, response: dict) -> None:
    print(f"Response: {status} for {path}")
    print(f"Response: {response}")

client = CacpClient(
    base_url="http://localhost:4001",
    api_key="your-key",
    on_request=log_request,
    on_response=log_response
)
```

### Request ID Tracking

Every request includes a unique `X-Request-ID` header for correlation and debugging:

```python
try:
    agent = await client.agents.get("some-id")
except CacpError as e:
    print(f"Error occurred for request ID: {e.request_id}")
    # Use this ID to correlate with broker logs
```

## Integration Examples

### LangChain Integration

```python
from langchain.agents import AgentExecutor
from cacp_sdk import CacpClient

class CacpAgentTool:
    """Use CACP agents as LangChain tools."""
    
    def __init__(self, client: CacpClient, agent_capability: str):
        self.client = client
        self.agent_capability = agent_capability
    
    async def __call__(self, input: str) -> str:
        # Find agent with capability
        agents = await self.client.agents.query_by_capability(
            capabilities=[self.agent_capability]
        )
        if not agents:
            return f"No agent found with capability: {self.agent_capability}"
        
        # Send RPC call
        response = await self.client.messaging.rpc_call(
            to_agent=agents[0].id,
            method="process",
            params={"input": input}
        )
        return response.result

# Use in LangChain
client = CacpClient(base_url="http://localhost:4001", api_key="key")
code_tool = CacpAgentTool(client, "code-generation")
```

### AutoGen Integration

```python
import autogen
from cacp_sdk import CacpClient

class CacpProxyAgent(autogen.ConversableAgent):
    """AutoGen agent that communicates via CACP."""
    
    def __init__(self, client: CacpClient, remote_agent_id: str, **kwargs):
        super().__init__(**kwargs)
        self.client = client
        self.remote_agent_id = remote_agent_id
    
    async def generate_reply(self, messages, **kwargs):
        last_message = messages[-1]["content"]
        
        response = await self.client.messaging.rpc_call(
            to_agent=self.remote_agent_id,
            method="chat",
            params={"message": last_message}
        )
        return response.result
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy cacp_sdk

# Linting
ruff check cacp_sdk

# Formatting
black cacp_sdk
```

## License

MIT License - see [LICENSE](LICENSE) for details.
# python-sdk
