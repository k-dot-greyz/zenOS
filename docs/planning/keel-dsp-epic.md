# Epic: keel DSP stack

**Issue:** #73  
**Integration branch:** `dev-master`  
**Umbrella PR branch:** `feat/keel-dsp`

Linux-first, ARM-native (NEON home ISA), f32 audio-thread kernels for zenOS `reference` and later CLAP plugins.

This is the engine. It is not the headphone catalog, Farina ritual, or target-curve product.

## Child issues

| Issue | Module | Branch |
|---|---|---|
| #74 | `keel-core` | `feat/keel-core` |
| #75 | `keel-iir` | `feat/keel-iir` |
| #76 | `keel-fft` | `feat/keel-fft` |
| #77 | `keel-fir` | `feat/keel-fir` |
| #78 | `keel-conv` | `feat/keel-conv` |
| #79 | `keel-design` | `feat/keel-design` |

## Order

1. core (law) → 2. iir → 3. fft → 4. fir → 5. conv → 6. design

## Gates before anything lands on `main`

- Goldens vs SciPy / PocketFFT as documented per crate
- Debug alloc guard clean in `process`
- 48 kHz / 64 stereo, 12 SOS + 65k uniform conv, p99 < 50% quantum on Pi-class A76
- Default features: no GPL, no ArmPL

See `docs/blueprints/keel/`.
