//! Regularized Kirkeby inversion with a max-boost ceiling.

use num_complex::Complex;

/// `C = H* T / (|H|^2 + β)` then cap `|C|` at `max_boost_db`.
pub fn kirkeby_invert(
    h: &[Complex<f64>],
    target: &[Complex<f64>],
    beta: &[f64],
    max_boost_db: f64,
) -> Vec<Complex<f64>> {
    assert_eq!(h.len(), target.len());
    assert_eq!(h.len(), beta.len());
    let cap = 10.0_f64.powf(max_boost_db / 20.0);
    h.iter()
        .zip(target.iter())
        .zip(beta.iter())
        .map(|((h, t), b)| {
            let denom = h.norm_sqr() + *b;
            let mut c = if denom > 0.0 {
                h.conj() * t / denom
            } else {
                Complex::new(0.0, 0.0)
            };
            let mag = c.norm();
            if mag > cap && mag > 0.0 {
                c *= cap / mag;
            }
            c
        })
        .collect()
}
