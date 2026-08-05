#!/usr/bin/env python3
"""
zenOS packaging shim and unified environment bootstrap.

- PEP 517 / setuptools commands: ``setuptools.setup()`` only (no zen imports).
- Developer bootstrap: ``python setup.py`` / ``python setup.py --unattended`` etc.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent

# Commands setuptools/distutils may pass as argv[1] during packaging.
_SETUPTOOLS_COMMANDS = frozenset(
    {
        "bdist",
        "bdist_dumb",
        "bdist_egg",
        "bdist_msi",
        "bdist_rpm",
        "bdist_wheel",
        "bdist_wininst",
        "build",
        "build_ext",
        "build_py",
        "check",
        "clean",
        "develop",
        "dist_info",
        "editable_wheel",
        "egg_info",
        "install",
        "install_egg_info",
        "install_lib",
        "install_scripts",
        "rotate",
        "saveopts",
        "sdist",
        "setopt",
        "upload",
        "upload_docs",
        "wheel",
    }
)


def _should_run_bootstrap() -> bool:
    """True for unified setup invocations, not pip/setuptools packaging hooks."""
    if __name__ != "__main__":
        return False
    if len(sys.argv) > 1 and sys.argv[1] in _SETUPTOOLS_COMMANDS:
        return False
    return "setup.py" in Path(sys.argv[0]).name


if _should_run_bootstrap():
    sys.path.insert(0, str(_ROOT))
    from zen.setup.unified_setup import main

    main()
else:
    from setuptools import setup

    setup()
