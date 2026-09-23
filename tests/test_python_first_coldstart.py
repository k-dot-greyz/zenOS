"""Python-first coldstart: floor before pip; never import zen as health."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
_SCRIPT = _REPO / "scripts" / "python-first-coldstart.sh"
_ENSURE = _REPO / "scripts" / "ensure-python314.sh"
_INSTALL = _REPO / "install.sh"
_ENV_INSTALL = _REPO / "scripts" / "zenos-env-install.sh"
_ENV_START = _REPO / "scripts" / "zenos-env-start.sh"
_ENV = _REPO / ".cursor" / "environment.json"


def test_python_first_script_exists() -> None:
    assert _SCRIPT.is_file()
    assert _ENSURE.is_file()


def test_order_is_python_then_pip() -> None:
    text = _SCRIPT.read_text(encoding="utf-8")
    i_py = text.find("ensure-python314")
    i_pip = text.find("pip install")
    assert i_py != -1 and i_pip != -1 and i_py < i_pip
    assert "--ignore-requires-python" not in text
    assert "import zen" not in text
    assert '".[dev]"' in text
    assert ".[dev,mcp]" not in text
    assert ".[product]" not in text
    assert "n8n" not in text


def test_boot_paths_never_import_zen() -> None:
    for path in (_SCRIPT, _ENSURE, _INSTALL, _ENV_INSTALL, _ENV, _ENV_START):
        text = path.read_text(encoding="utf-8")
        assert "import zen" not in text, path.name
        assert "ignore-requires-python" not in text, path.name
        assert "psutil, requests" not in text, path.name


def test_environment_json_python_first_and_absolute_start() -> None:
    cfg = json.loads(_ENV.read_text(encoding="utf-8"))
    assert "python-first-coldstart.sh" in cfg["install"]
    assert "psutil" not in cfg["install"]
    start = cfg["start"]
    assert start.startswith("bash /workspace/")
    assert "zenos-env-start.sh" in start


def test_pyproject_cli_qol_only() -> None:
    text = (_REPO / "pyproject.toml").read_text(encoding="utf-8")
    assert 'requires-python = ">=3.14.7"' in text
    assert "[product]" in text or "product = [" in text
    deps, _, rest = text.partition("[project.optional-dependencies]")
    for name in ("aiohttp", "pydantic", "beautifulsoup4", "httpx", "psutil", "schedule"):
        assert name not in deps
        assert name in rest
