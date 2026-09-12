//! ISA dispatch. Neon path is a hook: same packing, replace the butterfly later.

use crate::{scalar, Backend, FftPlan};

#[inline]
pub(crate) fn active() -> Backend {
    #[cfg(all(target_arch = "aarch64", target_feature = "neon"))]
    {
        Backend::Neon
    }
    #[cfg(not(all(target_arch = "aarch64", target_feature = "neon")))]
    {
        Backend::Scalar
    }
}

pub(crate) fn r2c(plan: &FftPlan, time: &[f32], spec: &mut [f32], scratch: &mut [f32]) {
    #[cfg(all(target_arch = "aarch64", target_feature = "neon"))]
    {
        neon::r2c(plan, time, spec, scratch);
        return;
    }
    scalar::r2c(plan, time, spec, scratch);
}

pub(crate) fn c2r(plan: &FftPlan, spec: &[f32], time: &mut [f32], scratch: &mut [f32]) {
    #[cfg(all(target_arch = "aarch64", target_feature = "neon"))]
    {
        neon::c2r(plan, spec, time, scratch);
        return;
    }
    scalar::c2r(plan, spec, time, scratch);
}

#[cfg(all(target_arch = "aarch64", target_feature = "neon"))]
mod neon {
    use super::FftPlan;

    /// Placeholder: packing stays here; swap `fft_radix2` for NEON butterflies.
    pub(crate) fn r2c(plan: &FftPlan, time: &[f32], spec: &mut [f32], scratch: &mut [f32]) {
        crate::scalar::r2c(plan, time, spec, scratch);
    }

    pub(crate) fn c2r(plan: &FftPlan, spec: &[f32], time: &mut [f32], scratch: &mut [f32]) {
        crate::scalar::c2r(plan, spec, time, scratch);
    }
}
