"""Tests for template registry engine, catalog, and validator."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def template_engine():
    from zen.utils.template import TemplateEngine

    return TemplateEngine(require_registry=True)


@pytest.fixture
def sample_standup():
    return {
        "date": "2025-11-11",
        "team": "zenOS",
        "updates": [
            {
                "member": "Kaspars",
                "yesterday": "Registry work",
                "today": "PR cleanup",
                "blockers": "None",
            }
        ],
    }


def test_template_engine_lists_registry_entries(template_engine):
    entries = list(template_engine.list_templates())
    assert len(entries) == 5


def test_render_by_id_daily_standup(template_engine, sample_standup):
    rendered = template_engine.render_by_id("doc.report.daily_standup", sample_standup)
    assert "zenOS" in rendered
    assert "Kaspars" in rendered


def test_template_catalog_exports(template_engine):
    from zen.templates import TemplateCatalog, TemplateValidator

    catalog = TemplateCatalog(engine=template_engine)
    assert len(catalog.catalog()) == 5

    validator = TemplateValidator(engine=template_engine)
    report = validator.validate(
        "doc.report.daily_standup",
        {
            "date": "2025-11-11",
            "team": "zenOS",
            "updates": [
                {
                    "member": "Kaspars",
                    "yesterday": "y",
                    "today": "t",
                    "blockers": "n",
                }
            ],
        },
    )
    assert report.is_valid


def test_agent_engine_works_without_registry_on_path(monkeypatch, tmp_path):
    from zen.core.agent import AgentManifest
    from zen.utils.template import TemplateEngine

    missing_registry_dir = tmp_path / "empty-templates"
    missing_registry_dir.mkdir()
    engine = TemplateEngine(template_dir=missing_registry_dir)
    assert engine.render("Hello {{ name }}", {"name": "world"}) == "Hello world"

    manifest = AgentManifest(name="test", description="test agent")
    from zen.core.agent import Agent

    class DummyAgent(Agent):
        def execute(self, prompt, variables):
            return prompt

    agent = DummyAgent(manifest)
    assert agent.template_engine.render("{{ x }}", {"x": "ok"}) == "ok"


def test_read_template_source_rejects_path_traversal(template_engine):
    from zen.utils.template import TemplateRegistryError

    with pytest.raises(TemplateRegistryError, match="escapes template directory"):
        template_engine.read_template_source("../../etc/passwd")
