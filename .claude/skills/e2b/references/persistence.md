# Sandbox Persistence

> **Beta Feature**: Sandbox persistence is currently in public beta. It's free for all users during the beta period.

## Overview

Sandbox persistence allows you to pause a sandbox and resume it later from the exact same state, including:
- **Filesystem state**: All files and directories
- **Memory state**: Running processes, loaded variables, data in memory

This is useful for:
- Long-running interactive sessions
- Reducing costs by pausing inactive sandboxes
- Maintaining state between user interactions
- Debugging and development workflows

## Sandbox States

Sandboxes can exist in three states:

1. **Running**: Actively executing and consuming resources
2. **Paused**: Execution suspended, state preserved
3. **Killed**: Terminated and resources released (terminal state)

### State Transition Diagram

```
         create()
            ↓
        [Running]
            ↓
     ┌──────┴──────┐
     ↓             ↓
beta_pause()    kill()
     ↓             ↓
  [Paused]    [Killed]
     ↓
 connect()
     ↓
 [Running]
```

## Pausing Sandboxes

When you pause a sandbox, both filesystem and memory state are saved.

**Python:**
```python
from e2b_code_interpreter import Sandbox

# Create sandbox
sandbox = Sandbox.create()
print(f"Sandbox created: {sandbox.sandbox_id}")

# Do some work
sandbox.run_code('x = 42')

# Pause the sandbox
sandbox.beta_pause()
print(f"Sandbox paused: {sandbox.sandbox_id}")

# Save the sandbox ID for later
save_to_database(user_id, sandbox.sandbox_id)
```

**JavaScript:**
```javascript
import { Sandbox } from '@e2b/code-interpreter'

// Create sandbox
const sandbox = await Sandbox.create()
console.log(`Sandbox created: ${sandbox.sandboxId}`)

// Do some work
await sandbox.runCode('x = 42')

// Pause the sandbox
await sandbox.betaPause()
console.log(`Sandbox paused: ${sandbox.sandboxId}`)

// Save the sandbox ID for later
saveToDatabase(userId, sandbox.sandboxId)
```

**Performance:**
- Pausing takes ~4 seconds per 1 GiB of RAM
- Paused sandboxes don't consume compute resources
- Storage is free during beta

## Resuming Sandboxes

Resume a paused sandbox to continue from where you left off.

**Python:**
```python
# Retrieve saved sandbox ID
sandbox_id = load_from_database(user_id)

# Connect to paused sandbox (automatically resumes)
sandbox = Sandbox.connect(sandbox_id)
print(f"Connected to sandbox: {sandbox.sandbox_id}")

# Continue work - variables are still in memory
result = sandbox.run_code('print(x)')  # Prints: 42
```

**JavaScript:**
```javascript
// Retrieve saved sandbox ID
const sandboxId = loadFromDatabase(userId)

// Connect to paused sandbox (automatically resumes)
const sandbox = await Sandbox.connect(sandboxId)
console.log(`Connected to sandbox: ${sandbox.sandboxId}`)

// Continue work - variables are still in memory
const result = await sandbox.runCode('print(x)')  // Prints: 42
```

**Performance:**
- Resuming takes ~1 second
- Timeout resets to default (5 minutes) or custom value

### Custom Timeout on Resume

**Python:**
```python
# Resume with custom timeout (60 seconds)
sandbox = Sandbox.connect(sandbox_id, timeout=60)
```

**JavaScript:**
```javascript
// Resume with custom timeout (60 seconds)
const sandbox = await Sandbox.connect(sandboxId, {
    timeoutMs: 60_000
})
```

## Listing Paused Sandboxes

List all your paused sandboxes.

**Python:**
```python
from e2b_code_interpreter import Sandbox

# List all paused sandboxes
paginator = Sandbox.list(query={'state': ['paused']})

# Get first page
sandboxes = paginator.next_items()

# Get all paused sandboxes
all_sandboxes = []
while paginator.has_next:
    items = paginator.next_items()
    all_sandboxes.extend(items)

for sandbox in all_sandboxes:
    print(f"ID: {sandbox['sandboxId']}")
    print(f"Started: {sandbox['startedAt']}")
```

**JavaScript:**
```javascript
import { Sandbox } from '@e2b/code-interpreter'

// List all paused sandboxes
const paginator = Sandbox.list({
    query: { state: ['paused'] }
})

// Get first page
const sandboxes = await paginator.nextItems()

// Get all paused sandboxes
const allSandboxes = [...sandboxes]
while (paginator.hasNext) {
    const items = await paginator.nextItems()
    allSandboxes.push(...items)
}

for (const sandbox of allSandboxes) {
    console.log(`ID: ${sandbox.sandboxId}`)
    console.log(`Started: ${sandbox.startedAt}`)
}
```

## Removing Paused Sandboxes

Delete paused sandboxes to free up storage.

**Python:**
```python
# Kill connected sandbox
sandbox.kill()

# Or kill by ID
Sandbox.kill(sandbox_id)
```

**JavaScript:**
```javascript
// Kill connected sandbox
await sandbox.kill()

// Or kill by ID
await Sandbox.kill(sandboxId)
```

**Important:**
- `kill()` permanently deletes the sandbox
- You cannot resume a killed sandbox
- Data cannot be recovered after killing

## Auto-Pause (Beta)

Automatically pause sandboxes when they time out instead of killing them.

**Python:**
```python
# Create with auto-pause enabled
sandbox = Sandbox.beta_create(
    auto_pause=True,
    timeout=10 * 60  # 10 minutes
)

# Sandbox will auto-pause after 10 minutes of inactivity
# Instead of being killed
```

**JavaScript:**
```javascript
// Create with auto-pause enabled
const sandbox = await Sandbox.betaCreate({
    autoPause: true,
    timeoutMs: 10 * 60 * 1000  // 10 minutes
})

// Sandbox will auto-pause after 10 minutes of inactivity
```

**Key Features:**
- Auto-pause persists across resumes
- Sandbox auto-pauses again after timeout when resumed
- Calling `kill()` still permanently deletes the sandbox
- Default inactivity timeout: 10 minutes

**Use Cases:**
- Interactive applications with intermittent user activity
- Development/debugging sessions
- Long-running computations with checkpoints

## Network Considerations

### Paused Sandboxes

- Services (e.g., web servers) become inaccessible
- All client connections are dropped
- Network ports are not preserved

### Resumed Sandboxes

- Services become accessible again
- Clients must reconnect
- Same ports are available

**Example:**
```python
# Start server in sandbox
sandbox.run_code("""
from http.server import HTTPServer, SimpleHTTPRequestHandler
server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
print('Server started on port 8000')
""")

# Get URL
url = sandbox.get_hostname(8000)
print(f"Server URL: {url}")

# Pause sandbox
sandbox.beta_pause()
# Server is now inaccessible

# Resume sandbox
sandbox = Sandbox.connect(sandbox.sandbox_id)
# Server is accessible again, but need new URL
url = sandbox.get_hostname(8000)
```

## Best Practices

### 1. Choose Between Pause and Kill

**Use Pause When:**
- User might return within minutes/hours
- Preserving state is important
- Running interactive sessions
- Debugging/development

**Use Kill When:**
- Task is completely done
- Won't need sandbox again
- Freeing resources is priority
- Approaching 30-day limit

### 2. Track Sandbox IDs

```python
# Associate sandboxes with users
user_sandbox_map = {}

def create_user_sandbox(user_id):
    sandbox = Sandbox.beta_create(auto_pause=True)
    user_sandbox_map[user_id] = sandbox.sandbox_id
    return sandbox

def get_user_sandbox(user_id):
    if user_id in user_sandbox_map:
        sandbox_id = user_sandbox_map[user_id]
        try:
            return Sandbox.connect(sandbox_id)
        except NotFoundException:
            # Sandbox expired or deleted
            del user_sandbox_map[user_id]
            return create_user_sandbox(user_id)
    return create_user_sandbox(user_id)
```

### 3. Handle Reconnection Failures

```python
from e2b_code_interpreter.exceptions import NotFoundException

def safe_connect(sandbox_id):
    try:
        return Sandbox.connect(sandbox_id)
    except NotFoundException:
        print(f"Sandbox {sandbox_id} not found. Creating new sandbox.")
        return Sandbox.create()
```

### 4. Clean Up Old Sandboxes

```python
from datetime import datetime, timedelta

def cleanup_old_sandboxes(max_age_days=25):
    """Remove sandboxes older than max_age_days"""
    paginator = Sandbox.list(query={'state': ['paused']})
    cutoff = datetime.now() - timedelta(days=max_age_days)

    while paginator.has_next:
        sandboxes = paginator.next_items()
        for sb in sandboxes:
            started = datetime.fromisoformat(sb['startedAt'])
            if started < cutoff:
                print(f"Removing old sandbox: {sb['sandboxId']}")
                Sandbox.kill(sb['sandboxId'])
```

## Common Patterns

### Pattern 1: Interactive Session

```python
# User starts session
sandbox = Sandbox.beta_create(
    auto_pause=True,
    timeout=600  # 10 minutes
)

# User does some work
sandbox.run_code(code1)
session_id = sandbox.sandbox_id

# User goes inactive
# ... sandbox auto-pauses after 10 minutes ...

# User returns (minutes or hours later)
sandbox = Sandbox.connect(session_id)

# Continue work with preserved state
sandbox.run_code(code2)
```

### Pattern 2: Checkpoint Long Computation

```python
# Start long computation
sandbox = Sandbox.create(timeout=300)
sandbox.run_code("""
results = []
for i in range(1000):
    results.append(expensive_computation(i))
    if i % 100 == 0:
        # Save checkpoint
        with open('/home/user/checkpoint.pkl', 'wb') as f:
            pickle.dump(results, f)
""")

# Pause to save progress
sandbox.beta_pause()
checkpoint_id = sandbox.sandbox_id

# Resume later
sandbox = Sandbox.connect(checkpoint_id)
sandbox.run_code("""
import pickle
with open('/home/user/checkpoint.pkl', 'rb') as f:
    results = pickle.load(f)
# Continue from checkpoint
""")
```

### Pattern 3: Development Environment

```python
# Create persistent dev environment
dev_sandbox = Sandbox.beta_create(auto_pause=True)

# Install dependencies once
dev_sandbox.run_code("""
!pip install pandas numpy matplotlib seaborn
""")

# Pause when not in use
dev_sandbox.beta_pause()
dev_id = dev_sandbox.sandbox_id

# Resume for each coding session
dev_sandbox = Sandbox.connect(dev_id)
# Packages already installed!
```

## Limitations (Beta)

Current limitations during beta period:

1. **Performance:**
   - Pausing: ~4 seconds per 1 GiB of RAM
   - Resuming: ~1 second

2. **Duration:**
   - Maximum sandbox age: 30 days from initial creation
   - After 30 days, data may be deleted
   - Cannot resume deleted sandboxes

3. **Error Handling:**
   - `NotFoundException` raised when trying to resume deleted/expired sandbox
   - Same exception for non-existent sandbox IDs

4. **Storage:**
   - No explicit storage limits during beta
   - Free storage during beta period

## Troubleshooting

### Cannot Resume Sandbox

**Problem:** `NotFoundException` when calling `connect()`

**Solutions:**
```python
try:
    sandbox = Sandbox.connect(sandbox_id)
except NotFoundException:
    # Sandbox expired (>30 days) or doesn't exist
    print("Sandbox not found. Creating new one.")
    sandbox = Sandbox.create()
```

### Memory State Not Preserved

**Problem:** Variables are lost after resume

**Check:**
1. Did you pause using `beta_pause()`?
2. Did you resume the correct sandbox ID?
3. Was sandbox killed instead of paused?

### Slow Pause/Resume

**Problem:** Pausing takes too long

**Explanation:**
- Pausing time scales with RAM usage (~4s per GiB)
- Clear unnecessary data before pausing:

```python
# Clear large variables before pausing
sandbox.run_code("""
import gc
# Delete large objects
del large_dataframe
del cached_results
# Force garbage collection
gc.collect()
""")

# Then pause
sandbox.beta_pause()
```

### Sandbox Deleted Before 30 Days

**Problem:** Cannot resume sandbox before 30-day limit

**Possible causes:**
1. Sandbox was killed (not paused)
2. Storage quota exceeded (unlikely during beta)
3. API key changed/invalidated

**Prevention:**
```python
# Verify sandbox state before assuming it's paused
info = sandbox.get_info()
print(f"State: {info.get('state', 'unknown')}")
```
