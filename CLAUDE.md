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
zen setup --validate-only   # environment + dependency sanity check (Python floor, pip-audit)
bash env-doctor.sh --with-submodules   # broader env discovery (OS/shell/tooling/git/creds)
pytest                  # tests/ — 15 tests as of this writing
pip-audit -r requirements.txt --strict
```

## 🩺 Environment auto-healing protocol

`env-doctor.sh` (vendored from
[k-dot-greyz/env-doctor](https://github.com/k-dot-greyz/env-doctor) — GPL-3.0,
see `third_party/README.md`; zenOS's own code stays MIT) is the canonical
local environment diagnostic. It's broader than `zen setup`'s checks: OS/shell
discovery, tooling presence, git/submodule drift, `.env` completeness — it
does **not** know about zenOS's Python-3.14 floor or dependency-vuln
scanning, those stay `zen setup`'s job. The two are complementary, run both.

If you hit an import error, a missing-command error, or a test-collection
failure and you're not sure why:

1. Don't guess the machine state.
2. Run the read-only diagnostic first: `bash env-doctor.sh --json --quiet`
   (or `make doctor` for the human-readable version).
3. If it reports failures, `zen setup --validate-only` for the zenOS-specific
   half (Python floor, `pip-audit`).
4. Only run mutating init (`make setup` / `bash env-doctor.sh --init --tier 1`)
   when the user has actually asked for environment changes — same rule as
   everything else in this repo, don't install things silently.
5. Re-run the failing command once the diagnosis is clean or understood —
   don't loop on the same failure without re-checking.

## When you find drift

If code, CI, or `zen setup` disagree with this file, fix the drift — don't
silently pick a side. Update this file in the same change if the *policy*
itself is what's moving.
