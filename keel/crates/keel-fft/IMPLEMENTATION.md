# keel-fft implementation — #76

## Done in this PR (scaffold)

- Frozen layout helpers: packed Hermitian `N + 2` (`packed_len`); full-complex interleaved `2N` (`complex_len`)
- `FftPlan::new` allocates 16-byte-aligned twiddles from f64 angles (prepare / main thread)
- Scalar radix-2 `r2c` / `c2r` / `c2c` / `c2c_inv`; inverses include `1/N`
- Caller-owned scratch (`2N` f32)
- `Rt` token on the hot path
- `backend()` reports `Scalar` until NEON butterflies are selected (hook module kept)
- Unit tests:
  - impulse + roundtrip on every `AUDIO_SIZE`
  - cosine bin 3 at N=64 (other bins ~0)
  - naive-DFT chirp oracle at N=64 and N=256 (`< 5e-5`)
  - `TimeLen` / `SpecLen` / `ScratchLen` buffer contract
  - 16-byte twiddle alignment
  - `c2c` roundtrip

## Still open

- [ ] Handwritten NEON radix-4/8 for 256..4096 (`backend::neon` is a dead hook)
- [ ] PocketFFT / SciPy CI goldens on aarch64 (`< 5e-5`)
- [ ] rustfft fallback only if we ever accept non-`AUDIO_SIZES`
- [ ] No `sin`/`cos` rebuild on the audio thread (already true)
- [ ] ArmPL stays feature-gated and off
- [ ] Do not close #76 from this scaffold
