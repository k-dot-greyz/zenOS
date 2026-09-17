# keel layouts

These are frozen. Changing them breaks IR files and goldens.

## Planar audio

```
io.ch[c][0..n]   // f32, 16-byte aligned preferred
```

Not interleaved `[L,R,L,R,…]` inside kernels.

## r2c packing (Hermitian interleaved `N+2`)

This is FFTW `r2c` / `scipy.fft.rfft` stored as interleaved `re,im` of length `N+2`. It is **not** FFTW `r2hc` (length `N` reals).

For real length `N`:

- output length `N/2 + 1` complex bins stored as interleaved `re,im` f32: `[re0, im0=0, re1, im1, …, reNyq, imNyq=0]`
- DC and Nyquist imaginary parts are zero

Full-complex `c2c` uses interleaved `2N` (`[re0, im0, …, re_{N-1}, im_{N-1}]`). Forward unnormalized; `c2c_inv` includes `1/N`.

`c2r` consumes the same layout. Scaling: forward unnormalized; inverse divides by `N` at the call site or documents `1/N` in the inverse kernel — pick one in the first FFT PR and do not flip it.

**Decision for keel:** inverse includes `1/N` so roundtrip energy is ~1. Document in `keel-fft` rustdoc.

## Alignment

- Buffers passed to NEON loads: 16-byte aligned when we allocate them
- Unaligned guest slices: scalar prelude, then aligned body
