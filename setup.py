#!/usr/bin/env python3
"""
zenOS packaging shim and unified environment bootstrap.

- PEP 517 builds: setuptools only (no zen imports at build time).
- Developer bootstrap: ``python setup.py`` / ``python setup.py --unattended`` etc.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent


def _user_invoked_setup_script() -> bool:
    """True when a human runs ``python setup.py ...``, not during pip/setuptools hooks."""
    return __name__ == "__main__" and "setup.py" in Path(sys.argv[0]).name


if _user_invoked_setup_script():
    sys.path.insert(0, str(_ROOT))
    from zen.setup.unified_setup import main

    main()
else:
    from setuptools import setup

    setup()
