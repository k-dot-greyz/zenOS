"""Dockerized zenOS security lab: deploy the image, hit /scan,
get a JSON security report with zero secret material in the body.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_dockerfile_uses_python_314_and_nonroot():
    text = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "python:3.14" in text
    assert "python:3.11" not in text
    assert "USER zen" in text
    assert "zen.lab" in text


def test_lab_compose_does_not_publish_database_ports():
    text = (ROOT / "docker-compose.lab.yml").read_text(encoding="utf-8")
    assert "5432:5432" not in text
    assert "6379:6379" not in text
    assert "8080" in text
    assert "zen-lab" in text


def test_lab_health_and_scan_never_echo_secrets(monkeypatch):
    from zen.lab.app import dispatch

    fake_github = "ghp_" + ("a" * 36)
    fake_or = "sk-or-v1-" + ("x" * 40)
    monkeypatch.setenv("GITHUB_TOKEN", fake_github)
    monkeypatch.setenv("OPENROUTER_API_KEY", fake_or)

    status, _headers, body = dispatch("GET", "/health")
    assert status == 200
    payload = json.loads(body)
    assert payload["ok"] is True
    assert fake_github not in body
    assert fake_or not in body

    status, _headers, body = dispatch("GET", "/auth/status")
    assert status in {200, 401, 403, 503}
    assert fake_github not in body
    assert fake_or not in body

    status, _headers, body = dispatch("GET", "/scan")
    assert status in {200, 503}
    report = json.loads(body)
    assert "auth" in report
    assert "secrets" in report
    assert "env_doctor" in report
    dumped = json.dumps(report)
    assert fake_github not in dumped


def test_lab_unknown_route_is_404():
    from zen.lab.app import dispatch

    status, _, body = dispatch("GET", "/nope")
    assert status == 404
    assert "ghp_" not in body


def test_deploy_manifests_exist():
    fly = (ROOT / "deploy" / "fly.toml").read_text(encoding="utf-8")
    render = (ROOT / "deploy" / "render.yaml").read_text(encoding="utf-8")
    assert "8080" in fly
    assert "zenos" in fly.lower() or "zen-lab" in fly
    assert "8080" in render
