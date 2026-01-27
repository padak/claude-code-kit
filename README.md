# Claude Code Skills Collection

A collection of [skills](https://www.claude.com/blog/skills) for [Claude Code](https://claude.com/claude-code).

## Quick Install

Just tell Claude:

```
Install skills from https://github.com/padak/claude-skills - download .skill files
from skills/ directory, put them in ~/.claude/skills/ and unzip them.
Also copy CLAUDE.md to ~/.claude/CLAUDE.md.
```

## Available Skills

| Skill | Description |
|-------|-------------|
| **claude-agent-sdk** | Build apps with Claude Agent SDK (TypeScript/Python) |
| **e2b** | Execute code in secure E2B cloud sandboxes with MCP gateway (200+ tools) |
| **polymarket** | Build trading bots on Polymarket prediction markets (py-clob-client SDK) |
| **second-opinion** | Get second opinion from OpenAI via Codex CLI |
| **skill-creator** | Guide for creating Claude Code skills |
| **swarm** | Orchestrated multi-agent implementation (Tech Lead + Developer pattern) |

## Manual Installation

**Skills:**
```bash
cd ~/.claude/skills
curl -LO https://github.com/padak/claude-skills/raw/main/skills/e2b.skill
unzip e2b.skill
```

**CLAUDE.md (global instructions):**
```bash
curl -L https://github.com/padak/claude-skills/raw/main/CLAUDE.md -o ~/.claude/CLAUDE.md
```

## License

MIT
