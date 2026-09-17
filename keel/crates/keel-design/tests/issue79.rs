//! Issue #79 goldens. These tests define the public offline design API.

use keel_core::{Kernel, PlanarMut, Prepare, Rt};
use keel_design::{
    FilterKind, IrFile, Phase, SosFile, butterworth_sos, kirkeby_invert,
    min_phase_ir_from_magnitude, rbj,
};
use keel_iir::{BiquadState, Sos, tick};
use num_complex::Complex;

const SR: f64 = 48_000.0;
const F0: f64 = 1_000.0;

// SciPy `butter(2, 1000, fs=48000, output='ba')` a0-normalized (f64).
const SCIPY_LP2: [f64; 5] = [
    3.91612666054736921e-03,
    7.83225332109473843e-03,
    3.91612666054736921e-03,
    -1.81534108270456795e+00,
    8.31005589346757501e-01,
];

fn max_abs_diff(c: keel_design::CoeffsF64, golden: [f64; 5]) -> f64 {
    let got = [c.b0, c.b1, c.b2, c.a1, c.a2];
    got.iter()
        .zip(golden.iter())
        .map(|(a, b)| (a - b).abs())
        .fold(0.0, f64::max)
}

#[test]
fn rbj_lowpass_1k_48k_matches_scipy_butter_biquad() {
    let c = rbj(FilterKind::Lowpass, SR, F0, 1.0 / 2.0_f64.sqrt(), 0.0);
    let err = max_abs_diff(c, SCIPY_LP2);
    assert!(
        err < 1e-6,
        "RBJ vs SciPy butter/biquad max abs err {err:e} coeffs={c:?}"
    );
}

#[test]
fn butterworth_sos_bilinear_prewarp_matches_rbj_order2() {
    let sos = butterworth_sos(2, SR, F0);
    assert_eq!(sos.len(), 1);
    let err = max_abs_diff(sos[0], SCIPY_LP2);
    assert!(err < 1e-6, "butter SOS vs SciPy err {err:e}");
}

#[test]
fn butterworth4_mag_at_cutoff_is_minus_3db() {
    let sos = butterworth_sos(4, SR, F0);
    let z = Complex::from_polar(1.0, 2.0 * std::f64::consts::PI * F0 / SR);
    let mut h = Complex::new(1.0, 0.0);
    for s in &sos {
        h *= s.eval(z);
    }
    let mag = h.norm();
    assert!(
        (mag - 0.5_f64.sqrt()).abs() < 1e-3,
        "order-4 |H(1kHz)| = {mag} want ~1/sqrt(2)"
    );
}

#[test]
fn kirkeby_does_not_boost_a_40db_notch_past_ceiling() {
    let n = 64;
    let mut h = vec![Complex::new(1.0, 0.0); n];
    h[8] = Complex::new(0.01, 0.0); // -40 dB
    let target = vec![Complex::new(1.0, 0.0); n];
    let beta = vec![1e-18; n];
    let ceiling_db = 12.0;
    let c = kirkeby_invert(&h, &target, &beta, ceiling_db);
    let boost_db = 20.0 * c[8].norm().max(1e-30).log10();
    assert!(
        boost_db <= ceiling_db + 1e-9,
        "notch boost {boost_db} dB exceeds ceiling {ceiling_db}"
    );
    // Flat bins stay ~0 dB.
    assert!((c[0].norm() - 1.0).abs() < 1e-6);
}

#[test]
fn emitted_sos_ticks_through_keel_iir_without_rebuild() {
    let designed = rbj(FilterKind::Lowpass, SR, F0, 1.0 / 2.0_f64.sqrt(), 0.0);
    let bytes = SosFile {
        sections: vec![designed],
    }
    .encode();
    let decoded = SosFile::decode(&bytes).expect("keel.sos roundtrip");
    assert_eq!(decoded.sections.len(), 1);

    let mut sos = Sos::default();
    sos.len = 1;
    sos.sections[0] = decoded.sections[0].to_f32();
    sos.prepare(Prepare {
        sample_rate: SR as f32,
        max_block: 4,
        channels: 1,
    })
    .unwrap();

    let mut x = [1.0f32, 0.0, 0.0, 0.0];
    {
        let mut chs: [&mut [f32]; 1] = [&mut x];
        sos.process(Rt::now(), PlanarMut { channels: &mut chs }, &mut []);
    }
    assert!(
        x.iter().any(|s| s.abs() > 0.0),
        "filter must produce output"
    );

    // Same coeffs via raw tick, no re-prepare.
    let mut z = BiquadState::default();
    let y0 = tick(1.0, decoded.sections[0].to_f32(), &mut z);
    assert!(y0.abs() > 0.0);
}

#[test]
fn emit_ir_carries_sr_latency_phase_header() {
    let ir = IrFile {
        sr: SR as f32,
        latency: 32.0,
        phase: Phase::Min,
        samples: vec![1.0, 0.0, -0.5],
    };
    let bytes = ir.encode();
    let back = IrFile::decode(&bytes).expect("keel.ir roundtrip");
    assert_eq!(back.sr, SR as f32);
    assert_eq!(back.latency, 32.0);
    assert_eq!(back.phase, Phase::Min);
    assert_eq!(back.samples, vec![1.0, 0.0, -0.5]);
    let wav = ir.encode_wav();
    assert!(wav.starts_with(b"RIFF"));
}

#[test]
fn min_phase_from_magnitude_is_causal() {
    // Decaying exponential is already min-phase; reconstruct from |H|.
    let n = 64;
    let ir: Vec<f64> = (0..n).map(|i| 0.8_f64.powi(i as i32)).collect();
    let mag = {
        // |rfft| via naive DFT real-even packing length n/2+1
        let mut m = vec![0.0; n / 2 + 1];
        for k in 0..m.len() {
            let mut re = 0.0;
            let mut im = 0.0;
            for (t, &x) in ir.iter().enumerate() {
                let w = 2.0 * std::f64::consts::PI * (k as f64) * (t as f64) / (n as f64);
                re += x * w.cos();
                im -= x * w.sin();
            }
            m[k] = (re * re + im * im).sqrt();
        }
        m
    };
    let y = min_phase_ir_from_magnitude(&mag);
    assert_eq!(y.len(), n);
    let head: f64 = y.iter().take(8).map(|v| v * v).sum();
    let tail: f64 = y.iter().rev().take(8).map(|v| v * v).sum();
    assert!(head > tail, "min-phase energy should sit at the start");
}

#[test]
fn rbj_emits_all_cookbook_kinds() {
    for kind in [
        FilterKind::Lowpass,
        FilterKind::Highpass,
        FilterKind::Peak,
        FilterKind::Lowshelf,
        FilterKind::Highshelf,
        FilterKind::Notch,
        FilterKind::Allpass,
    ] {
        let c = rbj(kind, SR, F0, 0.707, 6.0);
        assert!(c.b0.is_finite() && c.a2.is_finite(), "{kind:?}");
    }
}
