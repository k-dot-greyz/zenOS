# Get back on track (zenOS)

Short stack after the draft-CI exorcism. Not a novel — a runway.

## Order of operations

1. **Land CI floor** (this PR) — Python ≥3.14, kill template workflows, fix `requirements.txt` stdlib poison so installs work.
2. **Rebase / re-run [#47](https://github.com/k-dot-greyz/zenOS/pull/47)** (pokedex→dex) on top of the new gate. The old red CI was install failure, not proof the rebrand is broken.
3. **Then** merge wiki / agent integration ([#48](https://github.com/k-dot-greyz/zenOS/pull/48)) against a dex-aware `main`.
4. **Rust lane**: drop `Cargo.toml` (+ crates) when ready; CI already has an idle Rust job that activates on presence.

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
