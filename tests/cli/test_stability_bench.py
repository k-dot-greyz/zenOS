from __future__ import annotations

from pathlib import Path

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


def test_load_usecases_missing_path_mentions_path():
    from zen.cli_bench import load_usecases as load

    missing = Path("/tmp/zenos-missing-usecases.json")
    try:
        load(missing)
    except FileNotFoundError as exc:
        assert str(missing) in str(exc)
    else:
        raise AssertionError("expected FileNotFoundError")


def test_usecase_suite_exit_and_max_ms(zen_cli):
    from zen.cli_bench import compare, run_cases

    data = load_usecases()
    results = run_cases(zen_cli, data["cases"])
    failures = compare(results, {}, data["cases"])
    assert failures == []
