"""Regression tests for merge/CI crashers."""

from __future__ import annotations

from pathlib import Path

import pytest


def test_dex_catalog_handles_empty_yaml(tmp_path: Path):
    from zen.dex.catalog import DexCatalog

    dex_dir = tmp_path / "dex"
    dex_dir.mkdir()
    (dex_dir / "models.yaml").write_text("", encoding="utf-8")
    (dex_dir / "procedures.yaml").write_text("", encoding="utf-8")

    catalog = DexCatalog(base_path=dex_dir)
    assert catalog.models == {}
    assert catalog.selection_guide == {}
    assert catalog.combos == []


def test_pkm_statistics_include_cli_keys(tmp_path: Path):
    from zen.pkm.config import PKMConfig
    from zen.pkm.storage import PKMStorage

    pkm_dir = tmp_path / "pkm"
    config = PKMConfig(
        pkm_dir=pkm_dir,
        conversations_dir=pkm_dir / "conversations",
        knowledge_base_dir=pkm_dir / "knowledge_base",
        exports_dir=tmp_path / "pkm" / "exports",
    )
    stats = PKMStorage(config).get_statistics()
    for key in (
        "total_conversations",
        "conversations_count",
        "knowledge_entries_count",
        "conversations_dir",
        "knowledge_base_dir",
        "exports_dir",
        "total_size_mb",
    ):
        assert key in stats, key


def test_scheduler_default_jobs_accept_schedule_str(tmp_path: Path):
    from zen.pkm.config import PKMConfig
    from zen.pkm.scheduler import PKMScheduler

    pkm_dir = tmp_path / "pkm"
    config = PKMConfig(
        pkm_dir=pkm_dir,
        conversations_dir=pkm_dir / "conversations",
        knowledge_base_dir=pkm_dir / "knowledge_base",
        exports_dir=pkm_dir / "exports",
    )
    scheduler = PKMScheduler(config)
    scheduler.jobs.clear()
    scheduler._setup_default_jobs()
    assert "extract_conversations" in scheduler.jobs
    assert scheduler.jobs["extract_conversations"].schedule == config.cron_schedule


@pytest.mark.asyncio
async def test_tts_start_requires_engine():
    from tts_queue_system import TTSQueueManager

    manager = TTSQueueManager()
    with pytest.raises(RuntimeError, match="TTS engine is not configured"):
        await manager.start()
