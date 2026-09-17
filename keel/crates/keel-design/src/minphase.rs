//! Min-phase IR from a real r2c magnitude spectrum (cepstrum).

use num_complex::Complex;
use rustfft::FftPlanner;

/// `mag` is length `N/2+1` (DC..Nyquist). Returns a length-`N` min-phase IR.
pub fn min_phase_ir_from_magnitude(mag: &[f64]) -> Vec<f64> {
    assert!(mag.len() >= 2, "need at least DC and Nyquist");
    let n = (mag.len() - 1) * 2;
    let mut spec = vec![Complex::<f64>::new(0.0, 0.0); n];
    for (k, &m) in mag.iter().enumerate() {
        spec[k] = Complex::new(m.max(1e-30).ln(), 0.0);
    }
    for k in 1..mag.len() - 1 {
        spec[n - k] = spec[k];
    }

    let mut planner = FftPlanner::<f64>::new();
    planner.plan_fft_inverse(n).process(&mut spec);

    let mut cep = vec![Complex::new(0.0, 0.0); n];
    cep[0] = Complex::new(spec[0].re / n as f64, 0.0);
    for i in 1..n / 2 {
        cep[i] = Complex::new(2.0 * spec[i].re / n as f64, 0.0);
    }
    cep[n / 2] = Complex::new(spec[n / 2].re / n as f64, 0.0);

    planner.plan_fft_forward(n).process(&mut cep);
    for z in cep.iter_mut() {
        *z = z.exp();
    }
    planner.plan_fft_inverse(n).process(&mut cep);
    cep.iter().map(|z| z.re / n as f64).collect()
}
