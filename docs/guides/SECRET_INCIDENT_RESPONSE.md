# Secret incident response (SOP)

If a token, key, or `Bearer` blob hits git, a paste, a screenshot, or a CI log — treat it as burned. Do not "just amend".

## 1. Revoke (minutes)

1. GitHub → Settings → Developer settings → revoke the PAT / OAuth token / GitHub App token.
2. OpenRouter → keys → delete the leaked key.
3. AWS (if `AKIA…`) → IAM → deactivate + rotate.
4. If GitHub **push protection** blocked the push, the token may already be revoked. Confirm anyway.

## 2. Audit `git log`

```bash
git log --all -S 'ghp_' --oneline
git log --all -S 'github_pat_' --oneline
git log --all -S 'sk-or-v1-' --oneline
git rev-list --all | xargs git grep -n -E 'ghp_[A-Za-z0-9]{20,}' || true
```

Record: which commit, which file, whether it reached `origin`, whether forks/mirrors exist.

Assume anything pushed to a public remote is in other people's clones. History rewrite does **not** un-leak it.

## 3. Rotate

1. Mint a replacement named `zenos-mcp-<env>-YYYY-MM` with an expiry.
2. `python scripts/setup_env.py` (idempotent — it will fill the empty `GITHUB_TOKEN` after you clear the old value).
3. `zen auth status --format json` until `exit_code` is 0.
4. Update GitHub Actions secrets if the PAT was used as a repo secret.
5. Restart Cursor so MCP picks up the new env (see `CURSOR_MCP_SETUP.md`).

## 4. Notify

- If the token had `repo` / `workflow` / org scopes: notify anyone who shares that environment (and the org owners).
- If it lived on a hosted zenOS lab: rotate the host env vars (Fly / Render / Railway secrets) and redeploy. Do not bake the new token into the image.
- Open / update an issue: what leaked, when revoked, when rotated, which hosts were bounced. No secret values in the issue body.

## 5. Prevent the next one

- `scripts/pre-commit-secret-scan.sh` + `.pre-commit-config.yaml`
- CI secret-scan job
- Enable GitHub secret scanning + push protection: **Settings → Code security → Secret scanning**
- Keep `.env` and `.cursor/mcp.json` gitignored
