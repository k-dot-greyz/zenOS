#!/usr/bin/env python3
"""Generate scipy.signal.sosfilt goldens for keel-iir. Runtime tests do not import scipy."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfilt

FS = 48000.0
N = 256
F_SINE = 1000.0


def impulse(n: int) -> np.ndarray:
    x = np.zeros(n, dtype=np.float64)
    x[0] = 1.0
    return x


def sine(n: int, freq: float, fs: float) -> np.ndarray:
    t = np.arange(n, dtype=np.float64) / fs
    return np.sin(2.0 * np.pi * freq * t)


def pack_sos(sos: np.ndarray) -> list[list[float]]:
    # scipy: [b0, b1, b2, a0, a1, a2] per section
    return [[float(v) for v in row] for row in sos]


def run_case(name: str, sos: np.ndarray) -> dict:
    x_imp = impulse(N)
    x_sin = sine(N, F_SINE, FS)
    y_imp = sosfilt(sos, x_imp)
    y_sin = sosfilt(sos, x_sin)
    return {
        "name": name,
        "sos": pack_sos(sos),
        "impulse_in": x_imp.astype(np.float64).tolist(),
        "impulse_out": y_imp.astype(np.float64).tolist(),
        "sine_in": x_sin.astype(np.float64).tolist(),
        "sine_out": y_sin.astype(np.float64).tolist(),
    }


def main() -> None:
    cases = [
        run_case("butter_lpf_1sec", butter(2, 1000, btype="low", fs=FS, output="sos")),
        run_case("butter_lpf_2sec", butter(4, 1000, btype="low", fs=FS, output="sos")),
        run_case("butter_lpf_12sec", butter(24, 1000, btype="low", fs=FS, output="sos")),
    ]
    payload = {"fs": FS, "n": N, "f_sine": F_SINE, "max_abs_err": 1e-5, "cases": cases}
    out = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "sosfilt_goldens.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"wrote {out} ({len(cases)} cases, n={N})")
    for c in cases:
        print(f"  {c['name']}: {len(c['sos'])} sections")


if __name__ == "__main__":
    main()
