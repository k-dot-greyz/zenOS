//! Partitioned convolver. Implementation: issue #78 / `feat/keel-conv`.
//!
//! Year one: same-thread uniform OLS + short TD head. No worker pool.
//! `load_ir` cannot build frequency-domain partitions until `keel-fft` r2c/c2r
//! (#76) and `keel-fir` TD `process` (#77) exist. Until then `process` is a
//! wait-free identity (no alloc).

use keel_core::{Error, Kernel, Needs, PlanarMut, Prepare, Rt};
use keel_fft::FftPlan;
use keel_fir::MAX_TAPS;

/// #78 hybrid head: 32..=128 taps. Capped well below [`MAX_TAPS`].
pub const HEAD_TAPS_MIN: usize = 32;
pub const HEAD_TAPS_MAX: usize = 128;

const _: () = assert!(HEAD_TAPS_MAX <= MAX_TAPS);

/// Uniform partitioned convolver. Fields are private until an IR plan exists.
pub struct Convolver {
    ir_len: usize,
    head_taps: usize,
    max_block: usize,
    channels: usize,
}

impl Default for Convolver {
    fn default() -> Self {
        Self {
            ir_len: 0,
            head_taps: HEAD_TAPS_MIN,
            max_block: 0,
            channels: 0,
        }
    }
}

impl Convolver {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn max_block(&self) -> usize {
        self.max_block
    }

    pub fn channels(&self) -> usize {
        self.channels
    }

    pub fn ir_len(&self) -> usize {
        self.ir_len
    }

    /// Sample delay of the hybrid head. #78: latency == head length.
    pub fn latency_samples(&self) -> usize {
        self.head_taps
    }

    /// Main-thread IR load. Audio thread must see a finished plan (atomic swap later).
    ///
    /// Returns `Err` until #76/#77 provide r2c and a TD FIR head.
    pub fn load_ir(&mut self, ir: &[f32], head_taps: usize) -> Result<(), Error> {
        if !(HEAD_TAPS_MIN..=HEAD_TAPS_MAX).contains(&head_taps) {
            return Err(Error("head_taps must be 32..=128"));
        }
        if self.max_block == 0 {
            return Err(Error("call prepare before load_ir"));
        }
        // OLS FFT size is 2 * partition; partition == max_block.
        let fft_n = self.max_block.saturating_mul(2);
        if FftPlan::new(fft_n).is_none() {
            return Err(Error("OLS FFT size (2*max_block) is not an audio FFT size"));
        }
        let _ = ir;
        Err(Error(
            "IR plan blocked on keel-fft r2c and keel-fir TD head",
        ))
    }
}

impl Kernel for Convolver {
    fn prepare(&mut self, p: Prepare) -> Result<Needs, Error> {
        if p.max_block == 0 || p.channels == 0 {
            return Err(Error("max_block and channels must be > 0"));
        }
        self.max_block = p.max_block;
        self.channels = p.channels;
        // Overlap-save scratch: one extra partition of f32 per channel (placeholder).
        Ok(Needs {
            state_bytes: 0,
            scratch_bytes: p.max_block.saturating_mul(p.channels).saturating_mul(2),
        })
    }

    fn reset(&mut self) {
        // No delay-line state until an IR is planned.
    }

    fn process(&mut self, _rt: Rt<'_>, _io: PlanarMut<'_>, _scratch: &mut [f32]) {
        // Identity until load_ir succeeds. Wait-free: no alloc, lock, or I/O.
    }
}
