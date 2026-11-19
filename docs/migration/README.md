# zenOS council migration map

## Definitions

| Old (YAML) | New (JSON) |
|------------|------------|
| `dex/procedures.yaml` | `dex/procedures.json` |
| (new) | `dex/agents/*.json` |
| (new) | `schemas/*.schema.json` |

## Code

| Old (Python) | New (Rust) |
|--------------|------------|
| `zen/cli.py` and agent framework | `crates/council/` |
| (new) | `crates/discord-bridge/` |
| (new) | `crates/providers/` |

## Session flow (target)

1. Chairman opens session with task + selected agents
2. Progress reports are routed only to agents that declare `reacts_to`
3. Comments are collected and (optionally) posted via Discord bots
4. Full session log written as JSON

YAML and Python remain until the new path is proven. No silent deletes.
