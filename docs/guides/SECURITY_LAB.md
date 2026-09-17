# zenOS security lab (docker)

Deployable test env for a cheeky security check **using zenOS itself**.

The image runs Python 3.14, never copies `.env`, and exposes JSON endpoints that report auth / env-doctor / secret-scan **without echoing credential values**.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness |
| GET | `/ready` | Process is up |
| GET | `/auth/status` | `zen auth status` JSON (no live GitHub call by default) |
| GET | `/scan` | Auth + env-doctor + secret pattern scan |

## Local

```bash
docker compose -f docker-compose.lab.yml up --build
curl -sS localhost:8080/health
curl -sS localhost:8080/scan | python -m json.tool
```

Pass tokens at **runtime**:

```bash
GITHUB_TOKEN=… OPENROUTER_API_KEY=… docker compose -f docker-compose.lab.yml up --build
```

## Hosting (Fly / Render / any Docker host)

The container listens on `PORT` (default 8080). Set secrets in the host's secret store, not in the image.

### Fly.io

```bash
fly launch --config deploy/fly.toml
fly secrets set GITHUB_TOKEN=… OPENROUTER_API_KEY=…
fly deploy
```

### Render

`deploy/render.yaml` — connect the repo, Docker runtime, health check `/health`. Add env vars in the dashboard.

### Generic

```bash
docker build -t zenos-lab .
docker run --read-only --tmpfs /tmp -p 8080:8080 \
  -e PORT=8080 \
  -e GITHUB_TOKEN \
  -e OPENROUTER_API_KEY \
  zenos-lab
```

## What "security check using zenOS" means

Hitting `/scan` runs:

1. Credential presence (`GITHUB_TOKEN`, OpenRouter, OAuth client id)
2. `zen env-doctor` JSON (Python floor, CLI wiring, MCP URL)
3. The same secret-pattern scanner as the pre-commit hook, over the image's source tree

Use it to verify a host is wired correctly **before** you point Cursor MCP at it.
