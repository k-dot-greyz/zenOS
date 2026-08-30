"""Process-wide runtime floor for zenOS.

Python 3.14+ and the current stable core dependencies are required at
startup. Older interpreters are a hard fail, not a warning.
"""

from __future__ import annotations

import importlib
import sys
from typing import Optional, Sequence, TextIO

MIN_PYTHON = (3, 14)

REQUIRED_MODULES: tuple[str, ...] = (
    "click",
    "rich",
    "yaml",
    "jinja2",
    "pydantic",
    "aiohttp",
    "httpx",
    "dotenv",
    "prompt_toolkit",
    "bs4",
    "schedule",
    "aiofiles",
    "psutil",
)


def python_too_old(version_info: Optional[Sequence[int]] = None) -> bool:
    info = version_info or sys.version_info
    return (int(info[0]), int(info[1])) < MIN_PYTHON


def require_python(
    version_info: Optional[Sequence[int]] = None,
    *,
    stream: Optional[TextIO] = None,
) -> None:
    """Exit 1 if the interpreter is below Python 3.14."""
    info = version_info or sys.version_info
    major, minor = int(info[0]), int(info[1])
    micro = int(info[2]) if len(info) > 2 else 0
    if python_too_old(info):
        floor = f"{MIN_PYTHON[0]}.{MIN_PYTHON[1]}"
        print(
            f"zenOS requires Python {floor}+, got {major}.{minor}.{micro}. "
            "Install CPython 3.14+ (uv python install 3.14) and recreate the venv.",
            file=stream or sys.stderr,
        )
        raise SystemExit(1)


def require_runtime(
    version_info: Optional[Sequence[int]] = None,
    *,
    stream: Optional[TextIO] = None,
) -> None:
    """Exit 1 if Python is below 3.14 or a required package cannot be imported.

    This is an importability gate, not a version/outdated-package check.
    Use `zen doctor --outdated` for pip outdated reports.
    """
    out = stream or sys.stderr
    require_python(version_info=version_info, stream=out)
    missing: list[str] = []
    for module_name in REQUIRED_MODULES:
        try:
            importlib.import_module(module_name)
        except Exception:
            missing.append(module_name)
    if missing:
        print(
            "zenOS missing required packages: "
            + ", ".join(missing)
            + ". Install current stables with: python3.14 -m pip install -e .",
            file=out,
        )
        raise SystemExit(1)
