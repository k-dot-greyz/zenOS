"""Launch readiness spec stays complete and discoverable."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
CHECKLIST = ROOT / "docs" / "planning" / "LAUNCH_READINESS_CHECKLIST.md"
CHECKLIST_URL = (
    "https://github.com/k-dot-greyz/zenOS/blob/main/" "docs/planning/LAUNCH_READINESS_CHECKLIST.md"
)

INVARIANTS = (
    "Zero-egress static assets",
    "Affirmative clickwrap ledger",
    "Hardened age gate",
    "Default-deny telemetry and replay",
    "RFC 8058 outbound mail pipeline",
    "Symmetric click-to-cancel",
    "Pre-checkout renewal notice",
    "Merchant of Record (MoR) isolation",
    "DMCA safe harbor agent",
    "Accessibility navigation model",
    "Programmatic DSAR pipelines",
)

WIRED_FROM = (
    ROOT / "README.md",
    ROOT / "CONTRIBUTING.md",
    ROOT / "docs" / "AI_INSTRUCTIONS.md",
    ROOT / "docs" / "archive" / "README.md",
    ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md",
    ROOT / ".github" / "ISSUE_TEMPLATE" / "launch_readiness.yml",
    ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml",
)


def test_checklist_file_exists():
    assert CHECKLIST.is_file(), "Launch readiness checklist is missing"


def test_checklist_defines_eleven_invariants():
    text = CHECKLIST.read_text(encoding="utf-8")
    missing = [item for item in INVARIANTS if item not in text]
    assert not missing, f"Checklist is missing invariants: {missing}"
    assert text.count("| [ ] |") >= 11, "Matrix is missing unchecked status cells"


def test_checklist_is_wired_from_contributor_paths():
    needle = "LAUNCH_READINESS_CHECKLIST.md"
    missing = []
    for path in WIRED_FROM:
        if needle not in path.read_text(encoding="utf-8"):
            missing.append(path.relative_to(ROOT).as_posix())
    assert not missing, f"Checklist is not linked from: {missing}"


def _table_rows(heading):
    text = CHECKLIST.read_text(encoding="utf-8")
    section = text.split(f"## {heading}\n", 1)[1].split("\n## ", 1)[0]
    # Both tables have a header and a Markdown separator before their data rows.
    lines = [line for line in section.splitlines() if line.startswith("|")]
    return [[cell.strip() for cell in line.strip("|").split("|")] for line in lines[2:]]


def test_matrix_has_one_complete_row_per_invariant():
    rows = _table_rows("Launch readiness matrix")

    assert len(rows) == len(INVARIANTS)
    assert all(len(row) == 5 for row in rows), "Matrix rows must have five columns"
    assert [row[0] for row in rows] == [str(i) for i in range(1, len(INVARIANTS) + 1)]
    assert [row[1] for row in rows] == list(INVARIANTS)
    for number, invariant, hazard, fix, status in rows:
        assert hazard, f"Item {number} ({invariant}) has no hazard"
        assert fix, f"Item {number} ({invariant}) has no structural fix"
        assert status in {"[ ]", "[x]", "N/A"}, f"Item {number} has invalid status: {status}"


def test_surface_mapping_covers_every_matrix_item_once():
    rows = _table_rows("zenOS surface mapping")

    assert len(rows) == len(INVARIANTS)
    assert all(len(row) == 3 for row in rows), "Surface mapping must have three columns"
    assert [row[0].split(". ", 1)[0] for row in rows] == [
        str(i) for i in range(1, len(INVARIANTS) + 1)
    ]
    for item, surface, trigger in rows:
        assert surface, f"{item} has no current surface"
        assert trigger, f"{item} has no blocking trigger"


@pytest.mark.parametrize("source", ["README.md", "CONTRIBUTING.md", "docs/AI_INSTRUCTIONS.md"])
def test_markdown_checklist_links_resolve_from_the_source_directory(source):
    path = ROOT / source
    targets = re.findall(r"\[[^\]\n]+\]\(([^)\n]+)\)", path.read_text(encoding="utf-8"))
    checklist_targets = [target for target in targets if CHECKLIST.name in target]

    assert checklist_targets, f"{source} must contain a Markdown checklist link"
    for target in checklist_targets:
        assert (path.parent / target).resolve() == CHECKLIST, f"Broken link in {source}: {target}"


@pytest.mark.parametrize("source", ["docs/archive/README.md", ".github/PULL_REQUEST_TEMPLATE.md"])
def test_checklist_references_use_the_repository_path(source):
    text = (ROOT / source).read_text(encoding="utf-8")
    assert f"`{CHECKLIST.relative_to(ROOT).as_posix()}`" in text


@pytest.fixture
def launch_form():
    path = ROOT / ".github" / "ISSUE_TEMPLATE" / "launch_readiness.yml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_launch_form_has_metadata_and_unique_field_ids(launch_form):
    assert launch_form["name"] == "Launch readiness"
    assert launch_form["description"].strip()
    assert launch_form["title"].startswith("[launch]:")
    fields = [field for field in launch_form["body"] if field["type"] != "markdown"]
    ids = [field["id"] for field in fields]
    assert len(ids) == len(set(ids)), "Duplicate field IDs lose cutover information"
    assert {"surface", "matrix", "notes"} <= set(ids)


@pytest.mark.parametrize("field_id", ["surface", "notes"])
def test_launch_form_requires_surface_and_evidence(launch_form, field_id):
    field = next(field for field in launch_form["body"] if field.get("id") == field_id)

    assert field["type"] == "textarea"
    assert field["validations"]["required"] is True
    assert field["attributes"]["label"].strip()
    assert field["attributes"]["description"].strip()


def test_launch_form_matrix_matches_the_spec_and_allows_na_items(launch_form):
    field = next(field for field in launch_form["body"] if field.get("id") == "matrix")

    assert field["type"] == "checkboxes"
    assert "N/A" in field["attributes"]["description"]
    options = field["attributes"]["options"]
    assert len(options) == len(INVARIANTS)
    for number, (option, invariant) in enumerate(zip(options, INVARIANTS), start=1):
        # The form shortens two names; the number and subject must still agree.
        subject = invariant.removesuffix(" pipeline").replace(" (MoR)", "")
        assert option["label"].startswith(f"{number}. {subject} ("), option["label"]
        # Requiring a check would prevent a truthful N/A cutover record.
        assert option.get("required", False) is False


def test_launch_form_intro_links_to_the_canonical_spec(launch_form):
    intros = [field for field in launch_form["body"] if field["type"] == "markdown"]
    assert any(
        f"]({CHECKLIST_URL})" in field["attributes"]["value"] for field in intros
    ), "The launch form must link directly to the specification"


def test_issue_chooser_exposes_the_canonical_checklist_link():
    path = ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml"
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    links = [
        link for link in config["contact_links"] if link["name"] == "Launch readiness checklist"
    ]

    assert len(links) == 1, "The issue chooser must have one launch readiness entry"
    assert links[0]["url"] == CHECKLIST_URL
    assert links[0]["about"].strip()
