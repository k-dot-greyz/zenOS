//! Cascaded SOS. Runtime `len` capped by const `N` (default 16).

use keel_core::{Error, Kernel, Needs, PlanarMut, Prepare, Rt, begin_block};

use crate::biquad::{Biquad, BiquadState, Coeffs};

#[derive(Clone)]
pub struct Sos<const N: usize = 16> {
    sections: [Coeffs; N],
    len: usize,
    states: Vec<[BiquadState; N]>,
}

impl<const N: usize> Default for Sos<N> {
    fn default() -> Self {
        Self {
            sections: [Coeffs::identity(); N],
            len: 0,
            states: vec![[BiquadState::default(); N]; 1],
        }
    }
}

impl<const N: usize> Sos<N> {
    pub fn len(&self) -> usize {
        self.len
    }

    pub fn is_empty(&self) -> bool {
        self.len == 0
    }

    pub fn sections(&self) -> &[Coeffs] {
        &self.sections[..self.len]
    }

    /// Replace coefficients. Delay state is preserved (block-boundary swap).
    pub fn set_sections(&mut self, sections: &[Coeffs]) -> Result<(), Error> {
        if sections.len() > N {
            return Err(Error("sos len exceeds N"));
        }
        self.sections[..sections.len()].copy_from_slice(sections);
        for c in &mut self.sections[sections.len()..] {
            *c = Coeffs::identity();
        }
        self.len = sections.len();
        Ok(())
    }

    pub(crate) fn coeff_copy(&self) -> ([Coeffs; N], usize) {
        (self.sections, self.len)
    }

    fn resize_states(&mut self, channels: usize) {
        let channels = channels.max(1);
        self.states.resize(channels, [BiquadState::default(); N]);
    }

    fn cascade(sections: &[Coeffs; N], len: usize, x: f32, state: &mut [BiquadState; N]) -> f32 {
        let mut y = x;
        let n = len.min(N);
        for (i, c) in sections.iter().take(n).enumerate() {
            y = Biquad::tick(y, *c, &mut state[i]);
        }
        y
    }
}

impl<const N: usize> Kernel for Sos<N> {
    fn prepare(&mut self, p: Prepare) -> Result<Needs, Error> {
        self.resize_states(p.channels);
        Ok(Needs {
            state: p.channels * N * core::mem::size_of::<BiquadState>(),
            scratch: 0,
        })
    }

    fn reset(&mut self) {
        for ch in &mut self.states {
            *ch = [BiquadState::default(); N];
        }
    }

    fn process(&mut self, _rt: Rt<'_>, io: PlanarMut<'_>, _scratch: &mut [f32]) {
        begin_block();
        let n_ch = io.channels.len().min(self.states.len());
        let sections = self.sections;
        let len = self.len;
        for ch in 0..n_ch {
            let state = &mut self.states[ch];
            for s in io.channels[ch].iter_mut() {
                *s = Self::cascade(&sections, len, *s, state);
            }
        }
    }
}
