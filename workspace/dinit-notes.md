# /dinit session notes — 2026-06-06 (session 2)

## Setup

- Read `CONTRIBUTING.md` (on PR #37 branch `greyzxc/issue-planning-and-setup-f971`; not yet on `main`).
- **Submodule hydration** (§5 dev-master checkout):
  - `neuro-spicy-devkit` — public, reachable at `k-dot-greyz/neuro-spicy-devkit`.
  - `mcp-config`, `zenOS-dev` — private (404 without credentials); documented in `repos/registry.yaml` with `visibility: private`.
  - No `.gitmodules` on `main`; hydration is registry-documented, not git-submodule cloned in standalone zenOS.
- Architecture §4.5 "State Hydration" = serialize/restore snapshots, not git submodules.

## PR #37 status (prior session)

- Branch: `greyzxc/issue-planning-and-setup-f971`
- Covers: `CONTRIBUTING.md`, `.github/COMMIT_WORKFLOW_CHECKLIST.md` doc maintenance items
- Closes: **#26**, **#20** (duplicates)
- Labels: `documentation`

## Issue selected (this session)

**#27** — Create `DOCUMENTATION_GUIDE.md` (duplicate **#21** — bundle in one PR)

- Foundation doc for documentation knowledge-management epic.
- Scaffold files introduced so checklist paths exist on `main`:
  - `DECISION_LOG.md` (ADR-001, ADR-002 seed entries)
  - `docs/archive/README.md`
  - `repos/registry.yaml` (ecosystem switchboard)

## Agnostic implementation plan

1. Single canonical guide at `docs/guides/DOCUMENTATION_GUIDE.md` — tiers, layout, search, contribute, archive, ADR, switchboard, maintenance.
2. Wording is path-based and conditional — works for standalone clone and dev-master submodule checkout.
3. No hardcoded machine paths; search examples use `rg` from repo root.
4. Registry YAML is data, not code — agents/scripts can load without importing zenOS.
5. **Deferred** (separate PRs to avoid spam): #22 README sections, #23 AI_INSTRUCTIONS navigation, #24 TEMPLATE_POKEDEX_STATUS, #25 DEV_ENVIRONMENT_SETUP — all depend on this guide existing first.

## Verification

- [x] `DOCUMENTATION_GUIDE.md` includes all issue deliverable sections
- [x] Scaffold paths referenced in guide exist
- [x] `repos/registry.yaml` parses as valid YAML
- [x] No dev-master-internal SOPs committed
- [ ] PR labels: `documentation`
- [ ] Issue labels: `documentation`

## PR draft

- Title: `docs(guides): add DOCUMENTATION_GUIDE and knowledge-management scaffolds`
- Branch: `greyzxc/issue-planning-and-setup-54a2`
- Closes: #27, #21
