# zenOS REST API

Machine interface for agents, Dex, plugins, inbox, and chat. The CLI and HTTP
share the same services; OpenAPI is generated at `/docs` and `/openapi.json`.

## Start the server

```bash
# Loopback (token optional)
zen serve
# same thing:
python -m zen.api
python -m zen.core.api   # documented shim

# LAN / Termux / Docker — token required
export ZEN_API_TOKEN="a-long-random-secret"
zen serve --host 0.0.0.0 --port 8080
```

Defaults: `127.0.0.1:8080`. Binding anything other than loopback without
`ZEN_API_TOKEN` exits with an error.

Env vars: `ZEN_API_HOST`, `ZEN_API_PORT`, `ZEN_API_TOKEN`, `ZEN_API_CORS`
(comma-separated origins, never `*`). See `env.example`.

## Handshake (schema dump)

After connect, dump the packet schema (sysex-style). Later stream packets keep
this schema and omit unchanged field keys.

```bash
curl -sS -X POST http://127.0.0.1:8080/api/v1/session \
  ${ZEN_API_TOKEN:+-H "Authorization: Bearer $ZEN_API_TOKEN"}
```

Response is a `zen.session` card: `sid`, `packet_kinds`, `card_types`,
`capabilities`. Pass `X-Zen-Session: <sid>` on later requests to get
monotonically increasing `seq`.

Every other JSON body is a packet:

```json
{
  "v": 1,
  "sid": null,
  "seq": 0,
  "kind": "card",
  "type": "zen.agent",
  "id": "critic",
  "fields": { "name": "critic", "description": "..." }
}
```

Errors are `kind: "error"` / `type: "zen.error"` with `code`, `message`,
`details` — not FastAPI `{ "detail": ... }` alone.

## Auth

- `GET /health` is always public.
- If `ZEN_API_TOKEN` is set, all `/api/v1/*` routes require
  `Authorization: Bearer <token>`.
- OpenRouter keys never appear in responses.

## Endpoints

| Method | Path | Card type |
| --- | --- | --- |
| GET | `/health` | liveness JSON `{status, version}` |
| GET | `/api/v1/meta` | `zen.meta` |
| POST | `/api/v1/session` | `zen.session` handshake |
| GET | `/api/v1/cards/agents` | `zen.collection` of `zen.agent` |
| GET | `/api/v1/cards/agents/{id}` | `zen.agent` |
| POST | `/api/v1/agents/{id}/execute` | `zen.execute` (`?stream=true` SSE) |
| GET | `/api/v1/cards/models` | `zen.model` (`?tier=` `?task=`) |
| GET | `/api/v1/cards/models/{id}` | `zen.model` |
| GET | `/api/v1/cards/procedures` | `zen.procedure` |
| GET | `/api/v1/dex/stats` | `zen.dex.stats` |
| POST | `/api/v1/dex/sync` | `zen.dex.stats` (needs OpenRouter) |
| GET | `/api/v1/cards/plugins` | `zen.plugin` |
| POST | `/api/v1/plugins/{id}/execute` | `zen.execute` |
| GET | `/api/v1/inbox` | `zen.inbox.item` collection |
| POST | `/api/v1/inbox` | `zen.inbox.item` |
| POST | `/api/v1/chat` | SSE `zen.chat` deltas |

Interactive docs: `http://127.0.0.1:8080/docs`.

## Examples

```bash
# Health
curl -sS http://127.0.0.1:8080/health

# Dex models (legendary tier)
curl -sS "http://127.0.0.1:8080/api/v1/cards/models?tier=legendary"

# Execute an agent
curl -sS -X POST http://127.0.0.1:8080/api/v1/agents/critic/execute \
  -H "Content-Type: application/json" \
  -d '{"prompt":"review this prompt","critique":false}'

# Capture inbox
curl -sS -X POST http://127.0.0.1:8080/api/v1/inbox \
  -H "Content-Type: application/json" \
  -d '{"type":"note","content":"idea from n8n"}'
```

SSE streams emit `kind: delta` packets (only changed fields) and finish with
`kind: done`.

## Docker

`docker compose up zen-cli` serves the API on port 8080. Set `ZEN_API_TOKEN` in
`.env` — the container binds `0.0.0.0`.
