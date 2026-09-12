//! Audio-size f32 FFT.
//!
//! Layout: FFTW half-complex, interleaved `re,im`.
//! Packed length is `N + 2`. Inverse (`c2r`) includes `1/N`.
//! See `docs/blueprints/keel/layout.md`.
//!
//! Year-one kernels live in [`scalar`]. [`backend::neon`] is the swap point.

#![cfg_attr(not(feature = "std"), no_std)]

use keel_core::Rt;

mod backend;
mod scalar;

/// Power-of-two sizes the audio path is allowed to ask for.
pub const AUDIO_SIZES: &[usize] = &[64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384];

/// Interleaved half-complex length: DC + Nyquist each take a complex slot.
#[inline]
pub const fn packed_len(n: usize) -> usize {
    n + 2
}

/// Scratch floats for one transform: real workspace || imag workspace.
#[inline]
pub const fn scratch_floats(n: usize) -> usize {
    n * 2
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum FftError {
    UnsupportedSize,
    TimeLen,
    SpecLen,
    ScratchLen,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Backend {
    Scalar,
    Neon,
}

/// Prepared audio FFT. Twiddles are owned; process only reads them.
pub struct FftPlan {
    n: usize,
    /// Forward twiddles `W_n^k` for `k in 0..n/2`.
    tw_re: alloc_vec::Vec<f32>,
    tw_im: alloc_vec::Vec<f32>,
}

mod alloc_vec {
    #[cfg(feature = "std")]
    pub use std::vec::Vec;
    #[cfg(not(feature = "std"))]
    pub use alloc::vec::Vec;
}

impl FftPlan {
    /// Main-thread constructor. Returns `None` if `n` is not an [`AUDIO_SIZES`] entry.
    pub fn new(n: usize) -> Option<Self> {
        if !AUDIO_SIZES.contains(&n) {
            return None;
        }
        let half = n / 2;
        let mut tw_re = alloc_vec::Vec::with_capacity(half);
        let mut tw_im = alloc_vec::Vec::with_capacity(half);
        let ang = -2.0 * core::f32::consts::PI / n as f32;
        for k in 0..half {
            let a = ang * k as f32;
            tw_re.push(a.cos());
            tw_im.push(a.sin());
        }
        Some(Self { n, tw_re, tw_im })
    }

    #[inline]
    pub fn n(&self) -> usize {
        self.n
    }

    #[inline]
    pub fn spec_len(&self) -> usize {
        packed_len(self.n)
    }

    #[inline]
    pub fn scratch_floats(&self) -> usize {
        scratch_floats(self.n)
    }

    #[inline]
    pub fn backend(&self) -> Backend {
        backend::active()
    }

    /// Real → packed half-complex. `time.len() == n`, `spec.len() == n+2`,
    /// `scratch.len() >= 2n`.
    pub fn r2c(
        &self,
        _rt: Rt<'_>,
        time: &[f32],
        spec: &mut [f32],
        scratch: &mut [f32],
    ) -> Result<(), FftError> {
        self.check(time.len(), spec.len(), scratch.len())?;
        backend::r2c(self, time, spec, scratch);
        Ok(())
    }

    /// Packed half-complex → real. Inverse includes `1/N`.
    pub fn c2r(
        &self,
        _rt: Rt<'_>,
        spec: &[f32],
        time: &mut [f32],
        scratch: &mut [f32],
    ) -> Result<(), FftError> {
        self.check(time.len(), spec.len(), scratch.len())?;
        backend::c2r(self, spec, time, scratch);
        Ok(())
    }

    fn check(&self, time: usize, spec: usize, scratch: usize) -> Result<(), FftError> {
        if time != self.n {
            return Err(FftError::TimeLen);
        }
        if spec != packed_len(self.n) {
            return Err(FftError::SpecLen);
        }
        if scratch < scratch_floats(self.n) {
            return Err(FftError::ScratchLen);
        }
        Ok(())
    }

    fn tw(&self) -> (&[f32], &[f32]) {
        (&self.tw_re, &self.tw_im)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn plan(n: usize) -> FftPlan {
        FftPlan::new(n).expect("audio size")
    }

    #[test]
    fn rejects_odd_n() {
        assert!(FftPlan::new(1000).is_none());
        assert!(FftPlan::new(63).is_none());
    }

    #[test]
    fn impulse_is_flat_and_roundtrips() {
        for &n in AUDIO_SIZES {
            let p = plan(n);
            let mut time = vec![0.0f32; n];
            time[0] = 1.0;
            let mut spec = vec![0.0f32; p.spec_len()];
            let mut scratch = vec![0.0f32; p.scratch_floats()];
            p.r2c(Rt::now(), &time, &mut spec, &mut scratch).unwrap();
            assert!((spec[0] - 1.0).abs() < 2e-4);
            assert!(spec[1].abs() < 2e-6);
            for k in 1..=n / 2 {
                assert!((spec[2 * k] - 1.0).abs() < 2e-4, "n={n} bin={k}");
                assert!(spec[2 * k + 1].abs() < 2e-4, "n={n} bin={k} im");
            }
            let mut back = vec![0.0f32; n];
            p.c2r(Rt::now(), &spec, &mut back, &mut scratch).unwrap();
            for i in 0..n {
                assert!((back[i] - time[i]).abs() < 3e-5, "n={n} t={i}");
            }
        }
    }

    #[test]
    fn cosine_bin_three() {
        let n = 64;
        let p = plan(n);
        let k0 = 3usize;
        let mut time = vec![0.0f32; n];
        for t in 0..n {
            time[t] = (2.0 * core::f32::consts::PI * k0 as f32 * t as f32 / n as f32).cos();
        }
        let mut spec = vec![0.0f32; p.spec_len()];
        let mut scratch = vec![0.0f32; p.scratch_floats()];
        p.r2c(Rt::now(), &time, &mut spec, &mut scratch).unwrap();
        // Real cosine → energy split across +k and -k; packed +k is N/2.
        assert!((spec[2 * k0] - n as f32 / 2.0).abs() < 1e-3);
        assert!(spec[2 * k0 + 1].abs() < 1e-3);
        let mut back = vec![0.0f32; n];
        p.c2r(Rt::now(), &spec, &mut back, &mut scratch).unwrap();
        for i in 0..n {
            assert!((back[i] - time[i]).abs() < 3e-5);
        }
    }

    #[test]
    fn buffer_contract() {
        let p = plan(64);
        let time = [0.0f32; 64];
        let mut spec = [0.0f32; 66];
        let mut short = [0.0f32; 10];
        assert_eq!(
            p.r2c(Rt::now(), &time, &mut spec, &mut short),
            Err(FftError::ScratchLen)
        );
    }
}
