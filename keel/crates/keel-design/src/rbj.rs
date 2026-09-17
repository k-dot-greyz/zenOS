//! RBJ Audio EQ Cookbook (f64). Offline.

use crate::{CoeffsF64, normalize_a0};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum FilterKind {
    Lowpass,
    Highpass,
    Peak,
    Lowshelf,
    Highshelf,
    Notch,
    Allpass,
}

/// Cookbook biquad, a0-normalized. `gain_db` is used by peak/shelf; ignored otherwise.
pub fn rbj(kind: FilterKind, sr: f64, f0: f64, q: f64, gain_db: f64) -> CoeffsF64 {
    let w0 = 2.0 * std::f64::consts::PI * f0 / sr;
    let cosw = w0.cos();
    let sinw = w0.sin();
    let alpha = sinw / (2.0 * q);
    let a = 10.0_f64.powf(gain_db / 40.0);

    let (b0, b1, b2, a0, a1, a2) = match kind {
        FilterKind::Lowpass => (
            (1.0 - cosw) / 2.0,
            1.0 - cosw,
            (1.0 - cosw) / 2.0,
            1.0 + alpha,
            -2.0 * cosw,
            1.0 - alpha,
        ),
        FilterKind::Highpass => (
            (1.0 + cosw) / 2.0,
            -(1.0 + cosw),
            (1.0 + cosw) / 2.0,
            1.0 + alpha,
            -2.0 * cosw,
            1.0 - alpha,
        ),
        FilterKind::Peak => (
            1.0 + alpha * a,
            -2.0 * cosw,
            1.0 - alpha * a,
            1.0 + alpha / a,
            -2.0 * cosw,
            1.0 - alpha / a,
        ),
        FilterKind::Notch => (1.0, -2.0 * cosw, 1.0, 1.0 + alpha, -2.0 * cosw, 1.0 - alpha),
        FilterKind::Allpass => (
            1.0 - alpha,
            -2.0 * cosw,
            1.0 + alpha,
            1.0 + alpha,
            -2.0 * cosw,
            1.0 - alpha,
        ),
        FilterKind::Lowshelf => {
            let two_sa = 2.0 * a.sqrt() * alpha;
            (
                a * ((a + 1.0) - (a - 1.0) * cosw + two_sa),
                2.0 * a * ((a - 1.0) - (a + 1.0) * cosw),
                a * ((a + 1.0) - (a - 1.0) * cosw - two_sa),
                (a + 1.0) + (a - 1.0) * cosw + two_sa,
                -2.0 * ((a - 1.0) + (a + 1.0) * cosw),
                (a + 1.0) + (a - 1.0) * cosw - two_sa,
            )
        }
        FilterKind::Highshelf => {
            let two_sa = 2.0 * a.sqrt() * alpha;
            (
                a * ((a + 1.0) + (a - 1.0) * cosw + two_sa),
                -2.0 * a * ((a - 1.0) + (a + 1.0) * cosw),
                a * ((a + 1.0) + (a - 1.0) * cosw - two_sa),
                (a + 1.0) - (a - 1.0) * cosw + two_sa,
                2.0 * ((a - 1.0) - (a + 1.0) * cosw),
                (a + 1.0) - (a - 1.0) * cosw - two_sa,
            )
        }
    };
    normalize_a0(b0, b1, b2, a0, a1, a2)
}
