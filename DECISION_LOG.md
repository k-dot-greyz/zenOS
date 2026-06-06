# zenOS Architecture Decision Log

This file records **Architecture Decision Records (ADRs)** for zenOS. For process and templates, see [docs/guides/DOCUMENTATION_GUIDE.md](docs/guides/DOCUMENTATION_GUIDE.md#architecture-decision-records-adrs).

| Status | Meaning |
| :--- | :--- |
| `proposed` | Under discussion; not yet binding |
| `accepted` | Current decision |
| `deprecated` | No longer recommended; migration may be incomplete |
| `superseded` | Replaced by a newer ADR (link both ways) |

---

## ADR-001: Documentation knowledge-management tiers

**Status**: accepted  
**Date**: 2026-06-06  
**Context**: Contributors and agents needed a consistent way to distinguish active guides, archived conversations, and architecture decisions. Multiple open issues (#21–#27) targeted overlapping paths without a single canonical guide.  
**Decision**: Adopt three documentation tiers — active (`docs/`, `README.md`, `pokedex/`), archive (`docs/archive/`), and ADRs (`DECISION_LOG.md`) — documented in `docs/guides/DOCUMENTATION_GUIDE.md`, with ecosystem repo relationships in `repos/registry.yaml`.  
**Consequences**: Pre-commit checklist items in `.github/COMMIT_WORKFLOW_CHECKLIST.md` can reference stable paths. Follow-up issues update README, `AI_INSTRUCTIONS.md`, and `DEV_ENVIRONMENT_SETUP.md` with navigation pointers to this guide.

---

## ADR-002: GlitchWorks agnostic architecture protocol in CONTRIBUTING

**Status**: accepted  
**Date**: 2026-06-06  
**Context**: Platform code must stay decoupled across desktop, mobile (Termux), and offline modes without hardcoded paths or provider lock-in.  
**Decision**: Encode the GlitchWorks Agnostic Architecture Protocol (zero hardcoding, interface-driven contracts, open piping, boundary validation, state hydration, graceful degradation, injectable telemetry) in `CONTRIBUTING.md` §4 for all zenOS contributions.  
**Consequences**: Reviews can cite §4 for boundary and configuration violations. Implementation remains incremental per subsystem.

---

*Add new ADRs at the bottom with the next sequential number. Do not renumber existing entries.*
