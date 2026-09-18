"""Secret scan + hygiene: the commit boundary must catch a real PAT
and must never require committing .env or .cursor/mcp.json.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_gitignore_covers_secret_surfaces():
    gi = (ROOT / ".gitignore").read_text(encoding="utf-8")
    for pattern in (
        ".env",
        ".env.local",
        "*.pem",
        "*.key",
        "secrets/",
        ".cursor/mcp.json",
    ):
        assert pattern in gi, pattern


def test_env_is_not_tracked():
    listed = subprocess.check_output(
        ["git", "ls-files", "--", ".env", ".cursor/mcp.json"],
        cwd=ROOT,
        text=True,
    ).strip()
    assert listed == "", listed


def test_mcp_json_template_uses_env_interpolation_only():
    template = (ROOT / ".cursor" / "mcp.json.template").read_text(encoding="utf-8")
    assert "${env:GITHUB_TOKEN}" in template
    assert "${env:GITHUB_MCP_URL}" in template
    assert "${env:GITHUB_OAUTH_CLIENT_ID}" in template
    assert "ghp_" not in template
    assert "github-oauth" in template


def test_secret_scan_flags_classic_pat_and_ignores_prefix_mentions():
    from zen.auth.secret_scan import scan_text

    docs = "Classic tokens start with ghp_ and fine-grained with github_pat_."
    assert scan_text(docs) == []
    fake = "ghp_" + ("a" * 36)
    hits = scan_text(f"token={fake}\n")
    assert hits
    assert any(h.match.startswith("ghp_") for h in hits)


def test_secret_scan_flags_openrouter_and_aws():
    from zen.auth.secret_scan import scan_text

    blob = "\n".join(
        [
            "OPENROUTER_API_KEY=" + "sk-or-v1-" + ("a" * 40),
            "AWS=AKIA" + "IOSFODNN7EXAMPLE",
            "Authorization: Bearer " + ("B" * 24),
        ]
    )
    kinds = {h.kind for h in scan_text(blob)}
    assert "openrouter" in kinds or "generic_sk" in kinds
    assert "aws_access_key" in kinds
    assert "bearer" in kinds


def test_pre_commit_hook_script_exists_and_is_executable_pattern():
    script = ROOT / "scripts" / "pre-commit-secret-scan.sh"
    assert script.is_file()
    text = script.read_text(encoding="utf-8")
    assert "git diff --cached" in text
    assert "ghp_" in text


def test_pat_naming_and_rotation_are_documented():
    checklist = (ROOT / ".github" / "COMMIT_WORKFLOW_CHECKLIST.md").read_text(encoding="utf-8")
    assert "90-day" in checklist.lower() or "90 day" in checklist.lower()
    guide = (ROOT / "docs" / "guides" / "CURSOR_MCP_SETUP.md").read_text(encoding="utf-8")
    assert "zenos-mcp-" in guide
    assert "repo" in guide and "read:org" in guide


def test_cursor_mcp_guide_lives_in_dex_and_docs():
    docs = ROOT / "docs" / "guides" / "CURSOR_MCP_SETUP.md"
    dex = ROOT / "dex" / "03-docs" / "guides" / "CURSOR_MCP_SETUP.md"
    assert docs.is_file()
    assert dex.is_file()
    assert "OAuth" in docs.read_text(encoding="utf-8")


def test_adr_pat_vs_oauth_recorded():
    log = (ROOT / "docs" / "DECISION_LOG.md").read_text(encoding="utf-8")
    assert "PAT" in log and "OAuth" in log
    assert "Accepted" in log
    assert "Consequences" in log
    assert "Alternatives" in log


def test_incident_response_sop_exists():
    sop = (ROOT / "docs" / "guides" / "SECRET_INCIDENT_RESPONSE.md").read_text(encoding="utf-8")
    assert "revoke" in sop.lower()
    assert "git log" in sop
    assert "rotate" in sop.lower()
    assert "notify" in sop.lower()
