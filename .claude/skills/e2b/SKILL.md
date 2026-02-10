---
name: e2b
description: Execute AI-generated code in secure isolated E2B cloud sandboxes with advanced monitoring, MCP gateway integration (200+ tools), and multi-language support. Use for running Python/JavaScript/TypeScript/Bash code, managing sandbox lifecycle (create, pause, resume, kill, list, connect), monitoring metrics (CPU, memory, disk), handling lifecycle events, uploading/downloading files, streaming command output, environment variable management, and integrating LLMs with code execution capabilities.
---

# E2B Sandbox Skill

Secure isolated cloud VMs for executing AI-generated code. Sandboxes start in ~150ms with full code execution, filesystem, and network access.

## Quick Reference

| Feature | Reference |
|---------|-----------|
| Getting started | [quickstart.md](references/quickstart.md) |
| Lifecycle management | [sandbox-lifecycle.md](references/sandbox-lifecycle.md) |
| Code execution | [code-interpreting.md](references/code-interpreting.md) |
| File operations | [filesystem.md](references/filesystem.md) |
| Monitoring & events | [monitoring-and-events.md](references/monitoring-and-events.md) |
| Persistence (pause/resume) | [persistence.md](references/persistence.md) |
| MCP Gateway (200+ tools) | [mcp-gateway.md](references/mcp-gateway.md) |
| Custom templates | [custom-templates.md](references/custom-templates.md) |
| Advanced patterns | [advanced-sandbox.md](references/advanced-sandbox.md) |

## Installation

```bash
# Python
pip install e2b-code-interpreter

# JavaScript/TypeScript
npm i @e2b/code-interpreter
```

Required environment variable:
```bash
E2B_API_KEY=e2b_***  # Get from https://e2b.dev/dashboard?tab=keys
```

## Core Patterns

### Pattern 1: One-shot Code Execution

```python
from e2b_code_interpreter import Sandbox

with Sandbox() as sandbox:
    execution = sandbox.run_code('print("Hello from E2B!")')
    print(execution.text)
```

```javascript
import { Sandbox } from '@e2b/code-interpreter'

const sandbox = await Sandbox.create()
const execution = await sandbox.runCode('console.log("Hello!")')
console.log(execution.text)
await sandbox.kill()
```

### Pattern 2: Multi-language Execution

```python
# Python (default)
sandbox.run_code('import pandas as pd; df.describe()')

# JavaScript
sandbox.run_code('await fetch(url)', language='js')

# TypeScript
sandbox.run_code('const x: number = 42', language='ts')

# Bash
sandbox.run_code('ls -la /home/user', language='bash')
```

### Pattern 3: File Upload + Analysis

```python
# Upload dataset
sandbox.files.write('/home/user/data.csv', csv_content)

# Run analysis
execution = sandbox.run_code('''
import pandas as pd
df = pd.read_csv('/home/user/data.csv')
df.describe()
''')

# Download results
result = sandbox.files.read('/home/user/output.png')
```

### Pattern 4: Streaming Output

```python
sandbox.commands.run(
    'for i in {1..5}; do echo "Line $i"; sleep 1; done',
    on_stdout=lambda data: print(f"OUT: {data}"),
    on_stderr=lambda data: print(f"ERR: {data}")
)
```

### Pattern 5: Background Commands

```python
command = sandbox.commands.run(
    'python server.py',
    background=True
)
# ... do other work ...
command.kill()
```

### Pattern 6: Persistence (Beta)

```python
# Create with auto-pause
sandbox = Sandbox.beta_create(auto_pause=True, timeout=600)

# Do work...
sandbox.run_code(code)

# Pause (saves filesystem + memory)
sandbox.beta_pause()
saved_id = sandbox.sandbox_id

# Later: Resume
sandbox = Sandbox.connect(saved_id)
```

### Pattern 7: LLM Tool Integration

```python
from anthropic import Anthropic
from e2b_code_interpreter import Sandbox

tools = [{
    "name": "execute_python",
    "description": "Execute python code in sandbox",
    "input_schema": {
        "type": "object",
        "properties": {
            "code": {"type": "string", "description": "Python code to execute"}
        },
        "required": ["code"]
    }
}]

client = Anthropic()
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Calculate 2+2"}],
    tools=tools
)

if message.stop_reason == "tool_use":
    tool_use = next(b for b in message.content if b.type == "tool_use")
    with Sandbox() as sandbox:
        result = sandbox.run_code(tool_use.input['code'])
        print(result.text)
```

### Pattern 8: MCP Gateway

```python
sandbox = Sandbox.create(
    mcp={
        'github': {'githubPersonalAccessToken': os.environ['GITHUB_TOKEN']},
        'slack': {'botToken': os.environ['SLACK_BOT_TOKEN']}
    }
)

mcp_url = sandbox.get_mcp_url()
mcp_token = sandbox.get_mcp_token()
```

See [mcp-gateway.md](references/mcp-gateway.md) for 200+ available integrations.

## API Quick Reference

### Sandbox Lifecycle

```python
# Create
sandbox = Sandbox()                    # Default 5 min timeout
sandbox = Sandbox(timeout=300)         # Custom timeout (seconds)
sandbox = Sandbox(envs={'KEY': 'val'}) # With env vars
sandbox = Sandbox(metadata={'user': '123'})  # With metadata

# Info & timeout
info = sandbox.get_info()
sandbox.set_timeout(60)

# Kill
sandbox.kill()
Sandbox.kill(sandbox_id)
```

### Sandbox Discovery

```python
# List all
paginator = Sandbox.list()
sandboxes = paginator.next_items()

# Filter by state
paginator = Sandbox.list(query={'state': ['running', 'paused']})

# Filter by metadata
paginator = Sandbox.list(query={'metadata': {'userId': '123'}})

# Connect to existing
sandbox = Sandbox.connect(sandbox_id)
```

### Code Execution

```python
execution = sandbox.run_code(code, language='python', envs={'VAR': 'val'})

# Results
execution.text          # Combined output
execution.logs.stdout   # Standard output
execution.logs.stderr   # Standard error
execution.results       # Rich results (charts, tables)
execution.error         # Runtime errors
```

### Commands

```python
result = sandbox.commands.run('ls -la')
result = sandbox.commands.run('cmd', envs={'VAR': 'val'})
result = sandbox.commands.run('cmd', background=True)
result = sandbox.commands.run('cmd', on_stdout=callback, on_stderr=callback)
```

### Files

```python
sandbox.files.write('/home/user/file.txt', content)  # Upload
content = sandbox.files.read('/home/user/file.txt')  # Download
files = sandbox.files.list('/home/user')             # List
watcher = sandbox.files.watch('/path')               # Watch changes
```

### Monitoring

```python
metrics = sandbox.get_metrics()
# Returns: [{timestamp, cpuUsedPct, cpuCount, memUsed, memTotal, diskUsed, diskTotal}]
```

## Python vs JavaScript API

| Operation | Python | JavaScript |
|-----------|--------|------------|
| Create | `Sandbox()` | `await Sandbox.create()` |
| Timeout | `set_timeout(60)` | `setTimeout(60000)` (ms) |
| Run code | `run_code(code)` | `await runCode(code)` |
| Kill | `kill()` | `await kill()` |
| Pause | `beta_pause()` | `await betaPause()` |

## Default Environment Variables

Available in every sandbox:
- `E2B_SANDBOX=true`
- `E2B_SANDBOX_ID` - Current sandbox ID
- `E2B_TEAM_ID` - Team ID
- `E2B_TEMPLATE_ID` - Template used

## Best Practices

1. **Always clean up**: Use context manager or try/finally with `kill()`
2. **Use absolute paths**: `/home/user/file.txt` not `file.txt`
3. **Handle errors**: Check `execution.error` after `run_code()`
4. **Tag with metadata**: Use metadata for tracking user sessions
5. **Monitor resources**: Check `get_metrics()` for CPU/memory usage
6. **Set appropriate timeouts**: Short tasks 60-120s, analysis 300-600s

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Timeout too quick | `Sandbox(timeout=300)` or `set_timeout(300)` |
| Code fails | Check `execution.error` for details |
| File not found | Use absolute paths, verify with `files.list()` |
| High resource usage | Check `get_metrics()`, kill unused sandboxes |

For detailed documentation, see the reference files linked above.
