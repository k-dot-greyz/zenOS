//! Multi-channel SOS bank. Same coeffs on every channel; NEON is 4-wide across C.

use core::cell::UnsafeCell;
use core::sync::atomic::{AtomicU32, Ordering};

use keel_core::{Error, Kernel, Needs, PlanarMut, Prepare, Rt, begin_block};

use crate::biquad::{Biquad, BiquadState, Coeffs};
use crate::sos::Sos;

#[derive(Clone, Copy)]
struct SosCoeffs<const N: usize> {
    sections: [Coeffs; N],
    len: usize,
}

impl<const N: usize> Default for SosCoeffs<N> {
    fn default() -> Self {
        Self {
            sections: [Coeffs::identity(); N],
            len: 0,
        }
    }
}

/// Double-buffered coeffs. Single publisher. RT loads `generation` at block start.
struct CoeffSwap<const N: usize> {
    slots: [UnsafeCell<SosCoeffs<N>>; 2],
    generation: AtomicU32,
}

unsafe impl<const N: usize> Sync for CoeffSwap<N> {}

impl<const N: usize> CoeffSwap<N> {
    fn new() -> Self {
        Self {
            slots: [
                UnsafeCell::new(SosCoeffs::default()),
                UnsafeCell::new(SosCoeffs::default()),
            ],
            generation: AtomicU32::new(0),
        }
    }

    fn publish(&self, src: SosCoeffs<N>) {
        let g = self.generation.load(Ordering::Relaxed);
        let write = 1 - ((g & 1) as usize);
        unsafe {
            *self.slots[write].get() = src;
        }
        self.generation.store(g.wrapping_add(1), Ordering::Release);
    }

    fn load(&self) -> SosCoeffs<N> {
        let g = self.generation.load(Ordering::Acquire);
        let idx = (g & 1) as usize;
        unsafe { *self.slots[idx].get() }
    }
}

struct DelaySoA {
    z1: Vec<f32>,
    z2: Vec<f32>,
    channels: usize,
}

impl DelaySoA {
    fn new() -> Self {
        Self {
            z1: Vec::new(),
            z2: Vec::new(),
            channels: 0,
        }
    }

    fn resize(&mut self, channels: usize, sections: usize) {
        self.channels = channels;
        let n = channels.saturating_mul(sections);
        self.z1.clear();
        self.z1.resize(n, 0.0);
        self.z2.clear();
        self.z2.resize(n, 0.0);
    }

    fn reset(&mut self) {
        self.z1.fill(0.0);
        self.z2.fill(0.0);
    }

    #[inline(always)]
    fn index(&self, section: usize, ch: usize) -> usize {
        section * self.channels + ch
    }
}

pub struct Bank<const N: usize = 16> {
    swap: CoeffSwap<N>,
    delay: DelaySoA,
}

impl<const N: usize> Default for Bank<N> {
    fn default() -> Self {
        Self {
            swap: CoeffSwap::new(),
            delay: DelaySoA::new(),
        }
    }
}

impl<const N: usize> Bank<N> {
    /// Write the inactive coeff slot, then bump generation. Apply at next `process`.
    pub fn publish(&self, sos: &Sos<N>) {
        let (sections, len) = sos.coeff_copy();
        self.swap.publish(SosCoeffs { sections, len });
    }

    fn process_sample_channel(
        sections: &[Coeffs; N],
        len: usize,
        delay: &mut DelaySoA,
        ch: usize,
        x: f32,
    ) -> f32 {
        let mut y = x;
        let n = len.min(N);
        for (s, c) in sections.iter().take(n).enumerate() {
            let i = delay.index(s, ch);
            let mut z = BiquadState {
                z1: delay.z1[i],
                z2: delay.z2[i],
            };
            y = Biquad::tick(y, *c, &mut z);
            delay.z1[i] = z.z1;
            delay.z2[i] = z.z2;
        }
        y
    }
}

#[cfg(target_arch = "aarch64")]
#[inline(always)]
unsafe fn neon_section_4(
    x: core::arch::aarch64::float32x4_t,
    c: Coeffs,
    z1: *mut f32,
    z2: *mut f32,
) -> core::arch::aarch64::float32x4_t {
    use core::arch::aarch64::*;
    let y = vfmaq_n_f32(vld1q_f32(z1), x, c.b0);
    let t = vfmaq_n_f32(vld1q_f32(z2), x, c.b1);
    let z1n = vfmsq_n_f32(t, y, c.a1);
    let z2n = vfmsq_n_f32(vmulq_n_f32(x, c.b2), y, c.a2);
    vst1q_f32(z1, z1n);
    vst1q_f32(z2, z2n);
    y
}

impl<const N: usize> Kernel for Bank<N> {
    fn prepare(&mut self, p: Prepare) -> Result<Needs, Error> {
        self.delay.resize(p.channels, N);
        Ok(Needs {
            state: p.channels * N * 2 * core::mem::size_of::<f32>(),
            scratch: 0,
        })
    }

    fn reset(&mut self) {
        self.delay.reset();
    }

    fn process(&mut self, _rt: Rt<'_>, io: PlanarMut<'_>, _scratch: &mut [f32]) {
        begin_block();
        let coeffs = self.swap.load();
        let channels = io.channels.len().min(self.delay.channels);
        if channels == 0 {
            return;
        }
        let n_samples = io.channels[..channels]
            .iter()
            .map(|c| c.len())
            .min()
            .unwrap_or(0);
        let sections = coeffs.sections;
        let len = coeffs.len.min(N);

        for t in 0..n_samples {
            let mut ch = 0;
            #[cfg(target_arch = "aarch64")]
            {
                while ch + 4 <= channels {
                    unsafe {
                        use core::arch::aarch64::*;
                        let x = {
                            let x0 = *io.channels[ch].get_unchecked(t);
                            let x1 = *io.channels[ch + 1].get_unchecked(t);
                            let x2 = *io.channels[ch + 2].get_unchecked(t);
                            let x3 = *io.channels[ch + 3].get_unchecked(t);
                            let arr = [x0, x1, x2, x3];
                            vld1q_f32(arr.as_ptr())
                        };
                        let mut y = x;
                        for s in 0..len {
                            let i = self.delay.index(s, ch);
                            y = neon_section_4(
                                y,
                                sections[s],
                                self.delay.z1.as_mut_ptr().add(i),
                                self.delay.z2.as_mut_ptr().add(i),
                            );
                        }
                        let mut out = [0.0f32; 4];
                        vst1q_f32(out.as_mut_ptr(), y);
                        *io.channels[ch].get_unchecked_mut(t) = out[0];
                        *io.channels[ch + 1].get_unchecked_mut(t) = out[1];
                        *io.channels[ch + 2].get_unchecked_mut(t) = out[2];
                        *io.channels[ch + 3].get_unchecked_mut(t) = out[3];
                    }
                    ch += 4;
                }
            }
            while ch < channels {
                let y = Self::process_sample_channel(
                    &sections,
                    len,
                    &mut self.delay,
                    ch,
                    io.channels[ch][t],
                );
                io.channels[ch][t] = y;
                ch += 1;
            }
        }
    }
}
