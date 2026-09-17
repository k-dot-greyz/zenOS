"""Guiding story: Kaspars re-runs the wizard on a box that already has
GITHUB_TOKEN set. It must not clobber the existing value, must validate
new tokens via GET /user, and must write a versioned .env.
"""

from __future__ import annotations

from pathlib import Path

from zen.auth.wizard import TEMPLATE_VERSION, apply_env_updates, load_env_map, missing_keys


def test_template_header_is_versioned():
    text = (Path(__file__).resolve().parents[1] / ".env.template").read_text(encoding="utf-8")
    assert text.startswith("# zenOS env template v1.")
    assert "GITHUB_TOKEN=" in text
    assert "OPENROUTER_API_KEY=" in text
    assert "ZEN_ENGINE_MODE=" in text
    assert "GITHUB_MCP_URL=" in text
    assert "GITHUB_OAUTH_CLIENT_ID=" in text
    assert TEMPLATE_VERSION.startswith("1.")


def test_missing_keys_skips_values_already_set(tmp_path: Path):
    env_path = tmp_path / ".env"
    env_path.write_text("GITHUB_TOKEN=already-there\nOPENROUTER_API_KEY=\n", encoding="utf-8")
    current = load_env_map(env_path)
    assert current["GITHUB_TOKEN"] == "already-there"
    missing = missing_keys(current)
    assert "GITHUB_TOKEN" not in missing
    assert "OPENROUTER_API_KEY" in missing


def test_apply_env_updates_is_idempotent(tmp_path: Path):
    env_path = tmp_path / ".env"
    env_path.write_text("GITHUB_TOKEN=keep-me\n", encoding="utf-8")
    written = apply_env_updates(
        env_path,
        {"GITHUB_TOKEN": "should-not-overwrite", "GITHUB_USERNAME": "greyZ"},
        overwrite=False,
    )
    text = env_path.read_text(encoding="utf-8")
    assert "GITHUB_TOKEN=keep-me" in text
    assert "GITHUB_USERNAME=greyZ" in text
    assert "should-not-overwrite" not in text
    assert "GITHUB_USERNAME" in written
    assert "GITHUB_TOKEN" not in written


def test_wizard_validates_github_token_before_write(tmp_path: Path):
    from zen.auth.wizard import WizardError, run_wizard

    class Boom:
        def get(self, url, headers, timeout=10.0):
            return (401, {}, "nope")

    env_path = tmp_path / ".env"
    try:
        run_wizard(
            env_path=env_path,
            answers={"GITHUB_TOKEN": "ghp_" + "bad"},
            http=Boom(),
            interactive=False,
        )
        raise AssertionError("expected WizardError")
    except WizardError as exc:
        assert "invalid" in str(exc).lower() or "401" in str(exc)
    if env_path.exists():
        assert "ghp_" + "bad" not in env_path.read_text(encoding="utf-8")


def test_engine_modes_documented():
    from zen.auth.wizard import ENGINE_MODES

    assert ENGINE_MODES == ("product", "persona", "investment")
    docs = (Path(__file__).resolve().parents[1] / "docs" / "guides" / "ENV_TEMPLATE.md").read_text(
        encoding="utf-8"
    )
    for mode in ENGINE_MODES:
        assert mode in docs
