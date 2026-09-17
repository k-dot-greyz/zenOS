//! Offline SOS / Kirkeby / min-phase design. f64, may allocate.
//!
//! Never call these APIs from `Kernel::process`. This crate
//! does not implement `Kernel` and has no audio-thread entry point.

pub mod butter;
pub mod emit;
pub mod kirkeby;
pub mod minphase;
pub mod rbj;

pub use butter::butterworth_sos;
pub use emit::{IrFile, Phase, SosFile};
pub use kirkeby::kirkeby_invert;
pub use minphase::min_phase_ir_from_magnitude;
pub use rbj::{FilterKind, rbj};

use num_complex::Complex;

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct CoeffsF64 {
    pub b0: f64,
    pub b1: f64,
    pub b2: f64,
    pub a1: f64,
    pub a2: f64,
}

impl CoeffsF64 {
    pub fn to_f32(self) -> keel_iir::Coeffs {
        keel_iir::Coeffs {
            b0: self.b0 as f32,
            b1: self.b1 as f32,
            b2: self.b2 as f32,
            a1: self.a1 as f32,
            a2: self.a2 as f32,
        }
    }

    /// H(z) = (b0 + b1 z^-1 + b2 z^-2) / (1 + a1 z^-1 + a2 z^-2)
    pub fn eval(self, z: Complex<f64>) -> Complex<f64> {
        let z1 = z.inv();
        let z2 = z1 * z1;
        let num = Complex::new(self.b0, 0.0) + z1 * self.b1 + z2 * self.b2;
        let den = Complex::new(1.0, 0.0) + z1 * self.a1 + z2 * self.a2;
        num / den
    }
}

pub(crate) fn normalize_a0(b0: f64, b1: f64, b2: f64, a0: f64, a1: f64, a2: f64) -> CoeffsF64 {
    CoeffsF64 {
        b0: b0 / a0,
        b1: b1 / a0,
        b2: b2 / a0,
        a1: a1 / a0,
        a2: a2 / a0,
    }
}
