# Third-party code

zenOS as a whole is MIT-licensed (see the root [`LICENSE`](../LICENSE)). The
files below are vendored from other projects under their own licenses — MIT
covers zenOS's own code, not these.

| File | Source | License |
|------|--------|---------|
| [`env-doctor.sh`](../env-doctor.sh) | [k-dot-greyz/env-doctor](https://github.com/k-dot-greyz/env-doctor) | GPL-3.0 — full text: [`env-doctor.GPL-3.0.LICENSE`](env-doctor.GPL-3.0.LICENSE) |

`env-doctor.sh` is a single self-contained script (no build step, doesn't
link against or import zenOS code) invoked as a standalone diagnostic — see
[`CLAUDE.md`](../CLAUDE.md) and [`Makefile`](../Makefile). If you fork or
redistribute zenOS, keep `env-doctor.sh`'s own license header intact and
this notice alongside it.
