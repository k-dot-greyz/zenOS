# zenOS Rework / Refactor Sprint Audit

**Date:** 2026-08-05  
**Baseline:** `main` @ `c86daf5` (+ CI floor PR #49)  
**Auditor stance:** treat draft CI/docs as non-dogma; Python ≥3.14; Rust-bound.

---

## Executive verdict

zenOS is a **promising OS-shaped CLI** with real modules (agents, PKM, plugins, providers), but the repo currently behaves like **three unfinished products stapled together**:

1. Agent launcher + PromptOS critique (`zen/core`, `zen/agents`)
2. Pokédex / Battle Arena / offline mobile CLI (`cli_v2`, `pokedex/`, Termux adapters)
3. PKM + plugin marketplace + setup “unified” installer

The critical path is not “more features.” It’s **make `zen` importable and installable, collapse dual CLIs, finish pokedex→dex, then carve a thin Rust core** for the hot path. Everything else is satellite.

**Do not build visual-wiki / new product surface on `main` until #49 (CI floor) and #47 (dex) land in that order.**

---

## Severity map

| Sev | Finding | Why it matters |
|-----|---------|----------------|
| P0 | `zen` CLI does not import | `@click.alias` in `zen/inbox.py` — Click has no `.alias`. Entrypoint dead. |
| P0 | `zen.cli:main` missing | `pyproject.toml` scripts point at `main`; only `cli()` exists. |
| P0 | Packaging hole | `[tool.setuptools] packages = ["zen"]` — subpackages not declared; `zen/utils`, `zen/ai`, `zen/pokedex` lack `__init__.py` so `find_packages` skips them. |
| P0 | Install poison (fixed in #49) | `requirements.txt` listed stdlib (`threading`, …). Blocked all CI. |
| P1 | Dual CLI | `cli.py` (entrypoint) vs `cli_v2.py` (pokedex/battle/menu). Split brain. |
| P1 | pokedex→dex unfinished | #47 open, CI was red for install reasons; branding mid-migration. |
| P1 | Orphan gitlinks | `mcp-config`, `neuro-spicy-devkit` gitlink mode `160000` with empty dirs / no `.gitmodules`. |
| P1 | No real `tests/` on main | Root `test_*.py` are scripts/demos; several need API keys; empty/trivial files. |
| P2 | Setup god-objects | `unified_setup` 639LOC, `git_setup` 723, `mcp_setup` 503 — Phase theater. |
| P2 | Mobile/offline sprawl | `ui/mobile`, `ai/mobile_adapter`, `utils/mobile_optimizer`, `providers/offline` — large, Termux-coupled, `time.sleep` still present. |
| P2 | Docs / draft PR graveyard | Genesis novels + ~15 draft/stale PRs; planning docs still say Python 3.8. |
| P3 | Empty scaffolds | `agents/`, `modules/*`, `zenOS-dev/`, `integrations/` empty or placeholder. |
| P3 | RN prototype in-tree | `workspace/prototype` mobile UI — belongs in its own repo or clearly marked sandbox. |
| P3 | n8n subtree | Fine as optional integration; shouldn’t gate core CLI. |

---

## Architecture as-is (honest)

```
pyproject → zen.cli:main     ✗ broken (no main, inbox import crash)
                │
                ├─ plugins, receive(inbox), pkm     (wired but unreachable)
                ├─ cli_v2                            (orphaned richer CLI)
                ├─ core/{agent,launcher,critique}    (heart — critique TODOs)
                ├─ pokedex/ + root pokedex/*.yaml    (catalog data + sync)
                ├─ providers/{openrouter,offline}
                ├─ setup/*                           (installer monolith)
                └─ ui/, ai/, utils/                  (partial packages)
```

**Data catalogs** live at repo-root `pokedex/` (YAML). Dex PR moves this toward `dex/` + `zen/dex/`. Until that merges, every new feature that touches “catalog” is sinkhole risk.

**Rust:** none yet. CI (#49) has an idle Cargo lane. Good. Don’t pretend Python mobile adapters are the long-term runtime.

---

## Sprint proposal (sequenced)

Think **4 tracks**. Tracks 0–1 are non-negotiable before feature PRs. Tracks 2–3 can parallelize after Track 1.

### Track 0 — Unbreak the binary (1–2 focused PRs)

**Goal:** `pip install -e ".[dev]" && zen --help` works on Python 3.14.

1. Land **#49** (CI floor + requirements exorcism).
2. Fix inbox: drop `@click.alias`; register `cli.add_command(receive, name="inbox")` (or rename group).
3. Add `def main(): cli(obj={})` / `cli.main()` export.
4. Fix packaging: `find_packages` / explicit package list; add missing `__init__.py` for `utils`, `ai`, `pokedex`→`dex`.
5. Smoke job in CI: `zen --help` + `python -c "import zen.core, zen.pkm"`.

**Exit:** green smoke on PR; no import errors.

### Track 1 — Identity: dex wins (finish #47)

**Goal:** one catalog name, one CLI noun (`zen dex`), branding gate.

1. Rebase #47 onto #49; fix whatever *real* tests surface after install works.
2. Delete dual paths (`pokedex` leftovers, root YAML → `dex/`).
3. Collapse `cli_v2` pokedex commands into the surviving CLI (or delete `cli_v2` after porting battle/sync).
4. Keep branding check script if it stays cheap; don’t let it block Rust work.

**Exit:** `main` has `zen/dex`, no `zen/pokedex`, docs/README match.

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

1. **visual-wiki (#48)** — external repo; zen CLI client only (already the intent).
2. **PKM** — treat as optional extra (`pip install zenos[pkm]`); Gemini cookie auth is fragile — boundary it.
3. **Plugins** — keep Git-based loader; add contract tests; don’t merge marketplace dreams until dex stable.
4. **Mobile / Termux** — quarantine under `zen/mobile/`; replace `time.sleep` with async; don’t block desktop CI.
5. **workspace/prototype (RN)** — extract or mark `sandbox/` so it doesn’t confuse packaging.
6. **Rust crate zero** — `crates/zen-dex` read-only catalog parser + CLI `zen dex list` calling it (PyO3 or subprocess). Proves the lane.

---

## Suggested sprint board (MVP stories)

Use these as the guiding user stories (TDD default):

1. **As a user, I run `zen --help` after install and see real subcommands** (Track 0).
2. **As a user, I run `zen dex models` and get catalog entries from `dex/*.yaml`** (Track 1).
3. **As a contributor, I run `pytest` with no API keys and get green** (Track 2).
4. **As an agent, I run `zen wiki sync` and get context JSON from an external visual-wiki checkout** (Track 3).
5. **As a future Rust port, dex catalog parse has a fixture-backed golden test** (Track 2→3).

---

## Open PR hygiene (do this mid-sprint)

| Action | PRs |
|--------|-----|
| Merge first | #49 CI floor |
| Rebase + finish | #47 dex |
| Then | #48 wiki |
| Close or revive consciously | pile of draft Jules/security/docs PRs (#33–45 era) — most are noise |
| Conflict watch | #29 old dex-protocol vs #47 — pick one lineage |

Stale drafts are cognitive load. Mass-close with “superseded by rework sprint” unless someone claims them in 48h.

---

## Explicit non-goals this sprint

- Supporting Python &lt; 3.14
- Perfect mkdocs / genesis doc archaeology
- Expanding n8n or RN prototype features
- New multi-agent “swarm” surface area
- Vendoring visual-wiki into zenOS

---

## Metrics that mean we’re not lying

- [ ] `pip install -e ".[dev]" && zen --help` exits 0
- [ ] CI: Python 3.14 compileall + pytest + `zen --help` smoke
- [ ] Zero references to `pokedex` in runtime paths (branding gate optional)
- [ ] `tests/` ≥ N meaningful offline unit tests (start with packaging, dex load, inbox)
- [ ] No `160000` gitlinks without `.gitmodules`
- [ ] `Cargo.toml` exists OR consciously deferred with CI idle lane only

---

## Recommended next commit after this audit

Track 0 hotfixes on a branch off #49:

`fix(cli): remove click.alias, add main(), fix package discovery`

That single PR turns zenOS from “interesting tree” into “runnable tool,” which is the whole point of the OS metaphor.
