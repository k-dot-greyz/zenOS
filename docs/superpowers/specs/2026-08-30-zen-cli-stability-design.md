# zenCLI stability — design spec

Date: 2026-08-30
Branch intent: recover the live `zen` Click surface, cover a few real use cases, and bench them over time.
North star: [`tasks.md`](../../../tasks.md)

## Problem

The installed console script is `zen.cli:main` (Click 8.5, Python 3.14). Docs, README, and `cli_v2` help text all teach a different CLI than the one that actually runs.

Reproduced on this VM (`/workspace/.venv`, CPython 3.14.7):

| Documented | Actual |
| --- | --- |
| `zen chat` | `Error: No such command 'chat'` |
| `zen --list` | `Error: No such option '--list'` (flag lives on `run`) |
| `zen --version` | Group option exists, but Click still demands a subcommand → `Missing command` |
| `zen help` | No such command (`help` only exists on unwired `cli_v2`) |
| `zen run chat` / `zen run --chat` | `TypeError: run() missing 1 required positional argument: 'version'` |
| `zen doctor` | Works (wired this week) |
| `zen dex` / `zen dex procedures` | Works (imported from `cli_v2`) |

Root cause of the TypeError: `run()` still declares `version: bool` but there is no `@click.option` for it. Click 8 does not pass `version`, Python raises before any chat/agent logic.

Second CLI: `zen/cli_v2.py` is a full group (`chat`, `doctor`, `help`, `analyze` in the banner) that is **not** the entrypoint. Only `dex`, `bench`, `sync`, `arena` were `add_command`'d onto `zen.cli`. Two doctors, two help texts, one of each dead.

Existing automated coverage is 33 tests, almost none of them invoke user-facing commands except `--help` containing `doctor`.

## Goals

1. Documented happy path works on the live Click group.
2. Meaningful tests for a **small** set of use cases (boot, doctor, chat command, run --list / mocked run, dex browse).
3. A stability bench that records exit + duration for those argv vectors and fails CI on behavior or 2× slowdown.
4. No second console script. No CLI rewrite. No live network in default tests.

## Non-goals

- Rewriting agents, OpenRouter, PKM extract, plugin marketplace.
- Renaming root `setup.py` (installer script vs setuptools — separate docs-heavy change).
- Deleting `cli_v2.py` in the first pass (stop growing it; extract later).
- Interactive TUI e2e (prompt_toolkit). Tests cover command existence, help, and non-TTY refusal/stub only.

## Approaches considered

### A. Stabilize the live Click group (recommended)

Keep `zen.cli:cli` as the only group. Fix Click contracts (`invoke_without_command`, `version_option`, first-class `chat`, drop phantom `version` on `run`). Add `tests/cli/*` + a tiny `zen.cli_bench` harness.

- Pros: matches `pyproject.toml`, smallest diff, tests pin the UX we already advertised.
- Cons: `cli_v2` stays messy until a later extract.

### B. Promote `cli_v2` to the entrypoint

Point `zen = zen.cli_v2:cli`. Docs match the v2 banner, but `run`/plugins/pkm/inbox/`require_runtime` all live on v1. You would re-wire everything and still hit missing `chat`/`analyze` implementations inside v2 (they are banner-only).

- Pros: none that survive contact with the code.
- Cons: drops working commands; v2 `doctor` is the old weak checker.

### C. Greenfield Click/Typer rewrite

Clean command tree, new tests, migrate plugins/pkm later.

- Pros: pretty.
- Cons: YAGNI. The borks are contract bugs, not “Click is wrong”.

**Decision: A.**

## Target command tree (MVP)

```text
zen                         # usage, exit 0
zen --version               # zenOS vX.Y.Z, exit 0
zen --help

zen chat [--offline] [--eco] [-m MODEL]   # interactive; tests only hit --help + non-TTY
zen doctor / zen env-doctor
zen run [--list|--create|--chat|AGENT PROMPT]
zen dex [models|procedures]
zen bench / zen sync / zen arena          # already registered; contract-test help only
zen plugins | pkm | inbox | setup         # help-only in MVP tests
```

`zen run --chat` and `zen chat` call the same function. `zen help` becomes an alias of `--help` (so old docs stop lying).

Empty argv and `--version` require `@click.group(invoke_without_command=True)` plus `@click.version_option`.

## Test design

TDD. CliRunner against the **group** `zen.cli.cli`, never `main()` (Click 8.5 runner needs `.name`). Isolate cwd with `tmp_path` so `AgentRegistry` / dex YAML / `.env` do not touch the repo or run surprise `git config`.

Use-case files:

| File | Use case |
| --- | --- |
| `tests/cli/test_contract.py` | UC1 boot: help, version, command set, `help` alias, no-args usage |
| `tests/cli/test_doctor.py` | UC2 doctor exit + floor string (thin wrap of existing env-doctor tests) |
| `tests/cli/test_chat.py` | UC3 `chat` is a command; `--help`; `run --chat` does not TypeError |
| `tests/cli/test_run.py` | UC4 `--list`; mocked `Launcher.execute`; unknown agent → exit 1 |
| `tests/cli/test_dex.py` | UC5 fixture YAML browse |
| `tests/cli/test_stability_bench.py` | timed argv set vs baseline |

Network: default tests monkeypatch OpenRouter / `InteractiveChat.start` / `MobileChat.start`. A later optional `@pytest.mark.network` is out of MVP.

## Stability bench

Handshake schema (committed): `tests/cli/baselines/usecases.json`

```json
{
  "schema_version": 1,
  "python_min": [3, 14],
  "cases": [
    {"id": "no_args", "argv": [], "expect_exit": [0], "max_ms": 3000},
    {"id": "help", "argv": ["--help"], "expect_exit": [0], "max_ms": 3000},
    {"id": "version", "argv": ["--version"], "expect_exit": [0], "max_ms": 3000},
    {"id": "doctor", "argv": ["doctor"], "expect_exit": [0, 1], "max_ms": 15000},
    {"id": "chat_help", "argv": ["chat", "--help"], "expect_exit": [0], "max_ms": 3000},
    {"id": "run_list", "argv": ["run", "--list"], "expect_exit": [0], "max_ms": 8000},
    {"id": "dex", "argv": ["dex"], "expect_exit": [0], "max_ms": 8000},
    {"id": "dex_procedures", "argv": ["dex", "procedures"], "expect_exit": [0], "max_ms": 8000}
  ]
}
```

Committed timings: `tests/cli/baselines/timings.json` (`id → p95_ms` from a quiet 3.14 run).

Local history (gitignored): `var/cli_bench/history.jsonl` — one object per run, **only** `{ts, python, cases: {id: {exit, ms}}}` after the schema is known.

CI: `pytest tests/cli/test_stability_bench.py` fails if exit not in `expect_exit` or `ms > max(max_ms, 2 * baseline_p95)`.

No live model tokens. Dex cases use repo YAML or a tmp fixture copied by the bench.

## Error handling

- Click contract bugs → TypeError today. After fix, missing required args stay Click `UsageError` (exit 2).
- Runtime floor stays `SystemExit(1)` from `require_runtime()` in `main()`.
- Unknown agent → exit 1 with a message, not a traceback.
- Non-TTY `zen chat`: exit 1 with “need a TTY (or use tests/CI stub)” **or** skip starting prompt_toolkit. Pick one in implementation: **exit 1 + message** so CI cannot hang.

## Dual-cli / file boundaries

- `zen/cli.py` — group, chat, run, doctor, wiring.
- `zen/cli_v2.py` — temporary home of dex/bench/sync/arena callbacks. No new commands.
- Later (not MVP): move those four into `zen/cli_dex.py` and leave `cli_v2.py` as a shim.
- `zen/cli_bench.py` — load usecases.json, invoke CliRunner, write JSONL, compare.

## Docs

After the command tree is green, sync **startup-facing** command lists only: README quick start, `docs/guides/QUICKSTART.md`, `docs/AI_INSTRUCTIONS.md`. Do not rewrite archives.

## Risks

- `AgentRegistry.list_agents()` currently ran `git config --global core.editor` during investigation. Tests must not inherit that. Fix or mock in UC4 if it still fires.
- `pydantic_core` “outdated” WARN is a pin, not a bump.
- Root `setup.py` still poisons `pip install -e .` unless moved aside (already handled in env install script).
- `zen/setup/mcp_setup.py` has a Python 3.14 `SyntaxWarning` on `` \` `` — park unless it breaks import of doctor.
