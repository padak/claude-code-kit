# E2B Skill for Claude Code

> **Turn Claude Code into an E2B SDK expert - build AI code interpreters, data analysis tools, and apps powered by secure cloud sandboxes**

[![E2B](https://img.shields.io/badge/Powered%20by-E2B-orange)](https://e2b.dev)
[![Claude Code](https://img.shields.io/badge/Claude-Code%20Skill-blue)](https://docs.claude.com/en/docs/claude-code)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## 🚀 What is E2B Skill?

E2B Skill is a powerful Claude Code skill that gives Claude **expert knowledge of the E2B SDK** for building applications with secure, isolated cloud sandboxes.

With this skill, Claude can:
- **📝 Develop applications** that use E2B for code execution (AI code interpreters, data analysis tools, etc.)
- **🧪 Test and experiment** with E2B SDK features in real-time
- **🔧 Debug and troubleshoot** E2B integrations
- **🚀 Prototype** E2B-powered features quickly
- **📚 Teach you** how to use E2B SDK effectively

Think of it as giving Claude a complete understanding of E2B's capabilities, API, and best practices - so it can help you build powerful applications that leverage secure cloud sandboxes.

### Why E2B Skill?

**Without E2B Skill:**
- ❌ Claude runs code on your local machine (potential security risk)
- ❌ Experimental code can affect your system
- ❌ Need to install dependencies locally for every experiment
- ❌ No isolation between different projects
- ❌ Can't easily access 200+ tool integrations

**With E2B Skill:**
- ✅ Claude **builds E2B-powered applications** for you (AI interpreters, analysis tools, etc.)
- ✅ Expert knowledge of E2B SDK API, patterns, and best practices
- ✅ Real-time testing and debugging in cloud sandboxes (~150ms startup)
- ✅ Guides you through complex integrations (MCP Gateway, custom templates, etc.)
- ✅ Multi-language support (Python, JavaScript/TypeScript, Bash)
- ✅ 200+ tool integrations via MCP Gateway
- ✅ Interactive sessions with pause/resume capabilities
- ✅ Production-ready code with proper error handling

## 🎯 What Can Claude Do With E2B?

### 1️⃣ **Build E2B-Powered Applications**
Claude can develop complete applications that use E2B SDK:
```python
# Example: Claude builds you an AI code interpreter API
from fastapi import FastAPI
from e2b_code_interpreter import Sandbox
from pydantic import BaseModel

app = FastAPI()

class CodeRequest(BaseModel):
    code: str
    language: str = "python"

@app.post("/execute")
async def execute_code(request: CodeRequest):
    with Sandbox.create() as sandbox:
        execution = sandbox.run_code(
            request.code,
            language=request.language
        )
        return {
            "output": execution.text,
            "error": execution.error.value if execution.error else None,
            "results": execution.results
        }

# Claude writes this entire app, tests it, and helps you deploy it!
```

### 2️⃣ **Safe Code Execution & Testing**
Claude can experiment with E2B features in real-time:
```python
# Claude tests SDK features for you
execution = sandbox.run_code('''
def fibonacci(n):
    if n <= 1: return n
    return fibonacci(n-1) + fibonacci(n-2)

[fibonacci(i) for i in range(10)]
''')
# Instant results: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

### 3️⃣ **Data Analysis Without Local Setup**
Upload datasets, analyze, visualize - no installation needed:
```python
# Upload dataset
sandbox.files.write('/home/user/sales.csv', dataset)

# Claude analyzes and creates visualizations
execution = sandbox.run_code('''
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('/home/user/sales.csv')
df.groupby('region')['revenue'].sum().plot(kind='bar')
plt.savefig('/home/user/chart.png')
''')

# Download the chart
chart = sandbox.files.read('/home/user/chart.png')
```

### 4️⃣ **Rapid Prototyping**
Test libraries and approaches without polluting your environment:
```javascript
// Try out new npm packages instantly
const exec = await sandbox.runCode(`
import axios from 'axios';
const response = await axios.get('https://api.github.com/users/octocat');
response.data.name;
`, { language: 'typescript' })
```

### 5️⃣ **200+ Tool Integrations via MCP Gateway**
Claude can connect to databases, APIs, and services:
```python
# Create sandbox with GitHub + Slack + MongoDB
sandbox = Sandbox.create(mcp={
    'github': {'githubPersonalAccessToken': GITHUB_TOKEN},
    'slack': {'botToken': SLACK_BOT_TOKEN},
    'mongodb': {'connectionString': MONGO_URI}
})

# Claude can now query MongoDB, update GitHub issues, post to Slack
# All from within the sandbox environment!
```

### 6️⃣ **Multi-Step Interactive Sessions**
Complex workflows with state persistence:
```python
# Start analysis session
sandbox = Sandbox.create(timeout=600)

# Step 1: Load data
sandbox.run_code("import pandas as pd; df = pd.read_csv('data.csv')")

# Step 2: Clean data
sandbox.run_code("df = df.dropna(); df = df[df['value'] > 0]")

# Step 3: Analyze
sandbox.run_code("df.describe()")

# Pause if needed - come back later!
sandbox.beta_pause()

# Resume and continue
sandbox = Sandbox.connect(sandbox_id)
```

## 🛠️ Core Features

### Sandbox Management
- **Fast startup** - ~150ms cold start
- **Flexible timeouts** - 5 min default, configurable up to hours
- **Pause/Resume** - Save state between sessions (beta)
- **Metadata tagging** - Organize sandboxes by user, project, purpose
- **List & filter** - Find sandboxes by state, metadata, or tags

### Code Execution
- **Python** - Full Jupyter notebook environment
- **JavaScript/TypeScript** - ESM imports, top-level await
- **Bash** - System commands and scripts
- **Streaming output** - Real-time stdout/stderr
- **Background processes** - Long-running commands
- **Environment variables** - Global, execution, or command-scoped

### File Operations
- **Upload/Download** - Move files in and out of sandbox
- **Directory listing** - Browse filesystem
- **File watching** - Monitor changes in real-time
- **1-5GB storage** - Depending on tier

### Monitoring
- **Real-time metrics** - CPU, memory, disk usage
- **Lifecycle events** - Track sandbox creation, pause, resume, termination
- **Webhooks** - Get notified of important events

### MCP Gateway (200+ Integrations)
- **Databases** - MongoDB, PostgreSQL, Redis, Elasticsearch
- **Cloud** - AWS, Azure, Google Cloud, Kubernetes
- **Communication** - Slack, Discord, Telegram
- **Development** - GitHub, GitLab, Jira, Linear
- **AI Services** - OpenAI, Hugging Face, ElevenLabs
- **And 180+ more...**

## 📦 Installation

### Prerequisites
1. **E2B API Key** - Get yours at [e2b.dev/dashboard](https://e2b.dev/dashboard?tab=keys)
2. **Claude Code** - [Install Claude Code](https://docs.claude.com/en/docs/claude-code)

### Setup

1. **Clone this skill to your Claude Code skills directory:**
```bash
cd ~/.claude/skills
git clone https://github.com/padak/e2b-claude-skill.git e2b
```

2. **Set your E2B API key:**
```bash
export E2B_API_KEY=e2b_***
```

Or add to your `~/.zshrc` or `~/.bashrc`:
```bash
echo 'export E2B_API_KEY=e2b_***' >> ~/.zshrc
```

3. **That's it! Use the skill in Claude Code:**
```
Simply mention "use E2B" or "run this in a sandbox" and Claude will automatically invoke the skill!
```

> **Note:** You don't need to install the E2B SDK locally. Claude will handle all SDK operations inside the E2B sandbox automatically.

## 💡 Usage Examples

### Example 1: Build an E2B-Powered Application
```
You: "Create a FastAPI app that executes Python code in E2B sandboxes"

Claude: [Uses E2B skill]
- Writes complete FastAPI application with E2B SDK
- Implements endpoints for code execution
- Adds proper error handling and validation
- Tests the implementation in real E2B sandbox
- Provides deployment instructions
- Delivers production-ready code
```

### Example 2: Quick Data Analysis
```
You: "Analyze this CSV file and create a visualization"

Claude: [Uses E2B skill]
- Creates sandbox
- Uploads your CSV
- Runs pandas analysis
- Generates matplotlib chart
- Downloads result
- Shows you insights + chart
```

### Example 3: Test a Library
```
You: "Can you test how the 'httpx' library works for async requests?"

Claude: [Uses E2B skill]
- Creates sandbox
- Writes test code with httpx
- Executes it
- Shows you results and examples
- Explains how to use it
```

### Example 4: Multi-Step Development
```
You: "Build a script that fetches GitHub issues and posts summary to Slack"

Claude: [Uses E2B skill with MCP Gateway]
- Creates sandbox with GitHub + Slack MCP servers
- Develops the script iteratively
- Tests each step
- Handles errors
- Delivers working solution
```

### Example 5: Safe Experimentation
```
You: "I found this code snippet online, can you test if it works?"

Claude: [Uses E2B skill]
- Runs code in isolated sandbox
- Tests edge cases
- Identifies bugs
- Suggests improvements
- All without risk to your system!
```

## 🎓 Use Cases

- **🏗️ Build E2B Applications** - Develop AI code interpreters, data analysis tools, or any app using E2B SDK
- **🤖 LLM-Powered Tools** - Create agentic workflows with code execution and 200+ integrations
- **🔗 API Development** - Build and test APIs that execute user code safely in sandboxes
- **📊 Data Analysis Platforms** - Create tools for automated data processing and visualization
- **🚀 Rapid Prototyping** - Experiment with E2B features and SDK capabilities
- **🔬 Research Tools** - Build scientific computing and ML experimentation platforms
- **🧪 Code Testing** - Test and debug E2B integrations in real-time
- **📚 Learning** - Understand E2B SDK patterns and best practices with Claude's guidance

## 🏗️ Advanced Features

### Custom Templates
Build custom sandbox environments with specific dependencies:
```bash
# Create e2b.toml
cpu_count = 2
memory_mb = 4096
start_cmd = "python app.py"

# Build template
e2b template build
```

### Persistence (Beta)
Long-running sessions with state preservation:
```python
# Auto-pause when idle
sandbox = Sandbox.beta_create(auto_pause=True, timeout=600)

# Work continues across sessions
# Sandbox auto-pauses when inactive
# Resume instantly when needed
```

### Multi-Language Support
Switch between languages seamlessly:
```python
# Python
sandbox.run_code('import pandas as pd')

# JavaScript
sandbox.run_code('const x = await fetch(url)', language='js')

# Bash
sandbox.run_code('ls -la', language='bash')
```

## 📚 Documentation

- **[E2B Official Docs](https://e2b.dev/docs)** - Complete E2B documentation
- **[Skill Documentation](./SKILL.md)** - Detailed skill usage guide
- **[API Reference](./docs/)** - In-depth API documentation
- **[Examples](./examples/)** - Code examples and patterns

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🌟 Why Choose E2B Skill?

E2B Skill transforms Claude Code into an **E2B SDK expert** that can help you:
- ✅ **Build production apps** - Develop complete E2B-powered applications from scratch
- ✅ **Master the SDK** - Learn E2B API, patterns, and best practices with expert guidance
- ✅ **Ship faster** - Test and debug E2B integrations in real-time
- ✅ **Leverage 200+ tools** - Integrate databases, APIs, and services via MCP Gateway
- ✅ **Scale confidently** - Get production-ready code with proper error handling
- ✅ **Experiment safely** - Try features in isolated cloud sandboxes (start in ~150ms)

Whether you're building an AI code interpreter, data analysis platform, or integrating E2B into your app - **Claude becomes your expert E2B development partner**.

**Ready to build with E2B?** Install E2B Skill today! 🚀

---

<div align="center">

**[Get Your E2B API Key](https://e2b.dev/dashboard?tab=keys)** • **[Documentation](https://e2b.dev/docs)** • **[Join Discord](https://discord.gg/U7KEcGErtQ)**

Made with ❤️ by the E2B community

</div>
