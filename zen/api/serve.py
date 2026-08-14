"""Run the zenOS REST API (uvicorn)."""

from __future__ import annotations

import argparse
import os
import sys
from typing import Optional, Sequence

from zen.api.auth import require_token_for_bind

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8080


def build_parser() -> argparse.ArgumentParser:
    """CLI parser for `zen serve` / `python -m zen.api`."""
    parser = argparse.ArgumentParser(
        prog="zen serve",
        description="Run the zenOS REST API",
    )
    parser.add_argument(
        "--host",
        default=os.getenv("ZEN_API_HOST", DEFAULT_HOST),
        help=f"Bind host (default {DEFAULT_HOST}; non-loopback requires ZEN_API_TOKEN)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("ZEN_API_PORT", str(DEFAULT_PORT))),
        help=f"Bind port (default {DEFAULT_PORT})",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Reload on code changes (development)",
    )
    return parser


def run_server(host: str, port: int, reload: bool = False) -> None:
    """Validate bind policy and start uvicorn."""
    token = os.getenv("ZEN_API_TOKEN")
    require_token_for_bind(host, token)
    import uvicorn

    uvicorn.run(
        "zen.api.app:create_app",
        factory=True,
        host=host,
        port=port,
        reload=reload,
    )


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Parse args and serve. Returns a process exit code."""
    args = build_parser().parse_args(argv)
    try:
        run_server(args.host, args.port, args.reload)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
