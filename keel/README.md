# keel

ARM-native, Linux-first, f32 DSP kernels.

See `docs/blueprints/keel/` and epic #73.

**Toolchain:** Rust **1.85+** (edition 2024). This directory pins it via `rust-toolchain.toml`.

```bash
cd keel
rustc --version   # rustc 1.85.x
cargo test --workspace
```

Default features must stay GPL-free.
