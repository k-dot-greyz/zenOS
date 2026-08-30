# zenCLI stability Implementation Plan

> **For implementers:** Walk this plan task-by-task. Checkbox (`- [ ]`) steps are the source of truth and can be followed manually in any editor. Optional Cursor skills `superpowers:subagent-driven-development` or `superpowers:executing-plans` can dispatch/review those same steps; they are **not** required and are not defined in this repo.

**Goal:** Make the live `zen` Click group match the documented MVP UX in `tasks.md`, cover those use cases with TDD, and record a repeatable CLI stability bench.

**Architecture:** Single entrypoint `zen.cli:main`. Fix Click contracts on that group. Tests use `click.testing.CliRunner` against `cli` (not `main`). Bench reads a committed use-case schema and appends duration/exit deltas.

**Tech Stack:** Python 3.14+, Click 8.2+, pytest, CliRunner, Rich (output assertions on text, not ANSI when possible).

## Global Constraints

- Python `>=3.14` (`zen.runtime.MIN_PYTHON`); do not support older interpreters.
- Console scripts stay `zen = zen.cli:main` and `zenos = zen.cli:main`.
- No second entrypoint. Do not add commands to `zen/cli_v2.py`.
- Default tests: no network, no TTY chat loop, no OpenRouter.
- CliRunner must invoke the Click group `cli`, never `main()`.
- Do not bump `pydantic-core` past the version pydantic 2.13.x requires.
- Do not rename root `setup.py` in this plan.
- TDD: failing test first, watch it fail, then minimal code.

## File map

| Path | Role |
| --- | --- |
| `tasks.md` | Guiding user story (already written) |
| `zen/cli.py` | Live group: version, no-args usage, `chat`, `help`, fix `run` |
| `zen/cli_bench.py` | Use-case runner + JSONL compare |
| `tests/cli/conftest.py` | Runner + isolated cwd |
| `tests/cli/test_contract.py` | UC1 |
| `tests/cli/test_chat.py` | UC3 |
| `tests/cli/test_run.py` | UC4 |
| `tests/cli/test_dex.py` | UC5 |
| `tests/cli/test_stability_bench.py` | Timed argv set |
| `tests/cli/baselines/usecases.json` | Handshake schema |
| `tests/cli/baselines/timings.json` | Committed p95 |
| `var/cli_bench/` | Local JSONL history (gitignore) |
| `README.md`, `docs/guides/QUICKSTART.md`, `docs/AI_INSTRUCTIONS.md` | Command lists after green |

Existing `tests/test_cli_entrypoint.py` and `tests/test_env_doctor.py` stay; new tests live under `tests/cli/`.

---

### Task 1: Click contract — version, no-args, command inventory

**Files:**
- Create: `tests/cli/conftest.py`
- Create: `tests/cli/test_contract.py`
- Modify: `zen/cli.py` (group decorator + empty invoke)
- Modify: `.gitignore` (add `var/cli_bench/` if missing)

**Interfaces:**
- Consumes: `zen.cli.cli` Click group, `zen.__version__`
- Produces: `cli` callable with `invoke_without_command=True`; `--version` exits 0 without a subcommand; no-args exits 0 with Usage text

- [ ] **Step 1: Write the failing tests**

```python
# tests/cli/conftest.py
from __future__ import annotations

import pytest
from click.testing import CliRunner


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def zen_cli():
    from zen.cli import cli

    return cli
```

```python
# tests/cli/test_contract.py
from __future__ import annotations

REQUIRED_COMMANDS = {
    "arena",
    "bench",
    "dex",
    "doctor",
    "env-doctor",
    "help",
    "inbox",
    "receive",
    "pkm",
    "plugins",
    "run",
    "setup",
    "sync",
}


def test_help_lists_required_commands(runner, zen_cli):
    result = runner.invoke(zen_cli, ["--help"])
    assert result.exit_code == 0
    for name in sorted(REQUIRED_COMMANDS):
        assert name in result.output, name


def test_no_args_prints_usage_exit_zero(runner, zen_cli):
    result = runner.invoke(zen_cli, [])
    assert result.exit_code == 0
    assert "Usage:" in result.output


def test_version_flag_exit_zero(runner, zen_cli):
    from zen import __version__

    result = runner.invoke(zen_cli, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_help_command_alias(runner, zen_cli):
    result = runner.invoke(zen_cli, ["help"])
    assert result.exit_code == 0
    assert "Commands:" in result.output
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/cli/test_contract.py -q --no-cov`

Expected: FAIL — `chat`/`help` missing from help; no-args exit != 0; `--version` missing command.

- [ ] **Step 3: Minimal implementation**

In `zen/cli.py`:

- Change `@click.group()` to `@click.group(invoke_without_command=True)`.
- Replace `@click.option("--version", is_flag=True)` with `@click.version_option(version=__version__, prog_name="zen")`.
- Group callback: if `ctx.invoked_subcommand is None` and not version-handled, `click.echo(ctx.get_help())`.
- Add:

```python
@cli.command("help")
@click.pass_context
def help_command(ctx: click.Context) -> None:
    click.echo(ctx.parent.get_help() if ctx.parent else ctx.get_help())
```

Do **not** add `chat` yet — that is Task 2. Task 1 must go green without `chat` in `REQUIRED_COMMANDS`.

- [ ] **Step 4: Run tests**

`pytest tests/cli/test_contract.py tests/test_cli_entrypoint.py -q --no-cov`

Expected: Task 1 cases green except `chat` if deferred.

- [ ] **Step 5: Commit**

```bash
git add tests/cli/conftest.py tests/cli/test_contract.py zen/cli.py .gitignore
git commit -m "test(cli): pin Click contract for help, version, and no-args usage."
```

---

### Task 2: First-class `zen chat` and kill the `run(..., version)` TypeError

**Files:**
- Create: `tests/cli/test_chat.py`
- Modify: `zen/cli.py` (`run` signature + `chat` command)

**Interfaces:**
- Consumes: existing InteractiveChat / MobileChat (do not start them in tests)
- Produces: `chat` command; `run` callback params match Click options (no `version`)

- [ ] **Step 1: Write the failing tests**

Add `"chat"` to `REQUIRED_COMMANDS` in `tests/cli/test_contract.py` in this same red step.

```python
# tests/cli/test_chat.py
from __future__ import annotations


def test_chat_is_a_command(runner, zen_cli):
    result = runner.invoke(zen_cli, ["chat", "--help"])
    assert result.exit_code == 0
    assert "--offline" in result.output
    assert "--eco" in result.output


def test_run_chat_does_not_typeerror(runner, zen_cli, monkeypatch):
    monkeypatch.setattr("zen.cli._start_chat", lambda **kwargs: None)
    result = runner.invoke(zen_cli, ["run", "--chat"])
    assert result.exception is None
    assert result.exit_code == 0


def test_chat_non_tty_does_not_hang(runner, zen_cli):
    result = runner.invoke(zen_cli, ["chat"])
    assert result.exit_code == 1
    assert "TTY" in result.output or "tty" in result.output.lower()
```

- [ ] **Step 2: Run to verify fail**

`pytest tests/cli/test_chat.py -q --no-cov`

Expected: `No such command 'chat'` and/or `TypeError: run() missing ... version`.

- [ ] **Step 3: Minimal implementation**

1. Delete `version: bool` from `run()` and the `if version:` block.
2. Extract chat startup to `_start_chat(*, offline, eco, model)` used by both `run --chat` / `agent == "chat"` and new `@cli.command("chat")`.
3. At the top of `_start_chat`, if `not sys.stdin.isatty()`: print the TTY message and `raise SystemExit(1)`. CliRunner stdin is not a TTY by default, so `test_chat_non_tty_does_not_hang` stays honest. For `test_run_chat_does_not_typeerror`, the monkeypatch replaces `_start_chat` entirely.

```python
def _start_chat(*, offline: bool = False, eco: bool = False, model: str | None = None) -> None:
    import sys

    if not sys.stdin.isatty():
        console.print("[red]zen chat needs a TTY. Use an interactive terminal.[/red]")
        raise SystemExit(1)
    # existing InteractiveChat / MobileChat body moved here
```

- [ ] **Step 4: Run tests**

`pytest tests/cli/test_chat.py tests/cli/test_contract.py -q --no-cov`

Expected: PASS. Manually: `zen run chat` no longer TypeErrors (it should exit 1 in this non-TTY shell with the TTY message).

- [ ] **Step 5: Commit**

```bash
git add tests/cli/test_chat.py zen/cli.py
git commit -m "fix(cli): add zen chat and drop phantom run(version) TypeError."
```

---

### Task 3: `zen run --list` and mocked execute (UC4)

**Files:**
- Create: `tests/cli/test_run.py`
- Modify: `zen/cli.py` only if list/execute error paths are broken
- Possibly mock `zen.core.agent.AgentRegistry` if `list_agents()` still shells `git config`

**Interfaces:**
- Consumes: `show_agents()`, `run_agent()`, `Launcher`
- Produces: `--list` exit 0 with agent names; unknown agent exit 1; execute uses Launcher (mocked)

- [ ] **Step 1: Write the failing tests**

```python
# tests/cli/test_run.py
from __future__ import annotations


def test_run_list_includes_builtin_agents(runner, zen_cli):
    result = runner.invoke(zen_cli, ["run", "--list"])
    assert result.exit_code == 0
    for name in ("troubleshooter", "critic", "assistant"):
        assert name in result.output


def test_run_unknown_agent_exits_one(runner, zen_cli, monkeypatch):
    class Boom(Exception):
        pass

    def fake_load(self, name):
        raise Boom(f"unknown agent {name}")

    monkeypatch.setattr("zen.core.launcher.Launcher.load_agent", fake_load)
    result = runner.invoke(zen_cli, ["run", "nope", "hi", "--no-critique"])
    assert result.exit_code == 1
    assert "failed" in result.output.lower() or "unknown" in result.output.lower()


def test_run_execute_uses_launcher(runner, zen_cli, monkeypatch):
    calls = {}

    class FakeLauncher:
        def __init__(self, debug=False):
            calls["debug"] = debug

        def load_agent(self, name):
            calls["agent"] = name

        def critique_prompt(self, prompt):
            return prompt

        def execute(self, prompt, variables):
            calls["prompt"] = prompt
            return "pong"

    monkeypatch.setattr("zen.cli.Launcher", FakeLauncher)
    result = runner.invoke(
        zen_cli, ["run", "assistant", "ping", "--no-critique"]
    )
    assert result.exit_code == 0
    assert calls["agent"] == "assistant"
    assert calls["prompt"] == "ping"
    assert "pong" in result.output
```

- [ ] **Step 2: Run to verify fail**

`pytest tests/cli/test_run.py -q --no-cov`

Expected: `--list` may already pass; execute/unknown may fail. If `--list` triggers `git config --global`, treat that as a bug: mock or stop the registry from touching global git in `list_agents()` (minimal: skip git side effects when `ZEN_TEST=1` or when not a TTY — prefer **stop calling git in list_agents** if that is what happens).

- [ ] **Step 3: Minimal implementation**

Only what the tests require. If `run_agent` already catches exceptions and exits 1, unknown-agent is green once Launcher raises. If `--list` has git side effects, remove or guard them in the registry path used by list (do not “fix” git globally).

- [ ] **Step 4: Run tests**

`pytest tests/cli/test_run.py -q --no-cov`

Expected: PASS, and `git config --global` does not appear in test output.

- [ ] **Step 5: Commit**

```bash
git add tests/cli/test_run.py zen/cli.py zen/core/agent.py
git commit -m "test(cli): cover zen run --list and mocked agent execute."
```

---

### Task 4: Dex browse use case (UC5)

**Files:**
- Create: `tests/cli/test_dex.py`
- Modify: `zen/cli_v2.py` only if commands ignore cwd / always require repo-root `dex/`

**Interfaces:**
- Consumes: `dex` command, `dex/models.yaml`, `dex/procedures.yaml`
- Produces: exit 0 browse from isolated fixture dir

- [ ] **Step 1: Write the failing test**

```python
# tests/cli/test_dex.py
from __future__ import annotations

from pathlib import Path

import yaml


def test_dex_models_and_procedures_from_cwd(runner, zen_cli, tmp_path, monkeypatch):
    dex = tmp_path / "dex"
    dex.mkdir()
    (dex / "models.yaml").write_text(
        yaml.dump(
            {
                "models": [
                    {"id": "t", "name": "Test", "tier": "common"},
                ]
            }
        ),
        encoding="utf-8",
    )
    (dex / "procedures.yaml").write_text(
        yaml.dump(
            {
                "procedures": [
                    {
                        "id": "zen.chat",
                        "name": "Basic Chat",
                        "tier": "common",
                        "type": "interactive",
                        "stats": {"complexity": 1},
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    models = runner.invoke(zen_cli, ["dex"])
    assert models.exit_code == 0
    procs = runner.invoke(zen_cli, ["dex", "procedures"])
    assert procs.exit_code == 0
    assert "Basic Chat" in procs.output
```

- [ ] **Step 2: Run to verify fail/pass**

`pytest tests/cli/test_dex.py -q --no-cov`

If it already passes against `Path("dex/...")` after chdir, keep the test as a regression lock. If it fails on schema keys (`proc['stats']`), tighten the fixture, not production, unless production crashes on missing keys — then guard with `.get`.

- [ ] **Step 3: Minimal implementation** (only if red)

Prefer making `dex` use `Path.cwd() / "dex"` (already does). Add `.get` for optional fields only if the test proves a crash.

- [ ] **Step 4: Run tests**

`pytest tests/cli/test_dex.py -q --no-cov` → PASS

- [ ] **Step 5: Commit**

```bash
git add tests/cli/test_dex.py zen/cli_v2.py
git commit -m "test(cli): lock zen dex models and procedures browse."
```

---

### Task 5: Stability bench harness

**Files:**
- Create: `zen/cli_bench.py`
- Create: `tests/cli/baselines/usecases.json`
- Create: `tests/cli/baselines/timings.json`
- Create: `tests/cli/test_stability_bench.py`
- Modify: `.gitignore` → `var/cli_bench/`

**Interfaces:**
- Consumes: `usecases.json` schema below; `zen.cli.cli`
- Produces: `run_cases(cli, cases) -> dict[str, {exit, ms}]`; `compare(results, timings, cases) -> list[str]` of failure strings

`tests/cli/baselines/usecases.json`:

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

- [ ] **Step 1: Write failing tests for the harness (pure functions first)**

```python
# tests/cli/test_stability_bench.py
from __future__ import annotations

from zen.cli_bench import compare, load_usecases


def test_usecases_schema_loads():
    data = load_usecases()
    assert data["schema_version"] == 1
    ids = [c["id"] for c in data["cases"]]
    assert "chat_help" in ids
    assert "doctor" in ids


def test_compare_fails_on_exit_and_slow():
    cases = [
        {"id": "help", "expect_exit": [0], "max_ms": 1000},
    ]
    timings = {"help": 50}
    bad_exit = compare({"help": {"exit": 2, "ms": 10}}, timings, cases)
    assert any("exit" in m for m in bad_exit)
    slow = compare({"help": {"exit": 0, "ms": 5000}}, timings, cases)
    assert any("slow" in m or "ms" in m for m in slow)


def test_runner_executes_help(runner, zen_cli):
    from zen.cli_bench import run_cases

    results = run_cases(zen_cli, [{"id": "help", "argv": ["--help"]}])
    assert results["help"]["exit"] == 0
    assert results["help"]["ms"] >= 0
```

- [ ] **Step 2: Run to verify fail**

`pytest tests/cli/test_stability_bench.py -q --no-cov`

Expected: `ImportError: zen.cli_bench`.

- [ ] **Step 3: Implement `zen/cli_bench.py`**

```python
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Mapping, Sequence

from click.testing import CliRunner

ROOT = Path(__file__).resolve().parents[1]
USECASES = ROOT / "tests/cli/baselines/usecases.json"
TIMINGS = ROOT / "tests/cli/baselines/timings.json"


def load_json_file(path: Path, *, what: str) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(
            f"{what} not found at {path}. "
            "Run from a zenOS git checkout, or pass an explicit path. "
            "Installed wheels do not ship these baselines."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def load_usecases(path: Path | None = None) -> dict[str, Any]:
    return load_json_file(path or USECASES, what="CLI bench usecases.json")


def run_cases(cli, cases: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, float | int]]:
    runner = CliRunner()
    out: dict[str, dict[str, float | int]] = {}
    for case in cases:
        t0 = time.perf_counter()
        result = runner.invoke(cli, list(case.get("argv", [])))
        ms = (time.perf_counter() - t0) * 1000
        out[str(case["id"])] = {"exit": int(result.exit_code), "ms": ms}
    return out


def compare(
    results: Mapping[str, Mapping[str, float | int]],
    timings: Mapping[str, float],
    cases: Sequence[Mapping[str, Any]],
    *,
    timings_comparable: bool = False,
) -> list[str]:
    failures: list[str] = []
    for case in cases:
        cid = str(case["id"])
        got = results[cid]
        allowed = list(case["expect_exit"])
        if got["exit"] not in allowed:
            failures.append(f"{cid}: exit {got['exit']} not in {allowed}")
        cap = float(case["max_ms"])
        if timings_comparable and cid in timings:
            limit = max(cap, 2.0 * float(timings[cid]))
        else:
            limit = cap
        if float(got["ms"]) > limit:
            failures.append(f"{cid}: slow {got['ms']:.1f}ms > {limit:.1f}ms")
    return failures
```

`timings_comparable` is True only when `timings.json` exists, its `runner` equals `github-ubuntu-24.04-python-3.14`, and `ZEN_CLI_BENCH_COMPARE_TIMINGS=1`. Otherwise CI uses `max_ms` only.

Seed `timings.json` on ubuntu-24.04 CI after the suite is green; do not commit Cloud Agent laptop numbers as the official p95.

Also add a test that `load_usecases(Path("/tmp/missing.json"))` raises `FileNotFoundError` whose message mentions the path.

Optional: `--write` CLI that appends `var/cli_bench/history.jsonl`. Keep it behind `if __name__ == "__main__"` so pytest does not need it.

- [ ] **Step 4: Run tests**

`pytest tests/cli/test_stability_bench.py tests/cli/test_contract.py tests/cli/test_chat.py -q --no-cov`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add zen/cli_bench.py tests/cli/test_stability_bench.py tests/cli/baselines
git commit -m "test(cli): add use-case stability bench with exit and duration gates."
```

---

### Task 6: Docs match `--help`

**Files:**
- Modify: `README.md` (command examples that say `zen chat` stay; add `zen run --list` where `--list` was at top level)
- Modify: `docs/guides/QUICKSTART.md`
- Modify: `docs/AI_INSTRUCTIONS.md`

**Interfaces:** none beyond the live command tree.

- [ ] **Step 1: Write a failing grep-style test** (optional but keeps docs honest)

```python
# tests/cli/test_docs_commands.py
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_readme_does_not_advertise_zen_help_as_only_help():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "zen --help" in text or "zen help" in text
```

Prefer updating docs without a brittle full-README parser. If you skip this test, manually replace:

- `zen --list` → `zen run --list`
- `zen chat --copilot` → park as non-MVP (do not claim it works until a command exists)
- Keep `zen chat` now that it is real

- [ ] **Step 2: Edit docs**

- [ ] **Step 3: `pytest tests/cli -q --no-cov` PASS**

- [ ] **Step 4: Commit**

```bash
git add README.md docs/guides/QUICKSTART.md docs/AI_INSTRUCTIONS.md tests/cli/test_docs_commands.py
git commit -m "docs(cli): align startup command lists with the live Click group."
```

---

### Task 7: CI runs `tests/cli` (already under `tests/`)

**Files:**
- Modify: `.github/workflows/zenos-ci.yml` only if pytest path excludes `tests/cli` (it should not)

- [ ] **Step 1:** Confirm `pytest` collect includes `tests/cli`.
- [ ] **Step 2:** If CI `pip install -r requirements.txt` misses the package extra, add `pip install -e ".[dev]"` so `zen` imports. That is a real footgun — if CI currently relies on repo-root imports, leave it; if `tests/cli` fails in CI for missing install, this is the fix.
- [ ] **Step 3: Commit only if a file changed**

```bash
git add .github/workflows/zenos-ci.yml
git commit -m "ci: install zenOS editable so CLI contract tests import."
```

---

### Task 8: Parked follow-ups (do not implement in this plan)

Record in `tasks.md` only:

- Extract `dex`/`bench`/`sync`/`arena` from `cli_v2.py` → `zen/cli_dex.py`.
- Rename `setup.py` after a docs grep pass.
- Fix `mcp_setup.py` `` \` `` SyntaxWarning.
- `zen chat --copilot`, `zen analyze`, swarm — new specs.
- Network-marked live OpenRouter smoke.

No code in this task.

---

## Spec coverage check

| Spec requirement | Task |
| --- | --- |
| No-args usage exit 0 | 1 |
| `--version` exit 0 | 1 |
| `zen chat` exists, no TypeError | 2 |
| Non-TTY chat does not hang | 2 |
| doctor still works | 1/5 (argv) + existing env-doctor tests |
| `run --list` / mocked execute | 3 |
| dex browse | 4 |
| stability bench schema + compare | 5 |
| docs | 6 |
| single entrypoint | global constraint |
| no cli_v2 growth | global constraint |
| setup.py rename | Task 8 parked |

## Placeholder scan

No TBD/TODO in task bodies. Parked work is explicit in Task 8.

## Type consistency

- `run_cases(cli, cases) -> dict[str, dict[str, float | int]]` with keys `exit`, `ms`.
- `compare(...) -> list[str]`.
- `_start_chat(*, offline, eco, model)` keyword-only.
