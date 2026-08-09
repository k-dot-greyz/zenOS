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
    """True only for ``python setup.py [wizard flags]``.

    NOT true for a pip/setuptools build-backend invocation — those also run
    with ``__name__ == "__main__"`` and ``sys.argv[0] == "setup.py"`` (e.g.
    ``python setup.py egg_info``, ``sdist``, ``bdist_wheel``, or pip's legacy
    build fallback), so checking those two alone reintroduces the exact
    failure this shim exists to avoid: importing ``zen`` before its deps are
    installed. Every wizard flag (``--unattended``, ``--validate-only``,
    ``--phase <x>``, ``-h``/``--help``) is dash-prefixed; every setuptools/
    distutils command (``sdist``, ``egg_info``, ``install``, ...) is a bare
    word. That's the discriminator — no args, or the first arg is a flag.
    """
    if __name__ != "__main__" or Path(sys.argv[0]).name != "setup.py":
        return False
    args = sys.argv[1:]
    return not args or args[0].startswith("-")


if _user_invoked_setup_script():
    sys.path.insert(0, str(_ROOT))
    from zen.setup.unified_setup import main

    main()
else:
    from setuptools import setup

    setup()
