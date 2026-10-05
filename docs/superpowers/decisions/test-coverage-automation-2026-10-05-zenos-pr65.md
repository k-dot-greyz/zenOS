# Test coverage automation — zenOS PR #65

**Feat (merged):** [#65 Plan + harden base: zen receive, doctor TOML, install traps](https://github.com/k-dot-greyz/zenOS/pull/65)  
**Test PR:** (linked from automation) → base `greyzxcursor/py314-env-doctor-7f62`

## Intent (80/20)

| Story ID | Scenario | Impact | Type |
|----------|----------|--------|------|
| ZEN65-REC-01 | `zen receive add` + `list` happy path | **High** — primary inbox UX | pytest + Click |
| ZEN65-REC-02 | Invalid `--metadata` JSON | **Med** — graceful ablation | pytest |
| ZEN65-REC-03 | `move` updates status on disk | **High** — workflow | pytest |
| ZEN65-REC-04 | Unknown item id on `move` | **Med** — DX | pytest |
| ZEN65-REC-05 | Path traversal via `item_type` | **High** — security | pytest + inbox guard |
| ZEN65-REC-06 | Path segments in `item_id` on `move` | **High** — security | pytest + inbox guard |
| ZEN65-DOC-01 | Malformed `pyproject.toml` | **Med** — doctor TOML | pytest |
| ZEN65-DOC-02 | Missing `requires-python` | **High** — 3.14 floor alignment | pytest |
| ZEN65-DOC-03 | `format_report` OK/WARN/FAIL + AI mode | **Med** — doctor UX | pytest |
| ZEN65-DOC-04 | `zen doctor` exit 1 on failures | **High** — CI/DX gate | pytest |
| ZEN65-DOC-05 | `requires-python` fallback without packaging | **Med** — supply-chain / minimal env | pytest |
| ZEN65-DOC-06 | `pip list --outdated` failure → warn | **Low** — graceful ablation | pytest |
| ZEN65-DOC-07 | `--outdated` opt-in wiring | **Med** — perf default | pytest |

**Deferred (existing static coverage):** install.sh / `zenos-env-install.sh` trap strings (`test_env_doctor.py`), full bash trap integration (flaky in CI).

## Security notes

- **Vector:** `zen receive add` with `item_type` containing `../` could write JSON outside `inbox/incoming/` (path traversal).
- **Mitigation tested:** slug + resolved-path prefix checks in `zen/inbox.py`.
- **Vector:** Agentic/metadata injection via `--metadata`; invalid JSON must not create files (ZEN65-REC-02).

## Documentation follow-ups (issue todo)

- [ ] CLI stability plan: wire `tests/cli/` harness from `docs/superpowers/plans/2026-08-30-zen-cli-stability.md`
- [ ] Document inbox path rules in `inbox/README.md` (safe `item_type` vs stored `type` field)
