//! TPT SVF stub (modulated knobs). Not part of the sosfilt goldens.

#[derive(Clone, Copy, Debug)]
pub struct Svf {
    pub g: f32,
    pub k: f32,
    ic1eq: f32,
    ic2eq: f32,
}

impl Default for Svf {
    fn default() -> Self {
        Self {
            g: 0.0,
            k: 0.0,
            ic1eq: 0.0,
            ic2eq: 0.0,
        }
    }
}

impl Svf {
    /// One TPT sample. Returns `(lp, bp, hp)`.
    pub fn tick(&mut self, x: f32) -> (f32, f32, f32) {
        let g = self.g;
        let k = self.k;
        let dinv = 1.0 / g.mul_add(g + k, 1.0);
        let v1 = g * (x - self.ic2eq - k * self.ic1eq) * dinv;
        let v2 = self.ic1eq + v1;
        let v3 = self.ic2eq + g * v2;
        self.ic1eq = v2 + v1;
        self.ic2eq = v3 + g * v2;
        let lp = v3;
        let bp = v2;
        let hp = x - k * bp - lp;
        (lp, bp, hp)
    }
}
