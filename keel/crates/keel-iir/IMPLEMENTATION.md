# keel-iir implementation — #75

Blocked on #74.

- [ ] `Sos` goldens vs scipy.signal.sosfilt
- [ ] Separate state from coeffs; multi-channel shared coeffs
- [ ] NEON `Bank` across channels (4-wide)
- [ ] Block-boundary coeff swap
- [ ] Optional TPT SVF stub
