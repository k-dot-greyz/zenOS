"""Contracts for the contributor-facing GitHub templates and documentation."""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Set
from urllib.parse import urlparse

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
GITHUB = ROOT / ".github"
ISSUE_TEMPLATE_DIR = GITHUB / "ISSUE_TEMPLATE"
CONTRIBUTING_URL = "https://github.com/k-dot-greyz/zenOS/blob/main/CONTRIBUTING.md"


def load_yaml(path: Path) -> dict:
    """Load a YAML mapping and fail with the source path when its shape is wrong."""
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(document, dict), f"{path.relative_to(ROOT)} must contain a YAML mapping"
    return document


ISSUE_FORMS = (
    pytest.param(
        "bug_report.yml",
        "[bug]: ",
        "bug",
        {"summary", "steps", "expected", "actual", "environment"},
        "#writing-bug-reports",
        id="bug-report",
    ),
    pytest.param(
        "feature_request.yml",
        "[feat]: ",
        "enhancement",
        {"what", "why"},
        "#writing-issues",
        id="feature-request",
    ),
)


@pytest.mark.parametrize(
    ("filename", "title_prefix", "label", "required_ids", "guide_anchor"), ISSUE_FORMS
)
def test_issue_forms_capture_the_required_report_details(
    filename: str,
    title_prefix: str,
    label: str,
    required_ids: Set[str],
    guide_anchor: str,
):
    form = load_yaml(ISSUE_TEMPLATE_DIR / filename)

    assert form["name"]
    assert form["description"]
    assert form["title"] == title_prefix
    assert label in form["labels"]

    fields = form["body"]
    assert isinstance(fields, list) and fields
    for field in fields:
        assert field["type"] in {"checkboxes", "markdown", "textarea"}
        assert isinstance(field["attributes"], dict)
        if field["type"] == "markdown":
            assert field["attributes"]["value"]
            continue
        assert re.fullmatch(r"[a-z][a-z0-9_-]*", field["id"])
        assert field["attributes"]["label"]
        if field["type"] == "checkboxes":
            assert all(option["label"] for option in field["attributes"]["options"])

    identified_fields = [field for field in fields if "id" in field]
    field_ids = [field["id"] for field in identified_fields]

    # Duplicate IDs make a GitHub issue form invalid and can silently discard answers.
    assert len(field_ids) == len(set(field_ids))
    assert required_ids <= set(field_ids)

    by_id = {field["id"]: field for field in identified_fields}
    for field_id in required_ids:
        field = by_id[field_id]
        assert field["type"] == "textarea"
        assert field["attributes"]["label"]
        assert field.get("validations", {}).get("required") is True

    introductory_text = "\n".join(
        field.get("attributes", {}).get("value", "")
        for field in fields
        if field.get("type") == "markdown"
    )
    assert f"{CONTRIBUTING_URL}{guide_anchor}" in introductory_text


def test_issue_template_config_exposes_expected_https_resources():
    config = load_yaml(ISSUE_TEMPLATE_DIR / "config.yml")

    assert config["blank_issues_enabled"] is True
    links = config["contact_links"]
    assert {link["name"] for link in links} == {"Discussions", "Contributing guide"}

    for link in links:
        parsed = urlparse(link["url"])
        assert parsed.scheme == "https"
        assert parsed.netloc == "github.com"
        assert link["about"]


def test_pull_request_template_has_review_sections_in_workflow_order():
    template = (GITHUB / "PULL_REQUEST_TEMPLATE.md").read_text(encoding="utf-8")
    headings = re.findall(r"^## (.+)$", template, flags=re.MULTILINE)

    assert headings == [
        "What",
        "Why",
        "Before/After",
        "Test Results",
        "QA steps",
        "Checklist",
        "Related issues",
        "AI disclosure",
    ]

    expected_checks = {
        "`black --check .`",
        "`isort --check-only .`",
        "`flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics`",
        "`pytest --cov=. --cov-report=term-missing -v`",
        "Tests updated where behavior changed",
        "No secrets, `.env`, or dev-master-only docs in the diff",
    }
    checklist_items = set(re.findall(r"^- \[ \] (.+)$", template, flags=re.MULTILINE))
    assert expected_checks <= checklist_items


def github_heading_slug(heading: str) -> str:
    """Return the GitHub-style anchor used by headings in the changed guide."""
    normalized = heading.strip().lower().replace(" ", "-")
    return re.sub(r"[^a-z0-9_-]", "", normalized)


def markdown_links(document: Path) -> List[str]:
    text = document.read_text(encoding="utf-8")
    return re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", text)


@pytest.mark.parametrize(
    "document",
    [ROOT / "CONTRIBUTING.md", GITHUB / "copilot-instructions.md"],
    ids=["contributing-guide", "copilot-instructions"],
)
def test_local_documentation_links_resolve(document: Path):
    for target in markdown_links(document):
        if urlparse(target).scheme or target.startswith("#"):
            continue
        local_target = target.split("#", 1)[0]
        assert (document.parent / local_target).resolve().exists(), (
            f"{document.relative_to(ROOT)} links to missing path {local_target}"
        )


def test_contributing_guide_internal_anchors_resolve():
    guide = ROOT / "CONTRIBUTING.md"
    text = guide.read_text(encoding="utf-8")
    anchors = {
        github_heading_slug(heading)
        for heading in re.findall(r"^#{1,6} (.+)$", text, flags=re.MULTILINE)
    }
    internal_links = {
        target[1:]
        for target in markdown_links(guide)
        if target.startswith("#")
    }

    assert internal_links
    assert internal_links <= anchors


def test_contributing_guide_documents_the_complete_workflow():
    guide = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    headings = set(re.findall(r"^## (.+)$", guide, flags=re.MULTILINE))

    assert {
        "The prime directive: platform code here, internal guides in dev-master",
        "Fork-and-PR workflow",
        "Pull requests",
        "AI-assisted contributions",
        "Development guidelines",
        "Pre-commit audit",
        "Commit message style",
        "Writing issues",
        "Writing bug reports",
        "License",
    } <= headings

    for quality_gate in (
        "black --check .",
        "isort --check-only .",
        "flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics",
        "pytest --cov=. --cov-report=term-missing -v",
    ):
        assert quality_gate in guide
