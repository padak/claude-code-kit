# Sandbox Lifecycle Management

## Overview

E2B sandboxes are isolated VMs with configurable lifetimes. Understanding lifecycle management is crucial for efficient resource usage.

## Creating Sandboxes

### Default Creation

**Python:**
```python
from e2b_code_interpreter import Sandbox

# Create with default 5 minute timeout
sandbox = Sandbox.create()
print(sandbox.sandbox_id)
```

**JavaScript:**
```javascript
import { Sandbox } from '@e2b/code-interpreter'

// Create with default 5 minute timeout
const sandbox = await Sandbox.create()
console.log(sandbox.sandboxId)
```

### Custom Timeout

**Python:**
```python
# Timeout in seconds
sandbox = Sandbox.create(timeout=60)  # 60 seconds
```

**JavaScript:**
```javascript
// Timeout in milliseconds
const sandbox = await Sandbox.create({
  timeoutMs: 60_000  // 60 seconds
})
```

## Managing Timeout During Runtime

You can change the sandbox timeout while it's running. This resets the timeout to the new value from the current moment.

**Python:**
```python
# Change timeout to 30 seconds from now
sandbox.set_timeout(30)
```

**JavaScript:**
```javascript
// Change timeout to 30 seconds from now
await sandbox.setTimeout(30_000)  // milliseconds
```

**Use Cases:**
- Extend lifetime when user interacts with your app
- Periodically reset timeout for long-running sessions
- Shorten timeout when task is nearly complete

## Getting Sandbox Information

**Python:**
```python
info = sandbox.get_info()
print(info)
```

**JavaScript:**
```javascript
const info = await sandbox.getInfo()
console.log(info)
```

**Response Structure:**
```json
{
  "sandboxId": "iiny0783cype8gmoawzmx-ce30bc46",
  "templateId": "rki5dems9wqfm4r03t7g",
  "name": "base",
  "metadata": {},
  "startedAt": "2025-03-24T15:37:58.076Z",
  "endAt": "2025-03-24T15:42:58.076Z"
}
```

## Shutting Down Sandboxes

Always shut down sandboxes when finished to free resources and avoid unnecessary charges.

### Manual Shutdown

**Python:**
```python
# Shutdown immediately
sandbox.kill()

# Or by ID
Sandbox.kill(sandbox_id)
```

**JavaScript:**
```javascript
// Shutdown immediately
await sandbox.kill()

// Or by ID
await Sandbox.kill(sandboxId)
```

### Using Context Manager (Python)

Recommended approach for automatic cleanup:

```python
with Sandbox.create() as sandbox:
    # Do work
    execution = sandbox.run_code(code)
    # Sandbox automatically killed when exiting context
```

### Try-Finally Pattern

For languages without context managers or when more control is needed:

**Python:**
```python
sandbox = Sandbox.create()
try:
    # Do work
    execution = sandbox.run_code(code)
finally:
    sandbox.kill()  # Always executed
```

**JavaScript:**
```javascript
const sandbox = await Sandbox.create()
try {
  // Do work
  const execution = await sandbox.runCode(code)
} finally {
  await sandbox.kill()  // Always executed
}
```

## Sandbox States

Sandboxes can be in one of three states:

1. **Running** - Actively executing and consuming resources
2. **Paused** - Suspended but state preserved (Beta feature)
3. **Killed** - Terminated, all resources released (terminal state)

### State Transitions

```
              create()
                 ↓
             [Running]
                 ↓
         ┌───────┴───────┐
         ↓               ↓
  beta_pause()       kill()
         ↓               ↓
     [Paused]      [Killed]
         ↓
    connect()
         ↓
     [Running]
```

## Best Practices

### 1. Choose Appropriate Timeouts

```python
# Short task: 60-120 seconds
sandbox = Sandbox.create(timeout=60)

# Data analysis: 300-600 seconds
sandbox = Sandbox.create(timeout=300)

# Interactive session: Use auto-pause
sandbox = Sandbox.beta_create(
    auto_pause=True,
    timeout=600
)
```

### 2. Always Clean Up

```python
# Good: Automatic cleanup
with Sandbox.create() as sandbox:
    result = sandbox.run_code(code)

# Also good: Explicit cleanup
sandbox = Sandbox.create()
try:
    result = sandbox.run_code(code)
finally:
    sandbox.kill()

# Bad: No cleanup (sandbox times out eventually but wastes resources)
sandbox = Sandbox.create()
result = sandbox.run_code(code)
# Missing cleanup!
```

### 3. Track Sandbox IDs

For long-running or persisted sandboxes:

```python
# Save ID for later reconnection
sandbox = Sandbox.create()
sandbox_id = sandbox.sandbox_id
save_to_database(user_id, sandbox_id)

# Later: Reconnect
saved_id = load_from_database(user_id)
sandbox = Sandbox.connect(saved_id)
```

### 4. Handle Timeout Gracefully

```python
from e2b_code_interpreter.exceptions import TimeoutException

try:
    execution = sandbox.run_code(long_running_code)
except TimeoutException:
    print("Code execution timed out")
    # Handle appropriately
```

## Auto-Pause Feature (Beta)

For interactive applications where users may be inactive:

**Python:**
```python
# Create with auto-pause
sandbox = Sandbox.beta_create(
    auto_pause=True,
    timeout=10 * 60  # 10 minutes of inactivity
)

# Sandbox automatically pauses after timeout
# Instead of being killed
```

**JavaScript:**
```javascript
// Create with auto-pause
const sandbox = await Sandbox.betaCreate({
    autoPause: true,
    timeoutMs: 10 * 60 * 1000  // 10 minutes
})
```

**Key Points:**
- Sandbox pauses automatically after timeout
- Auto-pause persists across resume
- Calling `kill()` permanently deletes the sandbox
- Paused sandboxes can be resumed later

## Monitoring and Debugging

### Check Remaining Time

```python
info = sandbox.get_info()
started_at = info['startedAt']
end_at = info['endAt']

from datetime import datetime
remaining = datetime.fromisoformat(end_at) - datetime.now()
print(f"Sandbox will timeout in {remaining.total_seconds()} seconds")
```

### List All Sandboxes

```python
# List running sandboxes
paginator = Sandbox.list(query={'state': ['running']})
sandboxes = paginator.next_items()

for sb in sandboxes:
    print(f"ID: {sb['sandboxId']}, Started: {sb['startedAt']}")
```

## Common Patterns

### Pattern 1: Quick One-Off Execution

```python
with Sandbox.create() as sandbox:
    result = sandbox.run_code(code)
    return result.text
```

### Pattern 2: Multi-Step Processing

```python
sandbox = Sandbox.create(timeout=300)
try:
    # Step 1
    sandbox.run_code(setup_code)

    # Step 2
    sandbox.files.write('/home/user/data.csv', data)

    # Step 3
    result = sandbox.run_code(analysis_code)

    return result
finally:
    sandbox.kill()
```

### Pattern 3: Interactive Session

```python
# Create with auto-pause
sandbox = Sandbox.beta_create(
    auto_pause=True,
    timeout=600
)

# User does work
result = sandbox.run_code(code)

# User goes inactive → sandbox auto-pauses

# User returns → reconnect
sandbox = Sandbox.connect(sandbox.sandbox_id)

# Continue work
result = sandbox.run_code(next_code)
```

## Troubleshooting

### Sandbox Times Out Too Quickly
- Increase timeout on creation
- Reset timeout periodically during long operations
- Consider using auto-pause for interactive sessions

### Can't Reconnect to Sandbox
- Check if sandbox was killed (not paused)
- Verify sandbox hasn't exceeded 30-day limit
- Ensure sandbox ID is correct

### Memory/Resource Issues
- Kill unused sandboxes promptly
- Don't create too many sandboxes concurrently
- Use pause/resume instead of keeping multiple sandboxes running
