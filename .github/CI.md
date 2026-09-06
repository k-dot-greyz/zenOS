# zenOS CI & dependency policy

**Floor:** Python **3.14+**. Older interpreters are unsupported — do not add
matrix cells for them, and don't file this as a bug when `zen` refuses to
start on 3.13 or older. Enforced in three places, not just CI:
- `.github/workflows/zenos-ci.yml` (`actions/setup-python` pinned to `3.14`)
- `zen.runtime.require_runtime()` — every `zen`/`zenos` invocation hard-exits
  below the floor, before it can do anything else
- `zen doctor` / `zen env-doctor` (`zen/setup/env_doctor.py`) — full
  diagnostic report, checks the floor plus CLI wiring and deps

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
`pip-audit -r requirements.txt --strict` runs in two places:
- `zen doctor` (`zen/setup/env_doctor.py::check_dependency_vulnerabilities`)
  — a standard check, not opt-in like `--outdated`. Scoped to
  `requirements.txt`, never the whole live interpreter (a shared dev
  container's distro-vendored packages, e.g. system `pip` or `python-apt`,
  aren't zenOS's to fix and shouldn't block a doctor run over).
- CI's `security` job — a **hard gate**, not `continue-on-error: true`
  theater like the `bandit`/`safety` steps next to it.

A known-vulnerable pin blocks both. Fix it by bumping the pin deliberately
(`pip-audit --fix --dry-run` first, review, then apply) — don't add a
`continue-on-error` to make the light go green instead.

**Source of truth for Python deps:** `pyproject.toml`
(`pip install -e ".[dev]"`). `requirements.txt` is a mirror for tools that
still want `-r` (including `zen doctor`'s vulnerability scan) — keep it in
sync and never let it list a package that's imported but undeclared, or vice
versa.

**Don't match `[tool.black]`/`[tool.ruff]` `target-version` to
`requires-python`:** they're pinned at `py312`, deliberately below the
`py314` floor. Black's `py314` target auto-adopts PEP 758 (unparenthesized
`except A, B:`), which nothing older than 3.14 can parse — that's a real,
reproduced CI break (`Lint & Format Check` wants to rewrite files into
PEP-758 syntax the moment `target-version` includes `py314`), not a
hypothetical. Bump it only as an explicit, reviewed style decision.

**What we refuse:**
- Multi-version Python theater (a `python-app.yml` template workflow with a
  3.10–3.12 matrix predates the floor — don't resurrect that shape).
- `continue-on-error: true` security scans that pretend to gate merges.
- Aggregator jobs that only echo other failures without depending on them.
- New JavaScript, when TypeScript was the option.
- A root `setup.py` that has to be renamed out of the way before
  `pip install -e .` works. It's a PEP 517-safe shim now — see its own
  docstring and `zen.setup.env_doctor.check_setup_py_landmine`.

**Living gate:** `.github/workflows/zenos-ci.yml` — rewrite it when the stack
shifts; it is not dogma.
