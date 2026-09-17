//! IIR kernels. Implementation: issue #75 / `feat/keel-iir`.
//! Stub only on `feat/keel-core` — real DF2T process does not land from #74.

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

#[derive(Default)]
pub struct Sos {
    pub sections: [Coeffs; 16],
    pub len: usize,
    pub state: [BiquadState; 16],
}

impl Kernel for Sos {
    fn prepare(&mut self, _p: keel_core::Prepare) -> Result<keel_core::Needs, keel_core::Error> {
        let _ = keel_core::cache_isa();
        Ok(keel_core::Needs::default())
    }
    fn reset(&mut self) {
        self.state = [BiquadState::default(); 16];
    }
    fn process(
        &mut self,
        _rt: keel_core::Rt<'_>,
        _io: keel_core::PlanarMut<'_>,
        _scratch: &mut [f32],
    ) {
        // Intentionally empty: SOS process is #75 / feat/keel-iir.
    }
}
