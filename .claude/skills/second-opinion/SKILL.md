---
name: second-opinion
description: "Get second opinion from OpenAI models via Codex CLI. Use when validating architectural decisions, reviewing code security, comparing implementation approaches, or when multi-model consensus adds value. Triggers: get second opinion, validate with another model, ask Codex, multi-model analysis, compare perspectives, architectural review, security audit, code review needing external validation."
---

# Second Opinion via Codex CLI

Get external AI perspective from OpenAI models (GPT-5.3 Codex) to validate decisions or compare approaches.

## Quick Patterns

### Simple Question
```bash
codex exec -m gpt-5.3-codex --output-last-message /tmp/claude/answer.txt "Your question here"
cat /tmp/claude/answer.txt
```

### Structured Analysis (Recommended)

**IMPORTANT:** When using `--output-schema`, ALL objects (including nested ones) must have:
- `"additionalProperties": false`
- `"required": [...]` with all property names

```bash
cat > /tmp/claude/schema.json << 'EOF'
{
  "type": "object",
  "properties": {
    "assessment": { "type": "string" },
    "strengths": { "type": "array", "items": { "type": "string" } },
    "concerns": { "type": "array", "items": { "type": "string" } },
    "recommendation": { "type": "string" }
  },
  "required": ["assessment", "strengths", "concerns", "recommendation"],
  "additionalProperties": false
}
EOF

codex exec -m gpt-5.3-codex --output-schema /tmp/claude/schema.json \
  --output-last-message /tmp/claude/result.json \
  "Analyze [topic]. Provide structured assessment."

cat /tmp/claude/result.json
```

### Nested Objects Example
```bash
# Nested objects MUST also have additionalProperties: false
cat > /tmp/claude/nested_schema.json << 'EOF'
{
  "type": "object",
  "properties": {
    "summary": { "type": "string" },
    "details": {
      "type": "object",
      "properties": {
        "score": { "type": "string" },
        "items": { "type": "array", "items": { "type": "string" } }
      },
      "required": ["score", "items"],
      "additionalProperties": false
    }
  },
  "required": ["summary", "details"],
  "additionalProperties": false
}
EOF
```

## Use Cases

### Architecture Review
```bash
codex exec -m gpt-5.3-codex --output-last-message /tmp/claude/arch.txt \
  "Review this architecture decision: [description].
   Assess: scalability, maintainability, security risks, alternatives."
```

### Security Audit
```bash
codex exec -m gpt-5.3-codex --output-last-message /tmp/claude/security.txt \
  "Security review of [file/code]:
   - Input validation
   - Authentication/authorization
   - Data exposure risks
   Provide specific vulnerabilities and fixes."
```

### Code Review
```bash
codex exec -m gpt-5.3-codex --output-last-message /tmp/claude/review.txt \
  "Review [file] for: bugs, performance issues, maintainability.
   Provide line-level recommendations."
```

## Key Options

| Option | Purpose |
|--------|---------|
| `-m gpt-5.3-codex` | Default model (recommended) |
| `-m o4-mini` | Simple tasks (faster, cheaper) |
| `--output-schema file.json` | Structured JSON output |
| `--output-last-message file.txt` | Save response to file |
| `-i image.png` | Include image for analysis |

## Presenting Results

1. Label as "Second opinion (OpenAI/Codex)"
2. Compare with your own analysis
3. Highlight agreement and disagreement
4. Synthesize recommendation based on both perspectives

## Prerequisites

Verify Codex is available before use:
```bash
codex --version || echo "Codex CLI not installed"
```

If auth fails, user needs: `codex login` or set `OPENAI_API_KEY`.
