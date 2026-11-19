# Epic: Chairman-Driven Multi-Agent Council (zenOS / promptOS → JSON + Rust)

## End goal
A working multi-agent system where:
- **Chairman / Chief of Staff** sets the session task and orchestrates.
- Relevant agents (Researcher, Critic, Executor, …) react only when routed.
- Each role has a persistent, traceable personality (JSON agent card + Grok Bot memory).
- Optional Discord presentation: one bot account per role so identities are visible and logs are transparent.
- Full session transcript is written as JSON for after-action reporting (what / how / why).
- Definitions and code live in modern form: JSON (not YAML) and Rust (not Python).

## Why this exists
Legacy zenOS + promptOS had the right shape (procedures, evolution paths, multi-agent ideas, auto-critique) but the implementation is outdated. We are rewriting the relevant parts onto the current target stack so the system can actually run the council workflow we are building.

## Cross-repo / cross-PR picture
This work is split so agents can build in parallel without mixing concerns:

| PR / branch | Owns | Does not own |
|-------------|------|--------------|
| `feat/json-schemas-agent-cards` | Schemas, agent cards, procedures JSON | Rust code, Discord, providers |
| `feat/rust-council-orchestrator` | Session loop, routing, CLI | Discord, provider implementations, schema migration |
| `feat/discord-bridge` | Discord bots, posting, transcript export | Core orchestrator logic, schemas |
| `feat/providers-trait` | `AgentProvider` trait + Grok Bot adapter | Session logic, Discord |
| `docs/migration-map` | Path tables and how-to | Code changes |

## Success for the first vertical slice
1. Chairman opens a session with a task and 2–3 agents.
2. A progress report is routed only to agents that declare they react to it.
3. Comments appear (CLI first, Discord second).
4. Full session is written as JSON.
5. All definitions are JSON Schema-validated.
6. Python/YAML is no longer the source of truth for the new path.

## Constraints
- Star topology: cross-role coordination goes through Chairman.
- Fail closed: unknown is unknown; no silent creates or writes.
- Keep existing YAML/Python until the new path is proven.
- Agent cards point at existing Grok Bot IDs where possible.

Agents working on any part should read this file first so their output fits the whole system.
