# VITRINE — ARCHITECTURE.md

> Status: **v0.1 DRAFT — unroasted**. Companion to `VISION.md`.
> Contracts below are **shape sketches, normative**. They are not implementation and are not to be lifted into `src/`.

---

## 0. Invariants

These are non-negotiable and every decision below is scored against them.

| # | Invariant | Consequence |
|---|---|---|
| I1 | **Single spine.** Card is the only source of specimen truth. | No test may declare state the canvas can't render, and vice versa. |
| I2 | **No hardcoded values.** Viewports, themes, budgets, colours, rung thresholds, canvas geometry — all resolved from token/policy sources. | Zero literals in logic. Polymorphic defaults resolve at runtime from the manifest chain. |
| I3 | **Harness owns no rendering opinion.** | The harness must never import a component framework. |
| I4 | **Evidence over assertion.** Status is derived from artefacts with provenance. | No writable status field anywhere. |
| I5 | **Degrades to static.** Every mode must survive `build` → `file://`. | No mode may require a live server for *viewing*. |
| I6 | **Deny by default.** Specimens get no ambient capability (network, storage, clipboard, media) unless the card requests it and it's granted. | Carries the Justified Capability Attestation pattern forward. |

---

## 1. Layer map

```
┌──────────────────────────────────────────────────────────────┐
│  SHELL            Astro routes, static chrome, mode switch   │
│                   zero-JS by default, islands only where     │
│                   interaction is unavoidable                 │
├──────────────────────────────────────────────────────────────┤
│  LENSES           BENCH  │  CANVAS  │  GAUNTLET               │
│                   three views over one registry              │
├──────────────────────────────────────────────────────────────┤
│  ORCHESTRATOR     specimen lifecycle, capability broker,      │
│                   determinism injection, event tap,           │
│                   evidence collection                         │
├──────────────────────────────────────────────────────────────┤
│  SUBSTRATE        isolation boundary (see D1)                 │
│                   ← the one load-bearing unknown              │
├──────────────────────────────────────────────────────────────┤
│  REGISTRY         resolved specimen cards + evidence ledger   │
├──────────────────────────────────────────────────────────────┤
│  INGEST           CEM reader │ card reader │ token reader     │
│                   Vite glob discovery, watch, invalidate      │
└──────────────────────────────────────────────────────────────┘
                            ▲
                            │  (dev only)
                   ┌────────┴────────┐
                   │  SCRIBE plugin  │  write-back: layout,
                   │  Vite middleware│  baselines, evidence
                   └─────────────────┘
```

**Dependency rule:** strictly downward. Lenses never touch INGEST. SUBSTRATE never knows a lens exists. SCRIBE is dev-only and absent from the static build.

---

## 2. The spine — Specimen Card

The card is the atom. Discovery produces cards; humans refine them; everything else consumes them.

```ts
// NORMATIVE CONTRACT SKETCH — shapes only, no impl
interface SpecimenCard {
  id: SpecimenId;               // stable, content-addressed, never a filepath
  element: TagName;             // the custom element under test
  source: SourceRef;            // module specifier, resolved by Vite

  // WHAT TO RENDER  ── consumed by BENCH + CANVAS + GAUNTLET identically
  states: StateDescriptor[];    // named prop/attr/slot configurations
  matrix?: MatrixRef;           // viewport × theme × density axes, BY REFERENCE
                                // (I2: never inline literals here)

  // WHAT IT PROMISES  ── consumed by GAUNTLET, displayed by BENCH
  contract: {
    events?: EventDescriptor[];   // name, detail shape, when it must fire
    slots?: SlotDescriptor[];
    a11y?: A11yPolicyRef;         // by reference to policy set
    budgets?: BudgetRef;          // by reference to budget set
  };

  // WHAT IT MAY DO  ── I6, brokered, never ambient
  capabilities?: CapabilityRequest[];  // {capability, justification, tier}

  // WHERE IT SITS  ── CANVAS only; separable, see D2
  placement?: PlacementRef;
}
```

**Resolution chain (polymorphic defaults, I2):**

```
project policy  →  package policy  →  card override  →  session override
  (weakest)                                              (strongest, never persisted)
```

Nothing in the chain contains a literal that isn't a token reference. A viewport is `viewport.md`, not `768`. `768` lives in exactly one token file and is the token file's problem.

---

## 3. Ingest & discovery

**Primary source: Custom Elements Manifest (CEM).** If a package publishes `custom-elements.json`, the harness reads tag names, attributes, properties, slots, events, and CSS parts from it and synthesises cards with `DECLARED` rung. Zero hand-config adoption (VISION §8) is bought here, or not at all.

**Secondary: colocated card files.** `*.card.ts` next to the component, picked up by Vite glob import. Refines/overrides the CEM-derived card.

**Tertiary: nothing.** No central registry file. No `main.js` config listing globs listing paths. Discovery is convention + manifest, and both are watchable.

**Invalidate on:** component source change, card change, CEM change, token change, policy change. Each invalidation is scoped — a token change must not blow away the whole registry.

---

## 4. Substrate — isolation

**The load-bearing decision. See D1.** What the layer must provide regardless of which way D1 lands:

- `mount(card, state, env) → SpecimenHandle`
- `SpecimenHandle`: measured box, event tap, capability channel, teardown, HMR re-mount preserving scroll/interaction where possible
- `env`: injected determinism — seeded RNG, frozen clock, pinned locale/timezone, `prefers-*` overrides, forced viewport width **that media queries actually respect**

That last point is the crux and quietly kills the easy options: a component with `@media (max-width: 480px)` inside it will not respond to a CSS-transformed 480px-wide div. If specimens must honour their own media queries at arbitrary canvas widths — and for responsive concept validation they must — the substrate needs real per-specimen viewport semantics. Container queries help *if the component was written with them*, which is not a constraint the harness can impose on components under test.

---

## 5. Canvas model

**Live DOM under a transform, not a `<canvas>` bitmap.** Rasterising specimens forfeits inspection, interaction, a11y tree, and text selection — i.e. everything the harness is for. The word "canvas" here means *surface*, not the element.

```
World space (unbounded, specimen coordinates)
    │  transform: scale(k) translate(x,y)   ← single compositor-friendly transform
    ▼
Viewport (the actual scroll-less DOM window)
```

- **Frames** group specimens into a named *concept*; a frame is itself a first-class node with its own attestation rollup.
- **Overlay plane** (annotations, rung auras, measurement guides, connectors) renders in viewport space above the world, so overlay text does not scale into illegibility at low zoom. This is the correct call and slightly annoying to implement.
- **LOD:** below a zoom threshold, specimens degrade live-DOM → last-known-baseline image → coloured rung block. Threshold from tokens (I2), not a magic number.
- **Virtualisation** by world-space quadtree; specimens outside viewport + margin are unmounted or frozen. Unmount vs freeze is a real trade-off (state loss vs memory) and should be a per-card hint with a policy default.

---

## 6. Orchestrator

**Event tap.** Every `CustomEvent` crossing a specimen boundary is captured with timestamp, detail, and composed path. This is simultaneously: the BENCH event log, the GAUNTLET's evidence that declared events fired, and the recording layer for interaction replay. One mechanism, three consumers — a small proof that I1 is real.

**Capability broker (I6).** A specimen requesting `network`, `storage`, `clipboard`, or `media` gets a stub unless the card carries a justification and the tier is granted. Denied capabilities are *recorded*, not silently swallowed — an undeclared `fetch` attempt is itself evidence and should surface on the card.

**Determinism envelope.** Injected before mount, uniformly across all three lenses. If BENCH and GAUNTLET see different clocks, visual baselines are noise and the whole ladder is a lie.

---

## 7. Evidence ledger & attestation

Append-only. Each record: `{specimenId, rung, verdict, artefactRef, toolVersion, envHash, timestamp, signer}`.

- Rung is **computed** by folding evidence, never written (I4).
- `envHash` covers determinism envelope + token snapshot + substrate version. Evidence from a different `envHash` is *stale*, not *wrong*, and the UI must distinguish those.
- Rung 6 (`ATTESTED`) requires a human signer and decays when any lower-rung evidence is invalidated. Human sign-off does not outrank a failing test.

---

## 8. Gauntlet binding

Baseline checks are **generated from the card**, not authored. The runner is an adapter behind one interface so the choice (D4) stays reversible:

```ts
// NORMATIVE CONTRACT SKETCH
interface GauntletAdapter {
  plan(cards: SpecimenCard[]): TestPlan;   // card → cases, no hand-written glue
  run(plan: TestPlan, env: DeterminismEnv): Promise<EvidenceRecord[]>;
}
```

Requirement that constrains D4 hard: the runner must mount specimens through **the same substrate** as the canvas. Two mounting paths = two behaviours = baselines that pass in CI and lie on screen.

---

## 9. Build topology

| Phase | Astro | Vite | Notes |
|---|---|---|---|
| dev | dev server, routes, chrome | HMR, glob discovery, SCRIBE middleware | SCRIBE is the only write path to disk |
| build | static shell per route, prerendered card index | specimen chunks, code-split per component | registry serialised as static JSON |
| static view | — | — | canvas + bench read serialised registry; gauntlet unavailable, degrades visibly (I5) |

Astro earns its place by: static chrome with genuinely zero framework JS, content collections as a natural fit for the card registry, and clean per-mode routing. If in practice the canvas becomes one big island and Astro is reduced to a shell server, that's kill-criterion territory (`VISION §9`) — call it early, don't cargo-cult it.

---

## 10. Open decisions — ROAST THESE

**D1 — Isolation substrate.** *Blocks everything.*

| Option | Style isolation | Media queries | HMR | Cost/specimen | Verdict |
|---|---|---|---|---|---|
| Same document | none (global leak) | ✗ broken | trivial | ~0 | fast, lies |
| Shadow root wrapper | good (not perfect: inherited props, global sheets) | ✗ still viewport-wide | easy | low | tempting, still lies about responsive |
| iframe per specimen | true | ✓ real | painful across boundary | high (~MBs) | honest, expensive |
| iframe pool + recycling | true | ✓ real | painful | medium | complex, probably correct |

Leaning: **iframe with recycling pool, LOD-driven** — only specimens above the interactive zoom threshold get a live iframe; the rest are baseline images or rung blocks. Buys honesty and bounds the cost. Costs: an HMR bridge and a message-passing layer that touches every other subsystem. Roast this hardest; it's the decision the project lives or dies on.

**D2 — Layout persistence.** Committed `layout.json` (reviewable, diffable, merge-hostile) vs local-only (frictionless, ephemeral, kills VISION §5 "concept in a PR") vs hybrid: committed *named concepts* + local scratch space. Hybrid is probably right and is the most work. Also: how does layout survive a specimen id change?

**D3 — Card authorship.** CEM-derived + `*.card.ts` overlay (proposed) vs cards as the only source vs cards inside the component file as static metadata. CEM buys zero-config adoption but CEM's coverage of *states* is thin — it describes the API surface, not interesting configurations. Is the overlay actually carrying 90% of the weight, making "zero-config adoption" a hollow claim?

**D4 — Runner.** Vitest browser mode vs Playwright component-testing vs Playwright driving the harness itself as a page. Third option is odd but respects §8's same-substrate constraint for free, since it literally uses the harness. Downside: slow, and CI now depends on the whole app booting.

**D5 — Rung computation locus.** Client-side fold over the ledger (live, cheap, degrades with ledger size) vs SCRIBE-computed on write (fast reads, needs the dev server, breaks I5 for status display in static builds).

**D6 — Specimen identity.** Content-addressed from `{package, element, stateName}` (stable across moves, changes when you rename a state — nuking your layout and baselines) vs explicit human-assigned id (stable, requires discipline, collides). Renaming a state should not detonate history; neither should copy-paste create phantom identity.

---

## 11. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| HMR through iframe boundary (D1) | fatal — kill criterion | prototype **first**, before any other work; timebox it |
| Canvas perf at realistic specimen counts | severe | LOD + virtualisation designed in from day one, not retrofitted |
| CEM ecosystem coverage thinner than assumed | undermines zero-config claim | survey real packages before committing to D3 |
| Astro reduced to a shell server | architectural embarrassment | explicit checkpoint at v0.3 — keep or drop, no sunk cost |
| Scope: three products in one (VISION V3) | schedule death | consider GAUNTLET as v2 |
| Visual baselines flaky across environments | ladder becomes noise | `envHash` gating + containerised baseline capture |

---

## 12. Proposed sequence

Doc-first, per the rules. Nothing below starts until this doc is signed.

0. **Sign-off + D1–D6 resolved** (or explicitly deferred with a written reason)
1. **Spike: D1.** Isolation + HMR + forced-viewport media queries. Throwaway code, one question: does the honest option work? Kill criterion evaluated here.
2. **Spine.** Card schema, resolution chain, token/policy sources, CEM ingest.
3. **BENCH.** Cheapest lens, proves the spine end to end.
4. **CANVAS.** Transform, frames, LOD, virtualisation, D2 persistence.
5. **Ladder rungs 0–2.** Derived status with no test runner at all — proves I4 before GAUNTLET exists.
6. **GAUNTLET** — or defer to v2 per V3.
