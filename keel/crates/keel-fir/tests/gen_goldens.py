//! Offline generator for `keel-fir` convolution goldens (issue #77).
//!
//! ```
//! python3 keel/crates/keel-fir/tests/gen_goldens.py
//! ```

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

OUT = Path(__file__).with_name("goldens.json")


def causal_fir(x: np.ndarray, h: np.ndarray) -> np.ndarray:
    y = np.empty_like(x, dtype=np.float32)
    n = int(h.shape[0])
    for i in range(len(x)):
        s = np.float32(0)
        for k in range(n):
            j = i - k
            if j >= 0:
                s += h[k] * x[j]
        y[i] = s
    return y


def main() -> None:
    rng = np.random.default_rng(77)
    goldens: dict[str, object] = {}
    for n in (16, 32, 64, 128, 256):
        h = rng.standard_normal(n).astype(np.float32)
        x = rng.standard_normal(96).astype(np.float32)
        goldens[str(n)] = {
            "taps": h.tolist(),
            "x": x.tolist(),
            "y": causal_fir(x, h).tolist(),
        }

    for n in (17, 32):
        half = rng.standard_normal((n + 1) // 2).astype(np.float32)
        h = np.zeros(n, dtype=np.float32)
        for k in range(n):
            h[k] = half[min(k, n - 1 - k)]
        x = rng.standard_normal(48).astype(np.float32)
        goldens[f"sym{n}"] = {
            "taps": h.tolist(),
            "x": x.tolist(),
            "y": causal_fir(x, h).tolist(),
        }

    n = 15
    h = np.zeros(n, dtype=np.float32)
    h[7] = 0.5
    for k in range(1, 8, 2):
        v = np.float32(0.25 / k)
        h[7 + k] = v
        h[7 - k] = v
    x = rng.standard_normal(40).astype(np.float32)
    full = causal_fir(x, h)
    goldens["hb15"] = {
        "taps": h.tolist(),
        "x": x.tolist(),
        "y_full": full.tolist(),
        "y_decim": full[0::2].tolist(),
    }
    OUT.write_text(json.dumps(goldens))
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
