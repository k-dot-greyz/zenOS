# zenOS Documentation Guide

**For contributors, maintainers, and AI agents**

This guide explains how zenOS organizes knowledge, where to find information, and how to keep documentation healthy over time. It complements [CONTRIBUTING.md](../../CONTRIBUTING.md) (workflow and boundary rules) and [AI_INSTRUCTIONS.md](../AI_INSTRUCTIONS.md) (agent onboarding).

---

## Documentation tiers

zenOS uses three tiers so active guidance stays discoverable while history and decisions remain traceable.

| Tier | Location | Purpose | Audience |
| :--- | :--- | :--- | :--- |
| **Active** | `docs/`, `README.md`, `pokedex/` | Current setup, architecture, and product behavior | Everyone |
| **Archive** | `docs/archive/` | Session notes, superseded guides, durable conversation context | Contributors researching history |
| **ADRs** | `DECISION_LOG.md` | Architecture Decision Records — *what we decided and why* | Maintainers, agents planning changes |

### When to use each tier

- **Active docs** — User-facing behavior, CLI flags, setup steps, or public API contracts changed.
- **Archive** — A conversation or draft contains rationale not captured elsewhere; the active doc was replaced but the history is still useful.
- **ADRs** — You introduce, reverse, or materially change an architectural choice (storage format, provider abstraction, plugin contract, etc.).

> **Boundary rule** ([CONTRIBUTING.md §1](../../CONTRIBUTING.md)): platform documentation lives in this repo. Internal dev-master monorepo guides (dex routing, submodule bump SOPs) stay in the superproject — never commit them here.

---

## Directory layout

```
zenOS/
├── README.md                    # Product overview and quick start
├── DECISION_LOG.md              # ADR index (architecture decisions)
├── CONTRIBUTING.md              # Contribution workflow and agnostic architecture protocol
├── docs/
│   ├── AI_INSTRUCTIONS.md       # AI agent onboarding protocol
│   ├── GENESIS.md               # Philosophy and origin
│   ├── REPOSITORY_MANAGEMENT.md # Repo tooling and procedures
│   ├── CONVERSATION_ARCHIVE.md  # Legacy conversation log (migrating to docs/archive/)
│   ├── guides/                  # How-to and setup guides (you are here)
│   │   ├── DOCUMENTATION_GUIDE.md
│   │   ├── DEV_ENVIRONMENT_SETUP.md
│   │   └── QUICKSTART*.md
│   ├── planning/                # Roadmaps, specs, implementation status
│   ├── blueprints/              # Integration and feature blueprints
│   └── archive/                 # Archived conversations and superseded docs
├── pokedex/                     # Model and procedure catalog YAML
├── repos/
│   └── registry.yaml            # Ecosystem repository switchboard
└── .github/
    └── COMMIT_WORKFLOW_CHECKLIST.md
```

### Category quick reference

| Looking for… | Start here |
| :--- | :--- |
| First-time setup | [QUICKSTART.md](QUICKSTART.md), [DEV_ENVIRONMENT_SETUP.md](DEV_ENVIRONMENT_SETUP.md) |
| AI agent onboarding | [AI_INSTRUCTIONS.md](../AI_INSTRUCTIONS.md) |
| Architecture / roadmap | [docs/planning/](../planning/) |
| Repo tooling | [REPOSITORY_MANAGEMENT.md](../REPOSITORY_MANAGEMENT.md) |
| Models & procedures | `pokedex/` |
| Past decisions | [DECISION_LOG.md](../../DECISION_LOG.md) |
| Ecosystem repos | [repos/registry.yaml](../../repos/registry.yaml) |
| Contribution rules | [CONTRIBUTING.md](../../CONTRIBUTING.md) |

---

## Finding information

### By topic

1. Skim **README.md** for product scope and feature overview.
2. Check **docs/guides/** for procedural how-tos.
3. Check **docs/planning/** for specs, roadmaps, and implementation status.
4. Search **DECISION_LOG.md** before proposing architectural changes.
5. Search **docs/archive/** when debugging *why* something was built a certain way.

### Search commands

From the repository root:

```bash
# Search all markdown documentation
rg -i "your topic" docs/ README.md DECISION_LOG.md

# Search planning and blueprints only
rg -i "plugin" docs/planning/ docs/blueprints/

# List ADR titles
rg '^## ADR-' DECISION_LOG.md

# Find references to a path or module
rg -i "zen/pkm" docs/ zen/

# Search the repository switchboard
rg -i "dev-master" repos/registry.yaml
```

### Keyword routing (for agents)

| Keywords in task | Route to |
| :--- | :--- |
| setup, install, env, termux | `docs/guides/DEV_ENVIRONMENT_SETUP.md` |
| contribute, PR, commit, architecture | `CONTRIBUTING.md` |
| model, procedure, pokedex | `pokedex/`, `zen/pokedex.py` |
| plugin, sandbox | `docs/planning/PLUGIN_SYSTEM_SPECIFICATION.md`, `zen/plugins/` |
| repo, clone, audit | `docs/REPOSITORY_MANAGEMENT.md`, `zen_repo_manager.py` |
| decision, ADR, why | `DECISION_LOG.md` |
| ecosystem, submodule, related repo | `repos/registry.yaml` |

---

## Contributing to documentation

1. **Match the tier** — New behavior → active docs. Historical rationale → archive. Structural choices → ADR.
2. **Keep paths stable** — Prefer updating an existing guide over duplicating content.
3. **Link, don't repeat** — Cross-link related docs instead of copying large sections.
4. **Conditional accuracy** — If a feature is experimental, say so and point to `docs/planning/IMPLEMENTATION_STATUS.md`.
5. **Pre-commit checklist** — Follow the Documentation maintenance section in [COMMIT_WORKFLOW_CHECKLIST.md](../../.github/COMMIT_WORKFLOW_CHECKLIST.md).

### Pull request expectations

- Documentation-only PRs should state which tier(s) changed.
- Link the tracking issue (`Closes #…`).
- If you add a new top-level doc path, update this guide's directory layout table.

---

## Archiving guidelines

Move content to `docs/archive/` when:

- A guide is **superseded** by a newer doc (leave a one-line stub or redirect in the old location if linked externally).
- A **session or conversation** has durable design rationale not captured in active docs or ADRs.
- **Planning drafts** are obsolete but still useful for archaeology.

### Archive file naming

```
docs/archive/YYYY-MM-DD-short-topic-slug.md
```

Example: `docs/archive/2025-09-14-promptos-to-zenos-migration.md`

### Minimum archive header

```markdown
# Archived: <title>

**Archived**: YYYY-MM-DD
**Reason**: superseded | conversation | obsolete-plan
**Superseded by**: <path to active doc, if applicable>
```

See [docs/archive/README.md](../archive/README.md) for the archive policy index.

---

## Architecture Decision Records (ADRs)

Record decisions in [DECISION_LOG.md](../../DECISION_LOG.md) when they affect:

- Public CLI or API contracts
- Storage formats (PKM, inbox, plugin manifests)
- Provider or plugin abstraction boundaries
- CI, security, or deployment posture

### ADR entry template

```markdown
## ADR-NNN: Short title

**Status**: proposed | accepted | deprecated | superseded
**Date**: YYYY-MM-DD
**Context**: What problem or constraint drove the decision?
**Decision**: What we chose.
**Consequences**: Trade-offs, follow-up work, migration notes.
```

Number ADRs sequentially (`ADR-001`, `ADR-002`, …). When superseding, link the old and new entries.

---

## Repository switchboard

The **repository switchboard** ([repos/registry.yaml](../../repos/registry.yaml)) is the machine-readable map of zenOS ecosystem repositories — roles, visibility, remotes, and relationships (canonical, submodule, private fork, tooling).

### Why it exists

- Agents and scripts can resolve *which repo* handles a concern without hardcoding URLs.
- Contributors see how zenOS relates to dev-master, tooling repos, and templates.
- Registry updates accompany relationship changes (new submodule, renamed remote, deprecated fork).

### Common operations

```bash
# View the switchboard
cat repos/registry.yaml

# Find repos by role
rg "role:" repos/registry.yaml

# Validate YAML locally (requires Python PyYAML or yq)
python -c "import yaml, pathlib; yaml.safe_load(pathlib.Path('repos/registry.yaml').read_text())"
```

### Adding a repository

1. Add an entry to `repos/registry.yaml` with `id`, `url`, `visibility`, `role`, and `relationship`.
2. Document the *why* in an ADR if the relationship is architectural (e.g. new submodule in dev-master).
3. Update [REPOSITORY_MANAGEMENT.md](../REPOSITORY_MANAGEMENT.md) if new tooling is required.

### Submodule hydration (dev-master checkout)

When zenOS is checked out as a submodule inside [dev-master](https://github.com/k-dot-greyz/dev-master) at `dex/09-repos/zenOS`:

1. Make **zenOS-only** changes inside this directory.
2. Open PRs against `k-dot-greyz/zenOS` (not dev-master) for platform changes.
3. After merge, bump the submodule pointer in dev-master per the superproject's submodule workflow.
4. Consult `repos/registry.yaml` for which sibling repos exist; clone private repos only when credentials are available — do not commit private URLs or tokens here.

---

## Best practices

1. **One source of truth** — Each fact should have one canonical home; elsewhere link to it.
2. **Write for skimming** — Use tables, headings, and bullet lists; keep paragraphs short.
3. **Date ephemeral context** — Session notes belong in archive with a clear date.
4. **Prefer agnostic wording** — Document behavior and contracts, not one-off machine paths ([CONTRIBUTING.md §4](../../CONTRIBUTING.md)).
5. **Test commands you document** — Run setup and search examples before merging.
6. **Agent-friendly anchors** — Stable paths (`docs/guides/DOCUMENTATION_GUIDE.md`) beat chat-only explanations.

---

## Scheduled maintenance

Perform these checks periodically (e.g. quarterly or before a release):

| Task | Action |
| :--- | :--- |
| **Link rot** | `rg -o 'https?://[^)]+' docs/ README.md` and spot-check URLs |
| **Stale planning** | Compare `docs/planning/IMPLEMENTATION_STATUS.md` to codebase reality |
| **ADR hygiene** | Ensure accepted ADRs match current architecture; deprecate superseded entries |
| **Archive growth** | Move eligible content from root `docs/` into `docs/archive/` with headers |
| **Switchboard** | Verify `repos/registry.yaml` matches live remotes and roles |
| **README index** | Ensure README documentation section links to new guides |

Track maintenance outcomes in a GitHub issue or release notes when substantive drift is found.

---

## Related resources

- [CONTRIBUTING.md](../../CONTRIBUTING.md) — Fork-and-PR workflow, GlitchWorks agnostic architecture protocol
- [AI_INSTRUCTIONS.md](../AI_INSTRUCTIONS.md) — Agent onboarding
- [DEV_ENVIRONMENT_SETUP.md](DEV_ENVIRONMENT_SETUP.md) — Environment setup anchor
- [COMMIT_WORKFLOW_CHECKLIST.md](../../.github/COMMIT_WORKFLOW_CHECKLIST.md) — Pre-commit documentation checks
- [REPOSITORY_MANAGEMENT.md](../REPOSITORY_MANAGEMENT.md) — Repo manager tooling

---

*Good documentation is a living system — tier it, link it, and archive what ages.*
