# E2B Sandbox Skill

A comprehensive Claude Skill for working with E2B sandboxes - secure, isolated cloud VMs for executing AI-generated code.

## Overview

This skill provides Claude with deep knowledge of E2B's capabilities and best practices for:
- Creating and managing sandboxes
- Running Python and Bash code in isolated environments
- File operations (upload/download)
- Sandbox persistence (pause/resume)
- Integration with LLMs
- Data analysis workflows

## Structure

```
e2b/
├── SKILL.md                    # Main skill instructions (loaded when triggered)
├── README.md                   # This file
└── docs/                       # Reference documentation (loaded as needed)
    ├── quickstart.md           # Getting started guide
    ├── sandbox-lifecycle.md    # Lifecycle management
    ├── filesystem.md           # File operations
    ├── persistence.md          # Pause/resume features
    └── code-interpreting.md    # Data analysis patterns
```

## Installation

### For Claude Code

1. Copy this directory to your Claude Code skills directory:
   ```bash
   # Project-specific
   cp -r e2b /path/to/project/.claude/skills/

   # Or global (personal)
   cp -r e2b ~/.claude/skills/
   ```

2. Claude will automatically discover and use the skill when relevant.

### For Claude API

1. Package the skill as a zip file:
   ```bash
   cd e2b
   zip -r e2b-skill.zip .
   ```

2. Upload via the Skills API:
   ```bash
   curl -X POST https://api.anthropic.com/v1/skills \
     -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2025-02-25" \
     -H "anthropic-beta: skills-2025-10-02" \
     -F "file=@e2b-skill.zip"
   ```

### For Claude.ai

1. Zip the skill directory
2. Go to Settings > Features
3. Upload the zip file

## When This Skill is Used

Claude will automatically load this skill when you mention:
- "E2B sandbox"
- "Execute code in isolated environment"
- "Run Python code securely"
- "Create sandbox"
- "Upload files to sandbox"
- "Pause/resume sandbox"

## Quick Example

```python
from e2b_code_interpreter import Sandbox

# Create sandbox
with Sandbox.create() as sandbox:
    # Run code
    execution = sandbox.run_code('print("Hello from E2B!")')
    print(execution.text)
```

## Key Features Covered

### Sandbox Lifecycle
- Creating sandboxes with custom timeouts
- Managing sandbox state (running, paused, killed)
- Auto-pause for interactive sessions
- Proper cleanup and resource management

### Code Execution
- Running Python code
- Executing Bash commands
- Handling execution results and errors
- Multi-step code execution

### File Operations
- Uploading files to sandbox
- Downloading files from sandbox
- Listing and managing filesystem
- Working with different file types (CSV, JSON, images)

### Persistence
- Pausing sandboxes to save state
- Resuming paused sandboxes
- Managing long-running sessions
- Network considerations

### LLM Integration
- Tool use patterns
- Integration with Anthropic, OpenAI, and other LLMs
- Data analysis workflows
- Chart and visualization generation

## Prerequisites

The skill assumes users have:
- E2B account (sign up at https://e2b.dev/auth/sign-up)
- E2B API key (from https://e2b.dev/dashboard?tab=keys)
- `e2b-code-interpreter` package installed

## Documentation Sources

This skill was created from official E2B documentation:
- https://e2b.dev/docs
- Retrieved: 2025-11-10

## Updates

To update this skill with latest E2B documentation:

1. Use Firecrawl MCP to fetch updated docs
2. Update reference files in `docs/`
3. Update SKILL.md if there are API changes
4. Test with sample queries

## License

This skill is for use with Claude products. Documentation content is sourced from E2B's official documentation.

## Support

For issues with:
- **E2B platform**: https://e2b.dev/docs or E2B Discord
- **This skill**: Create an issue in your repository
- **Claude Skills**: https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills

## Version

- Version: 1.0
- Created: 2025-11-10
- E2B SDK Version: Latest (as of creation date)
- Compatible with: Python SDK and JavaScript/TypeScript SDK
