from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Mapping, Sequence

from click.testing import CliRunner

ROOT = Path(__file__).resolve().parents[1]
USECASES = ROOT / "tests/cli/baselines/usecases.json"
TIMINGS = ROOT / "tests/cli/baselines/timings.json"
HISTORY = ROOT / "var/cli_bench/history.jsonl"
CI_RUNNER = "github-ubuntu-24.04-python-3.14"


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


def load_timings(path: Path | None = None) -> dict[str, Any]:
    return load_json_file(path or TIMINGS, what="CLI bench timings.json")


def timings_are_comparable(timings: Mapping[str, Any] | None = None) -> bool:
    import os

    if os.environ.get("ZEN_CLI_BENCH_COMPARE_TIMINGS") != "1":
        return False
    data = timings if timings is not None else load_timings()
    return str(data.get("runner", "")) == CI_RUNNER


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


def append_history(results: Mapping[str, Mapping[str, float | int]]) -> Path:
    import datetime
    import sys

    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": datetime.datetime.now(datetime.UTC).isoformat(),
        "python": sys.version.split()[0],
        "cases": {cid: {"exit": got["exit"], "ms": got["ms"]} for cid, got in results.items()},
    }
    with HISTORY.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")
    return HISTORY


if __name__ == "__main__":
    import argparse

    from zen.cli import cli

    parser = argparse.ArgumentParser(description="zenOS CLI stability bench")
    parser.add_argument(
        "--write", action="store_true", help="Append results to var/cli_bench/history.jsonl"
    )
    args = parser.parse_args()
    data = load_usecases()
    results = run_cases(cli, data["cases"])
    timing_file = load_timings() if TIMINGS.is_file() else {"p95_ms": {}}
    p95 = {k: float(v) for k, v in dict(timing_file.get("p95_ms") or {}).items()}
    failures = compare(
        results,
        p95,
        data["cases"],
        timings_comparable=timings_are_comparable(timing_file),
    )
    if args.write:
        append_history(results)
    for cid, got in results.items():
        print(f"{cid}: exit={got['exit']} ms={got['ms']:.1f}")
    if failures:
        print("FAIL")
        for msg in failures:
            print(msg)
        raise SystemExit(1)
    print("OK")
