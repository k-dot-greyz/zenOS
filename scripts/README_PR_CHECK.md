# PR Status Checker

Tools to check pull request status, conflicts, and mergeability.

## GitHub Actions Workflow

The workflow (`.github/workflows/pr-status-check.yml`) automatically:
- Runs on PR events (opened, updated, etc.)
- Checks mergeability and conflicts
- Comments on PRs with status
- Can be triggered manually via `workflow_dispatch`

### Manual Trigger

Go to Actions → PR Status Check → Run workflow → Optionally specify a PR number

## Local Script

### Setup

```bash
pip install PyGithub
export GITHUB_TOKEN=your_token_here
# Or on Windows:
# $env:GITHUB_TOKEN="your_token_here"
```

Get a token at: https://github.com/settings/tokens
Required scopes: `repo` (for private repos) or `public_repo` (for public repos)

### Usage

```bash
# Check all open PRs
python scripts/check_prs.py

# Check specific PR
python scripts/check_prs.py --pr 42

# Show only PRs with conflicts
python scripts/check_prs.py --conflicts-only

# JSON output (for automation)
python scripts/check_prs.py --json

# Different repository
python scripts/check_prs.py --repo owner/repo-name
```

### Output Example

```
🔍 Checking all open PRs for k-dot-greyz/zenOS...

============================================================
PR #42: Add new feature
============================================================
Author: username
Branch: feature-branch → main
State: open
Created: 2025-01-15 10:30:00
Updated: 2025-01-15 14:20:00
URL: https://github.com/k-dot-greyz/zenOS/pull/42

📊 Merge Status:
  ✅ Mergeable: YES (no conflicts)
  ✅ Merge State: CLEAN

🔍 CI Status:
  ✅ lint: success
  ✅ test: success

👥 Reviews:
  ✅ Approvals: 2
  ❌ Changes Requested: 0
  📝 Total Reviews: 2

📝 Status: READY FOR REVIEW

📁 Files Changed: 5
  ✏️ modified: src/feature.py
  ➕ added: tests/test_feature.py

============================================================
✅ READY TO MERGE
============================================================
```

## What It Checks

- ✅ **Mergeability**: Can the PR be merged without conflicts?
- 🔍 **CI Status**: Are all checks passing?
- 👥 **Reviews**: Has it been approved?
- 📝 **Draft Status**: Is it ready for review?
- 📁 **Files Changed**: What files are affected?
- 🏷️ **Labels**: Any labels applied?

## Integration with Existing Workflows

This complements your existing CI workflows (`zenos-ci.yml`, `python-app.yml`) by:
- Providing PR-level status overview
- Identifying conflicts before merge attempts
- Summarizing review status
- Enabling automation based on PR state

