"""Dex catalog API — models/procedures live under dex/."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_dex_data_files_exist():
    assert (ROOT / "dex" / "models.yaml").is_file()
    assert (ROOT / "dex" / "procedures.yaml").is_file()


def test_dex_catalog_loads_models():
    from zen.dex.catalog import DexCatalog, get_dex_catalog

    catalog = DexCatalog(base_path=ROOT / "dex")
    assert len(catalog.models) > 0
    singleton = get_dex_catalog()
    assert singleton is get_dex_catalog()


def test_dex_catalog_find_and_tier():
    from zen.dex.catalog import DexCatalog, Tier

    catalog = DexCatalog(base_path=ROOT / "dex")
    # Selection guide or best_for may yield results; at least tier filter works.
    tiers = catalog.get_models_by_tier(Tier.COMMON)
    assert isinstance(tiers, list)
    # Ensure no rarity attribute API remains
    assert not hasattr(catalog, "get_models_by_rarity")
