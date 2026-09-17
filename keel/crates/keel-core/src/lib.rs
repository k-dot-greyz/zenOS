//! Realtime contract for keel kernels.
//! Minimum law surface for `keel-iir` (#75). Full #74 work stays on `feat/keel-core`.

#![cfg_attr(not(feature = "std"), no_std)]

use core::marker::PhantomData;

/// Audio-thread token. Construct at the top of `process` only.
#[derive(Clone, Copy)]
pub struct Rt<'a>(PhantomData<&'a ()>);

impl Rt<'static> {
    /// Admit this call is on the real or harness audio thread.
    pub fn enter() -> Rt<'static> {
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
pub struct Error(pub &'static str);

/// Planar f32 view. Lifetime is the caller's buffer.
pub struct PlanarMut<'a> {
    pub channels: &'a mut [&'a mut [f32]],
}

/// Flush denormals. Call once per audio callback, not per sample.
pub fn begin_block() {
    #[cfg(all(feature = "std", target_arch = "x86_64"))]
    unsafe {
        const FTZ: u32 = 1 << 15;
        const DAZ: u32 = 1 << 6;
        let mut mxcsr: u32 = 0;
        core::arch::asm!(
            "stmxcsr [{ptr}]",
            "or dword ptr [{ptr}], {bits}",
            "ldmxcsr [{ptr}]",
            ptr = in(reg) &mut mxcsr,
            bits = const FTZ | DAZ,
        );
        let _ = mxcsr;
    }
    #[cfg(all(feature = "std", target_arch = "aarch64"))]
    unsafe {
        let mut fpcr: u64;
        core::arch::asm!("mrs {0}, FPCR", out(reg) fpcr, options(nomem, nostack));
        fpcr |= (1 << 24) | (1 << 25);
        core::arch::asm!("msr FPCR, {0}", in(reg) fpcr, options(nomem, nostack));
    }
}

pub fn isa() -> Isa {
    #[cfg(target_arch = "aarch64")]
    {
        Isa::Neon
    }
    #[cfg(not(target_arch = "aarch64"))]
    {
        Isa::Scalar
    }
}

pub trait Kernel {
    fn prepare(&mut self, p: Prepare) -> Result<Needs, Error>;
    fn reset(&mut self);
    fn process(&mut self, rt: Rt<'_>, io: PlanarMut<'_>, scratch: &mut [f32]);
}
