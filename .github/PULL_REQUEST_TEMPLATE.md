## What

<<<<<<< HEAD
<!-- Concrete changes—not a file list. -->

## Why

<!-- Why this change exists and why this approach over alternatives. -->

## Before/After

<!-- Required for CLI/TUI/UI changes: video (preferred) or screenshots. -->
<!-- Docs-only or CI-only PRs: note "diff is the reviewable artifact" and skip media. -->

## Test Results

<!-- Commands run, for example: pytest, black --check, zen doctor -->

- [ ] `black --check .`
- [ ] `isort --check-only .`
- [ ] `flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics`
- [ ] `PYTHONPATH=. pytest --cov=. --cov-report=term-missing -v`
- [ ] `yamllint` (optional; non-blocking in CI)
- [ ] Other:

## QA steps

<!-- Steps a reviewer can follow to verify the change. -->

1. 
2. 

## Checklist

- [ ] Self-reviewed the diff (or left a self-review comment)
- [ ] No secrets, `.env`, or superproject-only docs in the diff
- [ ] Tests updated where behavior changed
- [ ] Public docs updated in `docs/` if user-facing behavior changed

## Related issues
=======
Machine-readable twin: update `.github/pr-intent.yaml` in this PR
(`intent`, `risk`, `supersedes`, `depends_on`, `touches_contracts`, `expiry_days`).
Contract diffs (`contracts/`, `zen/contracts/`, `dex/registry.yaml`) **must** set
`touches_contracts: true`. Overlapping open PRs **must** declare `supersedes`.

### Summary
Briefly describe what this PR does.
>>>>>>> f5fafaf (feat(harness): add Contract v1 for env-doctor, PR intent, and dex registry)

Closes #

---

## AI disclosure

<!-- If AI assisted: name the model and summarize prompts/context. Delete this section if not applicable. -->
