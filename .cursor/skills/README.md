# Project Cursor skills (dev-master)

**Canonical source:** this directory (committed in git).

**Personal mirror:** `~/.cursor/skills/` — same folder names, synced by:

```bash
bash dex/04-scripts/sync-cursor-skills.sh
```

`./env-doctor.sh --init` (tier 0+) runs that sync automatically on local machines.

| Location | Used by |
|----------|---------|
| `.cursor/skills/` | Cloud agents, CI, anyone who clones dev-master |
| `~/.cursor/skills/` | Cursor IDE across all local projects (after sync) |

Do **not** edit skills only under `~/.cursor/skills/` — changes will be overwritten on the next sync. Edit here, then sync.

## Skills

| ID | Purpose |
|----|---------|
| `a11y-compliance-audit` | WCAG / ARIA / EN 301 549 multi-spec audits → one `.md` report per spec |

## Ecosystem propagation

Also copied into sibling repos (edit in dev-master, then propagate):

```bash
bash dex/04-scripts/sync-cursor-skills.sh --propagate-ecosystem
```

| Repo | Path |
|------|------|
| zenOS | `dex/09-repos/zenOS/.cursor/skills/` |
| neuro-spicy-devkit | `dex/09-repos/neuro-spicy-devkit/.cursor/skills/` |

Targets list: `dex/04-scripts/ecosystem-skill-targets.yaml`.

## Add a skill

1. Create `.cursor/skills/<skill-id>/SKILL.md` (with YAML frontmatter).
2. Run `bash dex/04-scripts/sync-cursor-skills.sh --propagate-ecosystem`.
3. Invoke in Cursor by name or description match.
