# zenOS dex asset-lib scaffold

Draft. Roast this on the PR. Canonical contract: `dex/banks.yaml`.

dev-master itself is a private repo (`k-dot-greyz/dev-master`) this Cloud checkout cannot clone. The bank map below is the public mapping already in `dex/README.md`, plus the language-split pattern used by the public sibling `zen-electric-systems` (`engine/{js,py,rs}` + `implementations/` + `schemas/`).

## What this is

A **filetree scaffold**, not a rewrite of the Python runtime. `zen/` stays the importable package (`zen = zen.cli:main`). Catalog YAML stays at `dex/models.yaml` and `dex/procedures.yaml` so `zen dex` and env-doctor keep working.

## Bank parents (dex subdirs)

| MIDI bank | dir | domain |
| --- | --- | --- |
| `0x7F` | `dex/kernel/` | how to build |
| `0x7E` | `dex/ops/` | how to build |
| `0x7D` | `dex/dev/` | how to build |
| `0x7C` | `dex/agents/` | what's running |
| `0x7B` | `dex/audio/` | what's running |

Every bank has the same inner shape:

```text
dex/<bank>/
  README.md
  schemas/                 # implementation-agnostic by definition
  modules/
    agnostic/              # yaml/md/json reusable packs
    python/ rust/ bash/ termux-bash/ powershell/ javascript/ typescript/
  components/              # smaller than modules, same language split
    agnostic/ python/ rust/ bash/ ...
  projects/                # runnable implementations
    python/ rust/ bash/ termux-bash/ powershell/ javascript/ typescript/
  scripts/                 # one-shot / env ops, not imported as a library
    python/ rust/ bash/ termux-bash/ powershell/ javascript/ sql/ posix-sh/
```

## Shell policy (roast bait)

There is **no** `shell/` or `sh/` directory. Pick a dialect:

| dir | meaning |
| --- | --- |
| `bash/` | GNU Bash 4.2+ (`#!/usr/bin/env bash` or `#!/bin/bash`) |
| `termux-bash/` | Termux on Android (`#!/data/data/com.termux/files/usr/bin/bash`) |
| `posix-sh/` | POSIX sh only. Bashisms are a bug. |
| `powershell/` | Windows PowerShell 5.1 / pwsh 7+ (`*.ps1`) |

## Kind policy

| kind | put it here when |
| --- | --- |
| `schemas/` | JSON Schema / YAML schema. No code. |
| `modules/` | imported or copied by more than one project |
| `components/` | a piece of a module or UI, not a whole library |
| `projects/` | something you run (CLI, app, workflow, prototype) |
| `scripts/` | one-shot ops. If it grows imports and tests, promote it to `projects/` |

## What moved in this draft

| old | new |
| --- | --- |
| `scripts/*.sh` (GNU bash) | `dex/ops/scripts/bash/` or `dex/dev/scripts/bash/` |
| `scripts/*.sh` (Termux shebang) | `dex/ops/scripts/termux-bash/` |
| `scripts/*.ps1` | `dex/ops` or `dex/dev` `/scripts/powershell/` |
| `scripts/*.py` | `dex/ops/scripts/python/` |
| `scripts/extract-download-urls.js` | `dex/ops/scripts/javascript/` |
| `scripts/init-db.sql` | `dex/ops/scripts/sql/` |
| `tools/` | `dex/ops/components/python/tools/` |
| `modules/{roles,contexts,tasks,constraints}` | `dex/agents/modules/agnostic/` |
| `workspace/prototype` | `dex/dev/projects/typescript/mobile-prototype/` |
| `n8n/` | `dex/ops/projects/javascript/n8n/` |

Old `scripts/<file>` paths are **shims** that `exec` the canonical file, so README / Cloud `install` / `start` keep working.

## Deliberately not moved

- `zen/` — runtime import surface. Filing it under `dex/ops/projects/python/zenos-runtime` would break `pyproject.toml` for no gain in this draft.
- `tests/` — pytest convention at repo root.
- `docs/` — human docs stay put; this SCHEMA is the asset-lib map.
- Root `install.sh` / `start.sh` / `install.ps1` / `start.ps1` — public entrypoints. They can later thin-wrap `dex/ops/projects/...`.
- Catalog `dex/models.yaml`, `dex/procedures.yaml`, `dex/7E-00_dex-index.md`, `dex/7E-01_dex-yoinker.py`.

## Open questions for PR roast

1. Bank dirs named `ops` vs MIDI-prefixed `7E-ops` (yoinker-style)?
2. Should `zen/` grow a `package_dir` pointing at `dex/ops/projects/python/` later, or stay root-level forever?
3. Promote Termux into `projects/termux-bash/` instead of `scripts/`?
4. Add `posix-sh/` leaves only where a POSIX file exists, instead of empty dirs in every bank?
5. Root junk (`clone_all_repos.py`, `tts_*.py`, `test_pkm*.py`) — file under `dex/dev/projects/python/legacy/` or delete?
