//! Correctness oracle: iterative radix-2, precomputed twiddles, no alloc.

use crate::FftPlan;

pub(crate) fn fft_radix2(plan: &FftPlan, re: &mut [f32], im: &mut [f32], inverse: bool) {
    let n = plan.n();
    debug_assert_eq!(re.len(), n);
    debug_assert_eq!(im.len(), n);
    bit_reverse(re, im);

    let (tw_re, tw_im) = plan.tw();
    let mut len = 2usize;
    let mut tw_stride = n / 2;
    while len <= n {
        let half = len / 2;
        let mut i = 0;
        while i < n {
            let mut k = 0;
            while k < half {
                let tidx = k * tw_stride;
                let wr = tw_re[tidx];
                let wi = if inverse { -tw_im[tidx] } else { tw_im[tidx] };
                let j = i + k + half;
                let vr = re[j].mul_add(wr, -(im[j] * wi));
                let vi = re[j].mul_add(wi, im[j] * wr);
                let ur = re[i + k];
                let ui = im[i + k];
                re[i + k] = ur + vr;
                im[i + k] = ui + vi;
                re[j] = ur - vr;
                im[j] = ui - vi;
                k += 1;
            }
            i += len;
        }
        len *= 2;
        tw_stride /= 2;
    }
}

fn bit_reverse(re: &mut [f32], im: &mut [f32]) {
    let n = re.len();
    let mut j = 0usize;
    for i in 1..n {
        let mut bit = n >> 1;
        while j & bit != 0 {
            j ^= bit;
            bit >>= 1;
        }
        j ^= bit;
        if i < j {
            re.swap(i, j);
            im.swap(i, j);
        }
    }
}

pub(crate) fn r2c(plan: &FftPlan, time: &[f32], spec: &mut [f32], scratch: &mut [f32]) {
    let n = plan.n();
    let (re, rest) = scratch.split_at_mut(n);
    let im = &mut rest[..n];
    re.copy_from_slice(time);
    im.fill(0.0);
    fft_radix2(plan, re, im, false);
    spec[0] = re[0];
    spec[1] = 0.0;
    for k in 1..n / 2 {
        spec[2 * k] = re[k];
        spec[2 * k + 1] = im[k];
    }
    spec[n] = re[n / 2];
    spec[n + 1] = 0.0;
}

pub(crate) fn c2r(plan: &FftPlan, spec: &[f32], time: &mut [f32], scratch: &mut [f32]) {
    let n = plan.n();
    let (re, rest) = scratch.split_at_mut(n);
    let im = &mut rest[..n];
    re[0] = spec[0];
    im[0] = 0.0;
    re[n / 2] = spec[n];
    im[n / 2] = 0.0;
    for k in 1..n / 2 {
        let sr = spec[2 * k];
        let si = spec[2 * k + 1];
        re[k] = sr;
        im[k] = si;
        re[n - k] = sr;
        im[n - k] = -si;
    }
    fft_radix2(plan, re, im, true);
    let s = 1.0 / n as f32;
    for i in 0..n {
        time[i] = re[i] * s;
    }
}
