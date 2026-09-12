//! Realtime contract for keel kernels.
//! Implementation: issue #74 / `feat/keel-core`.

#![cfg_attr(not(feature = "std"), no_std)]

use core::marker::PhantomData;

/// Audio-thread token. Construct at the top of `process` only.
#[derive(Clone, Copy)]
pub struct Rt<'a>(PhantomData<&'a ()>);

impl Rt<'static> {
    /// Test / harness constructor. Production plugins should use a tighter lifetime.
    pub fn now() -> Rt<'static> {
        Rt(PhantomData)
    }
}

#[derive(Clone, Copy, Debug)]
pub struct Prepare {
    pub sample_rate: f32,
    pub max_block: usize,
    pub channels: usize,
}

#[derive(Clone, Copy, Debug, Default)]
pub struct Needs {
    pub state: usize,
    pub scratch: usize,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Isa {
    Scalar,
    Neon,
    Sve,
}

#[derive(Debug)]
pub struct Error(&'static str);

/// Planar f32 view. Lifetime is the caller's buffer.
pub struct PlanarMut<'a> {
    pub channels: &'a mut [&'a mut [f32]],
}

/// Flush denormals. Safe no-op until ISA work lands.
pub fn begin_block() {}

pub fn isa() -> Isa {
    Isa::Scalar
}

pub trait Kernel {
    fn prepare(&mut self, p: Prepare) -> Result<Needs, Error>;
    fn reset(&mut self);
    fn process(&mut self, rt: Rt<'_>, io: PlanarMut<'_>, scratch: &mut [f32]);
}
