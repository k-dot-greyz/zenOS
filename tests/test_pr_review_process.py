"""PR/review process contracts.

Guiding story: a contributor opens a PR and immediately sees what actually
blocks merge (Black 3.14, identity scanner, pytest) versus what they can
push back on — not a 20-checkbox guilt trip.
"""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def _load_workflow(rel: str) -> dict:
    data = yaml.safe_load(_read(rel))
    # PyYAML 1.1: the GitHub key `on` loads as boolean True.
    if True in data and "on" not in data:
        data["on"] = data.pop(True)
    return data


def test_pr_template_is_intent_and_verify_not_checkbox_theater():
    template = _read(".github/PULL_REQUEST_TEMPLATE.md")
    lower = template.lower()
    assert "how to verify" in lower
    assert "intent" in lower
    assert "closes #" in lower
    assert "benchmarked for performance" not in lower
    assert "origin" in lower
    assert ".env" in lower
    assert "intentionally skipped" in lower
    assert template.count("- [ ]") <= 5


def test_commit_checklist_points_at_review_guide_not_theater():
    checklist = _read(".github/COMMIT_WORKFLOW_CHECKLIST.md")
    assert "benchmarked for performance" not in checklist.lower()
    assert "docs/guides/REVIEW.md" in checklist
    assert checklist.count("- [ ]") <= 8


def test_duplicate_python_app_workflow_is_gone():
    assert not (ROOT / ".github/workflows/python-app.yml").exists()


def test_ci_runs_identity_scanner_and_does_not_block_tests_on_lint():
    ci_text = _read(".github/workflows/zenos-ci.yml")
    ci = _load_workflow(".github/workflows/zenos-ci.yml")
    jobs = ci["jobs"]

    test_job = jobs["test"]
    needs = test_job.get("needs")
    if needs is None:
        blocked_by_lint = False
    elif isinstance(needs, str):
        blocked_by_lint = needs == "lint"
    else:
        blocked_by_lint = "lint" in needs
    assert not blocked_by_lint, "test job must run in parallel with lint, not needs: lint"

    assert "check_no_identity_leaks.py" in ci_text
    assert 'pip install -e ".[dev]"' in ci_text
    assert "_setup.py.bak" in ci_text
    assert "pytest tests/" in ci_text
    assert "-o addopts=" in ci_text

    lint = jobs["lint"]
    lint_python = str(lint)
    assert "3.14" in lint_python

    success = jobs["ci-success"]
    required = success.get("needs") or []
    if isinstance(required, str):
        required = [required]
    assert "lint" in required
    assert "test" in required
    for optional in ("security", "shell-check", "docs"):
        assert optional not in required, f"{optional} must stay non-blocking"


def test_ci_runs_on_all_pull_requests():
    ci = _load_workflow(".github/workflows/zenos-ci.yml")
    pull = ci["on"]["pull_request"]
    # Empty mapping / None / missing branches = every PR, including stacked ones.
    if pull is None:
        return
    if pull is True:
        return
    if isinstance(pull, dict):
        branches = pull.get("branches")
        assert not branches, "CI must run on stacked PRs, not only PRs targeting main"


def test_coderabbit_turns_off_docstring_coverage_and_scopes_paths():
    text = _read(".coderabbit.yaml")
    cfg = yaml.safe_load(text)
    docs = cfg["reviews"]["pre_merge_checks"]["docstrings"]
    assert str(docs["mode"]).lower() == "off"
    instructions = cfg["reviews"]["path_instructions"]
    joined = "\n".join(
        f"{item.get('path', '')}\n{item.get('instructions', '')}" for item in instructions
    )
    assert "docs/archive" in joined
    assert "inbox/" in joined or "inbox/**" in joined
    assert "zen/origin.py" in joined
    assert "install" in joined.lower()
    assert "signed" in joined.lower()
    filters = cfg["reviews"].get("path_filters") or []
    joined_filters = "\n".join(str(f) for f in filters)
    assert "docs/archive" in joined_filters


def test_review_guide_names_merge_blocking_vs_push_back():
    review = _read("docs/guides/REVIEW.md")
    lower = review.lower()
    assert "merge-blocking" in lower or "merge blocking" in lower
    assert "black" in lower
    assert "identity" in lower
    assert "uvx --python 3.14 black" in review
    assert "reply" in lower and "resolve" in lower
    assert "coderabbit" in lower
    assert "suggestions" in lower
    assert "pytest tests/" in review


def test_readme_points_at_review_guide():
    readme = _read("README.md")
    assert "docs/guides/REVIEW.md" in readme
