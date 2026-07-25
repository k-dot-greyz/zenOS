#!/usr/bin/env python3
"""
Environment setup resilience tests.

These scenarios simulate real failure modes that Cloud Agents and developers
can hit when bootstrapping or re-running the zenOS install script. Each test
creates a broken precondition, runs a targeted recovery step, and asserts the
environment converges to a healthy state.

Run with: pytest tests/test_env_setup_resilience.py -v --no-cov
"""

import json
import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
VENV = ROOT / ".venv"
SETUP_PY = ROOT / "setup.py"
SETUP_BAK = ROOT / "_setup.py.bak"
ENV_JSON = ROOT / ".cursor" / "environment.json"


def _pip(*args, check=True):
    """Run pip inside the venv."""
    pip_bin = VENV / "bin" / "pip"
    if not pip_bin.exists():
        pytest.fail(f"pip binary missing at {pip_bin} — venv is broken")
    return subprocess.run(
        [str(pip_bin), *args],
        capture_output=True, text=True, check=check, cwd=str(ROOT),
    )


def _python(*args, check=True):
    """Run python inside the venv."""
    py_bin = VENV / "bin" / "python"
    if not py_bin.exists():
        pytest.fail(f"python binary missing at {py_bin} — venv is broken")
    return subprocess.run(
        [str(py_bin), *args],
        capture_output=True, text=True, check=check, cwd=str(ROOT),
    )


def _run_install_script():
    """Run the install script from environment.json in bash."""
    script = json.loads(ENV_JSON.read_text())["install"]
    return subprocess.run(
        ["bash", "-c", script],
        capture_output=True, text=True, cwd=str(ROOT),
    )


def _assert_core_imports():
    """Assert that zen core modules are importable."""
    r = _python("-c", textwrap.dedent("""\
        import zen
        from zen.core.agent import Agent, AgentRegistry
        from zen.core.launcher import Launcher
        from zen.core.critique import AutoCritique
        from zen.plugins import PluginRegistry
        from zen.agents import builtin_agents
        print(f"OK v{zen.__version__} agents={list(builtin_agents.keys())}")
    """))
    assert r.returncode == 0, f"Core import failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "OK v" in r.stdout


def _ensure_healthy_venv():
    """Guarantee a working venv exists — used by fixtures."""
    if not (VENV / "bin" / "python").exists():
        if VENV.exists():
            shutil.rmtree(VENV)
        r = _run_install_script()
        assert r.returncode == 0, f"Venv recovery failed:\n{r.stderr}"


@pytest.fixture(autouse=True)
def _restore_setup_py():
    """Ensure setup.py is always restored after each test."""
    original = SETUP_PY.read_text() if SETUP_PY.exists() else None
    yield
    if SETUP_BAK.exists():
        if not SETUP_PY.exists():
            SETUP_BAK.rename(SETUP_PY)
        else:
            SETUP_BAK.unlink()
    if original and not SETUP_PY.exists():
        SETUP_PY.write_text(original)


@pytest.fixture()
def healthy_venv():
    """Ensure venv is healthy before AND after the test."""
    _ensure_healthy_venv()
    yield
    _ensure_healthy_venv()


# ---------------------------------------------------------------------------
# Scenario 1: setup.py left renamed after an interrupted install
# ---------------------------------------------------------------------------
class TestSetupPyOrphan:
    """If the install script crashes between the mv and the restore,
    setup.py is gone and only _setup.py.bak exists. The next run must
    recover gracefully."""

    def test_orphan_bak_is_restored(self, healthy_venv):
        """Simulate: setup.py is missing, _setup.py.bak exists."""
        assert SETUP_PY.exists(), "Precondition: setup.py must exist"
        original = SETUP_PY.read_text()

        SETUP_PY.rename(SETUP_BAK)
        assert not SETUP_PY.exists()
        assert SETUP_BAK.exists()

        r = _run_install_script()

        assert SETUP_PY.exists(), (
            "Install script did not restore setup.py from _setup.py.bak"
        )
        assert SETUP_PY.read_text() == original

    def test_both_exist_prefers_original(self, healthy_venv):
        """If both setup.py AND _setup.py.bak exist (weird state),
        setup.py should remain untouched after install."""
        assert SETUP_PY.exists()
        original = SETUP_PY.read_text()

        SETUP_BAK.write_text("# stale backup")

        r = _run_install_script()

        assert SETUP_PY.exists()
        assert SETUP_PY.read_text() == original
        assert not SETUP_BAK.exists(), (
            "Stale _setup.py.bak should be cleaned up after install"
        )


# ---------------------------------------------------------------------------
# Scenario 2: undeclared deps missing — the aiofiles/psutil gap
# ---------------------------------------------------------------------------
class TestUndeclaredDeps:
    """aiofiles and psutil are imported by zen but not declared in
    pyproject.toml [project.dependencies]. If they're missing, core
    imports must fail. The install script must fix this."""

    @pytest.mark.parametrize("pkg", ["aiofiles", "psutil"])
    def test_missing_undeclared_dep_breaks_import(self, pkg, healthy_venv):
        """Removing an undeclared dep should break the import chain.
        Re-running the install script should fix it."""
        _pip("uninstall", "-y", pkg, check=False)

        r = _python("-c", f"import {pkg}", check=False)
        assert r.returncode != 0, (
            f"{pkg} should not be importable after uninstall"
        )

        r = _run_install_script()
        assert r.returncode == 0, (
            f"Install script failed after {pkg} removal:\n{r.stderr}"
        )

        r = _python("-c", f"import {pkg}", check=False)
        assert r.returncode == 0, (
            f"Install script did not reinstall {pkg}"
        )

        _assert_core_imports()


# ---------------------------------------------------------------------------
# Scenario 3: stale / corrupt venv
# ---------------------------------------------------------------------------
class TestStaleVenv:
    """A .venv directory exists but is broken — missing pip binary,
    corrupted pyvenv.cfg, or just empty. The install script should
    still converge."""

    def test_venv_missing_pip_binary(self):
        """Delete the pip binary inside the venv and re-run install.
        The improved script checks .venv/bin/python, not just -d .venv,
        so a missing pip alone may still work if python is intact.
        But deleting python should trigger recreation."""
        py_bin = VENV / "bin" / "python"
        if not py_bin.exists():
            pytest.skip("python binary not found — venv may not exist yet")

        py_bin.unlink()
        assert not py_bin.exists()

        r = _run_install_script()
        assert r.returncode == 0, f"Install failed after python deletion:\n{r.stderr}"
        assert py_bin.exists(), "python binary not restored"
        _assert_core_imports()

    def test_venv_corrupted_pyvenv_cfg(self):
        """Corrupt pyvenv.cfg to point at a nonexistent Python."""
        cfg = VENV / "pyvenv.cfg"
        if not cfg.exists():
            _ensure_healthy_venv()

        cfg.write_text("home = /nonexistent/python\n")

        r = _run_install_script()
        assert r.returncode == 0, f"Install failed with corrupt pyvenv.cfg:\n{r.stderr}"
        _assert_core_imports()

    def test_venv_is_empty_directory(self):
        """An empty .venv directory (no bin/, no lib/). Install should
        detect it's not a real venv and recreate."""
        if VENV.exists():
            shutil.rmtree(VENV)

        VENV.mkdir()
        assert not (VENV / "bin").exists()

        r = _run_install_script()
        assert r.returncode == 0, f"Install failed with empty .venv dir:\n{r.stderr}"
        _assert_core_imports()


# ---------------------------------------------------------------------------
# Scenario 4: build isolation chicken-egg (verify the problem exists)
# ---------------------------------------------------------------------------
class TestBuildIsolation:
    """pip install -e . WITH build isolation fails because setup.py
    triggers zen.__init__ -> zen.core.agent -> import yaml, and yaml
    isn't in the isolated build env. This test documents the problem
    and verifies our workaround (--no-build-isolation) is necessary."""

    def test_editable_install_with_isolation_fails(self, healthy_venv):
        """Standard `pip install -e .` should fail due to setup.py
        importing the package during the build."""
        r = subprocess.run(
            [str(VENV / "bin" / "pip"), "install", "-e", "."],
            capture_output=True, text=True, check=False, cwd=str(ROOT),
        )
        assert r.returncode != 0, (
            "pip install -e . should fail with build isolation "
            "(setup.py imports zen package which needs yaml in build env)"
        )
        assert "ModuleNotFoundError" in r.stderr or "error" in r.stderr.lower()

    def test_workaround_succeeds(self, healthy_venv):
        """Our workaround: rename setup.py, use --no-build-isolation."""
        original = SETUP_PY.read_text()
        SETUP_PY.rename(SETUP_BAK)
        try:
            r = subprocess.run(
                [str(VENV / "bin" / "pip"), "install",
                 "--no-build-isolation", "-e", ".[dev]"],
                capture_output=True, text=True, check=False, cwd=str(ROOT),
            )
            assert r.returncode == 0, (
                f"Workaround install failed:\n{r.stderr}"
            )
        finally:
            if SETUP_BAK.exists():
                SETUP_BAK.rename(SETUP_PY)

        _assert_core_imports()


# ---------------------------------------------------------------------------
# Scenario 5: full idempotency — dirty state then double-run
# ---------------------------------------------------------------------------
class TestIdempotency:
    """Run the install script twice in a row. The second run must
    succeed even when the first left everything in a 'done' state."""

    def test_consecutive_runs_converge(self, healthy_venv):
        """Two back-to-back install script runs should both exit 0."""
        r1 = _run_install_script()
        assert r1.returncode == 0, f"First run failed:\n{r1.stderr}"

        r2 = _run_install_script()
        assert r2.returncode == 0, f"Second run failed:\n{r2.stderr}"

        _assert_core_imports()

    def test_after_dep_downgrade(self, healthy_venv):
        """Downgrade a dep, then re-run install. It should upgrade
        back to the required version."""
        _pip("install", "click==8.0.0", "-q", check=False)

        r = _run_install_script()
        assert r.returncode == 0, f"Install failed:\n{r.stderr}"

        ver = _python(
            "-c", "import click; print(click.__version__)", check=False
        )
        assert ver.returncode == 0
        installed = ver.stdout.strip()
        assert tuple(int(x) for x in installed.split(".")) >= (8, 0, 0)

        _assert_core_imports()

    def test_after_uninstalling_editable_package(self, healthy_venv):
        """Uninstall zenos, re-run install, verify package metadata is back.
        Note: `import zen` still works after uninstall because Python adds
        cwd to sys.path and the zen/ source dir is right here. So we check
        pip metadata instead."""
        _pip("uninstall", "-y", "zenos", check=False)

        r = _pip("show", "zenos", check=False)
        assert r.returncode != 0, "zenos package metadata should be gone"

        r = _run_install_script()
        assert r.returncode == 0, f"Install failed:\n{r.stderr}"

        r = _pip("show", "zenos", check=False)
        assert r.returncode == 0, "zenos package metadata not restored"
        assert "zenos" in r.stdout.lower()

        _assert_core_imports()


# ---------------------------------------------------------------------------
# Scenario 6: environment.json contract — schema and field validation
# ---------------------------------------------------------------------------
class TestEnvironmentJsonContract:
    """Verify .cursor/environment.json is well-formed and the install
    field meets our expectations."""

    def test_valid_json(self):
        data = json.loads(ENV_JSON.read_text())
        assert "install" in data
        assert isinstance(data["install"], str)

    def test_has_name(self):
        data = json.loads(ENV_JSON.read_text())
        assert "name" in data
        assert isinstance(data["name"], str)
        assert len(data["name"]) > 0

    def test_install_script_is_non_empty(self):
        data = json.loads(ENV_JSON.read_text())
        assert len(data["install"].strip()) > 0

    def test_install_script_has_venv_creation(self):
        script = json.loads(ENV_JSON.read_text())["install"]
        assert "venv" in script

    def test_install_script_validates_venv_health(self):
        """Must check for executable python, not just directory existence."""
        script = json.loads(ENV_JSON.read_text())["install"]
        assert ".venv/bin/python" in script, (
            "Install script should check for .venv/bin/python, not just -d .venv"
        )

    def test_install_script_has_setup_py_workaround(self):
        script = json.loads(ENV_JSON.read_text())["install"]
        assert "_setup.py.bak" in script
        assert "mv setup.py" in script or "mv _setup.py.bak" in script

    def test_install_script_uses_no_build_isolation(self):
        script = json.loads(ENV_JSON.read_text())["install"]
        assert "--no-build-isolation" in script

    def test_install_script_installs_undeclared_deps(self):
        script = json.loads(ENV_JSON.read_text())["install"]
        assert "aiofiles" in script
        assert "psutil" in script

    def test_no_secrets_in_environment_json(self):
        """environment.json must never contain tokens or keys."""
        raw = ENV_JSON.read_text().lower()
        for pattern in ["sk-", "api_key", "password", "secret", "token"]:
            assert pattern not in raw, (
                f"Possible secret '{pattern}' found in environment.json"
            )

    def test_no_startup_commands_in_install(self):
        """install must not contain service startup commands."""
        script = json.loads(ENV_JSON.read_text())["install"].lower()
        for cmd in ["docker compose up", "docker-compose up",
                     "npm run dev", "pnpm dev", "python manage.py runserver"]:
            assert cmd not in script, (
                f"Service startup command '{cmd}' found in install script"
            )
