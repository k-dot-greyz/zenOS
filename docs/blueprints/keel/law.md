# keel law

## Four rules

1. **`process` is wait-free.** No alloc, lock, syscall, TLS growth, `format!`, or panic in release. Planning happens in `prepare(max_block, sr)` on the main thread (CLAP `activate`).
2. **f32 is native.** Audio path is `f32` only. `f64` lives in `keel-design`.
3. **Caller owns memory.** Every kernel declares `scratch_bytes` / `state_bytes`. You pass slices.
4. **Planar f32 internally.** `ch0[0..n], ch1[0..n], …` 16-byte aligned. Interleaved conversion is a plugin-edge adapter.

## Types

```rust
pub struct Rt<'a>(PhantomData<&'a ()>);

pub struct Prepare {
    pub sample_rate: f32,
    pub max_block: usize,
    pub channels: usize,
}

pub struct Needs { pub state: usize, pub scratch: usize }

pub trait Kernel {
    fn prepare(&mut self, p: Prepare) -> Result<Needs, Error>; // may alloc
    fn reset(&mut self);                                      // RT
    fn process(&mut self, rt: Rt<'_>, io: PlanarMut<'_>, scratch: &mut [f32]);
}
```

`Rt` exists so `process` cannot be called without admitting you are on the (fake or real) audio thread.

In debug, `prepare` may install an alloc hook. If `process` allocates, assert.

## ARM

```rust
pub fn begin_block(); // FPCR FZ+DN on aarch64; SSE MXCSR FTZ/DAZ on x86
pub fn isa() -> Isa;  // cached from prepare
```

Call `begin_block()` once per callback, not per sample. Do not restore FPCR unless a host requires it.
