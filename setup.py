#!/usr/bin/env python3
"""
zenOS packaging shim and unified environment bootstrap.

This file wears two hats:

- PEP 517 build backend hook: when pip/setuptools exec this file to build/
  install the package (e.g. ``pip install -e .``), it must stay a plain
  ``setuptools.setup()`` call and must NOT import ``zen`` — the package's own
  runtime deps (pyyaml, click, ...) aren't guaranteed to exist yet at that
  point, and doing so breaks editable installs with a confusing
  ``ModuleNotFoundError`` from deep inside the build backend.
- Developer bootstrap: when a human runs ``python setup.py`` directly, it
  drives the unified environment setup wizard.
    python setup.py                    # Full setup
    python setup.py --unattended       # Automated setup
    python setup.py --validate-only    # Just validate environment
    python setup.py --phase git_setup  # Start from specific phase
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent


def _user_invoked_setup_script() -> bool:
    """True when a human runs ``python setup.py ...``, not during a pip/setuptools build hook."""
    return __name__ == "__main__" and Path(sys.argv[0]).name == "setup.py"


if _user_invoked_setup_script():
    sys.path.insert(0, str(_ROOT))
    from zen.setup.unified_setup import main

    main()
else:
    from setuptools import setup

    setup()
