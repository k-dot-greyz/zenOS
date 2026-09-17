# keel

Permissive DSP substrate for zenOS and CLAP.

```
plugins / zenOS / measure
        ↓
   keel-dsp (optional linear chain)
        ↓
keel-conv  keel-iir  keel-fir  keel-fft
        ↓
              keel-core
```

- **Home ISA:** `aarch64-unknown-linux-gnu` + NEON
- **Home dtype:** f32 on the audio thread; f64 only in `keel-design`
- **Home caller:** CLAP `process()` / zenOS audio path
- **License intent:** MIT OR Apache-2.0
- **Not the product:** measurement, PAPFR, systemwide drivers

If a crate above `keel-core` allocates in `process`, imports a plugin framework, or does I/O, the architecture is already dead.

## Docs

- [law.md](law.md) — realtime contract
- [layout.md](layout.md) — planar buffers + r2c packing
- [isa.md](isa.md) — ARM backends
- [roadmap.md](roadmap.md) — order and OSS bar
