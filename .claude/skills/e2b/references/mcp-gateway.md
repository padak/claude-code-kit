# MCP Gateway

E2B's MCP Gateway provides seamless access to 200+ Model Context Protocol (MCP) servers, enabling sandboxes to integrate with external tools and services for data access, cloud operations, web scraping, business automation, and AI capabilities.

## What is MCP Gateway?

### Model Context Protocol Overview

The Model Context Protocol (MCP) is an open standard that allows AI agents and LLMs to securely connect to external data sources and tools. MCP servers expose capabilities through a standardized interface that any MCP client can consume.

### E2B's MCP Integration

E2B provides built-in MCP Gateway functionality that:
- **Hosts 200+ pre-configured MCP servers** from Docker's catalog
- **Runs servers inside sandboxes** with proper isolation
- **Provides HTTP access** both from outside and inside sandboxes
- **Manages authentication** through bearer tokens
- **Supports custom configuration** per server instance

### Benefits

1. **No Infrastructure Setup**: MCP servers are pre-configured and ready to use
2. **Secure Isolation**: Each sandbox gets its own MCP server instances
3. **Flexible Access**: Connect from external clients or from code running in the sandbox
4. **Rich Ecosystem**: Access to databases, cloud APIs, web tools, business platforms, and more
5. **Unified Interface**: All tools exposed through standardized MCP protocol

## Quickstart

### Enabling MCP Servers

Enable MCP servers when creating a sandbox by passing configuration for each server you want to use.

**Python (using JavaScript SDK):**
```python
from e2b_code_interpreter import Sandbox
import os

sandbox = Sandbox.create(
    mcp={
        'browserbase': {
            'apiKey': os.environ['BROWSERBASE_API_KEY'],
            'geminiApiKey': os.environ['GEMINI_API_KEY'],
            'projectId': os.environ['BROWSERBASE_PROJECT_ID']
        },
        'exa': {
            'apiKey': os.environ['EXA_API_KEY']
        },
        'notion': {
            'internalIntegrationToken': os.environ['NOTION_API_KEY']
        }
    }
)
```

**JavaScript:**
```javascript
import { Sandbox } from '@e2b/code-interpreter'

const sandbox = await Sandbox.create({
    mcp: {
        browserbase: {
            apiKey: process.env.BROWSERBASE_API_KEY,
            geminiApiKey: process.env.GEMINI_API_KEY,
            projectId: process.env.BROWSERBASE_PROJECT_ID
        },
        exa: {
            apiKey: process.env.EXA_API_KEY
        },
        notion: {
            internalIntegrationToken: process.env.NOTION_API_KEY
        }
    }
})
```

### Getting MCP URL and Token

Each sandbox provides a unique MCP URL and authentication token:

**Python:**
```python
# Get MCP endpoint URL
mcp_url = sandbox.get_mcp_url()
# Example: https://e2b-mcp-gateway.com/sandbox/abc123/mcp

# Get authentication token
mcp_token = sandbox.get_mcp_token()
```

**JavaScript:**
```javascript
const mcpUrl = sandbox.getMcpUrl()
const mcpToken = await sandbox.getMcpToken()
```

### Connecting from Outside the Sandbox

Connect to MCP servers from your application code running outside the sandbox.

**Using Official MCP Client (TypeScript):**
```typescript
import { Client } from '@modelcontextprotocol/sdk/client/index.js'
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js'

const client = new Client({
    name: 'e2b-mcp-client',
    version: '1.0.0'
})

const transport = new StreamableHTTPClientTransport(
    new URL(sandbox.getMcpUrl()),
    {
        requestInit: {
            headers: {
                'Authorization': `Bearer ${await sandbox.getMcpToken()}`
            }
        }
    }
)

await client.connect(transport)

// List available tools
const tools = await client.listTools()
console.log('Available tools:', tools.tools.map(t => t.name))

// Call a tool
const result = await client.callTool({
    name: 'some_tool',
    arguments: { param: 'value' }
})

await client.close()
await sandbox.kill()
```

### Connecting from Inside the Sandbox

Access the MCP gateway from code running within the sandbox itself:

**Internal MCP URL:**
```
http://localhost:50005/mcp
```

**Important**: When connecting from inside the sandbox, you must include the Authorization header with the MCP token. How this is added depends on your MCP client.

## Available Servers (200+)

E2B provides access to 200+ MCP servers organized by category. Below are the most commonly used servers in each category.

### Data & Database Servers

**MongoDB**
- **Purpose**: NoSQL document database operations
- **Configuration**: `mdbMcpConnectionString`
- **Use Cases**: CRUD operations, aggregations, document queries

**PostgreSQL**
- **Purpose**: Relational database operations
- **Configuration**: `url` (connection string)
- **Use Cases**: SQL queries, table operations, transactions

**CockroachDB**
- **Purpose**: Distributed SQL database
- **Configuration**: `host`, `port`, `username`, `crdbPwd`, SSL certificates
- **Use Cases**: Scalable SQL operations with high availability

**Elasticsearch**
- **Purpose**: Search and analytics engine
- **Configuration**: `url`, optional `esApiKey`
- **Use Cases**: Full-text search, log analytics, data aggregation

**Redis**
- **Purpose**: In-memory data store
- **Configuration**: `host`, `port`, credentials, SSL options
- **Use Cases**: Caching, session storage, pub/sub messaging

**Astra DB**
- **Purpose**: Cassandra-based cloud database
- **Configuration**: `astraDbApplicationToken`, `endpoint`
- **Use Cases**: Wide-column NoSQL operations

### Cloud & Infrastructure

**Azure Kubernetes Service (AKS)**
- **Purpose**: Kubernetes cluster management on Azure
- **Configuration**: `azureDir`, `kubeconfig`, `accessLevel`
- **Use Cases**: Deploy and manage containerized applications

**AWS CDK/Core**
- **Purpose**: AWS infrastructure as code
- **Configuration**: AWS credentials
- **Use Cases**: Define and provision AWS resources

**Google Cloud Run**
- **Purpose**: Serverless container deployment
- **Configuration**: `credentialsPath` to credentials file
- **Use Cases**: Deploy and manage Cloud Run services

**Kubernetes**
- **Purpose**: Container orchestration
- **Configuration**: `configPath` to kubeconfig file
- **Use Cases**: Manage pods, deployments, services

### Web & Content Tools

**Firecrawl**
- **Purpose**: Web scraping and content extraction
- **Configuration**: `apiKey`, retry configuration, credit thresholds
- **Use Cases**: Extract structured data from websites

**Brave Search**
- **Purpose**: Web search API
- **Configuration**: `apiKey`
- **Use Cases**: Privacy-focused web search queries

**Perplexity**
- **Purpose**: AI-powered search
- **Configuration**: `perplexityApiKey`
- **Use Cases**: Question answering, research queries

**DuckDuckGo**
- **Purpose**: Privacy-focused web search
- **Configuration**: None (no authentication needed)
- **Use Cases**: Anonymous web searches

**Tavily**
- **Purpose**: AI-optimized search API
- **Configuration**: `apiKey`
- **Use Cases**: Research, fact-checking, content discovery

### Business & Productivity

**Slack**
- **Purpose**: Team communication and automation
- **Configuration**: `botToken`, `teamId`, optional channel IDs
- **Use Cases**: Send messages, read channels, manage users

**Notion**
- **Purpose**: Workspace and knowledge management
- **Configuration**: `internalIntegrationToken`
- **Use Cases**: Create/read pages, manage databases, search content

**GitHub (Official)**
- **Purpose**: Git repository operations
- **Configuration**: `githubPersonalAccessToken`
- **Use Cases**: Code operations, issues, pull requests, workflows

**Jira/Confluence**
- **Purpose**: Project management and documentation
- **Configuration**: Base URLs, API tokens or personal tokens
- **Use Cases**: Issue tracking, documentation management

**HubSpot**
- **Purpose**: CRM and marketing automation
- **Configuration**: `apiKey`
- **Use Cases**: Contact management, deal tracking, email campaigns

### Development & Code

**GitHub Chat**
- **Purpose**: Conversational interface to GitHub
- **Configuration**: `githubApiKey`
- **Use Cases**: Repository queries, code search, issue management

**JetBrains IDE**
- **Purpose**: IDE integration
- **Configuration**: `port` configuration
- **Use Cases**: Code navigation, refactoring, debugging

**ast-grep**
- **Purpose**: Structural code search
- **Configuration**: `path` to code directory
- **Use Cases**: Find code patterns, refactor code

**Semgrep**
- **Purpose**: Static code analysis
- **Configuration**: Docker setup
- **Use Cases**: Security scanning, code quality checks

### AI & Content Generation

**OpenAI/Browserbase**
- **Purpose**: Browser automation with AI
- **Configuration**: Multiple API keys (Gemini, project ID)
- **Use Cases**: Automated web browsing, data extraction

**Hugging Face**
- **Purpose**: ML model hub
- **Configuration**: None (basic access)
- **Use Cases**: Model inference, dataset access

**ElevenLabs**
- **Purpose**: Text-to-speech AI
- **Configuration**: Optional `apiKey`, `data` path
- **Use Cases**: Voice generation, audio processing

### Finance & Commerce

**Stripe**
- **Purpose**: Payment processing
- **Configuration**: `secretKey`
- **Use Cases**: Process payments, manage subscriptions, invoicing

**Razorpay**
- **Purpose**: Payment gateway (India)
- **Configuration**: `keyId`, optional `keySecret`
- **Use Cases**: Accept payments, refunds, settlements

**Mercado Pago**
- **Purpose**: Payment platform (Latin America)
- **Configuration**: `mercadoPagoApiKey`
- **Use Cases**: Process payments, manage checkouts

### Special Purpose Servers

**Python Interpreter**
- **Purpose**: Execute Python code in notebook-like environment
- **Configuration**: None
- **Use Cases**: Code execution, data analysis

**Filesystem**
- **Purpose**: File system operations
- **Configuration**: `paths` array for allowed directory access
- **Use Cases**: Read/write files with controlled access

**Memory**
- **Purpose**: Knowledge graph-based persistent storage
- **Configuration**: None
- **Use Cases**: Store and retrieve structured information

**Time**
- **Purpose**: Timezone conversions and time operations
- **Configuration**: None
- **Use Cases**: Time zone management, date calculations

## Connection Examples

### Official MCP Client

**TypeScript:**
```typescript
import { Client } from '@modelcontextprotocol/sdk/client/index.js'
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js'

const client = new Client({
    name: 'e2b-mcp-client',
    version: '1.0.0'
})

const transport = new StreamableHTTPClientTransport(
    new URL(sandbox.getMcpUrl()),
    {
        requestInit: {
            headers: {
                'Authorization': `Bearer ${await sandbox.getMcpToken()}`
            }
        }
    }
)

await client.connect(transport)

// List available tools
const tools = await client.listTools()

// Call a tool
const result = await client.callTool({
    name: 'github_create_issue',
    arguments: {
        owner: 'myorg',
        repo: 'myrepo',
        title: 'Bug report',
        body: 'Description here'
    }
})
```

### Claude Desktop

Connect Claude Desktop to your E2B MCP Gateway:

```bash
claude mcp add \
    --transport http \
    e2b-mcp-gateway \
    <mcp_url> \
    --header "Authorization: Bearer <mcp_token>"
```

**Example:**
```bash
claude mcp add \
    --transport http \
    e2b-mcp-gateway \
    https://e2b-mcp-gateway.com/sandbox/abc123/mcp \
    --header "Authorization: Bearer eyJhbGc..."
```

### OpenAI Agents SDK

**TypeScript:**
```typescript
import { MCPServerStreamableHttp } from '@openai/agents'

const mcp = new MCPServerStreamableHttp({
    url: mcpUrl,
    name: 'E2B MCP Gateway',
    requestInit: {
        headers: {
            'Authorization': `Bearer ${await sandbox.getMcpToken()}`
        }
    }
})

// Use with OpenAI Agents
const agent = new Agent({
    name: 'Data Agent',
    mcpServers: [mcp]
})
```

### Custom Clients

Any HTTP client can connect to the MCP Gateway:

**Python with requests:**
```python
import requests

headers = {
    'Authorization': f'Bearer {mcp_token}',
    'Content-Type': 'application/json'
}

# List tools
response = requests.post(
    f'{mcp_url}/list_tools',
    headers=headers
)
tools = response.json()

# Call tool
response = requests.post(
    f'{mcp_url}/call_tool',
    headers=headers,
    json={
        'name': 'postgres_query',
        'arguments': {
            'query': 'SELECT * FROM users LIMIT 10'
        }
    }
)
result = response.json()
```

**cURL:**
```bash
# List tools
curl -X POST \
    -H "Authorization: Bearer $MCP_TOKEN" \
    -H "Content-Type: application/json" \
    "$MCP_URL/list_tools"

# Call tool
curl -X POST \
    -H "Authorization: Bearer $MCP_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"name":"slack_send_message","arguments":{"channel":"general","text":"Hello"}}' \
    "$MCP_URL/call_tool"
```

## MCP Inspector for Debugging

The [MCP Inspector](https://github.com/modelcontextprotocol/inspector) is an official debugging tool that provides a web interface for testing MCP servers.

**Running MCP Inspector:**
```bash
npx @modelcontextprotocol/inspector \
    --transport http \
    --url <mcp_url> \
    --header "Authorization: Bearer <mcp_token>"
```

**Example:**
```bash
npx @modelcontextprotocol/inspector \
    --transport http \
    --url https://e2b-mcp-gateway.com/sandbox/abc123/mcp \
    --header "Authorization: Bearer eyJhbGc..."
```

This opens a web interface where you can:
- **Browse available tools** - See all tools exposed by enabled MCP servers
- **Test tool calls** - Execute tools with different parameters
- **Inspect payloads** - View request/response JSON
- **Debug connection issues** - Verify authentication and connectivity
- **Explore schemas** - Understand tool input/output formats

## Common Patterns

### Pattern 1: Multi-Tool Agent

Enable multiple MCP servers for comprehensive capabilities:

```python
from e2b_code_interpreter import Sandbox
import os

sandbox = Sandbox.create(
    mcp={
        # Data access
        'postgres': {'url': os.environ['DATABASE_URL']},

        # Web research
        'brave': {'apiKey': os.environ['BRAVE_API_KEY']},
        'firecrawl': {'apiKey': os.environ['FIRECRAWL_API_KEY']},

        # Business automation
        'slack': {
            'botToken': os.environ['SLACK_BOT_TOKEN'],
            'teamId': os.environ['SLACK_TEAM_ID']
        },
        'github': {
            'githubPersonalAccessToken': os.environ['GITHUB_TOKEN']
        }
    }
)

# Now your agent can query databases, search the web,
# send Slack messages, and manage GitHub issues all through MCP
```

### Pattern 2: Data Pipeline

Use MCP for ETL operations:

```typescript
const sandbox = await Sandbox.create({
    mcp: {
        mongodb: { mdbMcpConnectionString: process.env.MONGO_URL },
        postgres: { url: process.env.POSTGRES_URL },
        redis: {
            host: 'localhost',
            port: 6379,
            password: process.env.REDIS_PASSWORD
        }
    }
})

// Connect MCP client
const client = new Client({ name: 'etl-pipeline', version: '1.0.0' })
const transport = new StreamableHTTPClientTransport(
    new URL(sandbox.getMcpUrl()),
    { requestInit: { headers: { 'Authorization': `Bearer ${await sandbox.getMcpToken()}` }}}
)
await client.connect(transport)

// Extract from MongoDB
const mongoData = await client.callTool({
    name: 'mongodb_find',
    arguments: { collection: 'users', query: {} }
})

// Transform (your code)
const transformed = transformData(mongoData)

// Load to PostgreSQL
await client.callTool({
    name: 'postgres_insert',
    arguments: { table: 'users', data: transformed }
})

// Cache in Redis
await client.callTool({
    name: 'redis_set',
    arguments: { key: 'users_cache', value: JSON.stringify(transformed) }
})
```

### Pattern 3: AI Agent with Tools

LLM-powered agent with MCP tool access:

```python
from anthropic import Anthropic
from e2b_code_interpreter import Sandbox

# Create sandbox with MCP servers
sandbox = Sandbox.create(
    mcp={
        'github': {'githubPersonalAccessToken': github_token},
        'notion': {'internalIntegrationToken': notion_token}
    }
)

# Get MCP tools as Claude tools
mcp_url = sandbox.get_mcp_url()
mcp_token = sandbox.get_mcp_token()

# Define tools for Claude (simplified example)
tools = get_mcp_tools_as_claude_tools(mcp_url, mcp_token)

# Create Claude client
client = Anthropic()

# Agent loop
while True:
    response = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1024,
        messages=messages,
        tools=tools
    )

    if response.stop_reason == "tool_use":
        # Execute tool via MCP
        tool_use = next(block for block in response.content if block.type == "tool_use")
        result = call_mcp_tool(mcp_url, mcp_token, tool_use.name, tool_use.input)

        # Continue conversation with result
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": result})
    else:
        break
```

### Pattern 4: Internal Sandbox Access

Access MCP from code running inside the sandbox:

```python
# This code runs INSIDE the E2B sandbox
import os
import requests

# MCP is available at localhost inside sandbox
MCP_URL = 'http://localhost:50005/mcp'
MCP_TOKEN = os.environ['E2B_MCP_TOKEN']  # Set when running code

headers = {
    'Authorization': f'Bearer {MCP_TOKEN}',
    'Content-Type': 'application/json'
}

# Query database via MCP
response = requests.post(
    f'{MCP_URL}/call_tool',
    headers=headers,
    json={
        'name': 'postgres_query',
        'arguments': {'query': 'SELECT * FROM products'}
    }
)

products = response.json()
print(f"Found {len(products)} products")
```

### Pattern 5: Dynamic Tool Discovery

Discover available tools at runtime:

```typescript
import { Client } from '@modelcontextprotocol/sdk/client/index.js'
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js'

// Create sandbox with MCP servers
const sandbox = await Sandbox.create({
    mcp: {
        github: { githubPersonalAccessToken: process.env.GITHUB_TOKEN },
        slack: { botToken: process.env.SLACK_BOT_TOKEN },
        notion: { internalIntegrationToken: process.env.NOTION_TOKEN }
    }
})

// Connect MCP client
const client = new Client({ name: 'dynamic-agent', version: '1.0.0' })
const transport = new StreamableHTTPClientTransport(
    new URL(sandbox.getMcpUrl()),
    { requestInit: { headers: { 'Authorization': `Bearer ${await sandbox.getMcpToken()}` }}}
)
await client.connect(transport)

// Discover all available tools
const toolsResult = await client.listTools()
const tools = toolsResult.tools

// Group by provider
const byProvider = {}
for (const tool of tools) {
    const provider = tool.name.split('_')[0]  // e.g., 'github' from 'github_create_issue'
    if (!byProvider[provider]) byProvider[provider] = []
    byProvider[provider].push(tool)
}

console.log('Available tools by provider:')
for (const [provider, providerTools] of Object.entries(byProvider)) {
    console.log(`  ${provider}: ${providerTools.length} tools`)
}

// Now use tools dynamically based on user intent
const userRequest = "Create a GitHub issue and notify Slack"
const toolsToUse = selectToolsForRequest(userRequest, tools)
```

## Troubleshooting

### Connection Issues

**Problem**: Cannot connect to MCP Gateway

**Solutions**:
1. Verify the MCP URL is correct:
   ```python
   print(f"MCP URL: {sandbox.get_mcp_url()}")
   ```

2. Check authentication token:
   ```python
   token = sandbox.get_mcp_token()
   print(f"Token length: {len(token)}")
   ```

3. Test with MCP Inspector:
   ```bash
   npx @modelcontextprotocol/inspector --transport http --url $MCP_URL --header "Authorization: Bearer $MCP_TOKEN"
   ```

### Authentication Errors

**Problem**: 401 Unauthorized or 403 Forbidden

**Solutions**:
1. Ensure Authorization header is properly formatted:
   ```
   Authorization: Bearer <token>
   ```
   (Note: "Bearer" followed by a space, then the token)

2. Verify token hasn't expired (recreate sandbox if needed)

3. Check that the token matches the sandbox:
   ```python
   # Token is sandbox-specific
   sandbox1 = Sandbox.create(mcp={...})
   token1 = sandbox1.get_mcp_token()

   # This won't work - wrong token
   sandbox2 = Sandbox.create(mcp={...})
   # Using token1 with sandbox2.get_mcp_url() will fail
   ```

### Missing Tools

**Problem**: Expected tools not available when listing

**Solutions**:
1. Verify MCP servers were enabled at sandbox creation:
   ```python
   # Must pass mcp config when creating
   sandbox = Sandbox.create(mcp={'github': {...}})
   ```

2. Check server configuration is correct:
   ```python
   # Each server has required configuration fields
   sandbox = Sandbox.create(
       mcp={
           'github': {
               'githubPersonalAccessToken': token  # Required!
           }
       }
   )
   ```

3. List tools to see what's actually available:
   ```javascript
   const tools = await client.listTools()
   console.log('Available:', tools.tools.map(t => t.name))
   ```

### Configuration Errors

**Problem**: MCP server fails to start due to invalid configuration

**Solutions**:
1. Review required configuration fields for each server (see Available Servers section)

2. Validate credentials before passing to sandbox:
   ```python
   import os

   # Check required env vars exist
   required = ['GITHUB_TOKEN', 'SLACK_BOT_TOKEN']
   missing = [key for key in required if not os.environ.get(key)]
   if missing:
       raise ValueError(f"Missing env vars: {missing}")

   sandbox = Sandbox.create(mcp={...})
   ```

3. Test server configuration independently if possible

### Timeout Issues

**Problem**: MCP tool calls timing out

**Solutions**:
1. Increase sandbox timeout:
   ```python
   sandbox = Sandbox.create(
       timeout=300,  # 5 minutes
       mcp={...}
   )
   ```

2. Check network connectivity from sandbox:
   ```python
   # Test if external service is reachable
   sandbox.run_code('''
   import requests
   response = requests.get("https://api.github.com/status")
   print(response.status_code)
   ''')
   ```

3. Use async operations where possible

### Tool Call Failures

**Problem**: Tool calls return errors

**Solutions**:
1. Check tool input schema:
   ```javascript
   const tools = await client.listTools()
   const tool = tools.tools.find(t => t.name === 'github_create_issue')
   console.log('Input schema:', tool.inputSchema)
   ```

2. Validate arguments match schema:
   ```python
   # Ensure all required fields are provided
   result = client.call_tool(
       name='postgres_query',
       arguments={
           'query': 'SELECT * FROM users'  # Required field
       }
   )
   ```

3. Review error messages in tool response:
   ```javascript
   try {
       const result = await client.callTool({...})
   } catch (error) {
       console.error('Tool error:', error.message)
       console.error('Details:', error.details)
   }
   ```

### Rate Limiting

**Problem**: External service rate limits exceeded

**Solutions**:
1. Implement exponential backoff:
   ```python
   import time

   retries = 3
   for i in range(retries):
       try:
           result = call_mcp_tool(...)
           break
       except RateLimitError:
           wait = 2 ** i  # 1s, 2s, 4s
           time.sleep(wait)
   ```

2. Cache results when possible:
   ```python
   # Use Redis MCP server to cache responses
   cache_key = f"github_user_{username}"

   # Try cache first
   cached = redis_get(cache_key)
   if cached:
       return cached

   # Fetch and cache
   result = github_get_user(username)
   redis_set(cache_key, result, ttl=3600)
   ```

3. Monitor usage and adjust accordingly

## Best Practices

### Security

1. **Never hardcode credentials**:
   ```python
   # Bad
   sandbox = Sandbox.create(
       mcp={'github': {'githubPersonalAccessToken': 'ghp_abc123'}}
   )

   # Good
   import os
   sandbox = Sandbox.create(
       mcp={'github': {'githubPersonalAccessToken': os.environ['GITHUB_TOKEN']}}
   )
   ```

2. **Use minimal permissions**: Configure API tokens with only required scopes

3. **Rotate credentials regularly**: Especially for production workloads

4. **Isolate per user**: Create separate sandboxes per user/session

### Performance

1. **Enable only needed servers**: Don't enable all 200+ servers if you only need a few
   ```python
   # Only enable what you need
   sandbox = Sandbox.create(
       mcp={
           'postgres': {'url': db_url},  # Just what's needed
       }
   )
   ```

2. **Reuse sandboxes**: Connect to existing sandboxes instead of creating new ones
   ```python
   # Create once
   sandbox = Sandbox.create(mcp={...})
   save_sandbox_id(sandbox.sandbox_id)

   # Reconnect later
   sandbox = Sandbox.connect(saved_id)
   ```

3. **Use batch operations**: When tools support it, batch multiple operations
   ```python
   # Better: Single batch call
   result = call_tool('postgres_batch_insert', {'data': records})

   # Worse: Multiple individual calls
   for record in records:
       call_tool('postgres_insert', {'data': record})
   ```

### Reliability

1. **Handle errors gracefully**:
   ```javascript
   try {
       const result = await client.callTool({...})
   } catch (error) {
       if (error.code === 'RATE_LIMIT') {
           // Wait and retry
       } else if (error.code === 'TIMEOUT') {
           // Handle timeout
       } else {
           // Log and alert
       }
   }
   ```

2. **Implement retries**: With exponential backoff for transient failures

3. **Monitor tool availability**: Check that required tools are available before use
   ```python
   tools = client.list_tools()
   required = ['postgres_query', 'slack_send_message']
   available = [t.name for t in tools.tools]

   if not all(r in available for r in required):
       raise ValueError("Required tools not available")
   ```

### Observability

1. **Log MCP operations**:
   ```python
   import logging

   logger = logging.getLogger(__name__)

   logger.info(f"Calling MCP tool: {tool_name}")
   result = call_mcp_tool(tool_name, args)
   logger.info(f"Tool {tool_name} completed in {elapsed}s")
   ```

2. **Track metrics**: Tool calls, success rates, latencies

3. **Use MCP Inspector during development**: Debug tool behavior before production

## Additional Resources

- **E2B Documentation**: https://e2b.dev/docs
- **MCP Specification**: https://modelcontextprotocol.io
- **MCP Server Catalog**: https://github.com/modelcontextprotocol/servers
- **E2B Cookbook**: https://github.com/e2b-dev/e2b-cookbook (examples and tutorials)
- **MCP Inspector**: https://github.com/modelcontextprotocol/inspector
