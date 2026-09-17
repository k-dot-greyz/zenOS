//! Audio-size f32 FFT.
//!
//! Packed real layout is FFTW `r2c` / `scipy.fft.rfft`: interleaved `re,im`,
//! length `N + 2`. Full-complex layout is interleaved `2N`. Inverse (`c2r`,
//! `c2c_inv`) includes `1/N`. See `docs/blueprints/keel/layout.md`.
//!
//! `scalar` is the correctness oracle. Year-one kernels are NEON radix-4/8;
//! `backend` is the ISA swap point and reports [`Backend::Scalar`] until
//! those butterflies are selected.

#![cfg_attr(not(feature = "std"), no_std)]

#[cfg(not(feature = "std"))]
extern crate alloc;

use keel_core::Rt;

mod backend;
mod scalar;

/// Power-of-two sizes the audio path is allowed to ask for.
pub const AUDIO_SIZES: &[usize] = &[64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384];

const SIMD_ALIGN: usize = 16;

/// Interleaved Hermitian packed length: DC + Nyquist each take a complex slot.
#[inline]
pub const fn packed_len(n: usize) -> usize {
    n + 2
}

/// Interleaved full-complex length (`re,im` per bin).
#[inline]
pub const fn complex_len(n: usize) -> usize {
    n * 2
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

/// `Vec<f32>` whose live region starts on a 16-byte boundary (NEON `vld1q`).
struct AlignedF32 {
    raw: alloc_vec::Vec<f32>,
    off: usize,
    len: usize,
}

impl AlignedF32 {
    fn zeros(len: usize) -> Self {
        let pad = SIMD_ALIGN / core::mem::size_of::<f32>();
        let mut raw = alloc_vec::Vec::new();
        raw.resize(len + pad, 0.0);
        let rem = raw.as_ptr() as usize % SIMD_ALIGN;
        let off = if rem == 0 {
            0
        } else {
            (SIMD_ALIGN - rem) / core::mem::size_of::<f32>()
        };
        debug_assert!(off + len <= raw.len());
        Self { raw, off, len }
    }

    fn as_slice(&self) -> &[f32] {
        &self.raw[self.off..self.off + self.len]
    }

    fn as_mut_slice(&mut self) -> &mut [f32] {
        let (off, len) = (self.off, self.len);
        &mut self.raw[off..off + len]
    }
}

/// Prepared audio FFT. Twiddles are owned; process only reads them.
pub struct FftPlan {
    n: usize,
    /// Forward twiddles `W_n^k` for `k in 0..n/2`.
    tw_re: AlignedF32,
    tw_im: AlignedF32,
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
        let mut tw_re = AlignedF32::zeros(half);
        let mut tw_im = AlignedF32::zeros(half);
        let re = tw_re.as_mut_slice();
        let im = tw_im.as_mut_slice();
        for k in 0..half {
            let a = -2.0 * core::f64::consts::PI * k as f64 / n as f64;
            let (s, c) = a.sin_cos();
            re[k] = c as f32;
            im[k] = s as f32;
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
    pub fn complex_len(&self) -> usize {
        complex_len(self.n)
    }

    #[inline]
    pub fn scratch_floats(&self) -> usize {
        scratch_floats(self.n)
    }

    #[inline]
    pub fn backend(&self) -> Backend {
        backend::active()
    }

    /// Real → packed Hermitian. `time.len() == n`, `spec.len() == n+2`,
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

    /// Packed Hermitian → real. Inverse includes `1/N`.
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

    /// Full-complex forward, interleaved `2N`. Unnormalized.
    pub fn c2c(
        &self,
        _rt: Rt<'_>,
        input: &[f32],
        output: &mut [f32],
        scratch: &mut [f32],
    ) -> Result<(), FftError> {
        self.check_c2c(input.len(), output.len(), scratch.len())?;
        backend::c2c(self, input, output, scratch, false);
        Ok(())
    }

    /// Full-complex inverse, interleaved `2N`. Includes `1/N`.
    pub fn c2c_inv(
        &self,
        _rt: Rt<'_>,
        input: &[f32],
        output: &mut [f32],
        scratch: &mut [f32],
    ) -> Result<(), FftError> {
        self.check_c2c(input.len(), output.len(), scratch.len())?;
        backend::c2c(self, input, output, scratch, true);
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

    fn check_c2c(&self, input: usize, output: usize, scratch: usize) -> Result<(), FftError> {
        if input != complex_len(self.n) {
            return Err(FftError::TimeLen);
        }
        if output != complex_len(self.n) {
            return Err(FftError::SpecLen);
        }
        if scratch < scratch_floats(self.n) {
            return Err(FftError::ScratchLen);
        }
        Ok(())
    }

    pub(crate) fn tw(&self) -> (&[f32], &[f32]) {
        (self.tw_re.as_slice(), self.tw_im.as_slice())
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
            assert!((spec[0] - 1.0).abs() < 5e-5);
            assert!(spec[1].abs() < 2e-6);
            for k in 1..=n / 2 {
                assert!((spec[2 * k] - 1.0).abs() < 5e-5, "n={n} bin={k}");
                assert!(spec[2 * k + 1].abs() < 5e-5, "n={n} bin={k} im");
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
        assert!((spec[2 * k0] - n as f32 / 2.0).abs() < 5e-4);
        assert!(spec[2 * k0 + 1].abs() < 5e-4);
        for k in 0..=n / 2 {
            if k == k0 {
                continue;
            }
            let mag2 = spec[2 * k] * spec[2 * k] + spec[2 * k + 1] * spec[2 * k + 1];
            assert!(mag2 < 1e-3, "leak bin={k} mag2={mag2}");
        }
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
        let mut half_bins = [0.0f32; 33];
        let mut scratch = [0.0f32; 128];
        assert_eq!(
            p.r2c(Rt::now(), &time, &mut half_bins, &mut scratch),
            Err(FftError::SpecLen)
        );
        let short_time = [0.0f32; 32];
        let mut packed = [0.0f32; 66];
        assert_eq!(
            p.r2c(Rt::now(), &short_time, &mut packed, &mut scratch),
            Err(FftError::TimeLen)
        );
    }

    #[test]
    fn backend_is_scalar_until_neon_butterflies() {
        assert_eq!(plan(64).backend(), Backend::Scalar);
    }

    #[test]
    fn twiddles_are_16_byte_aligned() {
        for &n in AUDIO_SIZES {
            let p = plan(n);
            let (re, im) = p.tw();
            assert_eq!((re.as_ptr() as usize) % 16, 0, "n={n} tw_re");
            assert_eq!((im.as_ptr() as usize) % 16, 0, "n={n} tw_im");
            assert_eq!(re.len(), n / 2);
            assert_eq!(im.len(), n / 2);
        }
    }

    fn naive_r2c(time: &[f32]) -> Vec<(f64, f64)> {
        let n = time.len();
        let mut bins = Vec::with_capacity(n / 2 + 1);
        for k in 0..=n / 2 {
            let mut re = 0.0f64;
            let mut im = 0.0f64;
            for (t, &x) in time.iter().enumerate() {
                let a = -2.0 * core::f64::consts::PI * k as f64 * t as f64 / n as f64;
                let (s, c) = a.sin_cos();
                re += x as f64 * c;
                im += x as f64 * s;
            }
            bins.push((re, im));
        }
        bins
    }

    fn chirp(n: usize) -> Vec<f32> {
        (0..n)
            .map(|t| {
                let tf = t as f64;
                (core::f64::consts::PI * tf * (tf + 1.0) / n as f64).cos() as f32
            })
            .collect()
    }

    #[test]
    fn r2c_matches_naive_dft_on_chirp() {
        for &n in &[64usize, 256] {
            let p = plan(n);
            let time = chirp(n);
            let mut spec = vec![0.0f32; p.spec_len()];
            let mut scratch = vec![0.0f32; p.scratch_floats()];
            p.r2c(Rt::now(), &time, &mut spec, &mut scratch).unwrap();
            let oracle = naive_r2c(&time);
            for k in 0..=n / 2 {
                let (or, oi) = oracle[k];
                let er = (spec[2 * k] as f64 - or).abs();
                let ei = (spec[2 * k + 1] as f64 - oi).abs();
                assert!(er < 5e-5, "n={n} bin={k} re err={er}");
                assert!(ei < 5e-5, "n={n} bin={k} im err={ei}");
            }
        }
    }

    #[test]
    fn c2c_roundtrips_and_matches_r2c_on_real_cosine() {
        let n = 64;
        let p = plan(n);
        let k0 = 3usize;
        let mut time = vec![0.0f32; complex_len(n)];
        for t in 0..n {
            time[2 * t] =
                (2.0 * core::f32::consts::PI * k0 as f32 * t as f32 / n as f32).cos();
        }
        let mut spec = vec![0.0f32; complex_len(n)];
        let mut scratch = vec![0.0f32; p.scratch_floats()];
        p.c2c(Rt::now(), &time, &mut spec, &mut scratch).unwrap();
        assert!((spec[2 * k0] - n as f32 / 2.0).abs() < 5e-4);
        assert!(spec[2 * k0 + 1].abs() < 5e-4);
        assert!((spec[2 * (n - k0)] - n as f32 / 2.0).abs() < 5e-4);
        let mut back = vec![0.0f32; complex_len(n)];
        p.c2c_inv(Rt::now(), &spec, &mut back, &mut scratch).unwrap();
        for i in 0..complex_len(n) {
            assert!((back[i] - time[i]).abs() < 3e-5, "t={i}");
        }
    }
}
