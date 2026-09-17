//! Correctness oracle: iterative radix-2, precomputed twiddles, no alloc.

use crate::FftPlan;

#[inline]
unsafe fn load_tw(tw_re: &[f32], tw_im: &[f32], tidx: usize, inverse: bool) -> (f32, f32) {
    debug_assert!(tidx < tw_re.len() && tidx < tw_im.len());
    let wr = unsafe { *tw_re.get_unchecked(tidx) };
    let wi = unsafe { *tw_im.get_unchecked(tidx) };
    (wr, if inverse { -wi } else { wi })
}

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
                let j = i + k + half;
                unsafe {
                    let (wr, wi) = load_tw(tw_re, tw_im, tidx, inverse);
                    let vr = re.get_unchecked(j).mul_add(wr, -(im.get_unchecked(j) * wi));
                    let vi = re.get_unchecked(j).mul_add(wi, im.get_unchecked(j) * wr);
                    let ur = *re.get_unchecked(i + k);
                    let ui = *im.get_unchecked(i + k);
                    *re.get_unchecked_mut(i + k) = ur + vr;
                    *im.get_unchecked_mut(i + k) = ui + vi;
                    *re.get_unchecked_mut(j) = ur - vr;
                    *im.get_unchecked_mut(j) = ui - vi;
                }
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

fn split_workspaces(scratch: &mut [f32], n: usize) -> Option<(&mut [f32], &mut [f32])> {
    if scratch.len() < n * 2 {
        return None;
    }
    let (re, rest) = scratch.split_at_mut(n);
    Some((re, &mut rest[..n]))
}

pub(crate) fn r2c(plan: &FftPlan, time: &[f32], spec: &mut [f32], scratch: &mut [f32]) {
    let n = plan.n();
    debug_assert_eq!(time.len(), n);
    debug_assert_eq!(spec.len(), n + 2);
    let Some((re, im)) = split_workspaces(scratch, n) else {
        return;
    };
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
    debug_assert_eq!(spec.len(), n + 2);
    debug_assert_eq!(time.len(), n);
    let Some((re, im)) = split_workspaces(scratch, n) else {
        return;
    };
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

pub(crate) fn c2c(
    plan: &FftPlan,
    input: &[f32],
    output: &mut [f32],
    scratch: &mut [f32],
    inverse: bool,
) {
    let n = plan.n();
    debug_assert_eq!(input.len(), n * 2);
    debug_assert_eq!(output.len(), n * 2);
    let Some((re, im)) = split_workspaces(scratch, n) else {
        return;
    };
    for k in 0..n {
        re[k] = input[2 * k];
        im[k] = input[2 * k + 1];
    }
    fft_radix2(plan, re, im, inverse);
    let s = if inverse { 1.0 / n as f32 } else { 1.0 };
    for k in 0..n {
        output[2 * k] = re[k] * s;
        output[2 * k + 1] = im[k] * s;
    }
}
