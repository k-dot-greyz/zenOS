# zenOS Rework / Refactor Sprint Audit

**Date:** 2026-08-05 (updated post–#47 rebase)  
**Baseline:** `main` @ `23cad77` (dex rebrand) + CI floor PR #49  
**Auditor stance:** treat draft CI/docs as non-dogma; Python ≥3.14; Rust-bound.

---

## Executive verdict

zenOS is a **promising OS-shaped CLI** with real modules (agents, PKM, plugins, providers), but the repo still behaves like **three unfinished products stapled together**:

1. Agent launcher + PromptOS critique (`zen/core`, `zen/agents`)
2. Dex catalog / Battle Arena / offline mobile CLI (`cli_v2`, `zen/dex`, Termux adapters)
3. PKM + plugin marketplace + setup “unified” installer

The critical path is not “more features.” It’s **make `zen` installable on 3.14, collapse dual CLIs, keep the dex branding gate green, then carve a thin Rust core** for the hot path. Everything else is satellite.

**#47 (dex) is on `main`. Land #49 (CI floor) next, then #48 (wiki).**

---

## Severity map

| Sev | Finding | Status / why it matters |
|-----|---------|-------------------------|
| P0 | `zen` CLI import | **Fixed in #49 branch:** drop invalid Click alias; register `inbox`; add `main()`. |
| P0 | Editable install | **Fixed:** `setup.py` shim — no `zen` import during PEP 517 builds. |
| P0 | Install poison | **Fixed in #49:** `requirements.txt` no longer lists stdlib stubs. |
| P0 | Packaging | **Fixed on main:** `packages.find` + `httpx` in metadata; subpackages under `zen*`. |
| P1 | Dual CLI | `cli.py` wires `cli_v2` dex/bench/sync — still split brain; collapse later. |
| P1 | Dex migration | **#47 merged** — `zen/dex`, root `dex/`; branding gate in CI via pytest. |
| P1 | Orphan gitlinks | `mcp-config`, `neuro-spicy-devkit` gitlink mode `160000` with empty dirs / no `.gitmodules`. |
| P1 | Root `test_*.py` | Scripts/demos; pytest now scoped to `tests/` only. |
| P2 | Setup god-objects | `unified_setup` 639LOC, `git_setup` 723, `mcp_setup` 503 — Phase theater. |
| P2 | Mobile/offline sprawl | `ui/mobile`, `ai/mobile_adapter`, `utils/mobile_optimizer`, `providers/offline`. |
| P2 | Docs / draft PR graveyard | Genesis novels + stale draft PRs; README now 3.14+. |
| P3 | Empty scaffolds | `agents/`, `modules/*`, `zenOS-dev/`, `integrations/` empty or placeholder. |
| P3 | RN prototype in-tree | `workspace/prototype` — sandbox or external repo. |
| P3 | n8n subtree | Optional integration; shouldn’t gate core CLI. |

---

## Architecture as-is (honest)

```
pyproject → zen.cli:main     ✓ (after Track 0 fixes on #49)
                │
                ├─ plugins, inbox, pkm, dex/bench/sync/arena (from cli_v2)
                ├─ core/{agent,launcher,critique}    (heart — critique TODOs)
                ├─ dex/ + zen/dex/                   (catalog data + sync)
                ├─ providers/{openrouter,offline}
                ├─ setup/*                           (installer monolith)
                └─ ui/, ai/, utils/                  (partial packages)
```

**Data catalogs** live at repo-root `dex/` (YAML) with runtime in `zen/dex/`. New catalog work should stay on that path only.

**Rust:** none yet. CI (#49) has an idle Cargo lane. Don’t pretend Python mobile adapters are the long-term runtime.

---

## Sprint proposal (sequenced)

Think **4 tracks**. Track 0 ships with #49; Track 1 largely done via #47; Tracks 2–3 follow.

### Track 0 — Unbreak the binary (#49)

**Goal:** `pip install -e ".[dev]" && zen --help` works on Python 3.14.

1. CI floor + requirements exorcism (#49).
2. Inbox: `cli.add_command(receive, name="inbox")`.
3. `def main(): cli(obj={})` for entrypoints.
4. `setup.py` PEP 517 shim (no import side effects during build).
5. CI smoke: `zen --help`; ruff hard gate `E9,F821`; pytest `tests/` only.

**Exit:** green Python 3.14 job on PR.

### Track 1 — Identity: dex wins (#47 on main)

**Goal:** one catalog name, one CLI noun (`zen dex`), branding gate.

1. Rebase #49 onto post-#47 `main` (**this PR**).
2. Remove any leftover legacy catalog paths; keep `scripts/check_no_legacy_branding.py` green.
3. Collapse `cli_v2` into `cli.py` when battle/menu surface is stable.
4. Don’t let branding checks block Rust work — but don’t regress tokens in runtime code.

**Exit:** `zen/dex` only; docs/README match; branding test passes.

### Track 2 — Core thin slice (refactor for Rust handoff)

**Goal:** a small, testable domain core that Rust can reimplement later.

| Keep in Python (glue) | Candidate Rust core later |
|-----------------------|---------------------------|
| Click CLI, Rich UI | Catalog load/query (dex YAML/JSON) |
| OpenRouter HTTP | Template render? (maybe stay Py) |
| PKM browser extract | Packet/sysex-style sync schemas |
| Setup wizards | Dex index / fingerprint |

Concrete Python cleanup this track:

1. Split `unified_setup` into detect / validate / apply; drop phase theater.
2. `ContextManager`: pure functions + injectable clock/fs (testable).
3. AutoCritique: implement or stub explicitly — no silent TODO.
4. Move root tests → `tests/`; rewrite as unit tests with fixtures (no live API by default).
5. Kill empty dirs or document them as intentional scaffolds in one `SCAFFOLDS.md`.
6. Remove or externalize orphan gitlinks (`mcp-config`, `neuro-spicy-devkit`).

**Exit:** `tests/` green offline; core modules &lt;300LOC each where practical; setup is a library + thin CLI.

### Track 3 — Product satellites (after Track 1)

Order:

1. **visual-wiki (#48)** — external repo; zen CLI client only.
2. **PKM** — optional extra (`pip install zenos[pkm]`).
3. **Plugins** — contract tests; marketplace later.
4. **Mobile / Termux** — quarantine; don’t block desktop CI.
5. **workspace/prototype (RN)** — extract or mark `sandbox/`.
6. **Rust crate zero** — `crates/zen-dex` read-only catalog parser.

---

## Suggested sprint board (MVP stories)

1. **As a user, I run `zen --help` after install and see real subcommands** (Track 0).
2. **As a user, I run `zen dex models` and get catalog entries from `dex/*.yaml`** (Track 1).
3. **As a contributor, I run `pytest` with no API keys and get green** (Track 2).
4. **As an agent, I run `zen wiki sync` against external visual-wiki** (Track 3).
5. **As a future Rust port, dex catalog parse has fixture-backed golden tests** (Track 2→3).

---

## Open PR hygiene

| Action | PRs |
|--------|-----|
| Merge next | #49 CI floor (rebased on #47) |
| Then | #48 wiki |
| Done | #47 dex |
| Close or revive consciously | stale Jules/security/docs PRs (#33–45 era) |

---

## Explicit non-goals this sprint

- Supporting Python &lt; 3.14
- Perfect mkdocs / genesis doc archaeology
- Expanding n8n or RN prototype features
- New multi-agent “swarm” surface area
- Vendoring visual-wiki into zenOS

---

## Metrics that mean we’re not lying

- [ ] `pip install -e ".[dev]" && zen --help` exits 0 on 3.14
- [ ] CI: Python 3.14 ruff (F821) + compileall + pytest + `zen --help`
- [ ] Branding gate (`tests/test_no_legacy_branding.py`) green
- [ ] `tests/` meaningful offline unit tests (dex load, catalog, branding)
- [ ] No `160000` gitlinks without `.gitmodules`
- [ ] `Cargo.toml` exists OR CI idle Rust lane only

---

## Next after #49 lands

`refactor(cli): fold cli_v2 into cli.py` and optional `crates/zen-dex` spike — only after CI is honest.
