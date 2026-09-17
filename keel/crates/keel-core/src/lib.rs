//! Realtime contract for keel kernels.
//! Implementation: issue #74 / `feat/keel-core`.

#![cfg_attr(not(feature = "std"), no_std)]

use core::marker::PhantomData;
use core::sync::atomic::{AtomicU8, Ordering};

#[cfg(all(feature = "std", debug_assertions))]
mod alloc_guard;

/// Audio-thread token. Obtain from [`Rt::enter`] at the top of the host callback.
#[derive(Clone, Copy)]
pub struct Rt<'a>(PhantomData<&'a ()>);

/// RAII scope for one host `process()` callback.
///
/// Dropping the scope clears the debug alloc guard. Call once per callback,
/// not per kernel.
pub struct ProcessScope {
    _not_copy: PhantomData<*const ()>,
}

impl ProcessScope {
    /// Token to pass into [`Kernel::process`]. Lifetime is tied to this scope.
    #[inline]
    pub fn token(&self) -> Rt<'_> {
        Rt(PhantomData)
    }
}

impl Drop for ProcessScope {
    fn drop(&mut self) {
        #[cfg(all(feature = "std", debug_assertions))]
        alloc_guard::exit();
    }
}

impl Rt<'_> {
    /// Call once per host audio callback, then pass [`ProcessScope::token`] down.
    pub fn enter() -> ProcessScope {
        cache_isa();
        #[cfg(all(feature = "std", debug_assertions))]
        alloc_guard::enter();
        ProcessScope {
            _not_copy: PhantomData,
        }
    }
}

#[cfg(test)]
impl Rt<'static> {
    /// Test / harness constructor. Does not arm the alloc guard.
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

/// Kernel error. Public tuple field so sibling crates can construct `Err`.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Error(pub &'static str);

/// 16-byte alignment check for NEON-friendly loads.
#[inline]
pub fn is_aligned_16(ptr: *const f32) -> bool {
    (ptr as usize) % 16 == 0
}

/// Immutable planar view: `ch[c][0..n]` contiguous per channel.
pub struct Planar<'a> {
    channels: &'a [&'a [f32]],
    frames: usize,
}

impl<'a> Planar<'a> {
    pub fn from_channels(channels: &'a [&'a [f32]]) -> Result<Self, Error> {
        let frames = equal_frames(channels.iter().map(|c| c.len()))?;
        Ok(Self { channels, frames })
    }

    #[inline]
    pub fn frames(&self) -> usize {
        self.frames
    }

    #[inline]
    pub fn channel(&self, i: usize) -> &[f32] {
        self.channels[i]
    }

    #[inline]
    pub fn is_aligned_16(&self) -> bool {
        self.channels.iter().all(|c| is_aligned_16(c.as_ptr()))
    }
}

/// Mutable planar view. Lifetime is the caller's buffer.
pub struct PlanarMut<'a> {
    channels: &'a mut [&'a mut [f32]],
    frames: usize,
}

impl<'a> PlanarMut<'a> {
    pub fn from_channels(channels: &'a mut [&'a mut [f32]]) -> Result<Self, Error> {
        let frames = equal_frames(channels.iter().map(|c| c.len()))?;
        Ok(Self { channels, frames })
    }

    #[inline]
    pub fn frames(&self) -> usize {
        self.frames
    }

    #[inline]
    pub fn channel(&self, i: usize) -> &[f32] {
        self.channels[i]
    }

    #[inline]
    pub fn channel_mut(&mut self, i: usize) -> &mut [f32] {
        self.channels[i]
    }

    #[inline]
    pub fn channels_mut(&mut self) -> &mut [&'a mut [f32]] {
        self.channels
    }

    #[inline]
    pub fn is_aligned_16(&self) -> bool {
        self.channels.iter().all(|c| is_aligned_16(c.as_ptr()))
    }

    /// Plugin-edge adapter: interleaved `[L,R,L,R,…]` → planar `ch[c][0..n]`.
    pub fn copy_from_interleaved(&mut self, interleaved: &[f32]) -> Result<(), Error> {
        let ch = self.channels.len();
        if ch == 0 {
            return Err(Error("planar: no channels"));
        }
        let frames = self.frames;
        if interleaved.len() != ch.checked_mul(frames).ok_or(Error("planar: overflow"))? {
            return Err(Error("planar: interleaved length != channels * frames"));
        }
        for f in 0..frames {
            for c in 0..ch {
                self.channels[c][f] = interleaved[f * ch + c];
            }
        }
        Ok(())
    }
}

fn equal_frames(mut lens: impl Iterator<Item = usize>) -> Result<usize, Error> {
    let Some(frames) = lens.next() else {
        return Err(Error("planar: no channels"));
    };
    if lens.any(|n| n != frames) {
        return Err(Error("planar: channel length mismatch"));
    }
    Ok(frames)
}

/// Flush denormals. Call once per callback, not per sample. Does not restore
/// FPCR/MXCSR unless a host requires it (we never restore here).
pub fn begin_block() {
    flush_denormals();
    let _ = cache_isa();
}

#[cfg(target_arch = "aarch64")]
fn flush_denormals() {
    // FPCR FZ (bit 24) + DN (bit 25).
    unsafe {
        let mut fpcr: u64;
        core::arch::asm!(
            "mrs {fpcr}, fpcr",
            fpcr = out(reg) fpcr,
            options(nomem, preserves_flags)
        );
        fpcr |= (1 << 24) | (1 << 25);
        core::arch::asm!(
            "msr fpcr, {fpcr}",
            fpcr = in(reg) fpcr,
            options(nomem, preserves_flags)
        );
    }
}

#[cfg(any(target_arch = "x86_64", target_arch = "x86"))]
fn flush_denormals() {
    // MXCSR FTZ (bit 15) + DAZ (bit 6).
    unsafe {
        let mut mxcsr = 0u32;
        core::arch::asm!(
            "stmxcsr [{ptr}]",
            ptr = in(reg) &mut mxcsr,
            options(nostack, preserves_flags)
        );
        mxcsr |= 0x8000 | 0x40;
        core::arch::asm!(
            "ldmxcsr [{ptr}]",
            ptr = in(reg) &mxcsr,
            options(nostack, preserves_flags)
        );
    }
}

#[cfg(not(any(target_arch = "aarch64", target_arch = "x86_64", target_arch = "x86")))]
fn flush_denormals() {}

const ISA_UNSET: u8 = 0;
const ISA_SCALAR: u8 = 1;
const ISA_NEON: u8 = 2;
const ISA_SVE: u8 = 3;

static CACHED_ISA: AtomicU8 = AtomicU8::new(ISA_UNSET);

/// Detect ISA once (typically from `prepare`) and cache it. Never call in the inner loop.
pub fn cache_isa() -> Isa {
    let cached = CACHED_ISA.load(Ordering::Relaxed);
    if cached != ISA_UNSET {
        return decode_isa(cached);
    }
    let detected = detect_isa();
    CACHED_ISA.store(encode_isa(detected), Ordering::Relaxed);
    detected
}

/// Cached ISA from [`cache_isa`]. Detects once if `prepare` has not run yet.
#[inline]
pub fn isa() -> Isa {
    let cached = CACHED_ISA.load(Ordering::Relaxed);
    if cached == ISA_UNSET {
        return cache_isa();
    }
    decode_isa(cached)
}

fn encode_isa(isa: Isa) -> u8 {
    match isa {
        Isa::Scalar => ISA_SCALAR,
        Isa::Neon => ISA_NEON,
        Isa::Sve => ISA_SVE,
    }
}

fn decode_isa(v: u8) -> Isa {
    match v {
        ISA_NEON => Isa::Neon,
        ISA_SVE => Isa::Sve,
        _ => Isa::Scalar,
    }
}

fn detect_isa() -> Isa {
    #[cfg(target_arch = "aarch64")]
    {
        detect_aarch64()
    }
    #[cfg(not(target_arch = "aarch64"))]
    {
        Isa::Scalar
    }
}

#[cfg(target_arch = "aarch64")]
fn detect_aarch64() -> Isa {
    #[cfg(feature = "std")]
    {
        if std::arch::is_aarch64_feature_detected!("sve") {
            return Isa::Sve;
        }
        if std::arch::is_aarch64_feature_detected!("neon") {
            return Isa::Neon;
        }
        Isa::Scalar
    }
    #[cfg(not(feature = "std"))]
    {
        aarch64_compile_time_isa()
    }
}

#[cfg(all(target_arch = "aarch64", not(feature = "std")))]
fn aarch64_compile_time_isa() -> Isa {
    #[cfg(target_feature = "sve")]
    {
        Isa::Sve
    }
    #[cfg(all(target_feature = "neon", not(target_feature = "sve")))]
    {
        Isa::Neon
    }
    #[cfg(not(any(target_feature = "neon", target_feature = "sve")))]
    {
        Isa::Scalar
    }
}

/// Realtime kernel. `process` takes caller-owned scratch slices, never `Vec`.
///
/// ```compile_fail
/// use keel_core::{Error, Kernel, Needs, PlanarMut, Prepare, Rt};
/// struct Bad;
/// impl Kernel for Bad {
///     fn prepare(&mut self, _p: Prepare) -> Result<Needs, Error> { Ok(Needs::default()) }
///     fn reset(&mut self) {}
///     fn process(&mut self, _rt: Rt<'_>, _io: PlanarMut<'_>, _scratch: Vec<f32>) {}
/// }
/// ```
pub trait Kernel {
    /// May allocate. Detect / cache ISA here (`cache_isa`).
    fn prepare(&mut self, p: Prepare) -> Result<Needs, Error>;
    /// Realtime. No alloc.
    fn reset(&mut self);
    /// Realtime. Caller owns `io` and `scratch`.
    fn process(&mut self, rt: Rt<'_>, io: PlanarMut<'_>, scratch: &mut [f32]);
}

/// Tracking allocator: panics in debug if allocation happens inside [`Rt::enter`].
///
/// Binaries that want the hook in their own process install:
/// `#[global_allocator] static A: keel_core::RtAlloc = keel_core::RtAlloc;`
#[cfg(all(feature = "std", debug_assertions))]
pub use alloc_guard::RtAlloc;

#[cfg(all(feature = "std", debug_assertions))]
#[global_allocator]
static ALLOC: alloc_guard::RtAlloc = alloc_guard::RtAlloc;
