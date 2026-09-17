//! #74 acceptance tests: planar wrap, alloc guard, begin_block, ISA cache.

use keel_core::{Error, Isa, Kernel, Needs, PlanarMut, Prepare, Rt, begin_block, cache_isa, isa};

#[test]
fn planar_wrap_interleaved_stereo_matches_naive() {
    let interleaved = [1.0f32, 2.0, 3.0, 4.0, 5.0, 6.0];
    let mut left = [0.0f32; 3];
    let mut right = [0.0f32; 3];
    let mut chans: [&mut [f32]; 2] = [&mut left, &mut right];
    let mut planar = PlanarMut::from_channels(&mut chans).expect("planar wrap");
    planar
        .copy_from_interleaved(&interleaved)
        .expect("deinterleave");

    let mut naive_l = [0.0f32; 3];
    let mut naive_r = [0.0f32; 3];
    for i in 0..3 {
        naive_l[i] = interleaved[2 * i];
        naive_r[i] = interleaved[2 * i + 1];
    }
    assert_eq!(planar.channel(0), &naive_l);
    assert_eq!(planar.channel(1), &naive_r);
    assert_eq!(planar.frames(), 3);
}

#[test]
fn planar_rejects_mismatched_channel_lengths() {
    let mut left = [0.0f32; 4];
    let mut right = [0.0f32; 2];
    let mut chans: [&mut [f32]; 2] = [&mut left, &mut right];
    assert!(PlanarMut::from_channels(&mut chans).is_err());
}

struct AllocatingKernel;

impl Kernel for AllocatingKernel {
    fn prepare(&mut self, _p: Prepare) -> Result<Needs, Error> {
        let _ = cache_isa();
        Ok(Needs::default())
    }

    fn reset(&mut self) {}

    fn process(&mut self, _rt: Rt<'_>, _io: PlanarMut<'_>, _scratch: &mut [f32]) {
        // Intentionally new+push: that is the alloc-guard tripwire.
        #[allow(clippy::vec_init_then_push)]
        {
            let mut v = Vec::<f32>::new();
            v.push(1.0);
        }
    }
}

#[cfg(debug_assertions)]
#[test]
fn process_vec_push_in_debug_fails_alloc_guard() {
    let mut k = AllocatingKernel;
    k.prepare(Prepare {
        sample_rate: 48_000.0,
        max_block: 64,
        channels: 2,
    })
    .unwrap();

    let scope = Rt::enter();
    let mut left = [0.0f32; 4];
    let mut right = [0.0f32; 4];
    let mut chans: [&mut [f32]; 2] = [&mut left, &mut right];
    let io = PlanarMut::from_channels(&mut chans).unwrap();
    let mut scratch = [0.0f32; 8];

    let blew = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
        k.process(scope.token(), io, &mut scratch);
    }));
    assert!(
        blew.is_err(),
        "Vec::push inside process must trip the debug alloc guard"
    );
}

#[test]
fn begin_block_does_not_panic() {
    begin_block();
    begin_block();
}

#[cfg(target_arch = "x86_64")]
#[test]
fn begin_block_sets_ftz_daz_on_x86() {
    begin_block();
    let mut mxcsr = 0u32;
    unsafe {
        core::arch::asm!(
            "stmxcsr [{ptr}]",
            ptr = in(reg) &mut mxcsr,
            options(nostack, preserves_flags)
        );
    }
    assert_ne!(mxcsr & 0x8000, 0, "FTZ (bit 15) must be set");
    assert_ne!(mxcsr & 0x40, 0, "DAZ (bit 6) must be set");
}

#[test]
fn isa_is_cached_from_prepare_and_never_scalar_on_aarch64() {
    let detected = cache_isa();
    assert_eq!(isa(), detected);
    assert_eq!(
        isa(),
        cache_isa(),
        "second call must not re-detect a different value"
    );
    #[cfg(target_arch = "aarch64")]
    assert!(
        matches!(detected, Isa::Neon | Isa::Sve),
        "home ISA is NEON (or SVE), not Scalar: {detected:?}"
    );
    #[cfg(not(target_arch = "aarch64"))]
    assert_eq!(detected, Isa::Scalar);
}
