//! Goldens and Kernel behavior for keel-iir (#75).
//!
//! Reference vectors are produced by `scripts/gen_goldens.py` via
//! `scipy.signal.sosfilt` (DF2T). Runtime tests do not import SciPy.

use keel_core::{Kernel, PlanarMut, Prepare, Rt, begin_block};
use keel_iir::{Bank, Biquad, BiquadState, Coeffs, Sos, Svf};
use serde::Deserialize;

const MAX_ABS_ERR: f32 = 1e-5;

#[derive(Deserialize)]
struct Goldens {
    cases: Vec<Case>,
}

#[derive(Deserialize)]
struct Case {
    name: String,
    sos: Vec<[f64; 6]>,
    impulse_in: Vec<f64>,
    impulse_out: Vec<f64>,
    sine_in: Vec<f64>,
    sine_out: Vec<f64>,
}

fn load_goldens() -> Goldens {
    serde_json::from_str(include_str!("fixtures/sosfilt_goldens.json")).unwrap()
}

fn coeffs_from_scipy_row(row: [f64; 6]) -> Coeffs {
    let a0 = row[3] as f32;
    assert!(a0 != 0.0);
    Coeffs {
        b0: row[0] as f32 / a0,
        b1: row[1] as f32 / a0,
        b2: row[2] as f32 / a0,
        a1: row[4] as f32 / a0,
        a2: row[5] as f32 / a0,
    }
}

fn f32s(v: &[f64]) -> Vec<f32> {
    v.iter().map(|x| *x as f32).collect()
}

fn max_abs_err(a: &[f32], b: &[f32]) -> f32 {
    a.iter()
        .zip(b)
        .map(|(x, y)| (x - y).abs())
        .fold(0.0_f32, f32::max)
}

fn render_mono(sos: &mut Sos<16>, input: &[f32]) -> Vec<f32> {
    let mut buf = input.to_vec();
    let mut chans: [&mut [f32]; 1] = [&mut buf];
    let io = PlanarMut {
        channels: &mut chans,
    };
    sos.process(Rt::enter(), io, &mut []);
    buf
}

#[test]
fn goldens_match_scipy_sosfilt_impulse_and_sine() {
    let goldens = load_goldens();
    for case in goldens.cases {
        let sections: Vec<Coeffs> = case
            .sos
            .iter()
            .copied()
            .map(coeffs_from_scipy_row)
            .collect();
        let mut sos = Sos::<16>::default();
        sos.set_sections(&sections)
            .unwrap_or_else(|_| panic!("{}", case.name));

        sos.reset();
        let y_imp = render_mono(&mut sos, &f32s(&case.impulse_in));
        let err_imp = max_abs_err(&y_imp, &f32s(&case.impulse_out));
        assert!(
            err_imp < MAX_ABS_ERR,
            "{} impulse max abs err {err_imp} (>= {MAX_ABS_ERR})",
            case.name
        );

        sos.reset();
        let y_sin = render_mono(&mut sos, &f32s(&case.sine_in));
        let err_sin = max_abs_err(&y_sin, &f32s(&case.sine_out));
        assert!(
            err_sin < MAX_ABS_ERR,
            "{} sine 1k/48k max abs err {err_sin} (>= {MAX_ABS_ERR})",
            case.name
        );
    }
}

#[test]
fn stereo_channels_do_not_share_delay_state() {
    let lpf = coeffs_from_scipy_row(load_goldens().cases[0].sos[0]);
    let mut sos = Sos::<16>::default();
    sos.set_sections(&[lpf]).unwrap();
    sos.prepare(Prepare {
        sample_rate: 48_000.0,
        max_block: 8,
        channels: 2,
    })
    .unwrap();

    let mut left = vec![1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0];
    let mut right = vec![0.0; 8];
    {
        let mut chans: [&mut [f32]; 2] = [&mut left, &mut right];
        let io = PlanarMut {
            channels: &mut chans,
        };
        sos.process(Rt::enter(), io, &mut []);
    }
    assert!(
        right.iter().all(|s| *s == 0.0),
        "right channel must stay silent; got {right:?}"
    );
    assert_ne!(left[0], 0.0, "left impulse should produce output");
}

#[test]
fn set_sections_rejects_len_above_const_n() {
    let mut sos = Sos::<2>::default();
    let too_many = [Coeffs::identity(), Coeffs::identity(), Coeffs::identity()];
    assert!(sos.set_sections(&too_many).is_err());
}

#[test]
fn biquad_tick_is_df2t_mul_add() {
    let c = Coeffs::identity();
    let mut z = BiquadState::default();
    assert_eq!(Biquad::tick(0.5, c, &mut z), 0.5);
    assert_eq!(Biquad::tick(0.0, c, &mut z), 0.0);
}

#[test]
fn bank_four_channels_match_independent_mono() {
    let sections: Vec<Coeffs> = load_goldens().cases[1]
        .sos
        .iter()
        .copied()
        .map(coeffs_from_scipy_row)
        .collect();
    let n = 64usize;
    let mut bank = Bank::<16>::default();
    bank.prepare(Prepare {
        sample_rate: 48_000.0,
        max_block: n,
        channels: 4,
    })
    .unwrap();
    bank.publish(&{
        let mut s = Sos::<16>::default();
        s.set_sections(&sections).unwrap();
        s
    });

    let mut ch: [Vec<f32>; 4] = std::array::from_fn(|i| {
        let mut v = vec![0.0; n];
        v[0] = (i as f32) + 1.0;
        v
    });
    {
        let [c0, c1, c2, c3] = &mut ch;
        let mut slices: [&mut [f32]; 4] = [c0, c1, c2, c3];
        let io = PlanarMut {
            channels: &mut slices,
        };
        begin_block();
        bank.process(Rt::enter(), io, &mut []);
    }

    for (i, bank_ch) in ch.iter().enumerate() {
        let mut mono = Sos::<16>::default();
        mono.set_sections(&sections).unwrap();
        mono.prepare(Prepare {
            sample_rate: 48_000.0,
            max_block: n,
            channels: 1,
        })
        .unwrap();
        let mut buf = vec![0.0; n];
        buf[0] = (i as f32) + 1.0;
        let y = render_mono(&mut mono, &buf);
        let err = max_abs_err(bank_ch, &y);
        assert!(err < MAX_ABS_ERR, "bank ch{i} vs mono err {err}");
    }
}

#[test]
fn coeff_swap_applies_at_block_start_not_mid_block() {
    let lpf = coeffs_from_scipy_row(load_goldens().cases[0].sos[0]);
    let id = Coeffs::identity();

    let mut bank = Bank::<16>::default();
    bank.prepare(Prepare {
        sample_rate: 48_000.0,
        max_block: 8,
        channels: 1,
    })
    .unwrap();

    let mut sos_lpf = Sos::<16>::default();
    sos_lpf.set_sections(&[lpf]).unwrap();
    bank.publish(&sos_lpf);

    let mut block1 = vec![1.0, 0.0, 0.0, 0.0];
    {
        let mut chans: [&mut [f32]; 1] = [&mut block1];
        bank.process(
            Rt::enter(),
            PlanarMut {
                channels: &mut chans,
            },
            &mut [],
        );
    }

    let mut sos_id = Sos::<16>::default();
    sos_id.set_sections(&[id]).unwrap();
    bank.publish(&sos_id);

    let mut block2 = vec![0.0, 0.0, 0.0, 0.0];
    {
        let mut chans: [&mut [f32]; 1] = [&mut block2];
        bank.process(
            Rt::enter(),
            PlanarMut {
                channels: &mut chans,
            },
            &mut [],
        );
    }

    let mut ref_sos = Sos::<16>::default();
    ref_sos.set_sections(&[lpf]).unwrap();
    let _ = render_mono(&mut ref_sos, &[1.0, 0.0, 0.0, 0.0]);
    ref_sos.set_sections(&[id]).unwrap();
    let expected = render_mono(&mut ref_sos, &[0.0, 0.0, 0.0, 0.0]);
    let err = max_abs_err(&block2, &expected);
    assert!(
        err < MAX_ABS_ERR,
        "swap at block boundary must continue state with new coeffs; err {err}"
    );
}

#[test]
fn begin_block_keeps_denormal_tail_finite() {
    begin_block();
    let c = Coeffs {
        b0: 1.0,
        b1: 0.0,
        b2: 0.0,
        a1: -1.999_999,
        a2: 0.999_999,
    };
    let mut z = BiquadState::default();
    let mut y = Biquad::tick(1e-38, c, &mut z);
    for _ in 0..10_000 {
        y = Biquad::tick(0.0, c, &mut z);
    }
    assert!(y.is_finite(), "denormal tail exploded: {y}");
}

#[test]
fn svf_tpt_stub_is_present() {
    let mut svf = Svf::default();
    let (lp, bp, hp) = svf.tick(0.1);
    assert!(lp.is_finite() && bp.is_finite() && hp.is_finite());
}
