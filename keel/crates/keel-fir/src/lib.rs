//! Time-domain FIR. Implementation: issue #77 / `feat/keel-fir`.

pub const MAX_TAPS: usize = 256;

pub struct FirTd {
    pub taps: [f32; MAX_TAPS],
    pub n: usize,
}

impl Default for FirTd {
    fn default() -> Self {
        Self {
            taps: [0.0; MAX_TAPS],
            n: 0,
        }
    }
}
