//! Audio FFT. Implementation: issue #76 / `feat/keel-fft`.
//! Inverse includes 1/N (see docs/blueprints/keel/layout.md).

pub const AUDIO_SIZES: &[usize] = &[64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384];

pub struct FftPlan {
    pub n: usize,
}

impl FftPlan {
    pub fn new(n: usize) -> Option<Self> {
        AUDIO_SIZES.contains(&n).then_some(Self { n })
    }

    pub fn spec_len(&self) -> usize {
        self.n / 2 + 1
    }
}
