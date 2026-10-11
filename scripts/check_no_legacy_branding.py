#!/usr/bin/env python3
"""Compatibility shim. Canonical file lives under dex/ops/scripts/python/."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parents[1] / "dex/ops/scripts/python/check_no_legacy_branding.py"
if not TARGET.is_file():
    sys.exit(f"canonical script missing: {TARGET}")
sys.argv[0] = str(TARGET)
runpy.run_path(str(TARGET), run_name="__main__")
