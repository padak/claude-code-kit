# Advanced Sandbox Management

This guide covers advanced sandbox management capabilities in E2B, including listing, filtering, connecting to running sandboxes, metadata tracking, and environment variable management.

## Table of Contents

- [Listing Sandboxes](#listing-sandboxes)
- [Metadata](#metadata)
- [Connecting to Running Sandboxes](#connecting-to-running-sandboxes)
- [Environment Variables](#environment-variables)
- [Common Patterns](#common-patterns)
- [Troubleshooting](#troubleshooting)

## Listing Sandboxes

The `Sandbox.list()` method provides paginated access to your sandboxes with support for filtering by state and metadata.

### Basic Listing

**Python:**
```python
from e2b_code_interpreter import Sandbox

# Get paginator
paginator = Sandbox.list()

# Fetch first page
sandboxes = paginator.next_items()

for sandbox in sandboxes:
    print(f"Sandbox ID: {sandbox.sandbox_id}")
    print(f"Template ID: {sandbox.template_id}")
    print(f"Started at: {sandbox.started_at}")
    print(f"Metadata: {sandbox.metadata}")
```

**JavaScript:**
```javascript
import { Sandbox } from '@e2b/code-interpreter'

const paginator = Sandbox.list()

// Get first page
const firstPage = await paginator.nextItems()

const sandbox = firstPage[0]
console.log('Sandbox ID:', sandbox.sandboxId)
console.log('Template ID:', sandbox.templateId)
console.log('Started at:', sandbox.startedAt)
console.log('Metadata:', sandbox.metadata)

// Get next page
const nextPage = await paginator.nextItems()
```

### Pagination Control

Control pagination with limit and offset parameters. The default and maximum limit is 100 items per page.

**Python:**
```python
# Custom pagination
paginator = Sandbox.list(limit=50, next_token='<base64-token>')

# Loop through all pages
all_sandboxes = []
while paginator.has_next:
    items = paginator.next_items()
    all_sandboxes.extend(items)

# Check pagination state
print(f"Has next page: {paginator.has_next}")
print(f"Next token: {paginator.next_token}")
```

**JavaScript:**
```javascript
const paginator = Sandbox.list({
  limit: 100,
  nextToken: '<base64-encoded-token>'
})

// Paginator properties
paginator.hasNext      // Whether there is a next page
paginator.nextToken    // Token for next page
await paginator.nextItems()  // Fetch next page

// Fetch all pages
const allSandboxes = []
while (paginator.hasNext) {
  const items = await paginator.nextItems()
  allSandboxes.push(...items)
}
```

### Filtering by State

Filter sandboxes by their current state: `running` or `paused`.

**Python:**
```python
# List only running sandboxes
paginator = Sandbox.list(
    query={'state': ['running']}
)

# List running or paused sandboxes
paginator = Sandbox.list(
    query={'state': ['running', 'paused']}
)

sandboxes = paginator.next_items()
```

**JavaScript:**
```javascript
// List running sandboxes
const paginator = Sandbox.list({
  query: {
    state: ['running', 'paused']
  }
})

const sandboxes = await paginator.nextItems()
```

### Filtering by Metadata

Filter sandboxes by metadata key-value pairs. Multiple pairs create an AND filter (sandbox must match all specified metadata).

**Python:**
```python
# Create sandbox with metadata
sandbox = Sandbox.create(
    metadata={
        'userId': '123',
        'env': 'dev',
        'app': 'my-app'
    }
)

# Find sandboxes matching metadata
paginator = Sandbox.list(
    query={'metadata': {'userId': '123', 'env': 'dev'}}
)

sandboxes = paginator.next_items()
```

**JavaScript:**
```javascript
// Create with metadata
const sandbox = await Sandbox.create({
  metadata: {
    env: 'dev',
    app: 'my-app',
    userId: '123'
  }
})

// Filter by metadata
const paginator = Sandbox.list({
  query: {
    metadata: { userId: '123', env: 'dev' }
  }
})

const sandboxes = await paginator.nextItems()
```

### Combined Filtering

Combine state and metadata filters for precise queries.

**Python:**
```python
# Find running sandboxes for specific user
paginator = Sandbox.list(
    query={
        'state': ['running'],
        'metadata': {'userId': '123'}
    }
)
```

**JavaScript:**
```javascript
const paginator = Sandbox.list({
  query: {
    state: ['running'],
    metadata: { userId: '123' }
  }
})
```

## Metadata

Metadata allows you to attach custom key-value pairs to sandboxes for tracking and organization purposes.

### Attaching Metadata on Creation

**Python:**
```python
from datetime import datetime

sandbox = Sandbox.create(
    metadata={
        'userId': 'user_12345',
        'sessionId': 'session_abc',
        'environment': 'production',
        'purpose': 'data-analysis',
        'created': datetime.now().isoformat(),
        'apiKey': 'internal_key_789'  # Track which API key created sandbox
    }
)
```

**JavaScript:**
```javascript
const sandbox = await Sandbox.create({
  metadata: {
    userId: 'user_12345',
    sessionId: 'session_abc',
    environment: 'production',
    purpose: 'data-analysis',
    created: new Date().toISOString(),
    apiKey: 'internal_key_789'
  }
})
```

### Reading Metadata

**Python:**
```python
# Get metadata from sandbox info
info = sandbox.get_info()
print(info.metadata)

# Or when listing
paginator = Sandbox.list()
sandboxes = paginator.next_items()
for sbx in sandboxes:
    print(f"Sandbox {sbx.sandbox_id}: {sbx.metadata}")
```

**JavaScript:**
```javascript
// Get metadata from info
const info = await sandbox.getInfo()
console.log(info.metadata)

// Or when listing
const paginator = Sandbox.list()
const sandboxes = await paginator.nextItems()
sandboxes.forEach(sbx => {
  console.log(`Sandbox ${sbx.sandboxId}:`, sbx.metadata)
})
```

### Use Cases for Metadata

**1. User Session Tracking:**
```python
# Create sandbox for user session
sandbox = Sandbox.create(
    metadata={
        'userId': user_id,
        'sessionId': session_id,
        'startedAt': datetime.now().isoformat()
    }
)

# Later: Find user's active sandboxes
paginator = Sandbox.list(
    query={'metadata': {'userId': user_id}}
)
user_sandboxes = paginator.next_items()
```

**2. Multi-Tenant Applications:**
```python
# Tag sandboxes by tenant
sandbox = Sandbox.create(
    metadata={
        'tenantId': tenant_id,
        'orgId': org_id,
        'tier': 'premium'  # Track service tier
    }
)

# Find all sandboxes for a tenant
paginator = Sandbox.list(
    query={'metadata': {'tenantId': tenant_id}}
)
```

**3. Environment Segregation:**
```python
# Tag by deployment environment
sandbox = Sandbox.create(
    metadata={
        'env': 'staging',  # or 'dev', 'production'
        'branch': 'feature-xyz',
        'commit': 'abc123'
    }
)

# List staging sandboxes
paginator = Sandbox.list(
    query={'metadata': {'env': 'staging'}}
)
```

**4. Cost Tracking and Attribution:**
```python
# Track sandbox usage per project/department
sandbox = Sandbox.create(
    metadata={
        'project': 'ml-research',
        'department': 'engineering',
        'costCenter': 'CC-1234',
        'userId': user_id
    }
)
```

**5. API Key Tracking:**
```python
# Track which API key created each sandbox
sandbox = Sandbox.create(
    metadata={
        'apiKeyId': 'key_abc123',
        'applicationId': 'app_xyz'
    }
)

# Audit sandboxes created by specific API key
paginator = Sandbox.list(
    query={'metadata': {'apiKeyId': 'key_abc123'}}
)
```

### Best Practices for Metadata

1. **Use consistent key names** across your application
2. **Keep metadata flat** (avoid nested objects)
3. **Use metadata for filtering**, not for storing large data
4. **Include timestamps** for tracking creation and lifecycle
5. **Add user/session identifiers** for multi-user applications
6. **Track environment and version** for debugging
7. **Limit metadata size** to essential tracking information

## Connecting to Running Sandboxes

Connect to existing sandboxes using their ID to resume work or inspect state.

### Connect by Sandbox ID

**Python:**
```python
# Connect to existing sandbox
sandbox = Sandbox.connect('ixjj3iankaishgcge4jwn-b0b684e9')

# Use the sandbox
execution = sandbox.run_code('print("Reconnected!")')
print(execution.text)

# Get sandbox info
info = sandbox.get_info()
print(f"Connected to: {info.sandbox_id}")
print(f"Template: {info.template_id}")
print(f"Metadata: {info.metadata}")
```

**JavaScript:**
```javascript
// Connect to existing sandbox
const sandbox = await Sandbox.connect('ixjj3iankaishgcge4jwn-b0b684e9')

// Use the sandbox
const execution = await sandbox.runCode('print("Reconnected!")')
console.log(execution.text)

// Get info
const info = await sandbox.getInfo()
console.log('Connected to:', info.sandboxId)
```

### Reconnect to Current Sandbox

**Python:**
```python
# Create sandbox
sandbox = Sandbox.create()
sandbox_id = sandbox.sandbox_id

# ... do some work ...

# Reconnect using the instance
reconnected = sandbox.connect()

# Or reconnect using the ID
reconnected = Sandbox.connect(sandbox_id)
```

**JavaScript:**
```javascript
// Create sandbox
const sandbox = await Sandbox.create()
const sandboxId = sandbox.sandboxId

// Reconnect using instance
const reconnected = await sandbox.connect()

// Or by ID
const reconnected2 = await Sandbox.connect(sandboxId)
```

### Use Cases for Connecting

**1. Resume Long-Running Work:**
```python
# Initial session
sandbox = Sandbox.create(metadata={'userId': user_id, 'task': 'analysis'})
sandbox.run_code('import pandas as pd; df = pd.read_csv("data.csv")')
sandbox_id = sandbox.sandbox_id

# Save sandbox ID for later
save_to_database(user_id, sandbox_id)

# Later: Resume work
saved_id = load_from_database(user_id)
sandbox = Sandbox.connect(saved_id)
sandbox.run_code('print(df.describe())')  # DataFrame still in memory
```

**2. Inspect Running Sandboxes:**
```python
# List all running sandboxes
paginator = Sandbox.list(query={'state': ['running']})
sandboxes = paginator.next_items()

# Connect to inspect each one
for sbx_info in sandboxes:
    sandbox = Sandbox.connect(sbx_info.sandbox_id)

    # Check what's running
    result = sandbox.commands.run('ps aux')
    print(f"Processes in {sbx_info.sandbox_id}:")
    print(result)
```

**3. Multi-User Session Management:**
```python
def get_or_create_user_sandbox(user_id):
    # Try to find existing sandbox
    paginator = Sandbox.list(
        query={
            'state': ['running', 'paused'],
            'metadata': {'userId': user_id}
        }
    )
    sandboxes = paginator.next_items()

    if sandboxes:
        # Reconnect to existing sandbox
        return Sandbox.connect(sandboxes[0].sandbox_id)
    else:
        # Create new sandbox for user
        return Sandbox.create(
            metadata={'userId': user_id}
        )
```

**4. Debugging and Monitoring:**
```python
# Connect to sandbox for debugging
sandbox = Sandbox.connect(sandbox_id)

# Check filesystem
files = sandbox.files.list('/home/user')
print("Files:", files)

# Check running processes
processes = sandbox.commands.run('ps aux')

# Get resource usage
metrics = sandbox.get_metrics()
if metrics:
    latest = metrics[-1]
    print(f"CPU: {latest['cpuUsedPct']}%")
    print(f"Memory: {latest['memUsed']} / {latest['memTotal']}")
```

**5. Persistence with Pause/Resume:**
```python
# Create sandbox with auto-pause
sandbox = Sandbox.beta_create(auto_pause=True, timeout=600)
sandbox_id = sandbox.sandbox_id

# Do some work
sandbox.run_code('data = [1, 2, 3, 4, 5]')

# Pause sandbox
sandbox.beta_pause()

# Later: Resume by reconnecting
sandbox = Sandbox.connect(sandbox_id)
result = sandbox.run_code('print(sum(data))')  # State preserved
print(result.text)  # Output: 15
```

## Environment Variables

E2B supports environment variables at three scoping levels: global (sandbox-wide), code execution, and command execution.

### Default E2B Environment Variables

E2B automatically sets metadata environment variables in every sandbox:

- `E2B_SANDBOX=true` - Indicates code is running inside an E2B sandbox
- `E2B_SANDBOX_ID` - The unique ID of the current sandbox
- `E2B_TEAM_ID` - Team ID that created the sandbox
- `E2B_TEMPLATE_ID` - Template ID used to create the sandbox

**Access via SDK:**

**Python:**
```python
sandbox = Sandbox.create()

# Check if running in E2B
result = sandbox.commands.run('echo $E2B_SANDBOX')
print(result)  # Output: true

# Get sandbox ID from inside
result = sandbox.commands.run('echo $E2B_SANDBOX_ID')
print(result)  # Output: ixjj3iankaishgcge4jwn-b0b684e9

# Get all E2B variables
result = sandbox.commands.run('env | grep E2B')
print(result)
```

**JavaScript:**
```javascript
const sandbox = await Sandbox.create()

const result = await sandbox.commands.run('echo $E2B_SANDBOX_ID')
console.log(result)
```

**Access via CLI:**

When using the E2B CLI, default variables are stored as dot files in `/run/e2b/`:

```bash
user@e2b:~$ ls -a /run/e2b/
.E2B_SANDBOX  .E2B_SANDBOX_ID  .E2B_TEAM_ID  .E2B_TEMPLATE_ID

user@e2b:~$ cat /run/e2b/.E2B_SANDBOX_ID
ixjj3iankaishgcge4jwn-b0b684e9
```

### Setting Environment Variables

#### 1. Global Environment Variables (Sandbox-Wide)

Set variables when creating the sandbox. These are available to all code and commands.

**Python:**
```python
sandbox = Sandbox.create(
    envs={
        'API_KEY': 'secret_key_123',
        'DATABASE_URL': 'postgres://localhost/db',
        'DEBUG': 'true'
    }
)

# Variables available to all code
result = sandbox.run_code('import os; print(os.environ.get("API_KEY"))')
print(result.text)  # Output: secret_key_123

# Also available to commands
result = sandbox.commands.run('echo $DATABASE_URL')
print(result)  # Output: postgres://localhost/db
```

**JavaScript:**
```javascript
const sandbox = await Sandbox.create({
  envs: {
    API_KEY: 'secret_key_123',
    DATABASE_URL: 'postgres://localhost/db',
    DEBUG: 'true'
  }
})

// Available globally
const result = await sandbox.runCode('import os; print(os.environ.get("API_KEY"))')
console.log(result.text)
```

#### 2. Code Execution Scope

Set variables for a specific code execution call. These override global variables for that execution only.

**Python:**
```python
sandbox = Sandbox.create(
    envs={'API_KEY': 'global_key'}
)

# Override for this execution
execution = sandbox.run_code(
    'import os; print(os.environ.get("API_KEY"))',
    envs={'API_KEY': 'execution_specific_key'}
)
print(execution.text)  # Output: execution_specific_key

# Global variable still unchanged
execution = sandbox.run_code('import os; print(os.environ.get("API_KEY"))')
print(execution.text)  # Output: global_key
```

**JavaScript:**
```javascript
const sandbox = await Sandbox.create({
  envs: { API_KEY: 'global_key' }
})

// Override for this execution
const exec = await sandbox.runCode(
  'import os; print(os.environ.get("API_KEY"))',
  {
    envs: { API_KEY: 'execution_specific_key' }
  }
)
console.log(exec.text)  // execution_specific_key
```

#### 3. Command Execution Scope

Set variables for a specific command execution.

**Python:**
```python
sandbox = Sandbox.create()

# Set variable for this command only
result = sandbox.commands.run(
    'echo $MY_VAR',
    envs={'MY_VAR': '123'}
)
print(result)  # Output: 123

# Variable not available in other commands
result = sandbox.commands.run('echo $MY_VAR')
print(result)  # Output: (empty)
```

**JavaScript:**
```javascript
const sandbox = await Sandbox.create()

await sandbox.commands.run('echo $MY_VAR', {
  envs: { MY_VAR: '123' }
})
```

### Environment Variable Scoping Summary

| Scope Level | Set When | Visibility | Override Behavior |
|-------------|----------|------------|-------------------|
| **Global** | `Sandbox.create(envs=...)` | All code and commands | Lowest priority |
| **Code Execution** | `run_code(..., envs=...)` | Single code execution | Overrides global for that execution |
| **Command Execution** | `commands.run(..., envs=...)` | Single command | Overrides global for that command |

**Important Notes:**
- Environment variables are **scoped to the execution** but **not private in the OS**
- Other processes in the sandbox may be able to see environment variables
- For sensitive data, consider using secure secrets management
- Variables set in code/command scope do not persist across executions

### Best Practices for Environment Variables

**1. Use Global Variables for Configuration:**
```python
sandbox = Sandbox.create(
    envs={
        'APP_ENV': 'production',
        'LOG_LEVEL': 'info',
        'FEATURE_FLAGS': 'feature1,feature2'
    }
)
```

**2. Use Execution Scope for Sensitive Operations:**
```python
# Don't expose API key globally
sandbox = Sandbox.create()

# Only provide when needed
sandbox.run_code(
    'import requests; requests.get(url, headers={"Authorization": token})',
    envs={'token': f'Bearer {api_token}'}
)
```

**3. Detect E2B Environment in Code:**
```python
# Code that runs both locally and in E2B
code = '''
import os

if os.environ.get('E2B_SANDBOX') == 'true':
    print("Running in E2B sandbox")
    sandbox_id = os.environ.get('E2B_SANDBOX_ID')
    print(f"Sandbox ID: {sandbox_id}")
else:
    print("Running locally")
'''

sandbox.run_code(code)
```

**4. Pass Configuration Files via Environment:**
```python
import json

config = {
    'api_url': 'https://api.example.com',
    'timeout': 30,
    'retry_count': 3
}

sandbox = Sandbox.create(
    envs={'APP_CONFIG': json.dumps(config)}
)

sandbox.run_code('''
import os
import json

config = json.loads(os.environ.get('APP_CONFIG'))
print(config['api_url'])
''')
```

## Common Patterns

### Pattern 1: Multi-User Session Management

Manage separate sandboxes for multiple users with automatic reconnection.

```python
from e2b_code_interpreter import Sandbox
from datetime import datetime

class UserSandboxManager:
    def __init__(self):
        self.sandbox_cache = {}

    def get_sandbox(self, user_id: str) -> Sandbox:
        """Get or create sandbox for user"""

        # Check cache first
        if user_id in self.sandbox_cache:
            return self.sandbox_cache[user_id]

        # Try to find existing sandbox
        paginator = Sandbox.list(
            query={
                'state': ['running', 'paused'],
                'metadata': {'userId': user_id}
            }
        )
        sandboxes = paginator.next_items()

        if sandboxes:
            # Reconnect to existing
            sandbox = Sandbox.connect(sandboxes[0].sandbox_id)
        else:
            # Create new sandbox
            sandbox = Sandbox.create(
                timeout=600,
                metadata={
                    'userId': user_id,
                    'created': datetime.now().isoformat()
                }
            )

        # Cache and return
        self.sandbox_cache[user_id] = sandbox
        return sandbox

    def cleanup_user_sandbox(self, user_id: str):
        """Clean up sandbox for user"""
        if user_id in self.sandbox_cache:
            self.sandbox_cache[user_id].kill()
            del self.sandbox_cache[user_id]

# Usage
manager = UserSandboxManager()

# Get sandbox for user
user_sandbox = manager.get_sandbox('user_123')
user_sandbox.run_code('data = [1, 2, 3]')

# Later: Same user gets same sandbox
same_sandbox = manager.get_sandbox('user_123')
result = same_sandbox.run_code('print(sum(data))')  # State preserved
```

### Pattern 2: Cleanup Orphaned Sandboxes

Periodically clean up old or unused sandboxes.

```python
from datetime import datetime, timedelta
from e2b_code_interpreter import Sandbox

def cleanup_old_sandboxes(max_age_minutes: int = 60):
    """Kill sandboxes older than max_age_minutes"""

    cutoff_time = datetime.now() - timedelta(minutes=max_age_minutes)

    # Get all running sandboxes
    paginator = Sandbox.list(query={'state': ['running']})

    killed_count = 0
    while paginator.has_next:
        sandboxes = paginator.next_items()

        for sbx_info in sandboxes:
            # Parse started_at timestamp
            started_at = datetime.fromisoformat(
                sbx_info.started_at.replace('Z', '+00:00')
            )

            if started_at < cutoff_time:
                print(f"Killing old sandbox: {sbx_info.sandbox_id}")
                Sandbox.kill(sbx_info.sandbox_id)
                killed_count += 1

    print(f"Cleaned up {killed_count} old sandboxes")
    return killed_count

# Run cleanup
cleanup_old_sandboxes(max_age_minutes=30)
```

### Pattern 3: Environment-Specific Configuration

Use metadata to manage different environments.

```python
def create_sandbox_for_env(env: str, user_id: str):
    """Create environment-specific sandbox"""

    # Environment-specific configuration
    configs = {
        'dev': {
            'timeout': 300,
            'envs': {
                'API_URL': 'https://dev-api.example.com',
                'LOG_LEVEL': 'debug'
            }
        },
        'staging': {
            'timeout': 600,
            'envs': {
                'API_URL': 'https://staging-api.example.com',
                'LOG_LEVEL': 'info'
            }
        },
        'production': {
            'timeout': 300,
            'envs': {
                'API_URL': 'https://api.example.com',
                'LOG_LEVEL': 'warning'
            }
        }
    }

    config = configs.get(env, configs['dev'])

    return Sandbox.create(
        timeout=config['timeout'],
        envs=config['envs'],
        metadata={
            'userId': user_id,
            'env': env,
            'created': datetime.now().isoformat()
        }
    )

# Create production sandbox
prod_sandbox = create_sandbox_for_env('production', 'user_123')
```

### Pattern 4: Audit and Monitoring

Track sandbox usage and resource consumption.

```python
import time

def audit_sandbox_usage():
    """Generate usage report for all sandboxes"""

    paginator = Sandbox.list(query={'state': ['running']})

    report = []
    while paginator.has_next:
        sandboxes = paginator.next_items()

        for sbx_info in sandboxes:
            # Connect and get metrics
            sandbox = Sandbox.connect(sbx_info.sandbox_id)

            # Wait for metrics to collect
            time.sleep(5)
            metrics = sandbox.get_metrics()

            if metrics:
                latest = metrics[-1]

                report.append({
                    'sandbox_id': sbx_info.sandbox_id,
                    'metadata': sbx_info.metadata,
                    'started_at': sbx_info.started_at,
                    'cpu_usage': latest['cpuUsedPct'],
                    'mem_used_mb': latest['memUsed'] / (1024 * 1024),
                    'disk_used_mb': latest['diskUsed'] / (1024 * 1024)
                })

    return report

# Generate report
usage_report = audit_sandbox_usage()
for entry in usage_report:
    print(f"Sandbox {entry['sandbox_id']}:")
    print(f"  User: {entry['metadata'].get('userId', 'unknown')}")
    print(f"  CPU: {entry['cpu_usage']:.1f}%")
    print(f"  Memory: {entry['mem_used_mb']:.1f} MB")
```

### Pattern 5: Graceful Degradation

Handle sandbox connection failures gracefully.

```python
def get_or_recreate_sandbox(sandbox_id: str, metadata: dict):
    """Connect to sandbox or create new one if failed"""

    try:
        # Try to connect to existing sandbox
        sandbox = Sandbox.connect(sandbox_id)

        # Verify it's responsive
        sandbox.run_code('print("alive")')

        return sandbox, False  # False = not recreated

    except Exception as e:
        print(f"Failed to connect to {sandbox_id}: {e}")
        print("Creating new sandbox...")

        # Create new sandbox with same metadata
        new_sandbox = Sandbox.create(metadata=metadata)

        return new_sandbox, True  # True = recreated

# Usage
sandbox, was_recreated = get_or_recreate_sandbox(
    'old-sandbox-id',
    metadata={'userId': 'user_123'}
)

if was_recreated:
    print("Note: New sandbox created, previous state lost")
    # Reinitialize state
    sandbox.run_code('data = []')
```

## Troubleshooting

### Issue: Sandbox Not Found When Connecting

**Problem:** `Sandbox.connect(id)` fails with "Sandbox not found"

**Possible Causes:**
1. Sandbox has already been killed
2. Sandbox timeout expired (default 5 minutes)
3. Sandbox ID is incorrect
4. Using wrong API key (sandboxes belong to team/API key)

**Solutions:**
```python
# Check if sandbox exists before connecting
paginator = Sandbox.list()
sandboxes = paginator.next_items()
sandbox_ids = [sbx.sandbox_id for sbx in sandboxes]

if target_id in sandbox_ids:
    sandbox = Sandbox.connect(target_id)
else:
    print(f"Sandbox {target_id} not found, creating new one")
    sandbox = Sandbox.create()
```

### Issue: Empty Results When Listing Sandboxes

**Problem:** `Sandbox.list()` returns empty results

**Possible Causes:**
1. No sandboxes currently running
2. All sandboxes have timed out
3. Filtering too restrictive
4. Using wrong API key

**Solutions:**
```python
# Check without filters
all_paginator = Sandbox.list()
all_sandboxes = all_paginator.next_items()
print(f"Total sandboxes: {len(all_sandboxes)}")

# Check specific states
running = Sandbox.list(query={'state': ['running']}).next_items()
paused = Sandbox.list(query={'state': ['paused']}).next_items()

print(f"Running: {len(running)}, Paused: {len(paused)}")

# Verify API key
print(f"API Key: {os.environ.get('E2B_API_KEY', 'NOT SET')}")
```

### Issue: Metadata Filtering Not Working

**Problem:** Filtering by metadata returns unexpected results

**Possible Causes:**
1. Metadata keys are case-sensitive
2. Multiple metadata pairs create AND filter (not OR)
3. Metadata value types must match exactly

**Solutions:**
```python
# Ensure exact key/value match
sandbox = Sandbox.create(
    metadata={'userId': '123'}  # String '123', not int 123
)

# This will match
Sandbox.list(query={'metadata': {'userId': '123'}})

# This won't match (type mismatch)
Sandbox.list(query={'metadata': {'userId': 123}})

# Multiple conditions are AND (not OR)
# This finds sandboxes with BOTH userId=123 AND env=dev
Sandbox.list(query={'metadata': {'userId': '123', 'env': 'dev'}})
```

### Issue: Environment Variables Not Available

**Problem:** Environment variables not accessible in code/commands

**Possible Causes:**
1. Variable set at wrong scope
2. Variable name typo
3. Using subprocess that doesn't inherit environment

**Solutions:**
```python
# Debug environment variables
sandbox = Sandbox.create(
    envs={'MY_VAR': 'test_value'}
)

# Check if variable is set
result = sandbox.commands.run('env | grep MY_VAR')
print(result)  # Should show MY_VAR=test_value

# In Python code
result = sandbox.run_code('''
import os
print("MY_VAR:", os.environ.get("MY_VAR"))
print("All env vars:", dict(os.environ))
''')
print(result.text)

# Verify scope
global_result = sandbox.run_code('import os; print(os.environ.get("GLOBAL_VAR"))')
scoped_result = sandbox.run_code(
    'import os; print(os.environ.get("SCOPED_VAR"))',
    envs={'SCOPED_VAR': 'value'}
)
```

### Issue: Pagination Stops Prematurely

**Problem:** Not all sandboxes returned when paginating

**Possible Causes:**
1. Not checking `has_next` properly
2. Sandboxes being killed during pagination
3. Limit set too low

**Solutions:**
```python
# Proper pagination loop
paginator = Sandbox.list(limit=100)
all_sandboxes = []

while paginator.has_next:
    try:
        items = paginator.next_items()
        all_sandboxes.extend(items)
        print(f"Fetched {len(items)} sandboxes, total: {len(all_sandboxes)}")
    except Exception as e:
        print(f"Error during pagination: {e}")
        break

print(f"Final count: {len(all_sandboxes)}")
```

### Issue: Stale Sandbox Connections

**Problem:** Connected sandbox becomes unresponsive

**Possible Causes:**
1. Sandbox killed externally
2. Network interruption
3. Sandbox timeout reached

**Solutions:**
```python
def ensure_responsive_sandbox(sandbox_id: str, metadata: dict = None):
    """Connect and verify sandbox is responsive"""
    try:
        sandbox = Sandbox.connect(sandbox_id)

        # Ping test
        result = sandbox.run_code('print("alive")', timeout=5)

        if result.error:
            raise Exception("Sandbox not responsive")

        return sandbox

    except Exception as e:
        print(f"Sandbox {sandbox_id} not responsive: {e}")
        print("Creating new sandbox...")

        return Sandbox.create(metadata=metadata or {})

# Usage with automatic failover
sandbox = ensure_responsive_sandbox(
    saved_sandbox_id,
    metadata={'userId': 'user_123'}
)
```

### Issue: High Memory Usage When Listing Many Sandboxes

**Problem:** Application runs out of memory when fetching all sandboxes

**Solutions:**
```python
# Process in batches instead of loading all at once
def process_sandboxes_in_batches(process_fn, batch_size=50):
    """Process sandboxes in batches to avoid memory issues"""

    paginator = Sandbox.list(limit=batch_size)

    batch_count = 0
    while paginator.has_next:
        sandboxes = paginator.next_items()
        batch_count += 1

        print(f"Processing batch {batch_count} ({len(sandboxes)} sandboxes)")

        # Process batch
        for sbx in sandboxes:
            process_fn(sbx)

        # Clear batch from memory
        del sandboxes

# Example usage
def cleanup_old_sandbox(sbx_info):
    started = datetime.fromisoformat(sbx_info.started_at.replace('Z', '+00:00'))
    if datetime.now() - started > timedelta(hours=1):
        Sandbox.kill(sbx_info.sandbox_id)

process_sandboxes_in_batches(cleanup_old_sandbox, batch_size=50)
```

## See Also

- [Sandbox Lifecycle](./sandbox-lifecycle.md) - Creating, pausing, and managing sandboxes
- [Monitoring & Events](./monitoring-and-events.md) - Metrics, events, and webhooks
- [Persistence Guide](./persistence.md) - Pausing and resuming sandboxes
- [Quickstart Guide](./quickstart.md) - Getting started with E2B
