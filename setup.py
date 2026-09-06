#!/usr/bin/env python3
"""
zenOS packaging shim and unified environment bootstrap.

This file wears two hats:

- PEP 517 build backend hook: when pip/setuptools exec this file to build/
  install the package (e.g. ``pip install -e .``), it must stay a plain
  ``setuptools.setup()`` call and must NOT import ``zen`` — the package's own
  runtime deps (pyyaml, click, ...) aren't guaranteed to exist yet at that
  point, and doing so breaks editable installs with a confusing
  ``ModuleNotFoundError`` from deep inside the build backend. This is exactly
  the landmine `zen.setup.env_doctor.check_setup_py_landmine` detects and
  warns about — this fixes it in place rather than renaming the file, so the
  warning should stop firing once this ships.
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


# Keep in sync with the argparse surface in zen.setup.unified_setup.main().
_WIZARD_BOOL_FLAGS = {"-h", "--help", "--unattended", "--validate-only"}
_WIZARD_VALUE_FLAGS = {"--path", "--phase"}  # take a value: either `--flag value` or `--flag=value`


def _user_invoked_setup_script() -> bool:
    """True only for ``python setup.py [wizard flags]``.

    NOT true for a pip/setuptools build-backend invocation — those also run
    with ``__name__ == "__main__"`` and ``sys.argv[0] == "setup.py"`` (e.g.
    ``python setup.py egg_info``, ``sdist``, ``bdist_wheel``, or pip's legacy
    build fallback), so checking those two alone reintroduces the exact
    failure this shim exists to avoid: importing ``zen`` before its deps are
    installed. A dash-prefixed first arg alone isn't enough either —
    setuptools/distutils accept their own dash-prefixed global options
    (``--quiet``, ``--help-commands``, ...), and ``python setup.py --quiet
    egg_info`` would otherwise be misrouted to the wizard's argparse, which
    doesn't know ``--quiet`` and errors out instead of running the build.
    Match only this file's actual wizard flags — including ``--path``/
    ``--phase``'s value, whether given as a separate arg or ``--flag=value``.
    """
    if __name__ != "__main__" or Path(sys.argv[0]).name != "setup.py":
        return False
    args = iter(sys.argv[1:])
    for arg in args:
        name = arg.split("=", 1)[0]
        if name in _WIZARD_BOOL_FLAGS:
            continue
        if name in _WIZARD_VALUE_FLAGS:
            if "=" not in arg and next(args, None) is None:
                return False  # `--phase` with no value at all — not a valid wizard call
            continue
        return False
    return True


if _user_invoked_setup_script():
    sys.path.insert(0, str(_ROOT))
    from zen.setup.unified_setup import main

    main()
else:
    from setuptools import setup

    setup()
