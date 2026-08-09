# zenOS — repo house rules

Read this before touching setup, CI, or dependencies. Full policy and
rationale: [`.github/CI.md`](.github/CI.md).

## Stack

- **Python floor is 3.14.** Nothing below it — not "discouraged," refused.
  `zen setup` enforces this at dev-session startup
  (`zen/setup/troubleshooter.py::MIN_PYTHON`), CI enforces it in
  `.github/workflows/zenos-ci.yml`. If you're on an older interpreter, that's
  the fix, not a reason to loosen the check.
- **New systems/perf tooling → Rust.** New browser/Node-facing code →
  **TypeScript**, current **Vite**/current **Astro** for anything that needs
  a bundler or static site. Don't add new `.js` files — legacy JS in `n8n/`
  and `workspace/prototype/` is pre-existing, not precedent.
- Existing Python surfaces (the `zen` CLI, `zen/`) stay Python. This is about
  what a *new* component should default to, not a rewrite mandate.

## Dependencies

- `pyproject.toml` is the source of truth (`pip install -e ".[dev]"`).
  `requirements.txt` mirrors it for `-r` installs — keep both in sync, and
  never let either list a package that's imported but undeclared (that class
  of bug is exactly what broke `zen.cli` before: `aiofiles`/`psutil` were
  imported by `zen/plugins/*` but declared nowhere).
- **Old and vulnerable dependencies are sanitized on startup, not just in
  CI.** `pip-audit -r requirements.txt --strict` runs both as part of
  `zen setup` / `python setup.py --validate-only` and as a blocking CI job —
  see `.github/CI.md` for why it's scoped to `requirements.txt` rather than
  the whole live interpreter.
- A finding blocks. Fix by bumping the pin deliberately, not by adding
  `continue-on-error: true`.

## Commands

```bash
zen --help              # canonical CLI surface
zen setup --validate-only   # environment + dependency sanity check
pytest                  # tests/ — 15 tests as of this writing
pip-audit -r requirements.txt --strict
```

## When you find drift

If code, CI, or `zen setup` disagree with this file, fix the drift — don't
silently pick a side. Update this file in the same change if the *policy*
itself is what's moving.
