#!/usr/bin/env python3
"""Interactive, idempotent .env wizard for zenOS.

Detects an existing .env, prompts only for missing values, validates
GITHUB_TOKEN via GET /user, and refuses to overwrite keys already set.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from zen.auth.wizard import main

if __name__ == "__main__":
    raise SystemExit(main())
