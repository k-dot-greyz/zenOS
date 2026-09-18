# zenOS `.env` template

Versioned header: `# zenOS env template v1.0` (see `.env.template`).

The wizard (`python scripts/setup_env.py`) is **idempotent**: re-running it never overwrites keys that are already set. It validates `GITHUB_TOKEN` with `GET /user` before writing.

```bash
python scripts/setup_env.py              # interactive
python scripts/setup_env.py --unattended # fill from existing env vars only
zen env-doctor --format json
zen auth status --format json
```

`.env` is gitignored. `env.example` remains as a short compatibility pointer and still documents the Python 3.14+ floor.

## Engine modes

`ZEN_ENGINE_MODE` selects which zenOS engine personality the runtime hydrates:

| Mode | What it is for | Extra keys you might add |
|---|---|---|
| `product` (default) | Shipping the zenOS platform, CI, MCP, agent ops | `GITHUB_TOKEN`, `OPENROUTER_API_KEY` |
| `persona` | Personal PKM / assistant / neuro-spicy workflows | same + optional `GITHUB_ORG` left empty |
| `investment` | Cross-repo / org-level ops and project boards | add `project` + `read:org` PAT scopes, set `GITHUB_ORG` |

Keep the **same key names** across modes so Product / Persona / Investment templates stay compatible with `dev-master` and `neuro-spicy-devkit`. Only values and scopes change.

## GitHub Actions mapping

| Local `.env` | Actions |
|---|---|
| `GITHUB_TOKEN` | Provided automatically as `secrets.GITHUB_TOKEN` (job token). For a PAT, store `ZENOS_GITHUB_TOKEN` as a repo secret and map it. |
| `OPENROUTER_API_KEY` | Repo secret `OPENROUTER_API_KEY` |
| `ZEN_ENGINE_MODE` | Plain env on the job, default `product` |
| `GITHUB_MCP_URL` | Optional; default `https://api.githubcopilot.com/mcp/` |

CI runs `zen auth status --format json --offline --ci` so a missing Actions token fails the pipeline without calling OpenRouter.

## Customisation pattern

1. Copy `.env.template` → `.env`
2. Fill only the keys that mode needs
3. Leave unused keys present but empty (dotenv-linter / the wizard expect the key to exist)
4. Bump the header to `v1.x` if you add keys so `setup_env.py` can detect migrations
