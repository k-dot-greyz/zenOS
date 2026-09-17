//! IIR kernels. Implementation: issue #75 / `feat/keel-iir`.

use keel_core::Kernel;

#[derive(Clone, Copy, Debug, Default)]
pub struct Coeffs {
    pub b0: f32,
    pub b1: f32,
    pub b2: f32,
    pub a1: f32,
    pub a2: f32,
}

#[derive(Clone, Copy, Debug, Default)]
pub struct BiquadState {
    pub z1: f32,
    pub z2: f32,
}

#[inline(always)]
pub fn tick(x: f32, c: Coeffs, z: &mut BiquadState) -> f32 {
    let y = c.b0.mul_add(x, z.z1);
    z.z1 = c.b1.mul_add(x, z.z2) - c.a1 * y;
    z.z2 = c.b2 * x - c.a2 * y;
    y
}

pub const MAX_SECTIONS: usize = 16;
pub const MAX_CHANNELS: usize = 8;

pub struct Sos {
    pub sections: [Coeffs; MAX_SECTIONS],
    pub len: usize,
    pub n_ch: usize,
    pub state: [[BiquadState; MAX_SECTIONS]; MAX_CHANNELS],
}

impl Default for Sos {
    fn default() -> Self {
        Self {
            sections: [Coeffs::default(); MAX_SECTIONS],
            len: 0,
            n_ch: 0,
            state: [[BiquadState::default(); MAX_SECTIONS]; MAX_CHANNELS],
        }
    }
}

impl Kernel for Sos {
    fn prepare(&mut self, p: keel_core::Prepare) -> Result<keel_core::Needs, keel_core::Error> {
        if p.channels == 0 || p.channels > MAX_CHANNELS {
            return Err(keel_core::Error("channel count"));
        }
        self.n_ch = p.channels;
        Ok(keel_core::Needs {
            state: core::mem::size_of::<Self>(),
            scratch: 0,
        })
    }
    fn reset(&mut self) {
        self.state = [[BiquadState::default(); MAX_SECTIONS]; MAX_CHANNELS];
    }
    fn process(
        &mut self,
        _rt: keel_core::Rt<'_>,
        io: keel_core::PlanarMut<'_>,
        _scratch: &mut [f32],
    ) {
        let nsec = self.len.min(MAX_SECTIONS);
        let n_ch = if self.n_ch == 0 {
            io.channels.len().min(MAX_CHANNELS)
        } else {
            self.n_ch.min(MAX_CHANNELS).min(io.channels.len())
        };
        for (ch_i, ch) in io.channels.iter_mut().take(n_ch).enumerate() {
            let state = &mut self.state[ch_i];
            for s in ch.iter_mut() {
                let mut x = *s;
                for i in 0..nsec {
                    x = tick(x, self.sections[i], &mut state[i]);
                }
                *s = x;
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use keel_core::{Kernel, PlanarMut, Prepare, Rt};

    #[test]
    fn process_does_not_share_delay_state_across_channels() {
        let mut sos = Sos::default();
        sos.len = 1;
        sos.sections[0] = Coeffs {
            b0: 1.0,
            b1: 0.0,
            b2: 0.0,
            a1: -0.9,
            a2: 0.0,
        };
        sos.prepare(Prepare {
            sample_rate: 48_000.0,
            max_block: 8,
            channels: 2,
        })
        .unwrap();

        let mut l = [1.0f32, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0];
        let mut r = [0.0f32; 8];
        {
            let mut chs: [&mut [f32]; 2] = [&mut l, &mut r];
            sos.process(Rt::now(), PlanarMut { channels: &mut chs }, &mut []);
        }

        let right_energy: f32 = r.iter().map(|x| x * x).sum();
        assert!(
            right_energy < 1e-12,
            "right channel must stay silent, got energy {right_energy} samples={r:?}"
        );
        assert!(l[0].abs() > 0.5, "left impulse must pass, got {:?}", l);
    }

    #[test]
    fn process_clamps_len_to_section_count() {
        let mut sos = Sos::default();
        sos.len = 99;
        sos.prepare(Prepare {
            sample_rate: 48_000.0,
            max_block: 1,
            channels: 1,
        })
        .unwrap();
        let mut l = [1.0f32];
        let mut chs: [&mut [f32]; 1] = [&mut l];
        sos.process(Rt::now(), PlanarMut { channels: &mut chs }, &mut []);
    }
}
