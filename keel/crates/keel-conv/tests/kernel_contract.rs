//! #78 contract: Kernel + hybrid-head bounds + wait-free identity until IR plan exists.
//! Uniform OLS / FD IR plan stay blocked on keel-fft r2c (#76) and keel-fir TD (#77).

use keel_conv::{Convolver, HEAD_TAPS_MAX, HEAD_TAPS_MIN};
use keel_core::{Kernel, PlanarMut, Prepare, Rt};

fn prep() -> Prepare {
    Prepare {
        sample_rate: 48_000.0,
        max_block: 64,
        channels: 2,
    }
}

#[test]
fn prepare_uses_max_block_as_partition() {
    let mut conv = Convolver::new();
    let needs = conv.prepare(prep()).expect("prepare");
    assert_eq!(conv.max_block(), 64);
    assert_eq!(conv.channels(), 2);
    assert!(needs.scratch_bytes >= 64 * 2);
}

#[test]
fn latency_equals_head_length() {
    let conv = Convolver::new();
    assert_eq!(conv.latency_samples(), HEAD_TAPS_MIN);
}

#[test]
fn load_ir_rejects_head_outside_32_128() {
    let mut conv = Convolver::new();
    conv.prepare(prep()).unwrap();
    assert!(conv.load_ir(&[1.0], HEAD_TAPS_MIN - 1).is_err());
    assert!(conv.load_ir(&[1.0], HEAD_TAPS_MAX + 1).is_err());
}

#[test]
fn load_ir_blocked_until_fft_and_fir_kernels_exist() {
    let mut conv = Convolver::new();
    conv.prepare(prep()).unwrap();
    let ir = vec![0.0f32; 1024];
    let err = conv
        .load_ir(&ir, 64)
        .expect_err("FD IR plan needs keel-fft r2c + keel-fir TD");
    let msg = format!("{err:?}");
    assert!(
        msg.contains("keel-fft") && msg.contains("keel-fir"),
        "unexpected error: {msg}"
    );
}

#[test]
fn process_is_identity_before_ir_plan() {
    let mut conv = Convolver::new();
    conv.prepare(prep()).unwrap();
    let mut ch0 = vec![0.25f32; 64];
    let mut ch1 = vec![-0.5f32; 64];
    let orig0 = ch0.clone();
    let orig1 = ch1.clone();
    {
        let mut channels: [&mut [f32]; 2] = [&mut ch0, &mut ch1];
        let io = PlanarMut {
            channels: &mut channels,
        };
        let mut scratch = vec![0.0f32; 256];
        conv.process(Rt::now(), io, &mut scratch);
    }
    assert_eq!(ch0, orig0);
    assert_eq!(ch1, orig1);
}
