"""Mobile optimizer must yield the event loop during throttle sleeps."""

from __future__ import annotations

import asyncio
import time
from types import SimpleNamespace

import pytest

from zen.utils import mobile_optimizer as mobile_opt
from zen.utils.mobile_optimizer import optimize_for_mobile


class _FakeOptimizer:
    def __init__(self, sleep_s: float = 0.2) -> None:
        self.config = SimpleNamespace(max_tokens=500)
        self.battery = SimpleNamespace(get_optimal_model=lambda model: model)
        self._sleep_s = sleep_s

    def should_sleep(self) -> bool:
        return True

    def get_sleep_duration(self) -> float:
        return self._sleep_s


@pytest.fixture
def mobile_env(monkeypatch: pytest.MonkeyPatch) -> _FakeOptimizer:
    optimizer = _FakeOptimizer()
    monkeypatch.setenv("COMPACT_MODE", "1")
    monkeypatch.setattr(mobile_opt, "get_optimizer", lambda: optimizer)
    return optimizer


@pytest.mark.asyncio
async def test_optimize_for_mobile_uses_asyncio_sleep_not_time_sleep(
    mobile_env: _FakeOptimizer, monkeypatch: pytest.MonkeyPatch
) -> None:
    slept: list[float] = []

    async def fake_asyncio_sleep(delay: float) -> None:
        slept.append(delay)

    def fake_time_sleep(delay: float) -> None:
        raise AssertionError(f"blocking time.sleep({delay}) must not run in async wrapper")

    monkeypatch.setattr(mobile_opt.asyncio, "sleep", fake_asyncio_sleep)
    monkeypatch.setattr(mobile_opt.time, "sleep", fake_time_sleep)

    @optimize_for_mobile
    async def work() -> str:
        return "ok"

    assert await work() == "ok"
    assert slept == [mobile_env.get_sleep_duration()]


@pytest.mark.asyncio
async def test_optimize_for_mobile_sleep_lets_background_tasks_run(
    mobile_env: _FakeOptimizer,
) -> None:
    ticks: list[float] = []

    async def heartbeat() -> None:
        deadline = time.perf_counter() + mobile_env.get_sleep_duration()
        while time.perf_counter() < deadline:
            ticks.append(time.perf_counter())
            await asyncio.sleep(0.02)

    @optimize_for_mobile
    async def work() -> str:
        return "ok"

    result, _ = await asyncio.gather(work(), heartbeat())
    assert result == "ok"
    assert len(ticks) >= 3, f"event loop was blocked; only {len(ticks)} heartbeat ticks"
