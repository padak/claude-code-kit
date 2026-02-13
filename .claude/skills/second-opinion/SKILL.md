---
name: second-opinion
description: "Get second opinion from OpenAI (Codex) or Google (Gemini) models. Use when validating architectural decisions, reviewing code security, comparing implementation approaches, or when multi-model consensus adds value. Supports both Codex CLI and Gemini CLI for flexibility."
---

# Second Opinion via Codex CLI and Gemini CLI

Get external AI perspective from OpenAI (via Codex CLI) or Google (via Gemini CLI) to validate decisions or compare approaches.

## Quick Patterns

### Using Codex (OpenAI)

#### Simple Question
```bash
codex exec -m gpt-5.3-codex --output-last-message /tmp/claude/answer.txt "Your question here"
cat /tmp/claude/answer.txt
```

#### Structured Analysis (Recommended)

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

### Using Gemini (Google)

#### Simple Question
```bash
gemini -p "Your question here" --output-format text > /tmp/claude/answer.txt
cat /tmp/claude/answer.txt
```

#### JSON Output
```bash
gemini -p "Analyze [topic]. Respond in JSON with: assessment (string), strengths (array), concerns (array), recommendation (string)" \
  --output-format json > /tmp/claude/result.json
cat /tmp/claude/result.json
```

**Note:** Gemini CLI doesn't support JSON Schema validation like Codex. For strict structured output, use Codex with `--output-schema`.

## Use Cases

### Architecture Review

**Codex:**
```bash
codex exec -m gpt-5.3-codex --output-last-message /tmp/claude/arch.txt \
  "Review this architecture decision: [description].
   Assess: scalability, maintainability, security risks, alternatives."
cat /tmp/claude/arch.txt
```

**Gemini:**
```bash
gemini -p "Review this architecture decision: [description].
  Assess: scalability, maintainability, security risks, alternatives." \
  --output-format text > /tmp/claude/arch.txt
cat /tmp/claude/arch.txt
```

### Security Audit

**Codex:**
```bash
codex exec -m gpt-5.3-codex --output-last-message /tmp/claude/security.txt \
  "Security review of [file/code]:
   - Input validation
   - Authentication/authorization
   - Data exposure risks
   Provide specific vulnerabilities and fixes."
cat /tmp/claude/security.txt
```

**Gemini:**
```bash
gemini -p "Security review of [file/code]:
  - Input validation
  - Authentication/authorization
  - Data exposure risks
  Provide specific vulnerabilities and fixes." \
  --output-format text > /tmp/claude/security.txt
cat /tmp/claude/security.txt
```

### Code Review

**Codex:**
```bash
codex exec -m gpt-5.3-codex --output-last-message /tmp/claude/review.txt \
  "Review [file] for: bugs, performance issues, maintainability.
   Provide line-level recommendations."
cat /tmp/claude/review.txt
```

**Gemini:**
```bash
gemini -p "Review [file] for: bugs, performance issues, maintainability.
  Provide line-level recommendations." \
  --output-format text > /tmp/claude/review.txt
cat /tmp/claude/review.txt
```

## Key Options

### Codex CLI Options

| Option | Purpose |
|--------|---------|
| `-m gpt-5.3-codex` | Best model (recommended) |
| `-m o4-mini` | Faster, cheaper for simple tasks |
| `--output-schema file.json` | Structured JSON with schema validation |
| `--output-last-message file.txt` | Save response to file |
| `-i image.png` | Include image for analysis |

### Gemini CLI Options

| Option | Purpose |
|--------|---------|
| `--model gemini-3-pro-preview` | Best reasoning (explicit selection) |
| `--model gemini-3-flash-preview` | Fast and capable |
| Auto-routing (default) | CLI selects best model automatically |
| `--output-format text` | Plain text output |
| `--output-format json` | JSON output (no schema validation) |
| `-p "prompt"` | Non-interactive mode (required) |

## Provider Comparison

| Use Case | Codex Recommendation | Gemini Recommendation |
|----------|---------------------|----------------------|
| Complex architectural review | `gpt-5.3-codex` | `gemini-3-pro-preview` or auto |
| Fast code review | `o4-mini` | `gemini-3-flash-preview` or auto |
| Security audit (deep) | `gpt-5.3-codex` | Auto-routing (recommended) |
| Structured output required | `gpt-5.3-codex` + schema | Use Codex (Gemini no schema) |
| Multi-provider consensus | Both! Run both and compare | Both! Run both and compare |

## Presenting Results

1. Label clearly which provider was used:
   - "Second opinion (OpenAI/Codex - gpt-5.3-codex)"
   - "Second opinion (Google/Gemini - gemini-3-pro)"
   - "Consensus (Codex + Gemini)" if using both
2. Compare with your own analysis
3. Highlight areas of agreement and disagreement
4. Synthesize recommendation based on multiple perspectives
5. Optional: Get consensus by asking both providers and comparing outputs

## Prerequisites

Verify CLIs are available before use:
```bash
# Check Codex
codex --version || echo "Codex CLI not installed"

# Check Gemini
gemini --version || echo "Gemini CLI not installed"
```

**Authentication:**
- **Codex:** `codex login` or set `OPENAI_API_KEY` env var
- **Gemini:** Already authenticated via Google OAuth or set `GEMINI_API_KEY` env var

## Multi-Provider Consensus Example

Get second opinions from both providers and compare:

```bash
# 1. Ask Codex
codex exec -m gpt-5.3-codex --output-last-message /tmp/claude/codex_opinion.txt \
  "Should we use Redis or PostgreSQL for session storage in e-commerce app?"

# 2. Ask Gemini
gemini -p "Should we use Redis or PostgreSQL for session storage in e-commerce app?" \
  --output-format text > /tmp/claude/gemini_opinion.txt

# 3. Compare outputs
echo "=== Codex (OpenAI) ===" && cat /tmp/claude/codex_opinion.txt
echo ""
echo "=== Gemini (Google) ===" && cat /tmp/claude/gemini_opinion.txt
```

Analyze agreement/disagreement and synthesize final recommendation.
