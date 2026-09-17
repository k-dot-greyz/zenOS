# keel-design implementation — #79

Offline only. Never call from process(). f64 allowed. May allocate.

- [x] RBJ → keel_iir::Coeffs (LP/HP/peak/shelf/notch/allpass)
- [x] Butterworth SOS bilinear + pre-warp
- [x] Kirkeby + max-boost ceiling
- [x] Min-phase via cepstrum
- [x] Emit keel.sos / keel.ir (+ IEEE-float WAV)
- [x] SciPy goldens (`tests/issue79.rs`)
