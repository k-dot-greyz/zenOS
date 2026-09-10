"""zenOS environment doctor — Python floor, deps, CLI wiring, landmines."""

from __future__ import annotations

import importlib
import json
import os
import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass, field
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as pkg_version
from pathlib import Path
from typing import Iterable, Optional, Sequence

from zen.runtime import MIN_PYTHON

CORE_IMPORTS: tuple[tuple[str, str], ...] = (
    ("click", "click"),
    ("rich", "rich"),
    ("yaml", "pyyaml"),
    ("jinja2", "jinja2"),
    ("pydantic", "pydantic"),
    ("aiohttp", "aiohttp"),
    ("httpx", "httpx"),
    ("dotenv", "python-dotenv"),
    ("prompt_toolkit", "prompt-toolkit"),
    ("bs4", "beautifulsoup4"),
    ("schedule", "schedule"),
    ("aiofiles", "aiofiles"),
    ("psutil", "psutil"),
)


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    severity: str
    message: str
    family: str = "runtime"
    repairable: bool = True


@dataclass
class DoctorReport:
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def has_failures(self) -> bool:
        return any(c.severity == "fail" for c in self.checks)

    @property
    def has_warnings(self) -> bool:
        return any(c.severity == "warn" for c in self.checks)


def _version_tuple(info: Sequence[int]) -> tuple[int, int, int]:
    major = int(info[0])
    minor = int(info[1]) if len(info) > 1 else 0
    micro = int(info[2]) if len(info) > 2 else 0
    return major, minor, micro


def check_python(version_info: Optional[Sequence[int]] = None) -> CheckResult:
    """Fail hard on anything below Python 3.14."""
    major, minor, micro = _version_tuple(version_info or sys.version_info)
    rendered = f"{major}.{minor}.{micro}"
    if (major, minor) < MIN_PYTHON:
        return CheckResult(
            name="python",
            ok=False,
            severity="fail",
            message=(
                f"Python {major}.{minor} detected ({rendered}). "
                "Python 3.14+ is required — older runtimes are EOL for zenOS."
            ),
            family="runtime",
            repairable=False,
        )
    return CheckResult(
        name="python",
        ok=True,
        severity="ok",
        message=f"Python {rendered} OK (floor 3.14)",
        family="runtime",
        repairable=False,
    )


def check_setup_py_landmine(root: Optional[Path] = None) -> CheckResult:
    """Root setup.py that is not a setuptools script breaks `pip install -e .`."""
    repo = Path(root) if root is not None else Path.cwd()
    setup_py = repo / "setup.py"
    pyproject = repo / "pyproject.toml"
    if not setup_py.exists():
        return CheckResult(
            name="setup_py",
            ok=True,
            severity="ok",
            message="No root setup.py landmine",
            family="git_state",
            repairable=True,
        )
    text = setup_py.read_text(encoding="utf-8", errors="replace")
    looks_like_setuptools = "setuptools" in text or "from setuptools" in text or "setup(" in text
    if pyproject.exists() and not looks_like_setuptools:
        return CheckResult(
            name="setup_py",
            ok=False,
            severity="warn",
            message=(
                "Root setup.py is a zenOS installer script, not setuptools. "
                "pip/build backends treat that filename as a package script — "
                "rename it (e.g. zenos_setup.py) before the next CLI fix pass."
            ),
            family="git_state",
            repairable=True,
        )
    return CheckResult(
        name="setup_py",
        ok=True,
        severity="ok",
        message="Root setup.py looks like a packaging script",
        family="git_state",
        repairable=True,
    )


def check_cli_entrypoint() -> CheckResult:
    try:
        from zen.cli import main as cli_main

        if not callable(cli_main):
            return CheckResult(
                name="cli_entry",
                ok=False,
                severity="fail",
                message="zen.cli:main exists but is not callable",
                family="runtime",
                repairable=False,
            )
        return CheckResult(
            name="cli_entry",
            ok=True,
            severity="ok",
            message="zen.cli:main is callable (console script entrypoint)",
            family="runtime",
            repairable=False,
        )
    except Exception as exc:
        return CheckResult(
            name="cli_entry",
            ok=False,
            severity="fail",
            message=f"zen.cli:main is missing or broken: {exc}",
            family="runtime",
            repairable=False,
        )


def check_cli_doctor_commands() -> CheckResult:
    try:
        from zen.cli import cli

        missing = [name for name in ("doctor", "env-doctor") if name not in cli.commands]
        if missing:
            return CheckResult(
                name="cli_doctor",
                ok=False,
                severity="fail",
                message=f"Main CLI missing commands: {', '.join(missing)}",
                family="runtime",
                repairable=False,
            )
        return CheckResult(
            name="cli_doctor",
            ok=True,
            severity="ok",
            message="zen doctor and zen env-doctor are registered",
            family="runtime",
            repairable=False,
        )
    except Exception as exc:
        return CheckResult(
            name="cli_doctor",
            ok=False,
            severity="fail",
            message=f"Could not inspect CLI commands: {exc}",
            family="runtime",
            repairable=False,
        )


def check_core_imports(pairs: Iterable[tuple[str, str]] = CORE_IMPORTS) -> list[CheckResult]:
    results: list[CheckResult] = []
    for module_name, dist_name in pairs:
        try:
            importlib.import_module(module_name)
            try:
                installed = pkg_version(dist_name)
            except PackageNotFoundError:
                installed = "unknown"
            results.append(
                CheckResult(
                    name=f"dep:{dist_name}",
                    ok=True,
                    severity="ok",
                    message=f"{dist_name} importable ({installed})",
                    family="package_manager",
                    repairable=False,
                )
            )
        except Exception as exc:
            results.append(
                CheckResult(
                    name=f"dep:{dist_name}",
                    ok=False,
                    severity="fail",
                    message=f"{dist_name} ({module_name}) failed to import: {exc}",
                    family="package_manager",
                    repairable=False,
                )
            )
    return results


def check_outdated_packages(python_executable: Optional[str] = None) -> CheckResult:
    exe = python_executable or sys.executable
    try:
        proc = subprocess.run(
            [exe, "-m", "pip", "list", "--outdated", "--format=json"],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        return CheckResult(
            name="outdated",
            ok=True,
            severity="warn",
            message=f"Could not scan outdated packages: {exc}",
            family="package_manager",
            repairable=True,
        )
    if proc.returncode != 0:
        return CheckResult(
            name="outdated",
            ok=True,
            severity="warn",
            message=f"pip list --outdated failed: {proc.stderr.strip() or proc.stdout.strip()}",
            family="package_manager",
            repairable=True,
        )
    try:
        rows = json.loads(proc.stdout or "[]")
    except json.JSONDecodeError:
        return CheckResult(
            name="outdated",
            ok=True,
            severity="warn",
            message="pip list --outdated returned non-JSON output",
            family="package_manager",
            repairable=True,
        )
    if not rows:
        return CheckResult(
            name="outdated",
            ok=True,
            severity="ok",
            message="No outdated pip packages reported",
            family="package_manager",
            repairable=True,
        )
    names = ", ".join(
        f"{row.get('name')} {row.get('version')}->{row.get('latest_version')}" for row in rows[:20]
    )
    extra = "" if len(rows) <= 20 else f" (+{len(rows) - 20} more)"
    return CheckResult(
        name="outdated",
        ok=True,
        severity="warn",
        message=f"{len(rows)} outdated package(s): {names}{extra}",
        family="package_manager",
        repairable=True,
    )


def check_env_file(root: Optional[Path] = None) -> CheckResult:
    repo = Path(root) if root is not None else Path.cwd()
    if (repo / ".env").exists():
        return CheckResult(
            name="dotenv",
            ok=True,
            severity="ok",
            message="Environment file found (.env)",
            family="secrets_presence",
            repairable=True,
        )
    if (repo / "env.example").exists():
        return CheckResult(
            name="dotenv",
            ok=True,
            severity="warn",
            message="No .env yet — copy env.example to .env and add keys",
            family="secrets_presence",
            repairable=True,
        )
    return CheckResult(
        name="dotenv",
        ok=False,
        severity="fail",
        message="Neither .env nor env.example found",
        family="secrets_presence",
        repairable=True,
    )


def check_dex_files(root: Optional[Path] = None) -> list[CheckResult]:
    repo = Path(root) if root is not None else Path.cwd()
    results: list[CheckResult] = []
    models = repo / "dex" / "models.yaml"
    procedures = repo / "dex" / "procedures.yaml"
    if models.exists():
        results.append(
            CheckResult(
                name="dex_models",
                ok=True,
                severity="ok",
                message="Model Dex found (dex/models.yaml)",
                family="runtime",
                repairable=True,
            )
        )
    else:
        results.append(
            CheckResult(
                name="dex_models",
                ok=True,
                severity="warn",
                message="Model Dex missing (dex/models.yaml) — run zen sync",
                family="runtime",
                repairable=True,
            )
        )
    if procedures.exists():
        results.append(
            CheckResult(
                name="dex_procedures",
                ok=True,
                severity="ok",
                message="Procedure Dex found (dex/procedures.yaml)",
                family="runtime",
                repairable=True,
            )
        )
    else:
        results.append(
            CheckResult(
                name="dex_procedures",
                ok=True,
                severity="warn",
                message="Procedure Dex missing (dex/procedures.yaml)",
                family="runtime",
                repairable=True,
            )
        )
    return results


def requires_python_meets_floor(spec: str, floor: tuple[int, int] = MIN_PYTHON) -> bool:
    """True if requires-python's lower bound is at least `floor`.

    Accepts compound specs such as ``>=3.14,<4``. Does not require exact
    quoting or spacing from the TOML source.
    """
    compact = spec.replace(" ", "")
    match = re.search(r">=(\d+)\.(\d+)", compact)
    if match:
        return (int(match.group(1)), int(match.group(2))) >= floor
    match = re.search(r"==(\d+)\.(\d+)", compact)
    if match:
        return (int(match.group(1)), int(match.group(2))) >= floor
    return False


def check_pyproject_python_floor(root: Optional[Path] = None) -> CheckResult:
    repo = Path(root) if root is not None else Path.cwd()
    pyproject = repo / "pyproject.toml"
    if not pyproject.exists():
        return CheckResult(
            name="pyproject",
            ok=False,
            severity="fail",
            message="pyproject.toml missing",
            family="runtime",
            repairable=False,
        )
    try:
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        spec = str(data.get("project", {}).get("requires-python", "")).strip()
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return CheckResult(
            name="pyproject",
            ok=False,
            severity="fail",
            message=f"pyproject.toml unreadable: {exc}",
            family="runtime",
            repairable=False,
        )
    if not spec or not requires_python_meets_floor(spec):
        floor = f"{MIN_PYTHON[0]}.{MIN_PYTHON[1]}"
        return CheckResult(
            name="pyproject",
            ok=False,
            severity="fail",
            message=f"pyproject.toml requires-python must be >={floor} (got {spec!r})",
            family="runtime",
            repairable=False,
        )
    return CheckResult(
        name="pyproject",
        ok=True,
        severity="ok",
        message=f"pyproject.toml requires-python {spec}",
        family="runtime",
        repairable=False,
    )


LOCKFILE_CANDIDATES = ("requirements.txt", "uv.lock", "poetry.lock", "Pipfile.lock")
REQUIRED_SECRET_NAMES = ("OPENROUTER_API_KEY",)
OPTIONAL_SECRET_NAMES = ("GITHUB_TOKEN",)


def check_lockfile(root: Optional[Path] = None) -> CheckResult:
    repo = Path(root) if root is not None else Path.cwd()
    found = [name for name in LOCKFILE_CANDIDATES if (repo / name).exists()]
    if found:
        return CheckResult(
            name="lockfile",
            ok=True,
            severity="ok",
            message=f"Lock/pin file present: {', '.join(found)}",
            family="lockfile",
            repairable=True,
        )
    return CheckResult(
        name="lockfile",
        ok=False,
        severity="fail",
        message="No requirements.txt / uv.lock / poetry.lock / Pipfile.lock",
        family="lockfile",
        repairable=True,
    )


def _secret_is_set(name: str) -> bool:
    value = os.environ.get(name, "").strip()
    if not value:
        return False
    return "your-" not in value.lower() and value.lower() not in {"changeme", "todo", "xxx"}


def check_secrets_presence(root: Optional[Path] = None) -> CheckResult:
    """Presence-only: names of unset keys, never values."""
    missing_required = [name for name in REQUIRED_SECRET_NAMES if not _secret_is_set(name)]
    missing_optional = [name for name in OPTIONAL_SECRET_NAMES if not _secret_is_set(name)]
    if missing_required:
        return CheckResult(
            name="secrets",
            ok=True,
            severity="warn",
            message="Unset env keys (names only): " + ", ".join(missing_required),
            family="secrets_presence",
            repairable=True,
        )
    if missing_optional:
        return CheckResult(
            name="secrets",
            ok=True,
            severity="warn",
            message="Optional env keys unset (names only): " + ", ".join(missing_optional),
            family="secrets_presence",
            repairable=True,
        )
    return CheckResult(
        name="secrets",
        ok=True,
        severity="ok",
        message="Required env keys present (values not logged)",
        family="secrets_presence",
        repairable=True,
    )


def check_git_state(root: Optional[Path] = None) -> CheckResult:
    repo = Path(root) if root is not None else Path.cwd()
    try:
        inside = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        return CheckResult(
            name="git_state",
            ok=True,
            severity="warn",
            message=f"git not inspectable: {exc}",
            family="git_state",
            repairable=True,
        )
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        return CheckResult(
            name="git_state",
            ok=False,
            severity="fail",
            message="Not a git work tree",
            family="git_state",
            repairable=True,
        )
    dirty = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain"],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    if dirty.returncode != 0:
        return CheckResult(
            name="git_state",
            ok=True,
            severity="warn",
            message="git status failed",
            family="git_state",
            repairable=True,
        )
    if dirty.stdout.strip():
        return CheckResult(
            name="git_state",
            ok=True,
            severity="warn",
            message="Working tree has uncommitted changes",
            family="git_state",
            repairable=True,
        )
    return CheckResult(
        name="git_state",
        ok=True,
        severity="ok",
        message="Git work tree clean",
        family="git_state",
        repairable=True,
    )


def run_env_doctor(
    *,
    root: Optional[Path] = None,
    version_info: Optional[Sequence[int]] = None,
    include_outdated: bool = False,
) -> DoctorReport:
    repo = Path(root) if root is not None else Path.cwd()
    report = DoctorReport()
    report.checks.append(check_python(version_info=version_info))
    report.checks.append(check_pyproject_python_floor(root=repo))
    report.checks.append(check_cli_entrypoint())
    report.checks.append(check_cli_doctor_commands())
    report.checks.append(check_setup_py_landmine(root=repo))
    report.checks.append(check_env_file(root=repo))
    report.checks.append(check_secrets_presence(root=repo))
    report.checks.append(check_lockfile(root=repo))
    report.checks.append(check_git_state(root=repo))
    report.checks.extend(check_dex_files(root=repo))
    report.checks.extend(check_core_imports())
    if include_outdated:
        report.checks.append(check_outdated_packages())
    return report


def format_report(report: DoctorReport, *, ai_mode: bool = False) -> str:
    lines: list[str] = []
    if ai_mode:
        lines.append("zenOS env-doctor AI mode")
    else:
        lines.append("")
        lines.append("zenOS Environment Diagnostics")
        lines.append("")
    marks = {"ok": "[OK]", "warn": "[WARN]", "fail": "[FAIL]", "info": "[INFO]"}
    for check in report.checks:
        mark = marks.get(check.severity, "[?]")
        lines.append(f"{mark} {check.message}")
    lines.append("")
    if report.has_failures:
        lines.append("Result: FAIL — fix the [FAIL] items before treating this env as healthy.")
    elif report.has_warnings:
        lines.append("Result: WARN — runtime is usable, but stale/deprecated items need a look.")
    else:
        lines.append("Result: OK — Python floor, CLI entrypoint, and core deps look current.")
    return "\n".join(lines) + "\n"
