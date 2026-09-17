"""Credential status, exit-code contract, and live token checks.

Exit codes (public contract):
  0  healthy
  10 repairable (token present but rejected by the provider)
  20 blocked (required credential missing)
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Protocol

AUTH_OK = 0
AUTH_INVALID = 10
AUTH_MISSING = 20

DEFAULT_GITHUB_MCP_URL = "https://api.githubcopilot.com/mcp/"
GITHUB_USER_URL = "https://api.github.com/user"
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"
GITHUB_TOKEN_SETTINGS_URL = "https://github.com/settings/tokens"
GITHUB_FINE_GRAINED_URL = "https://github.com/settings/personal-access-tokens"
PAT_NAMING_PATTERN = "zenos-mcp-<env>-YYYY-MM"
PAT_NAMING_EXAMPLE = "zenos-mcp-cursor-2026-09"

REQUIRED_SCOPES = {
    "ops": ("repo", "read:org"),
    "workflow": ("workflow",),
    "security": ("security_events",),
    "project": ("project",),
}


class HttpClient(Protocol):
    def get(
        self, url: str, headers: dict[str, str], timeout: float = 10.0
    ) -> tuple[int, dict[str, str], str]: ...


@dataclass
class CredentialStatus:
    name: str
    status: str
    message: str
    required: bool = True
    login: Optional[str] = None
    scopes: Optional[list[str]] = None
    exit_code: int = AUTH_OK

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": self.name,
            "status": self.status,
            "message": self.message,
            "required": self.required,
            "exit_code": self.exit_code,
        }
        if self.login:
            payload["login"] = self.login
        if self.scopes is not None:
            payload["scopes"] = self.scopes
        return payload


@dataclass
class AuthReport:
    credentials: list[CredentialStatus] = field(default_factory=list)
    github_mcp_url: str = DEFAULT_GITHUB_MCP_URL
    engine_mode: str = "product"

    def credential(self, name: str) -> CredentialStatus:
        for item in self.credentials:
            if item.name == name:
                return item
        raise KeyError(name)

    @property
    def exit_code(self) -> int:
        codes = [c.exit_code for c in self.credentials if c.required]
        if AUTH_MISSING in codes:
            return AUTH_MISSING
        if AUTH_INVALID in codes:
            return AUTH_INVALID
        return AUTH_OK

    @property
    def ok(self) -> bool:
        return self.exit_code == AUTH_OK

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "exit_code": self.exit_code,
            "github_mcp_url": self.github_mcp_url,
            "engine_mode": self.engine_mode,
            "credentials": [c.to_dict() for c in self.credentials],
            "repair": repair_hints(self) if not self.ok else [],
        }


def _present(value: Optional[str]) -> bool:
    return bool(value and value.strip())


def _env(environ: Mapping[str, str], key: str) -> str:
    return str(environ.get(key, "") or "")


def default_http() -> HttpClient:
    import httpx

    class _Httpx:
        def get(self, url: str, headers: dict[str, str], timeout: float = 10.0):
            response = httpx.get(url, headers=headers, timeout=timeout)
            header_map = {str(k): str(v) for k, v in response.headers.items()}
            return response.status_code, header_map, response.text

    return _Httpx()


def check_github_token(
    token: str,
    *,
    validate: bool,
    http: Optional[HttpClient] = None,
) -> CredentialStatus:
    if not _present(token):
        return CredentialStatus(
            name="GITHUB_TOKEN",
            status="missing",
            message="GITHUB_TOKEN is not set. Create a PAT named "
            f"{PAT_NAMING_EXAMPLE} and export it (or run python scripts/setup_env.py).",
            required=True,
            exit_code=AUTH_MISSING,
        )
    if not validate:
        return CredentialStatus(
            name="GITHUB_TOKEN",
            status="ok",
            message="GITHUB_TOKEN is set (not live-validated).",
            required=True,
            exit_code=AUTH_OK,
        )
    client = http or default_http()
    status, headers, body = client.get(
        GITHUB_USER_URL,
        {"Authorization": f"Bearer {token.strip()}", "Accept": "application/vnd.github+json"},
        10.0,
    )
    if status == 401:
        return CredentialStatus(
            name="GITHUB_TOKEN",
            status="invalid",
            message="GITHUB_TOKEN was rejected (401). Rotate it: zen auth rotate",
            required=True,
            exit_code=AUTH_INVALID,
        )
    if status == 403:
        return CredentialStatus(
            name="GITHUB_TOKEN",
            status="invalid",
            message="GITHUB_TOKEN is present but GitHub returned 403 (scope or SSO).",
            required=True,
            exit_code=AUTH_INVALID,
        )
    if status != 200:
        return CredentialStatus(
            name="GITHUB_TOKEN",
            status="invalid",
            message=f"GitHub GET /user returned HTTP {status}.",
            required=True,
            exit_code=AUTH_INVALID,
        )
    login = None
    try:
        login = json.loads(body or "{}").get("login")
    except json.JSONDecodeError:
        login = None
    scopes_raw = headers.get("X-OAuth-Scopes") or headers.get("x-oauth-scopes") or ""
    scopes = [s.strip() for s in scopes_raw.split(",") if s.strip()]
    return CredentialStatus(
        name="GITHUB_TOKEN",
        status="ok",
        message=f"GitHub token valid for {login or 'authenticated user'}.",
        required=True,
        login=login,
        scopes=scopes,
        exit_code=AUTH_OK,
    )


def check_openrouter_key(
    key: str,
    *,
    validate: bool,
    required: bool,
    http: Optional[HttpClient] = None,
) -> CredentialStatus:
    if not _present(key):
        status = "skipped" if not required else "missing"
        code = AUTH_OK if not required else AUTH_MISSING
        return CredentialStatus(
            name="OPENROUTER_API_KEY",
            status=status,
            message=(
                "OPENROUTER_API_KEY is not set."
                if required
                else "OPENROUTER_API_KEY not set (optional in this mode)."
            ),
            required=required,
            exit_code=code,
        )
    if not validate:
        return CredentialStatus(
            name="OPENROUTER_API_KEY",
            status="ok",
            message="OPENROUTER_API_KEY is set (not live-validated).",
            required=required,
            exit_code=AUTH_OK,
        )
    client = http or default_http()
    status, _headers, _body = client.get(
        OPENROUTER_MODELS_URL,
        {"Authorization": f"Bearer {key.strip()}"},
        10.0,
    )
    if status in {401, 403}:
        return CredentialStatus(
            name="OPENROUTER_API_KEY",
            status="invalid",
            message=f"OPENROUTER_API_KEY was rejected (HTTP {status}).",
            required=True,
            exit_code=AUTH_INVALID,
        )
    if status >= 400:
        return CredentialStatus(
            name="OPENROUTER_API_KEY",
            status="invalid",
            message=f"OpenRouter /models returned HTTP {status}.",
            required=True,
            exit_code=AUTH_INVALID,
        )
    return CredentialStatus(
        name="OPENROUTER_API_KEY",
        status="ok",
        message="OpenRouter key accepted.",
        required=required,
        exit_code=AUTH_OK,
    )


def collect_auth_status(
    *,
    environ: Optional[Mapping[str, str]] = None,
    validate: bool = True,
    http: Optional[HttpClient] = None,
    ci: bool = False,
) -> AuthReport:
    env = environ if environ is not None else os.environ
    mcp = _env(env, "GITHUB_MCP_URL").strip() or DEFAULT_GITHUB_MCP_URL
    engine = _env(env, "ZEN_ENGINE_MODE").strip() or "product"
    report = AuthReport(github_mcp_url=mcp, engine_mode=engine)
    report.credentials.append(
        check_github_token(_env(env, "GITHUB_TOKEN"), validate=validate, http=http)
    )
    # OpenRouter is optional for the exit-code contract unless it is present
    # and rejected. `--ci` keeps the same rule so Actions can pass with only
    # GITHUB_TOKEN. Agent preflight still *warns* when it is missing.
    report.credentials.append(
        check_openrouter_key(
            _env(env, "OPENROUTER_API_KEY"),
            validate=validate,
            required=False,
            http=http,
        )
    )
    oauth = _env(env, "GITHUB_OAUTH_CLIENT_ID")
    if _present(oauth):
        report.credentials.append(
            CredentialStatus(
                name="GITHUB_OAUTH_CLIENT_ID",
                status="ok",
                message="OAuth client id is set (public).",
                required=False,
                exit_code=AUTH_OK,
            )
        )
    else:
        report.credentials.append(
            CredentialStatus(
                name="GITHUB_OAUTH_CLIENT_ID",
                status="skipped",
                message="OAuth client id not set — PAT path in use.",
                required=False,
                exit_code=AUTH_OK,
            )
        )
    return report


def repair_hints(report: AuthReport) -> list[str]:
    hints: list[str] = []
    for cred in report.credentials:
        if cred.status == "missing" and cred.required:
            hints.append(
                f"Set {cred.name} via python scripts/setup_env.py "
                f"(PAT name {PAT_NAMING_EXAMPLE})."
            )
        elif cred.status == "invalid":
            hints.append(f"Rotate {cred.name}: zen auth rotate")
    return hints


def rotate_message() -> str:
    return (
        "Rotate GitHub PATs every 90 days.\n"
        f"Naming: {PAT_NAMING_PATTERN}  (example: {PAT_NAMING_EXAMPLE})\n"
        "Put purpose + machine name in the token description. Always set an expiry.\n"
        f"Classic tokens: {GITHUB_TOKEN_SETTINGS_URL}\n"
        f"Fine-grained tokens: {GITHUB_FINE_GRAINED_URL}\n"
        "After creating a new token, export GITHUB_TOKEN (or re-run "
        "python scripts/setup_env.py) and never paste it into mcp.json.\n"
    )


def format_human(report: AuthReport) -> str:
    lines = ["zenOS auth status", ""]
    marks = {"ok": "[OK]", "missing": "[MISSING]", "invalid": "[INVALID]", "skipped": "[SKIP]"}
    for cred in report.credentials:
        mark = marks.get(cred.status, "[?]")
        extra = f" login={cred.login}" if cred.login else ""
        lines.append(f"{mark} {cred.name}: {cred.message}{extra}")
    lines.append(f"GITHUB_MCP_URL={report.github_mcp_url}")
    lines.append(f"ZEN_ENGINE_MODE={report.engine_mode}")
    lines.append(f"exit_code={report.exit_code}")
    if not report.ok:
        lines.append("")
        lines.append("Repair:")
        for hint in repair_hints(report):
            lines.append(f"  - {hint}")
    return "\n".join(lines) + "\n"
