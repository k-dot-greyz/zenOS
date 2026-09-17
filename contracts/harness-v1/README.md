# Harness Contract v1

Portable preflight / PR-intake / capability-index contracts.

These files are the zenOS implementation of **Harness Contract v1** (extractable to `dev-master`). Other repos should consume the JSON schemas, not scrape CLI prose.

| Artifact | Role |
| --- | --- |
| `env-doctor.schema.json` | `zen env-doctor --format json` payload |
| `pr-intent.schema.json` | `.github/pr-intent.yaml` intake gate |
| `capability-registry.schema.json` | `dex/registry.yaml` + `zen dex search` |
| `issue-canonicals.yaml` | Duplicate GitHub/Linear issue mapping |

## env-doctor

```text
exit_codes: {0: healthy, 10: repairable, 20: blocked}
```

`--profile ci` keeps semantic `exit_code` in JSON but maps process exit `10 → 0` so CI stays green while an agent repairs. Process exit `20` still fails the job.

Families: `runtime`, `package_manager`, `lockfile`, `secrets_presence`, `git_state`.

## PR intent

Required fields: `intent`, `risk`, `supersedes`, `depends_on`, `touches_contracts`, `expiry_days`.

Overlapping changed paths with an open PR require a non-empty `supersedes` list. Diffs under `contracts/`, `zen/contracts/`, `dex/registry.yaml`, or `.github/pr-intent.yaml` require `touches_contracts: true`.

## Dex registry

Every entry answers four questions: **what** (owner, maturity, risk, purpose), **how** (entrypoint, env-doctor profile), **proof** (test + artifact), **supersedes**.
