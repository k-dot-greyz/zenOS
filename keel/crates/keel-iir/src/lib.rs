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

pub struct Sos {
    pub sections: [Coeffs; 16],
    pub len: usize,
    pub state: [BiquadState; 16],
}

impl Default for Sos {
    fn default() -> Self {
        Self {
            sections: [Coeffs::default(); 16],
            len: 0,
            state: [BiquadState::default(); 16],
        }
    }
}

impl Kernel for Sos {
    fn prepare(&mut self, _p: keel_core::Prepare) -> Result<keel_core::Needs, keel_core::Error> {
        Ok(keel_core::Needs::default())
    }
    fn reset(&mut self) {
        self.state = [BiquadState::default(); 16];
    }
    fn process(&mut self, _rt: keel_core::Rt<'_>, io: keel_core::PlanarMut<'_>, _scratch: &mut [f32]) {
        for ch in io.channels.iter_mut() {
            for s in ch.iter_mut() {
                let mut x = *s;
                for i in 0..self.len {
                    x = tick(x, self.sections[i], &mut self.state[i]);
                }
                *s = x;
            }
        }
    }
}
