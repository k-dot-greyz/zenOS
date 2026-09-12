# VITRINE — GLOSSARY.md

> Vocabulary is load-bearing here. The card/specimen conflation in `ARCHITECTURE §2` was a *naming* failure that would have become a data-model failure. Words are pinned so that does not happen twice.

---

## The spine

**Card** — a *family*. One component plus its declared states, ports, contract, traits and capability requests. Authored by humans, colocated with the component. Pure data. Never has placement, never has evidence.

**State** — one named configuration within a card: props, attrs, slots, context, preconditions. A label plus a minted `StateId`.

**Axis** — a dimension of variation declared in `axes/`: viewport, theme, density, locale, motion. Referenced by cards, never inlined.

**Specimen** — a *point*. One card, one state, one axis vector. Derived by expansion, never authored. Everything downstream — evidence, baselines, placement, wires — addresses specimens.

**Expansion** — the pure, deterministic transform from cards × axes to specimens. The only place families and points meet.

**Locator** — `{package, element, cardName}`. Derived, mutable, human-readable, **never load-bearing**. Renaming changes the locator and nothing else.

**Lock** (`vitrine.lock`) — git-tracked record of minted identities and rebind history. The only file SCRIBE writes to the spine.

**Rebind** — the operation when a state disappears and an unfamiliar one appears in the same card. Always *proposed*, never automatic, because a wrong rebind silently poisons baseline history.

**Fixture** — a value that cannot be pure data: live objects, large markup, generated content. Referenced by id, resolved by the substrate at mount. An escape hatch under active suspicion (O4).

**Trait** — a *fact* about a component (`ownMediaQueries`, `statefulMount`, `heavyInit`, `globalSideEffects`). Cards declare facts; `policy/substrate.toml` maps facts to strategies. This is what keeps D1 out of every card.

**Port** — a wire endpoint. `OutPort` is an event plus a detail schema reference; `InPort` is a prop plus an accepted schema reference. Connection is legal iff the resolver proves assignability.

---

## Evidence

**Evidence record** — an append-only ledger entry: specimen, check, verdict, artefact, `envHash`, tool version, timestamp, optional signer.

**envHash** — hash over the determinism envelope, token snapshot and substrate version. Evidence from a different `envHash` is **stale**, not **failed** — a distinction the UI must preserve and never collapse.

**Rung** — a maturity level, computed by folding evidence. Never written. The ladder: `DECLARED`, `STUB`, `RENDERS`, `BEHAVES`, `ACCESSIBLE`, `PINNED`, `ATTESTED`. (Whether all seven survive is V1.)

**Fold** — the pure function from evidence to rung. Specimen rung is the highest rung whose checks all currently pass; **card rung is the minimum over its specimens**, because averaging produces a comfortable number and a false one.

**Attestation** — rung `ATTESTED`. Requires a human signer and **decays when any lower-rung evidence is invalidated**. Sign-off never outranks a failing test.

**Provenance** — the layer chain behind a resolved value or a status claim. Applies to config as well as evidence: the UI must be able to answer *"why is this viewport 768?"*.

---

## Lenses and surfaces

**BENCH** — single specimen, full viewport, controls, event log, inspector. The building-the-thing lens.

**CANVAS** — pan/zoom surface holding live DOM specimens under one world transform. The comparison and concept-validation lens. The reason the project exists.

**GAUNTLET** — the prove lens. Baseline checks generated from cards, not authored. May be deferred to v2 (V3).

**SANDBOX** — the GMod-flavoured interaction layer over CANVAS: tool modes, direct manipulation, wires. Not a fourth lens; a way of operating the third.

**Concept** — a named frame grouping specimens on the canvas. A first-class node with its own attestation rollup. Lives in `concepts/`, keyed by `SpecimenId`.

**Wire** — a rendered `out.event → in.prop` connection in world space. Pulses when the event fires. Built from the orchestrator's existing event tap, which is I1 paying rent a third time.

---

## Runtime

**Substrate** — the isolation boundary. Provides mount, teardown, measured box, event tap, capability channel, determinism injection, HMR re-mount. **Unresolved (D1).**

**Determinism envelope** — seeded RNG, frozen clock, pinned locale and timezone, `prefers-*` overrides, forced viewport. Injected identically across all lenses; if BENCH and GAUNTLET see different clocks, every baseline is noise.

**Event tap** — capture of every `CustomEvent` crossing a specimen boundary. One mechanism, three consumers: the BENCH log, GAUNTLET's evidence, and the sandbox's wire pulses.

**Capability broker** — grants or stubs `network`, `storage`, `clipboard`, `media` per I6. Denied use is *recorded as evidence*, never silently swallowed.

**SCRIBE** — the dev-only Vite middleware that writes to disk: lock, layout, baselines, evidence. Absent from static builds by construction.

**World space / viewport space** — specimen coordinates vs the DOM window. One camera matrix, owned by `core-scene`, published to both the DOM and GPU planes so they cannot desync. Overlays render in viewport space so text stays legible at low zoom.

**LOD** — degradation ladder: live DOM → last-known baseline image → coloured rung block. Thresholds from tokens.

---

## Interaction

**Disclosure level** — `AMBIENT`, `PROXIMATE`, `FOCUSED`, `EDITING`, `EXPERT`. Additive overlays on a fixed layout.

**The superset law** — expert is a strict superset of every level below it *in the same spatial arrangement*. Nothing visible ever moves when you level up. Forces layout to be designed for expert first and subtracted downward. Executable as a test (`TESTING §4`).

**Tool mode** — `PLACE`, `GRAB`, `WIRE`, `PROBE`, `MEASURE`, `ATTEST`. The mode decides what a click means. Held and chorded, never a click target.

**Modifier grading** — same gesture, different resolution. The physgun and the FabFilter drag are the same primitive.

**Retarget** — a spring changing destination mid-flight without restarting. Why the integrator is hand-rolled rather than CSS keyframes.

---

## Borrowed terms

**CEM** — Custom Elements Manifest, `custom-elements.json`. The zero-config ingest path. Its actual coverage is unverified (O2).

**JCA** — Justified Capability Attestation. The tier model carried over from prior work: a capability request must carry a justification, and the grant is policy's decision, not the requester's.

**Concept in a PR** — the claim that canvas layout is a reviewable committed artifact rather than local ephemera. Contested (D2, V2).
