# keel-fft implementation — #76

Blocked on #74.

- [ ] Freeze r2c layout (layout.md) + inverse 1/N
- [ ] NEON r2c/c2r for 256, 512, 1024, 2048, 4096
- [ ] Remaining AUDIO_SIZES
- [ ] PocketFFT goldens `< 5e-5`
- [ ] rustfft fallback only for unsupported N
