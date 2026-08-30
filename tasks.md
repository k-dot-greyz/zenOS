# zenCLI — guiding user story (MVP)

This file is the alignment bar for the CLI recovery. Spec: `docs/superpowers/specs/2026-08-30-zen-cli-stability-design.md`. Plan: `docs/superpowers/plans/2026-08-30-zen-cli-stability.md`.

Python floor is already **3.14+** (`zen.runtime`). Do not reopen that.

---

## Main use case

**As** Kaspars (or an AI agent in this repo),
**I want** `zen` to boot on 3.14, match the commands the docs already teach, and fail loudly with a stable exit code when something is wrong,
**so that** I can chat / doctor / browse dex / run an agent without Click exploding, and so we can re-run the same few use cases later to see if the CLI got slower or weirder.

### MVP (in, or it is not done)

1. `zen` with no args prints usage and exits 0 (not `Missing command`).
2. `zen --version` prints `zenOS v…` and exits 0.
3. `zen chat --help` exists as a real command. `zen chat` in a non-TTY test runner does **not** TypeError.
4. `zen doctor` / `zen env-doctor` keep working (already gated).
5. `zen run --list` lists built-in agents without calling OpenRouter.
6. `zen dex` / `zen dex procedures` read local YAML and exit 0.
7. A frozen use-case bench records `{id, argv, exit, ms}` so we can compare runs over time.

### Out of MVP (parked)

- Live OpenRouter chat / copilot / swarm.
- PKM Gemini extract, plugin GitHub search.
- Renaming root `setup.py` (env-doctor WARN — needs its own docs pass).
- Deleting `zen/cli_v2.py` (stop wiring new commands there; extract later).
- Full TUI screenshot tests.

---

## MVP UX flow (the path we test every time)

```text
$ zen
  → short usage + command list, exit 0

$ zen --version
  → zenOS v0.1.0, exit 0

$ zen doctor
  → env report, exit 0 if usable (WARN ok), exit 1 only on FAIL

$ zen chat --help
  → documents offline/eco/model flags, exit 0

$ zen run --list
  → table of agents (troubleshooter, critic, assistant, …), exit 0

$ zen run assistant "ping" --no-critique --debug
  → mocked provider in tests; no network; exit 0 or a typed error

$ zen dex
$ zen dex procedures
  → local catalog, exit 0

$ pytest tests/cli -q
$ python -m zen.cli_bench --write
  → JSONL history + CI compare vs committed baseline
```

If a step in that flow TypeErrors, missing-commands, or hangs the test runner, the CLI is not “up to speed”.

---

## Stability / bench rule

Same argv, same cwd fixture, no network.

- Exit code change → test FAIL (behavior regression).
- Duration > 2× committed baseline (or over the case `max_ms`) → FAIL (perf regression).
- First run of a new case writes the full schema; later runs append only `{ts, cases[{id, exit, ms}]}` (delta packets, handshake schema already known).

---

## Dual-CLI rule

`pyproject.toml` console scripts stay `zen = zen.cli:main`. `zen/cli_v2.py` is a leftover module that currently donates `dex`/`bench`/`sync`/`arena`. Do not add a second entrypoint. New commands go on `zen.cli`.
