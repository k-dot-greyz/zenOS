//! Transposed Direct Form II biquad. Coeffs do not own delay state.

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Coeffs {
    pub b0: f32,
    pub b1: f32,
    pub b2: f32,
    pub a1: f32,
    pub a2: f32,
}

impl Default for Coeffs {
    fn default() -> Self {
        Self::identity()
    }
}

impl Coeffs {
    pub const fn identity() -> Self {
        Self {
            b0: 1.0,
            b1: 0.0,
            b2: 0.0,
            a1: 0.0,
            a2: 0.0,
        }
    }
}

#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct BiquadState {
    pub z1: f32,
    pub z2: f32,
}

/// DF2T section. State is passed in; this type exists so the tick is named.
pub struct Biquad;

impl Biquad {
    #[inline(always)]
    pub fn tick(x: f32, c: Coeffs, z: &mut BiquadState) -> f32 {
        let y = c.b0.mul_add(x, z.z1);
        z.z1 = (-c.a1).mul_add(y, c.b1.mul_add(x, z.z2));
        z.z2 = c.b2.mul_add(x, (-c.a2) * y);
        y
    }
}

#[inline(always)]
pub fn tick(x: f32, c: Coeffs, z: &mut BiquadState) -> f32 {
    Biquad::tick(x, c, z)
}
