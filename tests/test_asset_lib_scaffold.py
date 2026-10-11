"""Asset-lib scaffold: dex banks + explicit language buckets (no generic shell)."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
BANKS = ROOT / "dex" / "banks.yaml"

EXPECTED_BANKS = ("kernel", "ops", "dev", "agents", "audio")
EXPECTED_KINDS = ("modules", "components", "projects", "scripts")
# No generic "shell" / "sh" — dialect must be named.
FORBIDDEN_LANG_DIRS = ("shell", "sh")
REQUIRED_LANGS = ("python", "rust", "bash", "termux-bash", "powershell", "javascript")


def _banks() -> dict:
    assert BANKS.is_file(), "dex/banks.yaml is the scaffold contract"
    return yaml.safe_load(BANKS.read_text(encoding="utf-8"))


def test_banks_yaml_maps_dev_master_midi_ids():
    data = _banks()
    by_dir = {b["dir"]: b for b in data["banks"]}
    assert set(by_dir) == set(EXPECTED_BANKS)
    assert by_dir["kernel"]["id"] == "0x7F"
    assert by_dir["ops"]["id"] == "0x7E"
    assert by_dir["dev"]["id"] == "0x7D"
    assert by_dir["agents"]["id"] == "0x7C"
    assert by_dir["audio"]["id"] == "0x7B"


def test_languages_name_specific_shells_not_generic_shell():
    langs = _banks()["languages"]
    for forbidden in FORBIDDEN_LANG_DIRS:
        assert forbidden not in langs, forbidden
    for required in REQUIRED_LANGS:
        assert required in langs, required
    assert langs["bash"]["family"] == "bash"
    assert langs["termux-bash"]["family"] == "bash"
    assert langs["powershell"]["family"] == "powershell"


def test_each_dex_bank_has_asset_lib_shape():
    for bank in EXPECTED_BANKS:
        root = ROOT / "dex" / bank
        assert root.is_dir(), bank
        for kind in EXPECTED_KINDS:
            kind_dir = root / kind
            assert kind_dir.is_dir(), f"{bank}/{kind}"
            for forbidden in FORBIDDEN_LANG_DIRS:
                assert not (kind_dir / forbidden).exists(), f"{bank}/{kind}/{forbidden}"
            assert (kind_dir / "python").is_dir(), f"{bank}/{kind}/python"
            assert (kind_dir / "rust").is_dir(), f"{bank}/{kind}/rust"
            if kind != "modules":
                assert (kind_dir / "bash").is_dir(), f"{bank}/{kind}/bash"
        assert (root / "modules" / "agnostic").is_dir(), bank
        assert (root / "schemas").is_dir(), bank


def test_runtime_catalog_stays_at_dex_root():
    assert (ROOT / "dex" / "models.yaml").is_file()
    assert (ROOT / "dex" / "procedures.yaml").is_file()


def test_ops_bash_and_python_scripts_moved_with_shims():
    assert (ROOT / "dex" / "ops" / "scripts" / "bash" / "zenos-env-install.sh").is_file()
    assert (ROOT / "dex" / "ops" / "scripts" / "bash" / "zenos-env-start.sh").is_file()
    assert (ROOT / "dex" / "ops" / "scripts" / "python" / "check_no_legacy_branding.py").is_file()
    # Old paths remain as compatibility shims so docs / Cloud env keep working.
    assert (ROOT / "scripts" / "zenos-env-install.sh").is_file()
    assert (ROOT / "scripts" / "zenos-env-start.sh").is_file()
