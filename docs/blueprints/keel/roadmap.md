# keel roadmap

## Week order

1. `keel-core` + law tests + alloc guard
2. `keel-iir` scalar goldens → NEON `Bank`
3. `keel-fft` NEON r2c/c2r for 256..4096, then remaining audio sizes
4. `keel-fir` TD head + half-band
5. `keel-conv` uniform OLS + TD head
6. `keel-design` RBJ + Kirkeby emit

CLAP examples (`keel-peq`, `keel-convolve`) come after the matching kernel is golden. They are consumers, not owners of DSP.

## OSS bar

Public repo can be ugly. crates.io is a promise.

Do not publish crates until:

1. Goldens vs SciPy/PocketFFT on aarch64
2. Alloc hook + 10 s fake 48k/64 callback
3. Pi 5 (or equivalent) bench numbers in-tree
4. At least one kernel exercised in a real Linux ARM host (Reaper/Carla)
5. Bit-identical `keel-cli process` vs plugin planar path

First OSS drop: kernels. Keep measurement protocol and profiles private until they exist.
