#!/usr/bin/env python3
"""zenOS Unified Setup Script

The master setup script that combines the best procedures from promptOS and mcp-config
to create a bulletproof, environment-agnostic development environment.

Usage:
    python setup.py                    # Full setup
    python setup.py --unattended       # Automated setup
    python setup.py --validate-only    # Just validate environment
    python setup.py --phase git_setup  # Start from specific phase
"""

import sys
from pathlib import Path

# Add zenOS to path
sys.path.insert(0, str(Path(__file__).parent))

from zen.setup.unified_setup import main

if __name__ == "__main__":
    main()
