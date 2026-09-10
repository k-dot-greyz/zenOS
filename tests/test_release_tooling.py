"""Release tooling contracts: standard-version updaters and bumpFiles paths."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT_UPDATER = ROOT / "scripts" / "python-version-updater.js"
INIT_UPDATER = ROOT / "scripts" / "python-init-updater.js"


def test_standard_version_bump_files_point_at_real_updaters():
    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    bump_files = package["standard-version"]["bumpFiles"]
    paths = {entry["filename"]: ROOT / entry["updater"] for entry in bump_files}
    assert "pyproject.toml" in paths
    assert "zen/__init__.py" in paths
    for updater in paths.values():
        assert updater.is_file(), f"missing updater: {updater}"


@pytest.mark.parametrize(
    ("updater", "sample", "expected"),
    [
        (
            PYPROJECT_UPDATER,
            '[project]\nname = "zenos"\nversion = "0.1.0"\n',
            "0.1.0",
        ),
        (
            INIT_UPDATER,
            '"""zenOS"""\n\n__version__ = "0.1.0"\n',
            "0.1.0",
        ),
    ],
)
def test_standard_version_updaters_round_trip(updater: Path, sample: str, expected: str):
    node = subprocess.run(["node", "-v"], capture_output=True, text=True, check=False)
    if node.returncode != 0:
        pytest.skip("node is required to exercise standard-version JS updaters")

    script = f"""
const updater = require({json.dumps(str(updater))});
const sample = {json.dumps(sample)};
const current = updater.readVersion(sample);
if (current !== {json.dumps(expected)}) {{
  console.error('readVersion mismatch', current);
  process.exit(2);
}}
const next = updater.writeVersion(sample, "1.2.3");
const bumped = updater.readVersion(next);
if (bumped !== "1.2.3") {{
  console.error('writeVersion mismatch', bumped, next);
  process.exit(3);
}}
"""
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr + result.stdout
