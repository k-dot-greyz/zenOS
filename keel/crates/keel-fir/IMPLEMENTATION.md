# keel-fir implementation — #77

Blocked on #74 for alloc-guard / `Rt` hardening. This crate now ships the N≤256 TD head.

- [x] Duplicated delay line FirTd N≤256
- [x] NEON vfmaq inner loop (`cfg(target_arch = "aarch64")`, scalar tail)
- [x] Linear-phase symmetry path
- [x] FirHb half-band
- [x] numpy.convolve goldens
