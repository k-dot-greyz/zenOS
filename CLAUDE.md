# zenOS — repo house rules

Read this before touching setup, CI, or dependencies. Full policy and
rationale: [`.github/CI.md`](.github/CI.md).

## Stack

- **Python floor is 3.14.** Nothing below it — not "discouraged," refused.
  Enforced in three places:
  - `zen.runtime.require_runtime()` — hard `SystemExit(1)` on every `zen`/
    `zenos` invocation (`zen/cli.py:main`) below the floor or missing a core
    dep.
  - `zen doctor` / `zen env-doctor` (`zen/setup/env_doctor.py`) — full
    diagnostic: Python floor, `pyproject.toml` floor, CLI wiring, dependency
    vulnerabilities, core imports.
  - CI (`.github/workflows/zenos-ci.yml`), pinned to Python 3.14.
  If you're on an older interpreter, that's the fix, not a reason to loosen
  any of the three.
- **New systems/perf tooling → Rust.** New browser/Node-facing code →
  **TypeScript**, current **Vite**/current **Astro** for anything that needs
  a bundler or static site. Don't add new `.js` files — legacy JS in `n8n/`
  and `workspace/prototype/` is pre-existing, not precedent.
- Existing Python surfaces (the `zen` CLI, `zen/`) stay Python. This is about
  what a *new* component should default to, not a rewrite mandate.

## Dependencies

- `pyproject.toml` is the source of truth (`pip install -e ".[dev]"`).
  `requirements.txt` mirrors it for `-r` installs and for `zen doctor`'s
  vulnerability scan — keep both in sync, and never let either list a
  package that's imported but undeclared.
- **Old and vulnerable dependencies are sanitized on startup, not just in
  CI.** `zen doctor` runs `pip-audit -r requirements.txt --strict` as a
  standard (non-opt-in) check — scoped to `requirements.txt`, not the whole
  live interpreter, because a shared dev container also carries
  distro-vendored packages (system `pip`, `python-apt`, ...) that aren't
  zenOS's to fix and shouldn't block a doctor run. Same command is a
  blocking CI step in the `security` job.
- A finding blocks (`zen doctor` reports it `[FAIL]`, CI job fails). Fix by
  bumping the pin deliberately — review `pip-audit --fix --dry-run` first —
  not by adding `continue-on-error: true`.

## Commands

```bash
zen --help                          # canonical CLI surface (exits 1 below Python 3.14)
zen doctor                          # env-doctor: Python floor, CLI wiring, deps, pip-audit
zen doctor --outdated               # + informational pip list --outdated
pytest                              # tests/
pip-audit -r requirements.txt --strict
bash scripts/zenos-env-install.sh   # uv-based install: 3.14 venv + current deps
bash scripts/zenos-env-start.sh     # per-boot gate: fail fast if runtime isn't 3.14+
```

## CI gotcha: don't blindly match tool target-version to requires-python

`[tool.black]` / `[tool.ruff]` `target-version` are pinned to **`py312`**,
deliberately *below* the `py314` runtime floor — bumping either to `py314`
makes Black auto-adopt PEP 758 (unparenthesized multi-exception
`except A, B:`), which is invalid syntax on anything older than 3.14 and not
a style choice this repo has actually made. This has broken CI's
`Lint & Format Check` before; if you're tempted to "fix" the mismatch by
raising target-version to match `requires-python`, don't — that's the
regression, not the fix.

## When you find drift

If code, CI, or `zen doctor` disagree with this file, fix the drift — don't
silently pick a side. Update this file in the same change if the *policy*
itself is what's moving.
