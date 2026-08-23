# Template Registry Follow-Up Board

Parent planning doc: [TEMPLATE_REGISTRY_REHYDRATION.md](./TEMPLATE_REGISTRY_REHYDRATION.md)  
Blocks merge of: [PR #18](https://github.com/k-dot-greyz/zenOS/pull/18)

## Quick stats

| | Count |
|---|------|
| Total tracked tasks | 23 |
| Done in #18 | 7 |
| Partial | 2 |
| Open | 14 |

## GitHub issues (workstreams)

| Issue | Phase | Tasks |
|-------|-------|-------|
| [#57](https://github.com/k-dot-greyz/zenOS/issues/57) | 0 — Rehydration | T-00, T-01, T-02 |
| [#60](https://github.com/k-dot-greyz/zenOS/issues/60) | 1 — Runtime | T-03 … T-08 |
| [#58](https://github.com/k-dot-greyz/zenOS/issues/58) | 2 — Integration | T-09 … T-12 |
| [#59](https://github.com/k-dot-greyz/zenOS/issues/59) | 3 — CI & tests | T-13 … T-16 |

## PR checklist (before merging #18)

- [ ] T-00 naming ratified (Dex not Pokédex)
- [ ] T-02 branding gate passes
- [ ] T-03 `Agent()` works without `templates/`
- [ ] T-04 `TemplateValidator` exported
- [ ] T-05 path traversal guarded
- [ ] T-13 workflow permissions fixed
- [ ] T-14 CI green
- [ ] T-16 unit tests added
