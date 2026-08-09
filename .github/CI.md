# zenOS CI & dependency policy

**Floor:** Python **3.14+**. Older interpreters are unsupported — do not add
matrix cells for them, and don't file this as a bug when `zen setup` refuses
to run on 3.13 or older. Enforced in two places, not just CI:
- `.github/workflows/zenos-ci.yml` (`actions/setup-python` pinned to `3.14`)
- `zen/setup/troubleshooter.py::MIN_PYTHON` — `zen setup` / `python setup.py
  --validate-only` hard-stop on a banned interpreter at dev-session startup,
  they don't just print a warning and carry on.

**Stack preference for new code** (existing Python surfaces aren't being
rewritten wholesale — this governs what gets picked when something new is
added):
1. **Rust** for new systems-level or perf-sensitive tooling. There's no
   `Cargo.toml` yet; when one lands, give it a first-class CI job
   (`cargo check && cargo test`), not an idle placeholder.
2. **TypeScript + current Vite / current Astro** for anything browser- or
   Node-facing. Plain `.js` is not an option for new files — `n8n/` and
   `workspace/prototype/` predate this rule and aren't being retrofitted on
   sight, but don't add more JS next to them.
3. **Python 3.14+** stays the floor for the existing `zen` CLI and its
   surface area.

**Dependency hygiene — sanitize on startup, not just in CI:**
`pip-audit` runs against `requirements.txt` (not the live interpreter's full
site-packages — a shared dev container carries distro-vendored packages,
like a system `pip` or `python-apt`, that zenOS doesn't own and can't
version-bump) in two places:
- `zen setup` / `python setup.py --validate-only` — every dev-session start.
- CI `security` job — a **hard gate**, not `continue-on-error: true` theater.

A known-vulnerable pin blocks setup and blocks merge. Fix it by bumping the
pin deliberately (`pip-audit --fix --dry-run` first, review, then apply) —
don't add a `continue-on-error` to make the light go green instead.

**Source of truth for Python deps:** `pyproject.toml`
(`pip install -e ".[dev]"`). `requirements.txt` is a thin mirror for tools
that still want `-r`; it must never list stdlib modules or drift out of sync
on what's actually imported (`aiofiles`, `psutil` were both imported by
`zen/plugins/*` without being declared anywhere — that's the class of bug
this file exists to prevent).

**What we refuse:**
- Multi-version Python theater (3.10–3.12 matrices) — deleted in
  `.github/workflows/python-app.yml`.
- `continue-on-error: true` security scans that pretend to gate merges.
- Aggregator jobs that only echo other failures without depending on them.
- New JavaScript, when TypeScript was the option.

**Living gate:** `.github/workflows/zenos-ci.yml` — rewrite it when the stack
shifts; it is not dogma.
