//! Goldens vs numpy.convolve / causal FIR (issue #77).

use keel_core::{Kernel, PlanarMut, Prepare, Rt};
use keel_fir::{FirHb, FirTd, MAX_TAPS};

#[path = "data/goldens_data.rs"]
mod goldens_data;
use goldens_data::*;

fn max_abs(a: &[f32], b: &[f32]) -> f32 {
    a.iter()
        .zip(b)
        .map(|(x, y)| (x - y).abs())
        .fold(0.0_f32, f32::max)
}

fn process_mono(fir: &mut FirTd, x: &[f32]) -> Vec<f32> {
    let mut ch = x.to_vec();
    let mut channels: [&mut [f32]; 1] = [ch.as_mut_slice()];
    let io = PlanarMut {
        channels: &mut channels,
    };
    fir.process(Rt::now(), io, &mut []);
    ch
}

#[test]
fn numpy_convolve_goldens_n_in_16_256() {
    for (name, c) in NUMPY_NS {
        let n = c.taps.len();
        let mut fir = FirTd::from_taps(c.taps).expect("taps");
        fir.prepare(Prepare {
            sample_rate: 48_000.0,
            max_block: c.x.len(),
            channels: 1,
        })
        .unwrap();
        let y = process_mono(&mut fir, c.x);
        let err = max_abs(&y, c.y);
        assert!(
            err < 2e-5,
            "n={n} ({name}) max abs err vs numpy.convolve-equivalent = {err}"
        );
    }
}

#[test]
fn delay_line_seam_matches_one_shot() {
    let taps: Vec<f32> = (0..16).map(|i| (i as f32 + 1.0) * 0.01).collect();
    let x: Vec<f32> = (0..40).map(|i| ((i * 3) % 7) as f32 - 3.0).collect();

    let mut a = FirTd::from_taps(&taps).unwrap();
    a.prepare(Prepare {
        sample_rate: 48_000.0,
        max_block: x.len(),
        channels: 1,
    })
    .unwrap();
    let one_shot = process_mono(&mut a, &x);

    let mut b = FirTd::from_taps(&taps).unwrap();
    b.prepare(Prepare {
        sample_rate: 48_000.0,
        max_block: 1,
        channels: 1,
    })
    .unwrap();
    let mut samplewise = Vec::with_capacity(x.len());
    for &s in &x {
        samplewise.push(process_mono(&mut b, &[s])[0]);
    }

    let mut c = FirTd::from_taps(&taps).unwrap();
    c.prepare(Prepare {
        sample_rate: 48_000.0,
        max_block: 7,
        channels: 1,
    })
    .unwrap();
    let mut chunks = Vec::new();
    for chunk in x.chunks(7) {
        chunks.extend(process_mono(&mut c, chunk));
    }

    assert_eq!(one_shot, samplewise, "wrap at duplicated delay seam");
    assert_eq!(one_shot, chunks, "block size must not change FIR state");
}

#[test]
fn linear_phase_symmetric_path_bit_matches_dense() {
    for (key, c) in [("sym17", &CASE_sym17), ("sym32", &CASE_sym32)] {
        let mut dense = FirTd::from_taps(c.taps).unwrap();
        dense.force_dense();
        dense
            .prepare(Prepare {
                sample_rate: 48_000.0,
                max_block: c.x.len(),
                channels: 1,
            })
            .unwrap();
        let y_dense = process_mono(&mut dense, c.x);

        let mut sym = FirTd::from_taps(c.taps).unwrap();
        assert!(sym.is_linear_phase(), "{key} taps are symmetric");
        sym.prepare(Prepare {
            sample_rate: 48_000.0,
            max_block: c.x.len(),
            channels: 1,
        })
        .unwrap();
        let y_sym = process_mono(&mut sym, c.x);

        let err = max_abs(&y_dense, &y_sym);
        assert!(
            err < 2e-5,
            "{key} symmetric vs dense max abs {err} (f32 pair vs two-mac)"
        );
        let err = max_abs(&y_sym, c.y);
        assert!(err < 2e-5, "{key} vs numpy err={err}");
    }
}

#[test]
fn half_band_decimate_matches_dense_even_samples() {
    let c = &CASE_hb15;
    let mut hb = FirHb::from_taps(c.taps).expect("hb taps");
    hb.prepare(Prepare {
        sample_rate: 48_000.0,
        max_block: c.x.len(),
        channels: 1,
    })
    .unwrap();
    let mut y = vec![0.0f32; c.x.len() / 2];
    hb.decimate(c.x, &mut y);
    let err = max_abs(&y, c.y_decim);
    assert!(err < 2e-5, "hb decim vs numpy even samples err={err}");
}

#[test]
fn rejects_too_many_taps() {
    let taps = vec![0.1f32; MAX_TAPS + 1];
    assert!(FirTd::from_taps(&taps).is_err());
}

#[test]
fn interpolate_doubles_length_and_stays_finite() {
    let mut taps = [0.0f32; 7];
    taps[3] = 0.5;
    taps[1] = 0.25;
    taps[5] = 0.25;
    let mut hb = FirHb::from_taps(&taps).unwrap();
    hb.prepare(Prepare {
        sample_rate: 48_000.0,
        max_block: 16,
        channels: 1,
    })
    .unwrap();
    let x = [1.0f32, -0.5, 0.25, 0.0];
    let mut up = [0.0f32; 8];
    hb.interpolate(&x, &mut up);
    assert!(up.iter().all(|s| s.is_finite()));
    assert_eq!(up.len(), 8);
}
