# Get back on track (zenOS)

Short stack after the draft-CI exorcism. Full audit: [`docs/planning/REWORK_SPRINT_AUDIT.md`](../docs/planning/REWORK_SPRINT_AUDIT.md).

## Order of operations

1. **Land CI floor** (this PR) — Python ≥3.14, kill template workflows, fix `requirements.txt` stdlib poison so installs work.
2. **Unbreak `zen`** — packaging shim, `main()`, inbox registration, `zen --help` smoke (Track 0 in audit).
3. **Dex on main** ([#47](https://github.com/k-dot-greyz/zenOS/pull/47) merged) — keep branding gate green; collapse dual CLI paths.
4. **Then** merge wiki ([#48](https://github.com/k-dot-greyz/zenOS/pull/48)) against dex-aware `main`.
5. **Rust lane**: drop `Cargo.toml` (+ crates) when ready; CI already has an idle Rust job.

## Non-goals (for this cut)

- Supporting Python &lt; 3.14
- Keeping Bandit/Safety/mkdocs as merge theater
- Vendoring visual-wiki inside zenOS (stays separate / under dev-master)

## Commands

```bash
pip install -e ".[dev]"
pytest
# when crates exist:
cargo check --workspace && cargo test --workspace
```
