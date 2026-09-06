"""Regression: ModelBench fighter construction, SPECIAL path, and DEFEND correctness."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

_MODELS_FIXTURE = {
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


def _make_bench(tmp_path: Path, models: dict | None = None) -> "ModelBench":  # noqa: F821
    from zen.dex.bench import ModelBench

    dex_dir = tmp_path / "dex"
    dex_dir.mkdir(exist_ok=True)
    (dex_dir / "models.yaml").write_text(
        yaml.dump(models or _MODELS_FIXTURE), encoding="utf-8"
    )
    return ModelBench(dex_path=dex_dir)


def test_model_bench_create_fighter_and_special_move(tmp_path: Path):
    from zen.dex.bench import BattleMove

    bench = _make_bench(tmp_path)
    fighter = bench.create_fighter("test-model-a")
    assert fighter is not None
    assert fighter.feats == ["Deep Context", "Code Master"]

    dmg = bench.calculate_damage(fighter, BattleMove.SPECIAL, fighter)
    assert dmg > 0

    result = bench.battle("test-model-a", "test-model-b")
    assert "winner" in result


def test_defend_boost_does_not_compound_across_turns(tmp_path: Path):
    """DEFEND multiplies defense within the turn it is used but must reset between turns.

    Bug: calculate_damage() executed `attacker.defense *= 1.5` and never restored
    the value.  After N DEFEND uses the fighter's defense was ~(1.5**N) * base,
    making them nearly immune to damage and producing wrong battle results.

    Fix: battle_turn() snapshots each fighter's defense before any attack in the
    turn and restores it afterwards, so the boost is visible to that turn's
    incoming hit but does not accumulate.
    """
    from zen.dex.bench import BattleMove

    # Use a model with high cost_per_1k so `cost` stat is LOW (< attack),
    # which causes choose_move() to select DEFEND (not COST_DRAIN) at low HP.
    models = {
        "models": [
            {
                "id": "defender",
                "name": "Defender",
                "tier": "common",
                "stats": {"intelligence": 70, "reliability": 70, "speed": 50},
                "feats": [],
                # cost_per_1k.input = 5.0 → cost stat ≈ 5, well below attack ≈ 70
                # → choose_move picks DEFEND (not COST_DRAIN) when HP < 30 %
                "cost_per_1k": {"input": 5.0},
            },
            {
                "id": "attacker",
                "name": "Attacker",
                "tier": "common",
                "stats": {"intelligence": 50, "reliability": 50, "speed": 40},
                "feats": [],
                "cost_per_1k": {"input": 0.001},
            },
        ]
    }

    bench = _make_bench(tmp_path, models)
    f_def = bench.create_fighter("defender")
    f_att = bench.create_fighter("attacker")

    # Artificially drop defender's HP below the 30 % threshold so
    # choose_move() reliably selects DEFEND.
    f_def.hp = 1  # 1/100 HP = 1 % < 30 %

    baseline_defense = f_def.defense

    # Verify pre-condition: with cost < attack, DEFEND is chosen at low HP.
    chosen = bench.choose_move(f_def, f_att)
    assert chosen == BattleMove.DEFEND, (
        f"Pre-condition failed: expected DEFEND but got {chosen}. "
        f"cost={f_def.cost}, attack={f_def.attack}"
    )

    # Run several turns; defense must equal baseline after every turn.
    for turn in range(5):
        if not f_def.is_alive or not f_att.is_alive:
            break
        f_def.hp = max(f_def.hp, 1)  # keep defender barely alive so DEFEND fires
        bench.battle_turn(f_def, f_att)
        assert f_def.defense == baseline_defense, (
            f"Turn {turn + 1}: DEFEND permanently boosted defense "
            f"(expected {baseline_defense}, got {f_def.defense}). "
            "battle_turn() must restore the baseline defense after each turn."
        )
