"""OpenRouter pricing strings must parse to numbers before numeric ops."""

from __future__ import annotations

import pytest

from zen.dex.openrouter_sync import (
    ModelAPIStats,
    ModelBenchStats,
    OpenRouterSync,
    _safe_float,
)


@pytest.mark.parametrize(
    ("value", "default", "expected"),
    [
        (None, 0.0, 0.0),
        ("", 0.001, 0.001),
        ("0.0000015", 0.0, 0.0000015),
        ("  0.002  ", 0.0, 0.002),
        (0, 0.001, 0.0),
        (0.001, 0.0, 0.001),
        ("not-a-number", 0.001, 0.001),
        ({}, 0.0, 0.0),
        ([], 1.5, 1.5),
    ],
)
def test_safe_float_parses_or_falls_back(value, default, expected):
    assert _safe_float(value, default=default) == pytest.approx(expected)


def test_model_bench_stats_accept_string_pricing():
    api_stats = ModelAPIStats(
        id="vendor/test-model",
        name="Test Model",
        pricing={"prompt": "0.001", "completion": "0.002"},
        context_length=8000,
        top_provider={},
        architecture={},
    )
    stats = ModelBenchStats.calculate(
        api_stats,
        {"intelligence": 70, "reliability": 75, "speed": 80, "feats": []},
    )
    assert stats.cost == 99


def test_model_bench_stats_missing_prompt_uses_default_cost():
    api_stats = ModelAPIStats(
        id="vendor/free-model",
        name="Free Model",
        pricing={},
        context_length=4096,
        top_provider={},
        architecture={},
    )
    stats = ModelBenchStats.calculate(api_stats, {"feats": []})
    # default prompt 0.001 -> cost = 100 - min(1.0, 95) = 99
    assert stats.cost == 99


def test_determine_tier_compares_string_prompt_cost():
    sync = OpenRouterSync(api_key="test-key")
    assert sync.determine_tier("vendor/budget", {"prompt": "0.0005"}) == "uncommon"
    assert sync.determine_tier("vendor/mid", {"prompt": "0.005"}) == "rare"
    assert sync.determine_tier("vendor/free", {"prompt": None}) == "common"
    assert sync.determine_tier("vendor/broken", {"prompt": "n/a"}) == "common"


def test_cost_per_1k_multiplies_parsed_string_prices():
    prompt = _safe_float("0.0000015", default=0.0) * 1000
    completion = _safe_float("0.000006", default=0.0) * 1000
    assert prompt == pytest.approx(0.0015)
    assert completion == pytest.approx(0.006)
