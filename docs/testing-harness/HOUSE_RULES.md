# zenOS Testing Harness — House Rules

> Normative for agents and humans working in zenOS. Maps VITRINE invariants to this repo.
> Reference spine: [`TESTING.md`](TESTING.md) · provisioning: [`PROVISIONING.md`](PROVISIONING.md)

---

## 1. Default harness

**VITRINE** (documented in this directory) is zenOS's **default testing harness reference**. It is design-first — no VITRINE runtime ships in zenOS yet. Until it does:

| Today (zenOS) | VITRINE layer (target) |
|---|---|
| `pytest` + `tests/` | Rust unit + property (spine crates) |
| `test_runner.py` | Transitional smoke runner — not the harness |
| `zen/testing/hydrate.py` | DECLARE → NEGOTIATE → HYDRATE provisioning |
| `tokens/testing-harness.toml` | Token store (I2) |
| `zenos.stack.lock` | Binding lock for stack providers |
| `.github/workflows/zenos-ci.yml` | CI shape from `TESTING.md §7` |

Do not invent a second harness philosophy. Extend VITRINE docs here; implement against them.

---

## 2. Invariants (scored on every change)

| ID | Rule | zenOS enforcement |
|---|---|---|
| **I1** | Single spine — one source of specimen/procedure truth | Cards/procedures in dex + `procedures/`; tests derive from declared manifests |
| **I2** | No hardcoded values — literals only in `tokens/` and binding lock | CI budgets, perf `N`, timeouts → `tokens/testing-harness.toml` |
| **I3′** | Harness owns no stack opinion | Framework names only in `zenos.stack.lock`; code imports capabilities, not providers |
| **I4** | Evidence over assertion | CI results and ledger-style journals; no hand-written "passing" status |
| **I5** | Degrades to static | Docs and smoke tests runnable without live services where possible |
| **I6** | Deny by default | Capabilities (network, fs, secrets) explicit in cards/procedures |
| **I7** | One mutation path | All dep/state change via `zen.testing.hydrate` plan/apply + journal |

`I3′` and `I7` follow [`PROVISIONING.md §9`](PROVISIONING.md) — applied in zenOS even while VITRINE core remains design-only.

---

## 3. Token discipline (tokenmaxxed)

- **Scalars live in `tokens/`** — viewport widths, perf gate `N`, provisional binding TTL, pytest timeouts.
- **Versions and package names live in `zenos.stack.lock`** — the second literal store (I2 exemption per PROVISIONING §2).
- **Docs reference tokens by key**, not by repeating numbers (`testing.perf.specimen_count`, not "120 specimens").
- **Agents:** read tokens before guessing literals. If a value is missing, add it to tokens — do not inline.

---

## 4. Startup handshake (abstracted hydration)

All programmatic environment startup follows three phases from [`PROVISIONING.md §3`](PROVISIONING.md):

```
DECLARE   → read requirements, probes, profile (read-only)
NEGOTIATE → pure proposal: bindings + dependency delta (no mutation)
HYDRATE   → journaled plan/apply only (mutating)
```

**CLI:**

```bash
python -m zen.testing.hydrate declare --profile ci/headless
python -m zen.testing.hydrate negotiate --profile ci/headless
python -m zen.testing.hydrate hydrate --profile ci/headless   # applies approved plan
python -m zen.testing.hydrate status                          # observe without mutate
```

**Halt conditions** (exit non-zero, change nothing): unresolved requirement, binding change without approval, ungranted capability, lockfile disagreement with plan.

Unified setup (`python setup.py`) should call HYDRATE for the active profile — not raw `pip install` in automation paths.

---

## 5. Testing before implementation

Per [`TESTING.md §0`](TESTING.md): the harness tests itself through the public spine once it can render anything. For zenOS today:

1. Spine-adjacent logic (resolver, identity, negotiation purity) → unit/property tests first.
2. Chrome/UI dogfood → after spine tests pass.
3. Browser/substrate conformance → after D1 lands in VITRINE implementation.

**Bootstrap order matters.** Do not add browser e2e for harness chrome before spine tests exist.

---

## 6. CI gates (aligned with TESTING §7)

| Stage | Gate | Workflow job |
|---|---|---|
| Lint + format | must pass | `lint` |
| Python unit + property | must pass | `test` |
| Smoke / integration | must pass | `test` (pytest) |
| Security scan | advisory | `security` |
| Shell validation | advisory | `shell-check` |
| Docs build | advisory | `docs` |
| Harness validate | negotiation purity + token lint | `harness-validate` |
| Offline bootstrap | future: engine build network-off | not yet |

---

## 7. Open (zenOS-specific)

- **H1.** When VITRINE runtime lands, does it live in-repo or as a pinned provider in `zenos.stack.lock`?
- **H2.** Map zenOS plugins (`examples/sample-plugin`) to Card overlays — schema TBD.
- **H3.** Dex procedures as GAUNTLET plans — `zen.test.harness` procedure evolution path.
