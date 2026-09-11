# zenOS CI philosophy

**Floor:** Python **3.14+**. Older interpreters are unsupported — do not add matrix cells for them.

**Rust:** First-class when `Cargo.toml` exists. Until then the Rust job stays idle on purpose (no fake green).

**Source of truth for Python deps:** `pyproject.toml` (`pip install -e ".[dev]"`). `requirements.txt` is a thin mirror for tools that still want `-r`; it must never list stdlib modules.

**What we refuse:**
- Multi-version Python theater (3.8–3.12 matrices)
- `continue-on-error: true` security scans that pretend to gate merges
- Aggregator jobs that only echo other failures
- Draft GitHub template workflows that don't match zenOS

**Living gate:** `.github/workflows/zenos-ci.yml` — rewrite it when the stack shifts; it is not dogma.
