# keel-fft implementation — #76

## Done in this PR (scaffold)

- Frozen layout helpers (`packed_len` = `N + 2` interleaved half-complex)
- `FftPlan::new` allocates twiddles (prepare / main thread)
- Scalar radix-2 r2c / c2r, inverse includes `1/N`
- Caller-owned scratch (`2N` f32)
- `Rt` token on the hot path
- Unit tests: impulse, cosine bin, roundtrip on every `AUDIO_SIZE`
- `backend::neon` hook that still calls scalar (replace the butterfly, keep the packing)

## Still open

- [ ] Handwritten NEON radix-4/8 for 256..4096
- [ ] PocketFFT / SciPy CI goldens on aarch64 (`< 5e-5`)
- [ ] rustfft fallback only if we ever accept non-`AUDIO_SIZES`
- [ ] No `sin`/`cos` rebuild on the audio thread (already true)
- [ ] ArmPL stays feature-gated and off
