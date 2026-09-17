"""GitHub issue and PR template contracts.

Guiding story: a reporter opens an issue or PR and is asked to check
unmerged PRs and stale branches first, then fill a real form—not a
blank editor or a stock GitHub markdown duplicate of the YAML forms.
"""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ISSUE_DIR = ROOT / ".github" / "ISSUE_TEMPLATE"
PR_TEMPLATE = ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md"

PRECHECK_PHRASES = ("unmerged", "stale branch")


def _load_yaml(rel: Path) -> dict:
    data = yaml.safe_load(rel.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _body_markdown(data: dict) -> str:
    chunks: list[str] = []
    for item in data.get("body") or []:
        if not isinstance(item, dict):
            continue
        attrs = item.get("attributes") or {}
        if item.get("type") == "markdown":
            chunks.append(str(attrs.get("value") or ""))
        chunks.append(str(attrs.get("label") or ""))
        chunks.append(str(attrs.get("description") or ""))
    return "\n".join(chunks).lower()


def test_stock_markdown_issue_templates_are_not_shipped():
    for name in ("bug_report.md", "feature_request.md", "custom.md"):
        path = ISSUE_DIR / name
        assert not path.exists(), f"{path.name} duplicates the YAML issue forms and must not ship"


def test_issue_forms_exist_and_use_list_labels():
    expected = {
        "bug_report.yml": "Bug report",
        "feature_request.yml": "Feature request",
        "other.yml": "Something else",
    }
    for filename, name in expected.items():
        data = _load_yaml(ISSUE_DIR / filename)
        assert data.get("name") == name
        labels = data.get("labels", [])
        assert isinstance(labels, list), f"{filename} labels must be a YAML list, not a string"
        assert "" not in labels
        assignees = data.get("assignees", [])
        if assignees is not None:
            assert isinstance(assignees, list)
            assert "" not in assignees
        body = data.get("body")
        assert isinstance(body, list) and body, f"{filename} must have a form body"


def test_every_issue_form_asks_to_check_unmerged_prs_and_stale_branches():
    for filename in ("bug_report.yml", "feature_request.yml", "other.yml"):
        text = _body_markdown(_load_yaml(ISSUE_DIR / filename))
        for phrase in PRECHECK_PHRASES:
            assert phrase in text, f"{filename} is missing pre-check phrase {phrase!r}"


def test_other_issue_form_has_meaningful_prompts():
    data = _load_yaml(ISSUE_DIR / "other.yml")
    text = _body_markdown(data)
    assert "what" in text
    assert "why" in text
    labels = [item.get("attributes", {}).get("label", "") for item in data["body"]]
    assert any("what" in str(label).lower() for label in labels)


def test_bug_environment_placeholder_matches_python_314_floor():
    data = _load_yaml(ISSUE_DIR / "bug_report.yml")
    env = next(item for item in data["body"] if item.get("id") == "environment")
    placeholder = env["attributes"]["placeholder"]
    assert "3.14" in placeholder
    assert "3.12" not in placeholder


def test_pr_template_asks_for_prior_art_and_keeps_contributing_structure():
    template = PR_TEMPLATE.read_text(encoding="utf-8")
    lower = template.lower()
    assert "## what" in lower
    assert "## why" in lower
    assert "closes #" in lower
    assert "unmerged" in lower
    assert "stale" in lower
    assert "open pull request" in lower or "open pr" in lower
