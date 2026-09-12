# VITRINE

**A canvas-first workbench where a web component is specified, rendered, exercised, measured, and attested — from one manifest.**

> **Status: DESIGN (VITRINE runtime). zenOS adopts this as the default testing harness *reference*; hydrate + tokens + CI alignment ship in-repo. See [ZENOS_INTEGRATION.md](ZENOS_INTEGRATION.md).**
> Codename is a placeholder — a *vitrine* is a glass display case for specimens. Rename at will.

---

## The one-paragraph version

Component development is three disconnected surfaces: an isolation viewer that knows props, a test runner that knows assertions, and a status document that knows fiction. VITRINE collapses them onto one artifact — the **Card** — so that what you look at, what you assert on, and what you report cannot diverge. Progress stops being self-reported and becomes derived from evidence. The primary view is a spatial canvas rather than a sidebar tree, because concept validation means seeing twelve variants at three widths at once, not one specimen at a time.

---

## Read in this order

| Doc | What it settles |
|---|---|
| **[HOUSE_RULES](HOUSE_RULES.md)** | **zenOS normative rules — agents start here** |
| **[ZENOS_INTEGRATION](ZENOS_INTEGRATION.md)** | How this reference binds to zenOS code and CI |
| **[VISION](VISION.md)** | Problem, thesis, the three lenses, maturity ladder, non-goals, kill criteria |
| **[SPINE](SPINE.md)** | Card vs specimen, identity, the document set, resolution pipeline, ledger addressing |
| **[ARCHITECTURE](ARCHITECTURE.md)** | Invariants, layer map, ingest, canvas model, orchestrator, build topology |
| **[UX-STACK](UX-STACK.md)** | GMod × FabFilter interaction model, disclosure ladder, render planes, stack choices |
| **[TESTING](TESTING.md)** | The harness that must exist before implementation |
| **[PROVISIONING](PROVISIONING.md)** | Stack negotiation, idempotent init, refactor procedures — **PROPOSED, not in effect** |
| **[GLOSSARY](GLOSSARY.md)** | Pinned vocabulary |
| **[DECISIONS](DECISIONS.md)** | Every open question, consolidated, in dependency order |

`SPINE` supersedes `ARCHITECTURE §2` and corrects two errors in it. `UX-STACK` pressurises `ARCHITECTURE`'s D1 and says so. `PROVISIONING` proposes amendments to four docs and **does not apply them until signed** — so `ARCHITECTURE` and `TESTING` still carry framings `PROVISIONING` argues against. That disagreement is tracked in `DECISIONS`, not drift.

---

## Invariants

Every decision in every doc is scored against these.

| | |
|---|---|
| **I1** | **Single spine.** The Card is the only source of specimen truth. |
| **I2** | **No hardcoded values.** Literals live in `tokens/` and nowhere else. |
| **I3** | **The harness owns no rendering opinion.** It must never import a component framework. |
| **I4** | **Evidence over assertion.** Status is derived, with provenance. No writable status field exists. |
| **I5** | **Degrades to static.** Every mode survives `build` → `file://`. |
| **I6** | **Deny by default.** Specimens get no ambient capability unless requested and granted. |

---

## Current state

**Twenty-two open decisions. One blocking. Five settleable without writing code.**

Blocking: **D1, the isolation substrate.** Shadow roots are fast and lie about responsive behaviour; iframes are honest and may be untenable under a continuously animating world transform. The spine is deliberately designed to survive either answer — cards declare *traits*, policy maps traits to *strategy*, and when D1 lands exactly one file changes.

Do these before anything else, in this order:

- [ ] **Survey CEM coverage in real published packages** (O2). If Custom Elements Manifests carry tag names and attribute types but not states, port schemas or traits, then "zero-config adoption" is a hollow claim and VISION's success criteria need rewording. Cheap. An afternoon. Most likely assumption to be wrong.
- [ ] **Call V3** — is GAUNTLET in v1, or is v1 BENCH + CANVAS + derived rungs with the runner deferred?
- [ ] **Call S5** — is the native engine real, or does wgpu-in-a-browser earn it later or never?
- [ ] **Argue O1** — minted identity in a lockfile, or accept that renames nuke baselines?
- [ ] **Argue P1** — is negotiated provisioning justified at this scale, or is it Terraform for a solo tool? Gates all of `PROVISIONING`.

Then: the D1 spike, against the conformance suite already specified in `TESTING §3`. Throwaway code, hard gate, kill criterion evaluated there.

---

## Known open sores

Stated plainly so they are not rediscovered as surprises.

- **D1 is unresolved and the sandbox model makes it worse.** See `UX-STACK §7`. Three options, none clean, one needs a written exception to the same-substrate rule.
- **Zero-config adoption is unverified.** See O2 above.
- **Axis expansion blowup is unspecified.** Four states across five viewports, two themes and two densities is eighty specimens per component. Nothing currently bounds this.
- **Fixtures are an unconstrained escape hatch.** "Cards are pure data" holds only while fixtures stay small; nothing enforces that yet.
- **Scope is three products in a trenchcoat.** Isolation viewer, spatial canvas, test runner. V3 exists to cut this down.
- **Tauri is off the table for Linux for now** — WebKitGTK's frame rates and DMABuf failures are incompatible with the motion premise. Browser-first, revisit when CEF or a Servo webview lands.
- **Astro may be reduced to a shell server.** Explicit checkpoint at v0.3. No sunk cost.

---

## Non-goals

Not a component library. Not framework-agnostic-by-adapter — custom elements are the contract. Not a design tool and never a Figma round-trip. No cloud, no account, no telemetry, no phone-home, ever. Not a docs site generator. No visual card editor in v1 — cards are authored as code and reviewed as code.

---

## Shape, once it exists

```
vitrine.toml            project policy
vitrine.lock            minted identities            [SCRIBE-written]
tokens/                 scalars — the only literals in the system
axes/                   viewport, theme, density, locale, motion
policy/                 capabilities, budgets, a11y, substrate
fixtures/               impure values, referenced by id
concepts/               canvas layouts, keyed by SpecimenId
ledger/                 append-only evidence
crates/                 core-scene, core-render, core-interact, core-card, core-ledger
packages/chrome/        VITRINE's own components — dogfooded specimens
```

---

## Contributing to the design

Roast the docs, not the code — there is no code. Every doc ends with a numbered open-questions section; argue there. A decision is only closed when its entry in `docs/DECISIONS.md` moves, and entries carry their live objections with them so that "resolved" never quietly means "forgotten".
