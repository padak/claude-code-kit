---
name: post-merge
description: "Post-merge cleanup after a PR is merged on GitHub. Switches to main, pulls changes, deletes the merged branch, and watches CI/CD. Triggers: /post-merge, 'I merged the PR', 'PR is merged', 'cleanup after merge'."
---

# Post-Merge Cleanup

Run this after a PR has been merged on GitHub to sync local state and watch CI/CD.

## Arguments

- `/post-merge` - Auto-detect the merged branch (current branch or most recently merged PR)
- `/post-merge <branch-name>` - Specify the branch to clean up
- `/post-merge <pr-number>` - Specify the PR number

## Workflow

### Step 1: Identify the merged branch

If a branch name or PR number is provided as argument, use that. Otherwise:

```bash
# Check if we're on a feature branch (not main/master)
CURRENT=$(git branch --show-current)

# If on main already, find the most recently merged PR
if [ "$CURRENT" = "main" ] || [ "$CURRENT" = "master" ]; then
  gh pr list --state merged --limit 1 --json number,headRefName,mergedAt
fi
```

Store the branch name and PR number for later steps.

### Step 2: Switch to main and pull

```bash
# Determine default branch name
DEFAULT_BRANCH=$(git remote show origin | grep 'HEAD branch' | awk '{print $NF}')

git checkout "$DEFAULT_BRANCH"
git pull origin "$DEFAULT_BRANCH"
```

### Step 3: Delete the merged branch

```bash
# Delete local branch
git branch -d <branch-name>

# Prune remote tracking references
git remote prune origin
```

If `git branch -d` fails (branch not fully merged), warn the user instead of force-deleting. Never use `git branch -D` without asking.

### Step 4: Watch CI/CD

```bash
# Find the latest workflow run on the default branch
gh run list --branch "$DEFAULT_BRANCH" --limit 5 --json status,conclusion,name,databaseId,createdAt,headSha

# If any run is in_progress or queued, watch it
gh run watch <run-id>
```

Report the CI/CD status to the user:
- If all checks pass: confirm everything is green
- If checks are still running: show progress and wait
- If checks fail: show which checks failed and link to the run

### Step 5: Summary

Print a clean summary:

```
Post-merge cleanup complete:
- Switched to: main
- Pulled: <commit-count> new commits
- Deleted branch: feature/xyz
- CI/CD: all checks passed (or status)
```

## Error Handling

- **Uncommitted changes on feature branch:** Stash them before switching, warn the user
- **Branch already deleted:** Skip deletion, continue with pull and CI watch
- **No CI runs found:** Report that no workflows were triggered
- **CI timeout:** After 10 minutes of watching, stop and provide a link to check manually
