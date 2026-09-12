# keel ISA

| Target | Year-one kernel | Notes |
|---|---|---|
| `aarch64-unknown-linux-gnu` | NEON handwritten | **Product.** Pi 5, phones, Termux, Graviton 2 |
| `aarch64` + SVE2 | optional later crate | Grace CI only |
| `aarch64-apple-darwin` | `vdsp` feature | Bind Accelerate. Do not fight AMX |
| `x86_64` | scalar, then AVX2 | CI convenience, not identity |
| Cortex-M | out of scope | CMSIS is a cousin |

Runtime detect once in `prepare`. Store fn pointers. No feature detect in the inner loop.

One shipping Linux ARM artifact: NEON. SVE is a second binary, not `#ifdef` soup in the FIR head.

`armpl` feature is **off by default**. EULA. Never the source of truth. Never in the default CLAP.
