---
dex_id: "0x7E:0x03"
dex_type: "documentation"
status: "active"
tags: ["auth", "mcp", "cursor", "secrets"]
---

# Cursor MCP Setup

This dex copy exists so agents that index `dex/03-docs/` find the guide.

**Canonical guide:** [`docs/guides/CURSOR_MCP_SETUP.md`](../../../docs/guides/CURSOR_MCP_SETUP.md)

## Contract

- `.cursor/mcp.json` is gitignored
- `.cursor/mcp.json.template` is committed with `${env:…}` placeholders only
- PAT names: `zenos-mcp-<env>-YYYY-MM`
- Minimum scopes: `repo` + `read:org`
- OAuth optional via `GITHUB_OAUTH_CLIENT_ID` (see the canonical guide)
