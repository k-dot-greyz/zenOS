"""Regression: ModelBench fighter construction and SPECIAL path use feats."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_model_bench_create_fighter_and_special_move(tmp_path: Path):
    from zen.dex.bench import BattleMove, ModelBench

    models = {
        "models": [
            {
                "id": "test-model-a",
                "name": "Test A",
                "tier": "rare",
                "stats": {"intelligence": 80, "reliability": 70, "speed": 60},
                "feats": ["Deep Context", "Code Master"],
                "cost_per_1k": {"input": 0.001},
            },
            {
                "id": "test-model-b",
                "name": "Test B",
                "tier": "common",
                "stats": {"intelligence": 50, "reliability": 50, "speed": 50},
                "feats": ["Quick Response"],
                "cost_per_1k": {"input": 0.0001},
            },
        ]
    }
    dex_dir = tmp_path / "dex"
    dex_dir.mkdir()
    (dex_dir / "models.yaml").write_text(yaml.dump(models), encoding="utf-8")

    bench = ModelBench(dex_path=dex_dir)
    fighter = bench.create_fighter("test-model-a")
    assert fighter is not None
    assert fighter.feats == ["Deep Context", "Code Master"]

    dmg = bench.calculate_damage(fighter, BattleMove.SPECIAL, fighter)
    assert dmg > 0

    result = bench.battle("test-model-a", "test-model-b")
    assert "winner" in result
