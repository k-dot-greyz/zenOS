# keel-iir implementation — #75

Blocked on #74 for the full law crate. This PR carries the minimum `keel-core` surface IIR needs.

- [x] `Sos` goldens vs scipy.signal.sosfilt
- [x] Separate state from coeffs; multi-channel shared coeffs
- [x] NEON `Bank` across channels (4-wide)
- [x] Block-boundary coeff swap
- [x] Optional TPT SVF stub
