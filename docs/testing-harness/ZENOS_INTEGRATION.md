# zenOS ↔ VITRINE Integration

> How the default testing harness reference connects to zenOS code, CI, and agent onboarding.

---

## Document map

| Path | Role |
|---|---|
| [`README.md`](README.md) | VITRINE overview and read order |
| [`HOUSE_RULES.md`](HOUSE_RULES.md) | zenOS normative rules (start here for agents) |
| [`TESTING.md`](TESTING.md) | Harness layers, properties, CI shape |
| [`PROVISIONING.md`](PROVISIONING.md) | Stack negotiation, hydrate handshake |
| [`SPINE.md`](SPINE.md) | Card/specimen manifest layer |
| [`DECISIONS.md`](DECISIONS.md) | Open decision register |

---

## Repo layout (zenOS bindings)

```
docs/testing-harness/     ← VITRINE reference doc set (this directory)
tokens/testing-harness.toml ← scalars (I2)
zenos.stack.lock            ← provider bindings + pinned deps (I2 exemption)
policy/testing-harness.toml ← profile constraints
procedures/testing-harness/ ← hydrate + test procedures (YAML)
zen/testing/hydrate.py      ← DECLARE / NEGOTIATE / HYDRATE implementation
tests/test_harness_hydrate.py ← negotiation purity + hydrate properties
```

---

## Profiles

Bindings are chosen per **profile** (see `zenos.stack.lock`):

| Profile | Use |
|---|---|
| `linux/wayland/chromium/dev` | Local UI/component work (VITRINE default) |
| `ci/headless` | GitHub Actions — pytest, lint, harness validate |
| `static/file` | Offline / file:// degradation checks (I5) |

---

## Current zenOS test stack (transitional)

Until VITRINE runtime exists:

1. **Hydrate** deps for `ci/headless` before test runs in CI.
2. **pytest** runs unit tests in `tests/`.
3. **test_runner.py** — legacy smoke suite; migrate checks into pytest over time.
4. **Harness validate** — `python -m zen.testing.hydrate negotiate` must be deterministic; token keys referenced in CI must resolve.

When VITRINE implements substrate + lenses, zenOS adopts it as a **provider** bound in `zenos.stack.lock`, not a forked philosophy.

---

## Agent onboarding path

1. Read [`HOUSE_RULES.md`](HOUSE_RULES.md)
2. Read [`TESTING.md`](TESTING.md) §0–§2 (recursion rule + D1-independent layers)
3. Run `python -m zen.testing.hydrate status`
4. Run `pytest tests/test_harness_hydrate.py -v`
5. Consult [`DECISIONS.md`](DECISIONS.md) before proposing stack changes

See also [`docs/AI_INSTRUCTIONS.md`](../../AI_INSTRUCTIONS.md) Step 7.

---

## Provisioning amendments (zenOS-applied)

From [`PROVISIONING.md §9`](PROVISIONING.md), applied in this repo:

- **I3′** — stack names only in `zenos.stack.lock`
- **I7** — one mutation path via hydrate journal
- **D4** — runner is a binding, not a permanent decision
- **D1** — still open; spine buildable before substrate

`PROVISIONING.md` remains **PROPOSED** for VITRINE core; zenOS applies the amendments locally for dependency and CI hygiene.
