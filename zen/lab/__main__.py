"""python -m zen.lab — hosted security-check HTTP server."""

from __future__ import annotations

import os

from zen.lab.app import serve


def main() -> None:
    host = os.environ.get("ZEN_LAB_HOST", "0.0.0.0")
    port = int(os.environ.get("PORT") or os.environ.get("ZEN_LAB_PORT") or "8080")
    serve(host=host, port=port)


if __name__ == "__main__":
    main()
