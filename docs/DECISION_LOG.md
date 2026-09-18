# Decision log

ADR format: context, decision, consequences, alternatives. Status: Accepted | Superseded | Deprecated.

---

## ADR-001 — PAT vs OAuth for zenOS agent contexts

- **Status:** Accepted
- **Date:** 2026-09-17
- **Issue:** [#70](https://github.com/k-dot-greyz/zenOS/issues/70) / ZEN-314

### Context

zenOS agents need GitHub credentials for MCP, repo ops, and CI. Two paths exist:

1. **Personal Access Token (PAT)** in `GITHUB_TOKEN`, interpolated into Cursor MCP config via `${env:GITHUB_TOKEN}`.
2. **GitHub OAuth App** with a public `CLIENT_ID` and Cursor-handled `http://localhost` redirect.

Fine-grained PATs (`github_pat_…`) expose per-repo permissions. OAuth App scopes are coarser. GitHub Apps are the long-lived integration model, but they are heavier than either path for a personal sovereignty box.

### Decision

- **Default for single-user / agent boxes: PAT.** Name `zenos-mcp-<env>-YYYY-MM`, 90-day expiry, `repo` + `read:org` minimum, one token per environment.
- **Default for multi-user or hosted zenOS (the security lab, shared Cursor): OAuth.** Store only `GITHUB_OAUTH_CLIENT_ID` in env / template. Never a client secret in `mcp.json`.
- Both blocks live in `.cursor/mcp.json.template`. Enable one per environment. Do not put tokens in JSON.

### Consequences

- Agents get a boring, auditable credential lifecycle (`zen auth status` / `zen auth rotate`).
- Hosted docker lab can boot with OAuth or a runtime env var; the image never contains a PAT.
- Operators must rotate PATs. Missing rotation is a checklist item, not a surprise 401 mid-task.
- OAuth cannot match fine-grained PAT least-privilege. Over-granting is the trade-off we accept for shared hosts.

### Alternatives

| Option | Why not (now) |
|---|---|
| GitHub App (installation token) | Right long-term for org-wide zenOS; more moving parts than this epic needs. Revisit when multi-tenant auth is a product surface. |
| PAT only | Blocks the hosted security-lab / multi-user story. |
| OAuth only | Coarser scopes, worse for a personal agent box that should not see every repo. |
| Tokens in `mcp.json` | Accidental commit. Rejected. |
