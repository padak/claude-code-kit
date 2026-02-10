---
name: swarm
description: Orchestrated multi-agent implementation using Tech Lead + Developer pattern. Use when implementing phased plans from docs/PLAN.md. Triggers: /swarm, "implement the plan", "run phased implementation", "execute PLAN.md phases". Spawns Developer agents for each phase, reviews PRs, handles retries and escalation.
---

# Swarm - Orchestrated Multi-Agent Implementation

Execute a phased implementation plan using a Tech Lead + Developer agent pattern.

## Arguments

- `/swarm` - Use default plan file `docs/PLAN.md`
- `/swarm <plan-file>` - Use specified plan file

## Workflow

```
For each phase in plan:
  1. Create branch from current main
  2. Spawn Developer agent to implement
  3. Developer creates PR when done
  4. Tech Lead (this agent) reviews PR
  5. If APPROVED: merge and continue
  6. If CHANGES_REQUESTED: Developer fixes (max 3 attempts)
  7. If max attempts exceeded: ESCALATE to human
```

## Step 1: Parse Plan

Read the plan file and extract phases. Each phase has this structure:

```markdown
<!-- PHASE:N -->
## Phase N: Name

### Branch
`phase-N-name`

### Scope
...

### Files to Create/Modify
...

### Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

### Tests Required
...
<!-- /PHASE:N -->
```

## Step 2: For Each Phase

```bash
git checkout main && git pull
git checkout -b <branch-name>
```

## Step 3: Spawn Developer Agent

```
Task(
  subagent_type: "general-purpose",
  description: "Implement Phase N",
  prompt: """
You are a Developer agent implementing Phase N.

## Task
Read the plan file, find Phase N (between <!-- PHASE:N --> markers), implement EVERYTHING in Scope.

## CRITICAL: Your Work Will Be Rigorously Reviewed

The Tech Lead will verify:
1. **Every file** in "Files to Create/Modify" exists and has real implementation
2. **Every acceptance criterion** is fully implemented (not stubbed)
3. **Every test** in "Tests Required" exists and passes
4. **Integration points** - router registered, config in .env.example, migration matches ORM

DO NOT:
- Create stub implementations (empty functions, pass, TODO comments)
- Skip any file from the list
- Write trivial tests that don't verify real behavior
- Leave acceptance criteria partially implemented
- Forget to register routers or add config vars

## Rules
1. Follow CLAUDE.md configuration standards (no hardcoded values, fail fast)
2. Create ALL files listed in "Files to Create/Modify" - every single one
3. Write ALL tests specified in "Tests Required" - run them to verify they pass
4. For each acceptance criterion, identify WHERE in your code it's satisfied
5. Commit with clear messages referencing the phase

## Branch
You are on branch: <branch-name>

## Before Creating PR - Self-Review Checklist

Before creating the PR, verify yourself:
- [ ] All files from "Files to Create/Modify" exist
- [ ] No TODO/FIXME/placeholder comments in new code
- [ ] All acceptance criteria have corresponding implementation
- [ ] All tests pass: `python -m pytest <module>/tests/ -v`
- [ ] Router registered in main.py (if new module)
- [ ] Config vars in .env.example (if new config)

## When Done
Create PR with acceptance criteria as checklist:

gh pr create --title "Phase N: <name>" --body "$(cat <<'EOF'
## Implementation Summary
<brief description>

## Acceptance Criteria
- [ ] Criterion 1 - implemented in `file.py:function()`
- [ ] Criterion 2 - implemented in `file.py:function()`
...

## Tests
- `pytest <module>/tests/ -v` - X tests pass

## Files Changed
<list of files created/modified>
EOF
)"

Report back with PR number.
"""
)
```

## Step 4: Review the PR (RIGOROUS)

**IMPORTANT:** Previous swarm runs had phases that were incomplete or sloppy. This review MUST be thorough. Do NOT approve until ALL checks pass.

### 4.1 File Inventory Check

Read the phase's "Files to Create/Modify" list. For EACH file:
```bash
# Check file exists
ls -la <file-path>

# Read and verify content is substantial (not stub/placeholder)
Read <file-path>
```

**FAIL if:**
- Any listed file is missing
- Any file contains TODO/FIXME/placeholder comments
- Any file is a stub (empty class, pass-only functions)
- Any file has `# Implementation needed` or similar

### 4.2 Acceptance Criteria Verification

For EACH criterion in "Acceptance Criteria" section:

1. **Read the criterion literally** - what exactly does it require?
2. **Find evidence** - which file/function implements it?
3. **Verify behavior** - run specific test or manual check

```markdown
| Criterion | Evidence | Verified |
|-----------|----------|----------|
| "Can create quota for user" | quotas/service.py:create_quota() | ✓ test passes |
| "Unique constraint prevents duplicates" | migration has UNIQUE KEY | ✓ |
| "Only managers can set quotas" | router.py uses require_role("manager") | ✓ |
```

**FAIL if:**
- Any criterion has no corresponding implementation
- Any criterion is partially implemented
- Any criterion relies on code that doesn't exist yet

### 4.3 Test Coverage Check

```bash
# Run the phase's tests specifically
cd apps/crm-api && python -m pytest <module>/tests/ -v

# Check all tests pass
# Check test count matches "Tests Required" list
```

**FAIL if:**
- Any test fails
- Test count is significantly lower than specified in plan
- Tests are trivial (e.g., `assert True`)

### 4.4 Integration Points Check

For new modules, verify:

```bash
# Router registered in main.py?
grep -n "<router>" apps/crm-api/app/main.py

# Config vars in .env.example?
grep -n "<new_config_var>" apps/crm-api/.env.example

# ORM model matches migration?
# Compare column names, types, nullability
```

**FAIL if:**
- Router not registered (endpoints unreachable)
- Config vars missing from .env.example
- Migration and ORM model have mismatches

### 4.5 Code Quality Check

1. **No hardcoded values** - all thresholds from config
2. **No silent defaults** - missing required config = startup failure
3. **UUID not INT** - all IDs are VARCHAR(36)
4. **Follows existing patterns** - check similar modules for consistency

### 4.6 Final Verdict

Only after ALL above checks pass:

```markdown
## PR Review: Phase N

### File Inventory: ✓ PASS
- [x] All 8 files created
- [x] No stubs or placeholders

### Acceptance Criteria: ✓ PASS
| Criterion | Status |
|-----------|--------|
| Criterion 1 | ✓ Verified in service.py:45 |
| Criterion 2 | ✓ Test test_unique_constraint passes |
| ... | ... |

### Tests: ✓ PASS
- 8/8 tests pass
- Matches "Tests Required" list

### Integration: ✓ PASS
- Router registered in main.py:67
- Config vars in .env.example

### Code Quality: ✓ PASS

**VERDICT: APPROVED**
```

If ANY check fails:

```markdown
## PR Review: Phase N

### FAILED CHECKS:

1. **Acceptance Criteria #3 not implemented**
   - "Quota attainment calculates correctly from closed-won opportunities"
   - No implementation found in service.py
   - Required: Add get_quota_attainment() method

2. **Missing test**
   - "Tests Required" lists "Fiscal period calculation" but no such test exists

**VERDICT: CHANGES_REQUESTED**
```

## Step 5: Decision

**APPROVED:**
```bash
gh pr merge <pr-number> --squash --delete-branch
```
Continue to next phase.

**CHANGES_REQUESTED:**
```
Task(
  prompt: """
Your PR for Phase N needs changes.

## Feedback
<specific feedback>

## Required Changes
1. ...

Fix on same branch and push. Attempt: <N>/3
"""
)
```

**Attempt >= 3:**
```
ESCALATE: Phase N requires human intervention.
PR: <url>
Issues: <summary>
```
Stop and notify user.

## Step 6: Progress Tracking

After each phase:

```
## Swarm Progress

| Phase | Status | PR | Attempts |
|-------|--------|-----|----------|
| 1     | DONE   | #12 | 1        |
| 2     | IN_PROGRESS | #13 | 1   |
| 3     | PENDING | -  | -        |
```

## Error Handling

- **Git conflict:** Escalate immediately
- **CI failure:** Count as failed review attempt
- **Agent timeout:** Retry once, then escalate
- **Network error:** Retry with backoff
