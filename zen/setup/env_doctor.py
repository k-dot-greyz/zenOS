"""zenOS environment doctor — Python floor, deps, CLI wiring, landmines."""

from __future__ import annotations

import importlib
import json
import subprocess
import sys
from dataclasses import dataclass, field
from importlib.metadata import PackageNotFoundError, version as pkg_version
from pathlib import Path
from typing import Iterable, Optional, Sequence

MIN_PYTHON = (3, 14)

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
        )
    return CheckResult(
        name="python",
        ok=True,
        severity="ok",
        message=f"Python {rendered} OK (floor 3.14)",
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
        )
    return CheckResult(
        name="setup_py",
        ok=True,
        severity="ok",
        message="Root setup.py looks like a packaging script",
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
            )
        return CheckResult(
            name="cli_entry",
            ok=True,
            severity="ok",
            message="zen.cli:main is callable (console script entrypoint)",
        )
    except Exception as exc:
        return CheckResult(
            name="cli_entry",
            ok=False,
            severity="fail",
            message=f"zen.cli:main is missing or broken: {exc}",
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
            )
        return CheckResult(
            name="cli_doctor",
            ok=True,
            severity="ok",
            message="zen doctor and zen env-doctor are registered",
        )
    except Exception as exc:
        return CheckResult(
            name="cli_doctor",
            ok=False,
            severity="fail",
            message=f"Could not inspect CLI commands: {exc}",
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
                )
            )
        except Exception as exc:
            results.append(
                CheckResult(
                    name=f"dep:{dist_name}",
                    ok=False,
                    severity="fail",
                    message=f"{dist_name} ({module_name}) failed to import: {exc}",
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
        )
    if proc.returncode != 0:
        return CheckResult(
            name="outdated",
            ok=True,
            severity="warn",
            message=f"pip list --outdated failed: {proc.stderr.strip() or proc.stdout.strip()}",
        )
    try:
        rows = json.loads(proc.stdout or "[]")
    except json.JSONDecodeError:
        return CheckResult(
            name="outdated",
            ok=True,
            severity="warn",
            message="pip list --outdated returned non-JSON output",
        )
    if not rows:
        return CheckResult(
            name="outdated",
            ok=True,
            severity="ok",
            message="No outdated pip packages reported",
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
    )


def check_env_file(root: Optional[Path] = None) -> CheckResult:
    repo = Path(root) if root is not None else Path.cwd()
    if (repo / ".env").exists():
        return CheckResult(
            name="dotenv",
            ok=True,
            severity="ok",
            message="Environment file found (.env)",
        )
    if (repo / "env.example").exists():
        return CheckResult(
            name="dotenv",
            ok=True,
            severity="warn",
            message="No .env yet — copy env.example to .env and add keys",
        )
    return CheckResult(
        name="dotenv",
        ok=False,
        severity="fail",
        message="Neither .env nor env.example found",
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
            )
        )
    else:
        results.append(
            CheckResult(
                name="dex_models",
                ok=True,
                severity="warn",
                message="Model Dex missing (dex/models.yaml) — run zen sync",
            )
        )
    if procedures.exists():
        results.append(
            CheckResult(
                name="dex_procedures",
                ok=True,
                severity="ok",
                message="Procedure Dex found (dex/procedures.yaml)",
            )
        )
    else:
        results.append(
            CheckResult(
                name="dex_procedures",
                ok=True,
                severity="warn",
                message="Procedure Dex missing (dex/procedures.yaml)",
            )
        )
    return results


def check_pyproject_python_floor(root: Optional[Path] = None) -> CheckResult:
    repo = Path(root) if root is not None else Path.cwd()
    pyproject = repo / "pyproject.toml"
    if not pyproject.exists():
        return CheckResult(
            name="pyproject",
            ok=False,
            severity="fail",
            message="pyproject.toml missing",
        )
    text = pyproject.read_text(encoding="utf-8")
    if 'requires-python = ">=3.14"' not in text:
        return CheckResult(
            name="pyproject",
            ok=False,
            severity="fail",
            message='pyproject.toml must set requires-python = ">=3.14"',
        )
    return CheckResult(
        name="pyproject",
        ok=True,
        severity="ok",
        message="pyproject.toml requires-python >=3.14",
    )


def run_env_doctor(
    *,
    root: Optional[Path] = None,
    version_info: Optional[Sequence[int]] = None,
    include_outdated: bool = True,
) -> DoctorReport:
    repo = Path(root) if root is not None else Path.cwd()
    report = DoctorReport()
    report.checks.append(check_python(version_info=version_info))
    report.checks.append(check_pyproject_python_floor(root=repo))
    report.checks.append(check_cli_entrypoint())
    report.checks.append(check_cli_doctor_commands())
    report.checks.append(check_setup_py_landmine(root=repo))
    report.checks.append(check_env_file(root=repo))
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
