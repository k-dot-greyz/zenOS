# Documentation Archive

These documents are **not** current procedures. This directory holds **archived** documentation — superseded guides, session notes, and conversation exports that contain durable rationale but are no longer the canonical source of truth.

## Current sources of truth

- `dex/` — catalog + protocol index
- `docs/GENESIS.md` — philosophy / PCC (Personal Context Core)
- `docs/AI_INSTRUCTIONS.md` — agent onboarding
- `README.md` — product overview
- [DOCUMENTATION_GUIDE.md](../guides/DOCUMENTATION_GUIDE.md) — documentation knowledge-management

## Policy

| Criterion | Action |
| :--- | :--- |
| Guide superseded by a newer doc | Move here with archive header; leave redirect stub at old path if externally linked |
| Valuable design conversation | Export here with date and topic slug |
| Obsolete planning draft | Archive with link to replacement in `docs/planning/` |

## Naming convention

```
YYYY-MM-DD-short-topic-slug.md
```

## Required header

```markdown
# Archived: <title>

**Archived**: YYYY-MM-DD
**Reason**: superseded | conversation | obsolete-plan
**Superseded by**: <path>, if applicable
```

## Migration note

Legacy conversation content already lives in [CONVERSATION_ARCHIVE.md](CONVERSATION_ARCHIVE.md) in this directory. New archives should be created as individual dated files here. Migrate remaining bulk logs opportunistically when editing related active docs.

## See also

- [DOCUMENTATION_GUIDE.md](../guides/DOCUMENTATION_GUIDE.md) — full archiving guidelines
- [DECISION_LOG.md](../../DECISION_LOG.md) — architecture decisions (not general archives)
