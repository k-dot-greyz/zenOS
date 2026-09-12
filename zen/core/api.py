"""Compatibility shim for `python -m zen.core.api`.

Historical docs and Termux guides call this module. The HTTP app lives in
`zen.api`; this module forwards to the same server entrypoint.
"""

from zen.api.serve import main

if __name__ == "__main__":
    raise SystemExit(main())
