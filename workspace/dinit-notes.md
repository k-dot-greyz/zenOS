# /dinit session notes — 2026-06-06

## Setup

- Read `CONTRIBUTING.md` from `origin/docs/add-contributing-workflow` (cherry-picked onto `greyzxc/issue-planning-and-setup-f971`).
- Submodule hydration: `neuro-spicy-devkit` cloned from `k-dot-greyz/neuro-spicy-devkit`. `mcp-config` and `zenOS-dev` repos return 404 (private or removed); `.gitmodules` missing on `main` — not fixed in this PR (out of scope for #26).
- Architecture protocol (§4.5) "State Hydration" = serialize/restore snapshots, not git submodules. Submodule workflow is §5 (dev-master checkout).

## Issue selected

**#26** — Add documentation maintenance checklist items to `COMMIT_WORKFLOW_CHECKLIST.md`

- Duplicate of **#20** — bundle in one PR, close both via `Closes #26, Closes #20`.
- Related epic (#21–#27) deferred to avoid PR spam; this PR only touches the commit checklist.

## Agnostic implementation plan

1. Extend the existing **Documentation** section with a **Documentation maintenance** sub-checklist (no new files).
2. Use canonical paths from the issue spec: `docs/`, `DECISION_LOG.md`, `docs/archive/`, `repos/registry.yaml`.
3. Wording is conditional ("when applicable") so the checklist works before rollout issues land those files.
4. Cross-link `CONTRIBUTING.md` §6 boundary rules — platform docs here, dev-master internals there.
5. No code changes; markdown-only, zero runtime impact.

## Verification

- [ ] `COMMIT_WORKFLOW_CHECKLIST.md` renders valid markdown
- [ ] New items match issue deliverable bullets
- [ ] PR labels: `documentation`
- [ ] Issue labels: `documentation`, `in progress` if available

## PR draft

- Title: `docs(ci): add documentation maintenance items to commit checklist`
- Branch: `greyzxc/issue-planning-and-setup-f971`
- Includes: `CONTRIBUTING.md` (foundation) + checklist update
