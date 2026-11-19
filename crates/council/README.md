# zenos-council

Rust orchestrator for Chairman-driven multi-agent sessions.

- Loads agent cards from `dex/agents/*.json`
- Chairman opens session with task + selected agents
- Routes progress reports only to agents that declare they react to them
- Emits session log as JSON

This crate is presentation-agnostic (no Discord).
