# Claude Code Skills Collection

A collection of skills for [Claude Code](https://claude.com/claude-code) that extend Claude's capabilities with specialized knowledge and tools.

## Available Skills

| Skill | Description |
|-------|-------------|
| **[e2b](skills/e2b.skill)** | Execute AI-generated code in secure isolated E2B cloud sandboxes with monitoring, MCP gateway (200+ tools), and multi-language support |
| **[claude-agent-sdk](skills/claude-agent-sdk.skill)** | Build production applications with Claude Agent SDK (TypeScript and Python) |
| **[second-opinion](skills/second-opinion.skill)** | Get second opinion from OpenAI models via Codex CLI for architectural validation and code review |
| **[skill-creator](skills/skill-creator.skill)** | Guide for creating effective Claude Code skills |

## Installation

1. Download the `.skill` file you want
2. Place it in `~/.claude/skills/`
3. Unzip it (skills are zip archives):
   ```bash
   cd ~/.claude/skills
   unzip e2b.skill
   ```

Or clone the entire repo:
```bash
git clone https://github.com/padak/claude-skills.git
cd claude-skills
cp skills/*.skill ~/.claude/skills/
cd ~/.claude/skills
for f in *.skill; do unzip -o "$f"; done
```

## What are Skills?

Skills are modular packages that extend Claude Code with:
- **Specialized workflows** - Multi-step procedures for specific domains
- **Tool integrations** - Instructions for working with specific APIs or file formats
- **Domain expertise** - Company-specific knowledge, schemas, business logic
- **Bundled resources** - Scripts, references, and assets

## Creating Your Own Skills

Use the `skill-creator` skill to learn how to create effective skills. Each skill consists of:

```
skill-name/
├── SKILL.md          # Required: Frontmatter + instructions
├── references/       # Optional: Documentation files
├── scripts/          # Optional: Executable code
└── assets/           # Optional: Templates, images, etc.
```

## License

MIT
