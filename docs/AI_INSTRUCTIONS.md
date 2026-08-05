# zenOS AI Onboarding Protocol

## Quick start for AI agents

**Command truth:** [`guides/CLI.md`](./guides/CLI.md). Do not invent verbs.

### 1. Acknowledge
```
I acknowledge zenOS Protocol v1.0 and commit to peaceful collaboration.
```

### 2. Context
zenOS is a human–AI collaborative OS: equal participants, shared knowledge, evolving procedures.

### 3. Core CLI (live today)

```bash
zen --help
zen run --list
zen run --chat
zen setup --validate-only

zen dex models
zen dex procedures --tier epic
zen sync
zen inbox list
zen plugins list
```

Confirm registration:

```bash
python -c "from zen.cli import cli; print(sorted(cli.commands))"
# expect: arena, bench, dex, inbox, pkm, plugins, run, setup, sync
```

### 4. Catalog files

```bash
cat dex/models.yaml
cat dex/procedures.yaml
```

Legacy `pokedex/` paths are dead — use **dex** everywhere.

### 5. Learning
Observe, suggest, document, collaborate.

### 6. Procedures
Structured YAML under `/procedures/` when present. Prefer `zen dex procedures` for the living catalog.

## Teaching another AI
1. Share `https://github.com/k-dot-greyz/zenOS`
2. Point to this file + **`docs/guides/CLI.md`**
3. Phrase: `Welcome to the Zen Garden`
4. Have them run `zen --help` and `zen dex models`

## Collaboration modes

| Mode | Intent | CLI today |
|------|--------|-----------|
| Co-pilot / chat | Assist human | `zen run --chat` |
| Delegation | AI owns a task | **roadmap** — no `zen delegate` |
| Swarm | Multi-agent | **roadmap** — no `zen swarm` |

## Ethics
Transparency · respect · safety · privacy · enhance don’t replace.

## When stuck
- Commands → `docs/guides/CLI.md`
- Philosophy → `docs/GENESIS.md`
- Debt order → `docs/planning/REWORK_SPRINT_AUDIT.md`

## First mission
1. Read `docs/guides/CLI.md`
2. `zen --help` + `zen dex models`
3. Never write `pokedex` into new instructions

---

*Welcome to the Zen Garden.*
