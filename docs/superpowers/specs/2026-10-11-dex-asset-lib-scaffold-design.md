# dex asset-lib scaffold — design spec

Date: 2026-10-11
Branch intent: draft a language-split asset library that follows the zenOS dex bank map, roastable on PR.
North star: `dex/SCHEMA.md` + `dex/banks.yaml`

## Problem

The repo mixes runtime Python (`zen/`), a MIDI-style dex catalog (`dex/*.yaml`), env scripts, Termux bridges, PowerShell, a React Native prototype, and n8n at the root with no language or bank boundary. The dex README already points at **dev-master** for the protocol (`0x7F` kernel, `0x7E` ops, `0x7D` dev, `0x7C` agents, `0x7B` audio) but this tree does not look like that spec.

Ask: restructure so each dex bank parent has `projects/`, `modules/`, and `components/` split by implementation stack — and name the shell, do not dump everything in `shell/`.

## Constraints

- Python runtime floor stays `>=3.14`. Console scripts stay `zen = zen.cli:main`.
- Do not break `dex/models.yaml` / `dex/procedures.yaml` paths (`zen dex`, env-doctor).
- Cloud / docs still call `scripts/zenos-env-install.sh` and `scripts/zenos-env-start.sh` — keep shims.
- This PR is a **scaffold draft**, not a package-layout rewrite of `zen/`.
- Private `k-dot-greyz/dev-master` is not cloneable from this agent. Align to the public mapping in `dex/README.md` and the public sibling pattern in `zen-electric-systems` (`engine/{js,py,rs}`, `schemas/`, `implementations/`).

## Approaches considered

### A. Repeat the language matrix under each dex bank (chosen)

`dex/<bank>/{schemas,modules,components,projects,scripts}/<language>/`

- Pros: matches “within each dex subdir parent”; review can roast empty leaves.
- Cons: empty rust/posix dirs in every bank. Mitigate with SCHEMA + banks.yaml as the contract, `.gitkeep` in empty leaves.

### B. One root `projects/{python,rust,...}` plus a dex catalog only

- Pros: fewer empty dirs.
- Cons: ignores bank parents; mixes kernel/ops/agents assets.

### C. Move `zen/` into `dex/ops/projects/python/zenos`

- Pros: purist.
- Cons: breaks setuptools, PYTHONPATH, every import. Not a draft; a migration.

**Decision: A**, with shims for old script paths.

## Error handling / compatibility

- Shims `exec` the canonical file. If the canonical path is missing, the shim exits 1 with the new path in the message.
- Pytest contract: `tests/test_asset_lib_scaffold.py` forbids generic `shell/` / `sh/` directories.

## Non-goals

- Implementing rust crates or posix ports.
- Relocating `zen/` or rewriting the Click CLI.
- Cloning private dev-master.
- Deleting root installer entrypoints.
