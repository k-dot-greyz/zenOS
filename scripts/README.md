# scripts/ — compatibility shims

Canonical copies live under dex bank parents, split by **named** language:

| dialect | path |
| --- | --- |
| GNU bash | `dex/ops/scripts/bash/`, `dex/dev/scripts/bash/` |
| Termux bash | `dex/ops/scripts/termux-bash/` |
| PowerShell | `dex/ops/scripts/powershell/`, `dex/dev/scripts/powershell/` |
| Python 3.14+ | `dex/ops/scripts/python/` |
| JavaScript | `dex/ops/scripts/javascript/` |
| SQL | `dex/ops/scripts/sql/` |

Files in this directory `exec` the canonical path so existing docs (`bash scripts/zenos-env-install.sh`) keep working.

See `dex/SCHEMA.md`. There is no `shell/` bucket.
