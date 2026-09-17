//! ISA dispatch. Neon path is a hook: same packing, replace the butterfly later.
//!
//! `active()` stays [`Backend::Scalar`] until a NEON butterfly is actually
//! selected. Reporting `Neon` early poisons benches and later dispatch.

use crate::{scalar, Backend, FftPlan};

#[inline]
pub(crate) fn active() -> Backend {
    Backend::Scalar
}

pub(crate) fn r2c(plan: &FftPlan, time: &[f32], spec: &mut [f32], scratch: &mut [f32]) {
    scalar::r2c(plan, time, spec, scratch);
}

pub(crate) fn c2r(plan: &FftPlan, spec: &[f32], time: &mut [f32], scratch: &mut [f32]) {
    scalar::c2r(plan, spec, time, scratch);
}

pub(crate) fn c2c(
    plan: &FftPlan,
    input: &[f32],
    output: &mut [f32],
    scratch: &mut [f32],
    inverse: bool,
) {
    scalar::c2c(plan, input, output, scratch, inverse);
}

/// Placeholder: packing stays here; swap `fft_radix2` for NEON butterflies.
/// Not selected until butterflies exist.
#[cfg(all(target_arch = "aarch64", target_feature = "neon"))]
#[allow(dead_code)]
mod neon {
    use super::FftPlan;

    pub(crate) fn r2c(plan: &FftPlan, time: &[f32], spec: &mut [f32], scratch: &mut [f32]) {
        crate::scalar::r2c(plan, time, spec, scratch);
    }

    pub(crate) fn c2r(plan: &FftPlan, spec: &[f32], time: &mut [f32], scratch: &mut [f32]) {
        crate::scalar::c2r(plan, spec, time, scratch);
    }

    pub(crate) fn c2c(
        plan: &FftPlan,
        input: &[f32],
        output: &mut [f32],
        scratch: &mut [f32],
        inverse: bool,
    ) {
        crate::scalar::c2c(plan, input, output, scratch, inverse);
    }
}
