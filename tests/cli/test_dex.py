from __future__ import annotations

from pathlib import Path

import yaml


def test_dex_models_and_procedures_from_cwd(runner, zen_cli, tmp_path, monkeypatch):
    dex = tmp_path / "dex"
    dex.mkdir()
    (dex / "models.yaml").write_text(
        yaml.dump(
            {
                "models": [
                    {"id": "t", "name": "Test", "tier": "common"},
                ]
            }
        ),
        encoding="utf-8",
    )
    (dex / "procedures.yaml").write_text(
        yaml.dump(
            {
                "procedures": [
                    {
                        "id": "zen.chat",
                        "name": "Basic Chat",
                        "tier": "common",
                        "type": "interactive",
                        "stats": {"complexity": 1},
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    models = runner.invoke(zen_cli, ["dex"])
    assert models.exit_code == 0
    procs = runner.invoke(zen_cli, ["dex", "procedures"])
    assert procs.exit_code == 0
    assert "Basic Chat" in procs.output
