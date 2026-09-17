//! Butterworth SOS via analog prototype, pre-warp, bilinear transform.

use crate::{CoeffsF64, normalize_a0};
use num_complex::Complex;

/// Lowpass Butterworth as a0-normalized SOS. Even or odd order.
pub fn butterworth_sos(order: usize, sr: f64, f0: f64) -> Vec<CoeffsF64> {
    assert!(order >= 1, "butterworth order must be >= 1");
    let wo = 2.0 * sr * (std::f64::consts::PI * f0 / sr).tan();
    let analog: Vec<Complex<f64>> = (1..=order)
        .map(|k| {
            let theta =
                std::f64::consts::PI * (2.0 * k as f64 + order as f64 - 1.0) / (2.0 * order as f64);
            Complex::from_polar(wo, theta)
        })
        .collect();

    let fs2 = 2.0 * sr;
    let digital: Vec<Complex<f64>> = analog
        .iter()
        .map(|p| (Complex::new(fs2, 0.0) + p) / (Complex::new(fs2, 0.0) - p))
        .collect();

    let mut used = vec![false; digital.len()];
    let mut sections = Vec::new();
    for i in 0..digital.len() {
        if used[i] {
            continue;
        }
        if digital[i].im.abs() < 1e-10 {
            used[i] = true;
            let a1 = -digital[i].re;
            sections.push(normalize_a0(1.0, 1.0, 0.0, 1.0, a1, 0.0));
            continue;
        }
        let mut paired = false;
        for j in (i + 1)..digital.len() {
            if used[j] {
                continue;
            }
            if (digital[i].conj() - digital[j]).norm() < 1e-8 {
                used[i] = true;
                used[j] = true;
                let p1 = digital[i];
                let p2 = digital[j];
                let a1 = -(p1 + p2).re;
                let a2 = (p1 * p2).re;
                sections.push(normalize_a0(1.0, 2.0, 1.0, 1.0, a1, a2));
                paired = true;
                break;
            }
        }
        assert!(paired, "unpaired complex butterworth pole");
    }

    // Force DC gain 1 (lowpass).
    let dc: Complex<f64> = sections.iter().fold(Complex::new(1.0, 0.0), |acc, s| {
        acc * s.eval(Complex::new(1.0, 0.0))
    });
    if dc.norm() > 0.0 {
        sections[0].b0 /= dc.re;
        sections[0].b1 /= dc.re;
        sections[0].b2 /= dc.re;
    }
    sections
}
