# Custom Templates

Custom templates allow you to create pre-configured sandbox environments with pre-installed packages, running services, and custom configurations. Templates dramatically reduce sandbox startup time by snapshotting ready-to-use environments.

## Table of Contents

1. [Overview](#overview)
2. [Build System 2.0 vs Legacy](#build-system-20-vs-legacy)
3. [When to Use Custom Templates](#when-to-use-custom-templates)
4. [Build System 2.0 (Recommended)](#build-system-20-recommended)
5. [Installing Packages](#installing-packages)
6. [Template Configuration](#template-configuration)
7. [How Templates Work](#how-templates-work)
8. [Examples](#examples)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

## Overview

### What Are Templates

Templates are pre-configured sandbox snapshots that include:

- **Pre-installed packages** - Python packages (pip), Node.js packages (npm), system packages (apt)
- **Running services** - Pre-started servers, databases, or background processes
- **Custom configurations** - Environment variables, file system setup, runtime settings
- **Resource allocation** - Custom CPU and RAM configurations

Templates enable:
- **Fast sandbox startup** - Load pre-configured environments in ~300ms
- **Consistent environments** - Same configuration across all sandbox instances
- **Reduced runtime overhead** - No package installation delays during execution
- **Complex setups** - Pre-configured development environments with multiple services

### Build System 2.0 vs Legacy

E2B offers two template building systems:

| Feature | Build System 2.0 (Recommended) | Legacy System |
|---------|-------------------------------|---------------|
| **Method** | SDK programmatic API | CLI with Dockerfiles |
| **Configuration** | TypeScript/JavaScript code | `e2b.toml` + Dockerfile |
| **Package Installation** | `.pipInstall()`, `.npmInstall()` | Manual in Dockerfile |
| **Ease of Use** | High - fluent API | Medium - requires Docker knowledge |
| **Documentation** | Current | Deprecated |
| **Status** | Active development | Maintenance only |

**Recommendation:** Use Build System 2.0 for all new templates. Legacy system is maintained for backward compatibility.

### When to Use Custom Templates

**Use custom templates when:**

✅ You need the same packages across multiple sandbox instances
✅ Package installation takes significant time (>5 seconds)
✅ You want to pre-start services (databases, web servers)
✅ You need specific CPU/RAM configurations
✅ You want to minimize user wait times

**Use runtime installation when:**

❌ Packages are only needed once or occasionally
❌ You're prototyping or testing
❌ Package requirements change frequently
❌ Installation is very fast (<2 seconds)

## Build System 2.0 (Recommended)

### Using SDK Programmatically

Build System 2.0 uses a fluent API to define and build templates programmatically.

#### 1. Install E2B SDK

```bash
npm install e2b dotenv
```

Create a `.env` file:

```
E2B_API_KEY=e2b_***
```

#### 2. Define Your Template

Create `template.ts` with your configuration:

```typescript
// template.ts
import { Template } from "e2b";

export const template = Template()
  .fromTemplate("code-interpreter-v1")  // Base template
  .pipInstall(['pandas', 'numpy', 'matplotlib'])  // Python packages
  .npmInstall(['express', 'axios'])  // Node.js packages
```

#### 3. Create Build Script

Create `build.prod.ts`:

```typescript
// build.prod.ts
import "dotenv/config";
import { Template, defaultBuildLogger } from "e2b";
import { template } from "./template";

async function main() {
  await Template.build(template, {
    alias: "my-custom-template",  // Template name/alias
    cpuCount: 2,                  // CPU cores
    memoryMB: 2048,               // RAM in MB
    onBuildLogs: defaultBuildLogger(),  // Show build logs
  });
}

main().catch(console.error);
```

#### 4. Build the Template

```bash
npx tsx build.prod.ts
```

The build process will:
1. Create a base container
2. Install specified packages
3. Execute any start commands
4. Wait for readiness
5. Create a snapshot
6. Register the template with your alias

#### 5. Use Your Custom Template

```typescript
import { Sandbox } from 'e2b'

// Create sandbox from your custom template
const sbx = await Sandbox.create("my-custom-template")

// Packages are already installed and ready
const result = await sbx.runCode(`
  import pandas as pd
  import numpy as np
  print("Packages ready!")
`)
```

### Template Configuration Options

#### Base Templates

Start from pre-configured base templates:

```typescript
// Code interpreter (Python, Node.js, Bash)
Template().fromTemplate("code-interpreter-v1")

// Custom base template
Template().fromTemplate("your-base-template-id")
```

#### Package Installation

```typescript
const template = Template()
  .fromTemplate("code-interpreter-v1")

  // Python packages
  .pipInstall(['pandas', 'scikit-learn', 'requests'])

  // Node.js packages
  .npmInstall(['express', 'lodash', 'axios'])

  // System packages (requires custom Dockerfile)
  // See Legacy System section for apt-get packages
```

#### CPU and RAM Customization

Configure resources during build:

```typescript
await Template.build(template, {
  alias: "high-memory-template",
  cpuCount: 4,      // 1-8 CPU cores
  memoryMB: 8192,   // RAM in megabytes (512-16384)
  onBuildLogs: defaultBuildLogger(),
});
```

**Resource Limits:**
- CPU: 1-8 cores
- RAM: 512 MB - 16 GB (512-16384 MB)

**Recommendations:**
- **Light workloads:** 1 CPU, 512-1024 MB
- **Standard workloads:** 2 CPUs, 2048 MB
- **Heavy workloads:** 4+ CPUs, 4096+ MB

## Installing Packages

There are two approaches to package installation in E2B sandboxes:

1. **Template-based (build time)** - Packages pre-installed in template
2. **Runtime installation** - Install packages when sandbox is running

### Template-Based Installation (Recommended)

Pre-install packages in your template for faster sandbox startup.

#### Python Packages (pip)

```typescript
const template = Template()
  .fromTemplate("code-interpreter-v1")
  .pipInstall([
    'pandas',
    'numpy',
    'matplotlib',
    'scikit-learn',
    'requests'
  ])
```

**Use case:** Common data science libraries that don't change often

#### Node.js Packages (npm)

```typescript
const template = Template()
  .fromTemplate("code-interpreter-v1")
  .npmInstall([
    'express',
    'axios',
    'lodash',
    'moment'
  ])
```

**Use case:** Web server dependencies, utility libraries

#### System Packages (Legacy System Only)

For system packages like `curl`, `git`, `postgresql-client`, you need to use the legacy Dockerfile approach:

**e2b.Dockerfile:**
```dockerfile
FROM e2bdev/code-interpreter:latest

RUN apt-get update && apt-get install -y \
    curl \
    git \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*
```

**Build with CLI:**
```bash
e2b template build --dockerfile e2b.Dockerfile --name system-tools
```

### Runtime Installation

Install packages dynamically when the sandbox is running.

**Advantages:**
- No template rebuild needed
- Flexible for changing requirements
- Good for prototyping

**Disadvantages:**
- Increases sandbox startup time
- Installation time on every sandbox instance
- No caching across instances

#### Python Packages

```typescript
import { Sandbox } from '@e2b/code-interpreter'

const sbx = await Sandbox.create()

// Install package at runtime
await sbx.commands.run('pip install cowsay')

// Use immediately
await sbx.runCode(`
  import cowsay
  cowsay.cow("Hello, world!")
`)
```

#### Node.js Packages

```typescript
import { Sandbox } from '@e2b/code-interpreter'

const sbx = await Sandbox.create()

// Install package at runtime
await sbx.commands.run('npm install cowsay')

// Use immediately
await sbx.runCode(`
  const cowsay = require('cowsay')
  console.log(cowsay.say({ text: 'Hello, world!' }))
`, { language: 'javascript' })
```

#### System Packages

```typescript
const sbx = await Sandbox.create()

// Update package list and install
await sbx.commands.run('apt-get update && apt-get install -y curl git')

// Use immediately
await sbx.commands.run('curl --version')
```

**Note:** E2B sandboxes are Debian-based, so you can use any Debian-supported package manager.

### When to Use Each Approach

| Scenario | Template-Based | Runtime |
|----------|---------------|---------|
| Same packages every time | ✅ Yes | ❌ No |
| Changing requirements | ❌ No | ✅ Yes |
| Long installation time | ✅ Yes | ❌ No |
| Quick prototyping | ❌ No | ✅ Yes |
| Production use | ✅ Yes | ⚠️ Maybe |

## Template Configuration

### Legacy System: e2b.toml Format

The legacy build system uses `e2b.toml` for configuration.

**Basic e2b.toml:**
```toml
# This is a config for E2B sandbox template
template_id = "1wdqsf9le9gk21ztb4mo"
dockerfile = "e2b.Dockerfile"
template_name = "my-agent-sandbox"
start_cmd = "/root/.jupyter/start-up.sh"
ready_cmd = 'curl -s -o /dev/null -w "%{http_code}" http://localhost:8888 | grep -q "200"'
```

**Configuration Options:**

| Field | Type | Description |
|-------|------|-------------|
| `template_id` | string | Unique template identifier |
| `dockerfile` | string | Path to Dockerfile (default: `e2b.Dockerfile`) |
| `template_name` | string | Human-readable template name |
| `start_cmd` | string | Command to run at startup |
| `ready_cmd` | string | Command to check readiness |

### Start Commands

Start commands run automatically when your sandbox is created, allowing you to:
- Pre-start web servers
- Initialize databases
- Run background processes
- Set up development environments

#### How Start Commands Work

1. Template builds with base configuration
2. Start command executes in the container
3. System waits for readiness (ready command)
4. Snapshot is created with the running process
5. New sandboxes spawn with the process already running

#### Defining Start Commands

**Build System 2.0 (not yet supported):**
Currently, Build System 2.0 doesn't support start commands directly. Use legacy system for this feature.

**Legacy System (e2b.toml):**
```toml
start_cmd = "/root/.jupyter/start-up.sh"
```

**Legacy System (CLI):**
```bash
e2b template build -c "/root/.jupyter/start-up.sh"
```

#### Example: Pre-start Jupyter Server

**start-jupyter.sh:**
```bash
#!/bin/bash
jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root
```

**e2b.toml:**
```toml
template_id = "jupyter-ready"
template_name = "jupyter-prestarted"
start_cmd = "/root/start-jupyter.sh"
ready_cmd = 'curl -s http://localhost:8888 > /dev/null'
```

When you create a sandbox from this template, Jupyter is already running.

#### Retrieving Start Command Logs

```bash
e2b sandbox logs <sandbox-id>
```

Logs include output from the start command during the build phase.

### Readiness Checks

Readiness commands determine when a template sandbox is ready for snapshotting.

#### How Readiness Works

1. Start command begins execution
2. Readiness command runs in an infinite loop
3. Exits when ready command returns **exit code 0**
4. Snapshot is created once ready

#### Defining Ready Commands

**e2b.toml:**
```toml
ready_cmd = 'curl -s http://localhost:3000 > /dev/null'
```

**CLI:**
```bash
e2b template build --ready-cmd 'curl -s http://localhost:3000 > /dev/null'
```

#### Default Behavior

- **No start command:** `sleep 0` (immediately ready)
- **With start command:** `sleep 20` (wait 20 seconds)

#### Examples

**Wait for HTTP server (200 status):**
```toml
ready_cmd = 'curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200"'
```

**Wait for specific process:**
```toml
ready_cmd = 'pgrep my-process-name > /dev/null'
```

**Wait for file to exist:**
```toml
ready_cmd = '[ -f /tmp/ready.flag ]'
```

**Wait for PostgreSQL:**
```toml
ready_cmd = 'pg_isready -h localhost -p 5432'
```

**Wait for port to be open:**
```toml
ready_cmd = 'nc -z localhost 3000'
```

### Environment Variables

You can access template metadata via environment variables in sandboxes.

**Default environment variables:**
- `E2B_SANDBOX` - Set to `true` (indicates running in E2B)
- `E2B_SANDBOX_ID` - Sandbox instance ID
- `E2B_TEAM_ID` - Your E2B team ID
- `E2B_TEMPLATE_ID` - Template ID used for this sandbox

**Example:**
```typescript
const sandbox = await Sandbox.create()
const result = await sandbox.commands.run('echo $E2B_TEMPLATE_ID')
console.log(result.stdout) // Prints template ID
```

**CLI access (as files):**
```bash
ls -a /run/e2b/
# .E2B_SANDBOX  .E2B_SANDBOX_ID  .E2B_TEAM_ID  .E2B_TEMPLATE_ID
```

## How Templates Work

### Build Process

Every template build follows these steps:

1. **Container creation**
   - Base container created from definition
   - Filesystem extracted

2. **Provisioning**
   - Install required dependencies
   - Run layer commands
   - Apply configurations

3. **Startup** (if start command specified)
   - Execute start command
   - Begin readiness monitoring

4. **Readiness check**
   - Default: 20 seconds if start command, else immediate
   - Custom: Run ready command until exit code 0

5. **Snapshot creation**
   - Capture entire filesystem
   - Serialize running processes
   - Save as template

### Snapshotting

Snapshots are saved running sandboxes that include:

- **Complete filesystem** - All files, directories, packages
- **Running processes** - Active services, background jobs
- **Process state** - Memory, connections, open files
- **System configuration** - Environment variables, network setup

Snapshots can be loaded later in **~300ms** with:
- All processes already running
- Filesystem exactly as saved
- Zero installation or startup time

### Load Time Benefits

**Without template (runtime installation):**
```
Create sandbox (300ms)
  → Install pandas (15s)
  → Install numpy (10s)
  → Install matplotlib (12s)
  → Start Jupyter (5s)
  → Total: ~42 seconds
```

**With template (pre-installed):**
```
Create sandbox from template (300ms)
  → Everything already ready
  → Total: 0.3 seconds
```

**Speedup: 140x faster**

### Default User and Workdir

Templates include default user and working directory settings:

- **Default user:** `user` (non-root)
- **Default workdir:** `/home/user`
- **Home directory:** `/home/user`

You can customize these in Dockerfiles (legacy system).

### Caching

E2B caches template builds for faster subsequent builds:

- **Layer caching** - Docker layers cached
- **Package caching** - Downloaded packages cached
- **Template caching** - Built templates cached

**Note:** See [Caching documentation](https://e2b.dev/docs/template/caching) for details.

## Examples

### Example 1: Data Science Template

Pre-install common data science packages.

**template.ts:**
```typescript
import { Template } from "e2b";

export const template = Template()
  .fromTemplate("code-interpreter-v1")
  .pipInstall([
    'pandas',
    'numpy',
    'matplotlib',
    'seaborn',
    'scikit-learn',
    'jupyter'
  ])
```

**build.prod.ts:**
```typescript
import "dotenv/config";
import { Template, defaultBuildLogger } from "e2b";
import { template } from "./template";

async function main() {
  await Template.build(template, {
    alias: "data-science",
    cpuCount: 2,
    memoryMB: 4096,
    onBuildLogs: defaultBuildLogger(),
  });
}

main().catch(console.error);
```

**Usage:**
```typescript
const sbx = await Sandbox.create("data-science")

// Immediately use pre-installed packages
await sbx.runCode(`
  import pandas as pd
  import numpy as np

  data = pd.DataFrame({
    'A': np.random.randn(100),
    'B': np.random.randn(100)
  })

  print(data.describe())
`)
```

### Example 2: Web Development Template

Pre-install Node.js packages for web development.

**template.ts:**
```typescript
import { Template } from "e2b";

export const template = Template()
  .fromTemplate("code-interpreter-v1")
  .npmInstall([
    'express',
    'axios',
    'lodash',
    'moment',
    'dotenv'
  ])
```

**build.prod.ts:**
```typescript
import "dotenv/config";
import { Template, defaultBuildLogger } from "e2b";
import { template } from "./template";

async function main() {
  await Template.build(template, {
    alias: "web-dev",
    cpuCount: 2,
    memoryMB: 2048,
    onBuildLogs: defaultBuildLogger(),
  });
}

main().catch(console.error);
```

**Usage:**
```typescript
const sbx = await Sandbox.create("web-dev")

// Create Express server instantly
await sbx.filesystem.write('/home/user/server.js', `
  const express = require('express')
  const app = express()

  app.get('/', (req, res) => {
    res.send('Hello from E2B!')
  })

  app.listen(3000, () => {
    console.log('Server running on port 3000')
  })
`)

await sbx.commands.run('node /home/user/server.js &')
```

### Example 3: Machine Learning Template (High Resources)

Template with heavy ML libraries and more resources.

**template.ts:**
```typescript
import { Template } from "e2b";

export const template = Template()
  .fromTemplate("code-interpreter-v1")
  .pipInstall([
    'tensorflow',
    'torch',
    'transformers',
    'datasets',
    'scikit-learn'
  ])
```

**build.prod.ts:**
```typescript
import "dotenv/config";
import { Template, defaultBuildLogger } from "e2b";
import { template } from "./template";

async function main() {
  await Template.build(template, {
    alias: "ml-heavy",
    cpuCount: 4,      // More CPU for training
    memoryMB: 8192,   // 8GB RAM for large models
    onBuildLogs: defaultBuildLogger(),
  });
}

main().catch(console.error);
```

### Example 4: Legacy System with Running Service

Use legacy system to pre-start a web server.

**e2b.Dockerfile:**
```dockerfile
FROM e2bdev/code-interpreter:latest

# Install Node.js if not present
RUN apt-get update && apt-get install -y nodejs npm

# Install Express
RUN npm install -g express

# Create startup script
RUN echo '#!/bin/bash\nnode /home/user/server.js' > /root/start-server.sh
RUN chmod +x /root/start-server.sh

# Create sample server
RUN echo "const express = require('express')\n\
const app = express()\n\
app.get('/', (req, res) => res.send('Ready!'))\n\
app.listen(3000, () => console.log('Server started'))" > /home/user/server.js
```

**e2b.toml:**
```toml
template_id = "express-server"
dockerfile = "e2b.Dockerfile"
template_name = "express-prestarted"
start_cmd = "/root/start-server.sh"
ready_cmd = 'curl -s http://localhost:3000 > /dev/null'
```

**Build:**
```bash
e2b template build
```

**Usage:**
```typescript
const sbx = await Sandbox.create("express-server")
// Server is already running on port 3000!
```

## Best Practices

### 1. Choose the Right Build System

**Use Build System 2.0 when:**
- Installing pip/npm packages only
- Want programmatic template definitions
- Need integration with TypeScript/JavaScript workflows
- Building modern applications

**Use Legacy System when:**
- Need system packages (apt-get)
- Want to run services at startup
- Require complex Dockerfile customizations
- Need precise container control

### 2. Optimize Package Installation

**Pin package versions:**
```typescript
.pipInstall([
  'pandas==2.0.0',
  'numpy==1.24.0'
])
```

**Group related packages:**
```typescript
// Good: Related packages together
.pipInstall(['pandas', 'numpy', 'matplotlib'])

// Avoid: Separate installs for each
.pipInstall(['pandas'])
.pipInstall(['numpy'])
.pipInstall(['matplotlib'])
```

### 3. Resource Allocation

**Match resources to workload:**
```typescript
// Light workloads
cpuCount: 1, memoryMB: 512

// Standard workloads (web servers, APIs)
cpuCount: 2, memoryMB: 2048

// Heavy workloads (ML, data processing)
cpuCount: 4, memoryMB: 8192
```

**Don't over-provision:**
- Higher resources = higher cost
- Start small, scale up if needed

### 4. Template Naming

Use descriptive, versioned aliases:

```typescript
// Good
alias: "data-science-v2"
alias: "web-api-prod"
alias: "ml-inference-gpu"

// Avoid
alias: "template1"
alias: "test"
alias: "my-template"
```

### 5. Start Commands and Readiness

**Keep start commands simple:**
```bash
# Good: Simple, focused
start_cmd = "python /app/server.py"

# Avoid: Complex chains
start_cmd = "cd /app && npm install && npm start"
```

**Use appropriate readiness checks:**
```toml
# For web servers: Check HTTP response
ready_cmd = 'curl -s http://localhost:8000 > /dev/null'

# For databases: Check connection
ready_cmd = 'pg_isready -h localhost'

# For processes: Check if running
ready_cmd = 'pgrep my-service > /dev/null'
```

### 6. Template Versioning

Version your templates for reproducibility:

```typescript
// Option 1: Version in alias
alias: "data-science-v1.2.0"

// Option 2: Save template ID
const templateId = await Template.build(template, { ... })
// Save templateId to config/database
```

### 7. Build Logging

Always enable build logs to debug issues:

```typescript
await Template.build(template, {
  alias: "my-template",
  onBuildLogs: defaultBuildLogger(),  // Essential for debugging
});
```

### 8. Testing Templates

Test templates before production:

```typescript
// Build test template
await Template.build(template, {
  alias: "my-template-test",
  onBuildLogs: defaultBuildLogger(),
});

// Test functionality
const sbx = await Sandbox.create("my-template-test")
// Run test code...

// If successful, build production template
await Template.build(template, {
  alias: "my-template-prod",
});
```

### 9. Documentation

Document your templates:

```typescript
// template.ts
/**
 * Data Science Template v2.0
 *
 * Includes:
 * - pandas 2.0.0
 * - numpy 1.24.0
 * - matplotlib 3.7.0
 * - scikit-learn 1.3.0
 *
 * Resources: 2 CPU, 4GB RAM
 * Use cases: Data analysis, visualization, ML prototyping
 */
export const template = Template()
  .fromTemplate("code-interpreter-v1")
  .pipInstall([
    'pandas==2.0.0',
    'numpy==1.24.0',
    'matplotlib==3.7.0',
    'scikit-learn==1.3.0'
  ])
```

## Troubleshooting

### Build Failures

**Problem:** Template build fails during package installation

**Solutions:**
```typescript
// 1. Check package names are correct
.pipInstall(['pandas', 'numpy'])  // Correct
.pipInstall(['panda', 'numpie'])  // Incorrect

// 2. Pin package versions to avoid conflicts
.pipInstall([
  'pandas==2.0.0',
  'numpy==1.24.0'
])

// 3. Enable build logs to see error details
onBuildLogs: defaultBuildLogger()
```

### Readiness Timeout

**Problem:** Template build times out waiting for readiness

**Solutions:**
```toml
# 1. Verify ready command works manually
ready_cmd = 'curl -s http://localhost:3000 > /dev/null'

# 2. Simplify ready command
# Instead of: Complex check with multiple conditions
ready_cmd = 'curl -s http://localhost:3000 && pgrep server'
# Use: Simple single check
ready_cmd = 'curl -s http://localhost:3000 > /dev/null'

# 3. Increase timeout (if needed)
# Check E2B documentation for timeout settings
```

### Start Command Not Running

**Problem:** Start command doesn't execute in spawned sandboxes

**Solution:**
```toml
# Ensure start command is executable
start_cmd = "/root/start.sh"

# In Dockerfile:
RUN chmod +x /root/start.sh
```

### Package Not Found at Runtime

**Problem:** Packages installed in template not found in sandbox

**Solutions:**
```typescript
// 1. Verify template was built successfully
// Check build logs for errors

// 2. Ensure using correct template
const sbx = await Sandbox.create("correct-template-name")

// 3. Verify package was added to template definition
.pipInstall(['missing-package'])

// 4. Rebuild template after changes
await Template.build(template, { ... })
```

### High Memory Usage

**Problem:** Template uses too much memory

**Solutions:**
```typescript
// 1. Reduce resource allocation
memoryMB: 2048  // Instead of 8192

// 2. Reduce number of pre-installed packages
// Only include essential packages

// 3. Monitor with metrics
const metrics = await sbx.getMetrics()
console.log(metrics.memory)
```

### Slow Build Times

**Problem:** Template builds take too long

**Solutions:**
```typescript
// 1. Use caching - rebuild from existing template
.fromTemplate("existing-template-id")

// 2. Reduce package count
// Only install frequently-used packages
// Install rare packages at runtime

// 3. Pin package versions
// Avoids dependency resolution overhead
.pipInstall(['pandas==2.0.0'])
```

### Template Not Found

**Problem:** Cannot create sandbox from template

**Solutions:**
```typescript
// 1. Verify template alias is correct
const sbx = await Sandbox.create("exact-alias-name")

// 2. Check template was built successfully
// Review build logs

// 3. Use template ID instead of alias
const sbx = await Sandbox.create("1wdqsf9le9gk21ztb4mo")
```

### Port Conflicts

**Problem:** Service in template can't bind to port

**Solutions:**
```toml
# 1. Use unique ports for each service
start_cmd = "python server.py --port 8000"

# 2. Check no other service uses the port
# In Dockerfile, ensure clean state

# 3. Use environment variables for port config
start_cmd = "PORT=8000 python server.py"
```

### Permission Errors

**Problem:** Permission denied errors in template

**Solutions:**
```dockerfile
# 1. Ensure files are owned by correct user
RUN chown -R user:user /home/user/

# 2. Make scripts executable
RUN chmod +x /root/start.sh

# 3. Run as appropriate user
USER user
```

### Getting Help

If you encounter issues:

1. **Check build logs:** `onBuildLogs: defaultBuildLogger()`
2. **Review documentation:** [E2B Template Docs](https://e2b.dev/docs/template)
3. **Search GitHub issues:** [E2B GitHub](https://github.com/e2b-dev/e2b/issues)
4. **Contact support:** [E2B Discord](https://discord.gg/U7KEcGErtQ)

---

**Related Documentation:**
- [Quickstart Guide](/docs/quickstart.md)
- [Code Interpreting](/docs/code-interpreting.md)
- [Sandbox Lifecycle](/docs/sandbox-lifecycle.md)
- [E2B Template Reference](https://e2b.dev/docs/template)
