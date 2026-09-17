# Cursor MCP Setup

One token per environment. No secrets in JSON. Auth paths are first-class.

Canonical companion: [ENV_TEMPLATE.md](./ENV_TEMPLATE.md) · [DECISION_LOG.md](../DECISION_LOG.md)

## PAT naming and scopes

Name every GitHub PAT:

```
zenos-mcp-<env>-YYYY-MM
```

Example: `zenos-mcp-cursor-2026-09`. Put **purpose + machine name** in the token description. Always set an expiry. Rotate every 90 days (`zen auth rotate`).

Classic tokens start with `ghp_`. Fine-grained tokens start with `github_pat_`. Prefer fine-grained when you can; classic is acceptable for personal agent boxes.

| Use-case | Minimum scopes |
|---|---|
| Agentic zenOS / dev-master ops | `repo` + `read:org` |
| CI triggering | `workflow` |
| Secret scanning / Dependabot reads | `security_events` |
| GitHub Projects read/write | `project` |

## Global Cursor config

`~/.cursor/mcp.json` — interpolate env vars, never paste a token:

```json
{
  "mcpServers": {
    "github": {
      "url": "${env:GITHUB_MCP_URL}",
      "headers": {
        "Authorization": "Bearer ${env:GITHUB_TOKEN}"
      }
    }
  }
}
```

Copy the committed template:

```bash
cp .cursor/mcp.json.template ~/.cursor/mcp.json
```

`.cursor/mcp.json` is gitignored. `.cursor/mcp.json.template` is the only JSON that belongs in git.

## Per-project config

Project file: `.cursor/mcp.json` with an `envFile` pointing at the project `.env` (still gitignored):

```json
{
  "envFile": ".env",
  "mcpServers": {
    "github": {
      "url": "${env:GITHUB_MCP_URL}",
      "headers": {
        "Authorization": "Bearer ${env:GITHUB_TOKEN}"
      }
    }
  }
}
```

## Persist `GITHUB_TOKEN` so Cursor actually sees it

Cursor inherits the environment of the process that launched it. A token sitting in your shell is not enough if you started Cursor from the Dock / Start Menu.

### macOS (`launchctl`)

```bash
launchctl setenv GITHUB_TOKEN "$GITHUB_TOKEN"
launchctl setenv GITHUB_MCP_URL "${GITHUB_MCP_URL:-https://api.githubcopilot.com/mcp/}"
```

Restart Cursor after setting these. To persist across logins, add a LaunchAgent that runs `launchctl setenv` — do **not** put the token in a tracked plist.

### Linux (`/etc/environment` or systemd user env)

User-level (preferred):

```bash
mkdir -p ~/.config/environment.d
printf 'GITHUB_TOKEN=%s\nGITHUB_MCP_URL=%s\n' \
  "$GITHUB_TOKEN" \
  "${GITHUB_MCP_URL:-https://api.githubcopilot.com/mcp/}" \
  > ~/.config/environment.d/zenos.conf
```

Machine-wide `/etc/environment` works but is shared. Never commit that file.

### Verification checklist

1. `zen auth status --format json` → `exit_code` 0, no raw token in the payload.
2. Cursor → **Settings → Tools & Integrations → MCP Tools** → GitHub server shows a green dot.
3. `echo "$GITHUB_TOKEN"` in a **new** terminal is non-empty (length only — do not paste it into chat).

## OAuth path (token-free option)

For multi-user or hosted zenOS where 90-day PAT rotation is painful:

1. GitHub → **Settings → Developer Settings → OAuth Apps → New OAuth App**
2. Homepage URL: your zenOS host (or `http://localhost` for local Cursor)
3. Callback URL: `http://localhost` (Cursor handles the redirect)
4. Copy the **client id** (public-safe) into `GITHUB_OAUTH_CLIENT_ID`
5. Enable the `github-oauth` block in `.cursor/mcp.json.template`

```json
{
  "mcpServers": {
    "github-oauth": {
      "url": "https://api.githubcopilot.com/mcp/",
      "auth": {
        "CLIENT_ID": "${env:GITHUB_OAUTH_CLIENT_ID}"
      }
    }
  }
}
```

OAuth scopes are coarser than fine-grained PAT permissions. See the ADR in `docs/DECISION_LOG.md`.

## Related

- GitHub MCP install for Cursor: https://github.com/github/github-mcp-server/blob/main/docs/installation-guides/install-cursor.md
- Cursor MCP docs: https://cursor.com/docs/mcp
- Token security: https://github.com/github/github-mcp-server#token-security-best-practices
