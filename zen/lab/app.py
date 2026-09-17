"""HTTP surface for the dockerized zenOS security lab.

Never serializes credential values. Intended for a hosted cheeky self-check:
GET /health, GET /auth/status, GET /scan.
"""

from __future__ import annotations

import json

from zen import __version__
from zen.auth.credentials import collect_auth_status
from zen.auth.secret_scan import scan_paths
from zen.setup.env_doctor import run_env_doctor

JSON_HEADERS = {"Content-Type": "application/json; charset=utf-8"}


def _json(status: int, payload: dict) -> tuple[int, dict[str, str], str]:
    return status, JSON_HEADERS, json.dumps(payload, indent=2) + "\n"


def _auth_payload(*, validate: bool = False) -> dict:
    report = collect_auth_status(validate=validate)
    return report.to_dict()


def _scan_payload() -> dict:
    from pathlib import Path

    auth = collect_auth_status(validate=False).to_dict()
    doctor = run_env_doctor(include_outdated=False, include_auth=True, validate_auth=False)
    root = Path.cwd()
    skip = {".git", ".venv", "venv", "node_modules", "__pycache__"}
    files = [
        p
        for p in root.rglob("*")
        if p.is_file()
        and not any(part in skip for part in p.parts)
        and p.stat().st_size < 1_000_000
    ]
    grouped = scan_paths(files)
    secrets = {
        "ok": not grouped,
        "files": {
            path: [{"kind": h.kind, "line": h.line} for h in hits] for path, hits in grouped.items()
        },
    }
    return {
        "ok": auth.get("ok") and not doctor.has_failures and secrets["ok"],
        "auth": auth,
        "env_doctor": doctor.to_dict(),
        "secrets": secrets,
        "service": "zenos-security-lab",
        "version": __version__,
    }


def dispatch(method: str, path: str) -> tuple[int, dict[str, str], str]:
    method = method.upper()
    path = path.split("?", 1)[0]
    if method != "GET":
        return _json(405, {"ok": False, "error": "method not allowed"})
    if path == "/health":
        return _json(
            200,
            {"ok": True, "service": "zenos-security-lab", "version": __version__},
        )
    if path == "/auth/status":
        payload = _auth_payload(validate=False)
        status = 200 if payload.get("ok") else 503
        return _json(status, payload)
    if path in {"/scan", "/security/scan"}:
        payload = _scan_payload()
        status = 200 if payload.get("ok") else 503
        return _json(status, payload)
    if path == "/ready":
        return _json(200, {"ok": True})
    return _json(404, {"ok": False, "error": "not found"})


def serve(host: str = "0.0.0.0", port: int = 8080) -> None:
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args) -> None:
            sys_stderr_write = __import__("sys").stderr.write
            sys_stderr_write("%s - %s\n" % (self.address_string(), fmt % args))

        def do_GET(self) -> None:  # noqa: N802
            status, headers, body = dispatch("GET", self.path)
            data = body.encode("utf-8")
            self.send_response(status)
            for key, value in headers.items():
                self.send_header(key, value)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"zenOS security lab listening on {host}:{port}", flush=True)
    httpd.serve_forever()
