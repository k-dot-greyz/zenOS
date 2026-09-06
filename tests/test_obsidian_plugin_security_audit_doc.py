"""Structural and content validation for docs/guides/OBSIDIAN_PLUGIN_SECURITY_AUDIT.md.

This guide is a security audit protocol document (not executable code). These
tests guard against accidental regressions to its structure and required
content: required sections, official reference links, checklist items, and
the embedded YAML/KQL code blocks.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "docs" / "guides" / "OBSIDIAN_PLUGIN_SECURITY_AUDIT.md"

EXPECTED_TOP_LEVEL_SECTIONS = [
    "1. Scope and threat model",
    "2. Official policy and review references (SSOT)",
    "3. Automated scanning rules (what Obsidian's reviewer checks)",
    "4. Manual review criteria (human audit checklist)",
    "5. Identifying malicious plugins: red flags",
    "6. Baseline hardening for sensitive PKM vaults",
    "7. Ongoing monitoring & update policy",
    "8. Reference manifest (for automation & PRs)",
    "9. Appendix: detection rules (Elastic-style KQL examples)",
    "10. zenOS integration notes",
]

EXPECTED_SSOT_URLS = [
    "https://github.com/obsidianmd/obsidian-help/blob/master/en/Extending%20Obsidian/Plugin%20security.md",
    "https://obsidian.md/blog/future-of-plugins/",
    "https://docs.obsidian.md/oo/plugin",
    "https://obsidian.md/blog/less-is-safer/",
    "https://community.obsidian.md/plugins",
]

URL_RE = re.compile(r"https?://[^\s)>\]\"]+")


@pytest.fixture(scope="module")
def doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_doc_file_exists():
    assert DOC_PATH.is_file(), f"Expected guide not found at {DOC_PATH}"


def test_doc_is_non_empty(doc_text: str):
    assert len(doc_text.strip()) > 0


def test_doc_starts_with_expected_h1_title(doc_text: str):
    first_line = doc_text.splitlines()[0]
    assert first_line.startswith("# "), "Document must start with an H1 heading"
    assert "Security Audit Protocol" in first_line
    assert "Obsidian Community Plugin" in first_line


def test_doc_has_no_yaml_frontmatter(doc_text: str):
    # Unlike dex-catalog markdown, guides in docs/guides/ start directly with
    # an H1 title and do not use YAML frontmatter delimiters.
    assert not doc_text.startswith("---\n")


@pytest.mark.parametrize("section_title", EXPECTED_TOP_LEVEL_SECTIONS)
def test_doc_contains_expected_top_level_section(doc_text: str, section_title: str):
    assert f"## {section_title}" in doc_text, f"Missing section heading: {section_title}"


def test_doc_top_level_sections_appear_in_order(doc_text: str):
    positions = [doc_text.index(f"## {title}") for title in EXPECTED_TOP_LEVEL_SECTIONS]
    assert positions == sorted(positions), "Top-level sections are out of order"


def test_doc_has_exactly_ten_top_level_sections(doc_text: str):
    headings = re.findall(r"^## .+$", doc_text, re.MULTILINE)
    assert len(headings) == len(EXPECTED_TOP_LEVEL_SECTIONS)


def test_doc_has_no_duplicate_top_level_headings(doc_text: str):
    headings = re.findall(r"^## (.+)$", doc_text, re.MULTILINE)
    assert len(headings) == len(set(headings)), "Duplicate top-level section headings found"


@pytest.mark.parametrize("url", EXPECTED_SSOT_URLS)
def test_doc_contains_expected_ssot_reference_url(doc_text: str, url: str):
    assert url in doc_text, f"Missing expected SSOT reference URL: {url}"


def test_doc_all_urls_are_well_formed(doc_text: str):
    urls = URL_RE.findall(doc_text)
    assert len(urls) >= len(EXPECTED_SSOT_URLS)
    for url in urls:
        assert url.startswith("http://") or url.startswith("https://")
        # Must not contain whitespace or unbalanced markdown link characters.
        assert " " not in url
        assert url == url.strip()


def test_doc_checklist_items_use_markdown_checkbox_syntax(doc_text: str):
    checklist_items = re.findall(r"^- \[ \] .+$", doc_text, re.MULTILINE)
    # Sections 4.1, 4.3, 6, and 7 each contribute checklist items.
    assert len(checklist_items) >= 15


@pytest.mark.parametrize(
    "subsection_title,expected_min_items",
    [
        ("4.1 Pre-install triage (directory & scorecard)", 4),
        ("4.3 Runtime behavior validation (dynamic analysis)", 4),
    ],
)
def test_doc_subsection_has_expected_checklist_items(
    doc_text: str, subsection_title: str, expected_min_items: int
):
    heading = f"### {subsection_title}"
    assert heading in doc_text
    start = doc_text.index(heading) + len(heading)
    # Slice up to the next heading (## or ###) to scope the search.
    rest = doc_text[start:]
    next_heading_match = re.search(r"^#{2,3} ", rest, re.MULTILINE)
    section_body = rest[: next_heading_match.start()] if next_heading_match else rest
    items = re.findall(r"^- \[ \] .+$", section_body, re.MULTILINE)
    assert len(items) >= expected_min_items


def test_doc_contains_yaml_reference_manifest_block(doc_text: str):
    match = re.search(r"```yaml\n(.*?)\n```", doc_text, re.DOTALL)
    assert match is not None, "Expected a fenced yaml code block for the reference manifest"


def test_doc_yaml_manifest_is_valid_and_well_formed(doc_text: str):
    yaml = pytest.importorskip("yaml")
    match = re.search(r"```yaml\n(.*?)\n```", doc_text, re.DOTALL)
    assert match is not None
    parsed = yaml.safe_load(match.group(1))

    assert isinstance(parsed, dict)
    assert parsed.get("title") == "Obsidian Plugin Security & Blast Radius Audit"
    assert "sources" in parsed
    assert isinstance(parsed["sources"], list)
    assert len(parsed["sources"]) == len(EXPECTED_SSOT_URLS)

    for source in parsed["sources"]:
        assert set(source.keys()) == {"name", "url", "role"}
        assert source["url"] in EXPECTED_SSOT_URLS
        assert source["name"]
        assert source["role"]

    manifest_urls = {source["url"] for source in parsed["sources"]}
    assert manifest_urls == set(EXPECTED_SSOT_URLS)


def test_doc_contains_kql_detection_rules_block(doc_text: str):
    match = re.search(r"```kql\n(.*?)\n```", doc_text, re.DOTALL)
    assert match is not None, "Expected a fenced kql code block with detection rules"
    kql_body = match.group(1)
    assert "process.name" in kql_body
    assert "Obsidian.exe" in kql_body
    assert "file.directory" in kql_body
    assert ".obsidian/plugins" in kql_body


def test_doc_kql_block_references_expected_shell_interpreters(doc_text: str):
    match = re.search(r"```kql\n(.*?)\n```", doc_text, re.DOTALL)
    assert match is not None
    kql_body = match.group(1)
    for interpreter in ("powershell.exe", "cmd.exe", "bash", "zsh", "osascript"):
        assert interpreter in kql_body


def test_doc_mentions_restricted_mode_hardening_guidance(doc_text: str):
    assert "Restricted Mode ON" in doc_text


def test_doc_mentions_safety_scorecard_concept(doc_text: str):
    assert "safety scorecard" in doc_text.lower()


def test_doc_zenos_integration_notes_reference_repository_management(doc_text: str):
    integration_section = doc_text[doc_text.index("## 10. zenOS integration notes") :]
    assert "docs/REPOSITORY_MANAGEMENT.md" in integration_section
    assert "docs/guides/" in integration_section


def test_doc_file_is_located_under_docs_guides():
    # Self-consistency: section 10 recommends placing the guide under
    # docs/guides/, which is where this file must actually live.
    assert DOC_PATH.parent.name == "guides"
    assert DOC_PATH.parent.parent.name == "docs"


def test_doc_ends_with_single_trailing_newline():
    raw = DOC_PATH.read_bytes()
    assert raw.endswith(b"\n")
    assert not raw.endswith(b"\n\n")


def test_doc_code_blocks_are_balanced(doc_text: str):
    fence_count = doc_text.count("```")
    assert fence_count % 2 == 0, "Unbalanced triple-backtick code fences"
