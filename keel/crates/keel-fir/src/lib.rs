//! Time-domain FIR. Implementation: issue #77 / `feat/keel-fir`.
//!
//! Duplicated delay line, N ≤ 256, contiguous inner product.
//! On `aarch64`, the dense path is `vfmaq_f32` 4-wide + scalar tail.
//! Long IRs belong in `keel-conv` (#78).

use keel_core::{Error, Kernel, Needs, PlanarMut, Prepare, Rt};

pub const MAX_TAPS: usize = 256;
const MAX_CH: usize = 8;

pub struct FirTd {
    taps: [f32; MAX_TAPS],
    n: usize,
    delay: [f32; 2 * MAX_TAPS * MAX_CH],
    w: [usize; MAX_CH],
    channels: usize,
    linear_phase: bool,
    force_dense: bool,
}

impl Default for FirTd {
    fn default() -> Self {
        Self {
            taps: [0.0; MAX_TAPS],
            n: 0,
            delay: [0.0; 2 * MAX_TAPS * MAX_CH],
            w: [0; MAX_CH],
            channels: 1,
            linear_phase: false,
            force_dense: false,
        }
    }
}

impl FirTd {
    pub fn from_taps(taps: &[f32]) -> Result<Self, Error> {
        if taps.is_empty() {
            return Err(Error::new("FIR needs at least one tap"));
        }
        if taps.len() > MAX_TAPS {
            return Err(Error::new("FIR N exceeds MAX_TAPS (256)"));
        }
        let mut s = Self::default();
        s.n = taps.len();
        s.taps[..s.n].copy_from_slice(taps);
        s.linear_phase = is_symmetric(&s.taps[..s.n]);
        Ok(s)
    }

    pub fn n(&self) -> usize {
        self.n
    }

    pub fn is_linear_phase(&self) -> bool {
        self.linear_phase
    }

    /// Test hook: disable the paired-tap path even when coeffs are symmetric.
    pub fn force_dense(&mut self) {
        self.force_dense = true;
    }

    fn delay_off(&self, ch: usize) -> usize {
        ch * 2 * MAX_TAPS
    }

    fn tick_ch(&mut self, ch: usize, x: f32) -> f32 {
        let n = self.n;
        if n == 0 {
            return x;
        }
        let off = self.delay_off(ch);
        let w = self.w[ch];
        self.delay[off + w] = x;
        self.delay[off + w + n] = x;
        let y = if self.linear_phase && !self.force_dense {
            dot_sym(&self.taps[..n], &self.delay[off..off + 2 * n], w)
        } else {
            dot_dense(&self.taps[..n], &self.delay[off..off + 2 * n], w)
        };
        let mut nw = w + 1;
        if nw == n {
            nw = 0;
        }
        self.w[ch] = nw;
        y
    }
}

fn is_symmetric(taps: &[f32]) -> bool {
    let n = taps.len();
    n >= 2 && (0..n / 2).all(|k| taps[k] == taps[n - 1 - k])
}

/// y = Σ taps[k] * delay[w + n - k], window is contiguous in the duplicate.
fn dot_dense(taps: &[f32], delay: &[f32], w: usize) -> f32 {
    let n = taps.len();
    let window = &delay[w + 1..w + 1 + n];
    inner_rev(taps, window)
}

fn inner_rev(taps: &[f32], window: &[f32]) -> f32 {
    debug_assert_eq!(taps.len(), window.len());
    #[cfg(target_arch = "aarch64")]
    {
        return unsafe { inner_rev_neon(taps, window) };
    }
    #[cfg(not(target_arch = "aarch64"))]
    {
        inner_rev_scalar(taps, window)
    }
}

fn inner_rev_scalar(taps: &[f32], window: &[f32]) -> f32 {
    let n = taps.len();
    let mut acc = 0.0f32;
    for i in 0..n {
        acc = taps[n - 1 - i].mul_add(window[i], acc);
    }
    acc
}

#[cfg(target_arch = "aarch64")]
unsafe fn inner_rev_neon(taps: &[f32], window: &[f32]) -> f32 {
    use core::arch::aarch64::{
        vdupq_n_f32, vfmaq_f32, vgetq_lane_f32, vld1q_dup_f32, vld1q_f32, vsetq_lane_f32,
    };
    let n = taps.len();
    let mut accv = vdupq_n_f32(0.0);
    let mut i = 0;
    while i + 4 <= n {
        let w = vld1q_f32(window.as_ptr().add(i));
        let mut t = vld1q_dup_f32(taps.as_ptr().add(n - 1 - i));
        t = vsetq_lane_f32::<1>(taps[n - 2 - i], t);
        t = vsetq_lane_f32::<2>(taps[n - 3 - i], t);
        t = vsetq_lane_f32::<3>(taps[n - 4 - i], t);
        accv = vfmaq_f32(accv, w, t);
        i += 4;
    }
    let mut acc = vgetq_lane_f32::<0>(accv)
        + vgetq_lane_f32::<1>(accv)
        + vgetq_lane_f32::<2>(accv)
        + vgetq_lane_f32::<3>(accv);
    while i < n {
        acc = taps[n - 1 - i].mul_add(window[i], acc);
        i += 1;
    }
    acc
}

fn dot_sym(taps: &[f32], delay: &[f32], w: usize) -> f32 {
    let n = taps.len();
    let mut acc = 0.0f32;
    let last = n / 2;
    for k in 0..last {
        let d0 = delay[w + n - k];
        let d1 = delay[w + 1 + k];
        acc = taps[k].mul_add(d0 + d1, acc);
    }
    if n % 2 == 1 {
        let mid = n / 2;
        acc = taps[mid].mul_add(delay[w + n - mid], acc);
    }
    acc
}

impl Kernel for FirTd {
    fn prepare(&mut self, p: Prepare) -> Result<Needs, Error> {
        if p.channels == 0 || p.channels > MAX_CH {
            return Err(Error::new("FIR channels must be 1..=8"));
        }
        self.channels = p.channels;
        self.reset();
        Ok(Needs {
            state: 2 * self.n * self.channels * core::mem::size_of::<f32>(),
            scratch: 0,
        })
    }

    fn reset(&mut self) {
        self.delay = [0.0; 2 * MAX_TAPS * MAX_CH];
        self.w = [0; MAX_CH];
    }

    fn process(&mut self, _rt: Rt<'_>, io: PlanarMut<'_>, _scratch: &mut [f32]) {
        let nch = io.channels.len().min(self.channels).min(MAX_CH);
        for ch in 0..nch {
            for s in io.channels[ch].iter_mut() {
                *s = self.tick_ch(ch, *s);
            }
        }
    }
}

/// Half-band wrapper: every other tap is zero; decimate/interpolate by 2.
pub struct FirHb {
    inner: FirTd,
}

impl FirHb {
    pub fn from_taps(taps: &[f32]) -> Result<Self, Error> {
        Ok(Self {
            inner: FirTd::from_taps(taps)?,
        })
    }

    pub fn decimate(&mut self, x: &[f32], y: &mut [f32]) {
        let out_n = x.len() / 2;
        if y.len() < out_n {
            return;
        }
        let mut out_i = 0;
        for (i, &xi) in x.iter().enumerate() {
            let yi = self.inner.tick_ch(0, xi);
            if i % 2 == 0 && out_i < out_n {
                y[out_i] = yi;
                out_i += 1;
            }
        }
    }

    pub fn interpolate(&mut self, x: &[f32], y: &mut [f32]) {
        let out_n = x.len().saturating_mul(2);
        if y.len() < out_n {
            return;
        }
        for (i, &xi) in x.iter().enumerate() {
            y[2 * i] = self.inner.tick_ch(0, xi);
            y[2 * i + 1] = self.inner.tick_ch(0, 0.0);
        }
    }
}

impl Kernel for FirHb {
    fn prepare(&mut self, p: Prepare) -> Result<Needs, Error> {
        self.inner.prepare(p)
    }

    fn reset(&mut self) {
        self.inner.reset();
    }

    fn process(&mut self, rt: Rt<'_>, io: PlanarMut<'_>, scratch: &mut [f32]) {
        self.inner.process(rt, io, scratch);
    }
}
