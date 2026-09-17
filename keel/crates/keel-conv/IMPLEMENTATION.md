# keel-conv implementation — #78

Blocked on #76 (`keel-fft` r2c/c2r) and #77 (`keel-fir` TD `process`).
Sibling PRs: #83, #84. Do not land OLS until those kernels transform.

- [x] `Kernel` contract: `prepare` / `reset` / `process` (identity until IR plan)
- [x] Head tap clamp 32..=128; `latency_samples() == head length`
- [x] `load_ir` on main thread (returns Err until FFT/FIR exist)
- [ ] Uniform OLS, partition == max_block (needs #76)
- [ ] TD head 32..128 taps in `process` (needs #77)
- [ ] IR swap: new plan, atomic pointer at block boundary, free old on main
- [ ] fftconvolve golden 65k IR, err < 1e-4 f32
- [ ] Alloc guard clean in `process` (needs #74 hook)
- [ ] Pi-class budget note in `benches/` (placeholder only)

Latency: documented as **head length in samples** (`Convolver::latency_samples`).
Year one: same thread for the tail. No worker pool.
