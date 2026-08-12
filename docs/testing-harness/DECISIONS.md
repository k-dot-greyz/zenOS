# VITRINE — DECISIONS.md

> The register. Every open question raised anywhere in the doc set, in one place, with dependency order.
> Source docs remain authoritative for *reasoning*; this file is authoritative for *status*.
> Status: **v0.2** · verified against doc set 2026-07-27.

---

## Tally

| | Count |
|---|---|
| Raised across the doc set | twenty-five |
| Resolved | two |
| Reclassified | one |
| **Open** | **twenty-two** |
| Open and blocking | one |

Raised: VISION four (`V*`), ARCHITECTURE six (`D*`), UX-STACK five (`S*`), SPINE five (`O*`), PROVISIONING five (`P*`).
Resolved: `D3` and `D6`, both by `SPINE.md`.
Reclassified: `D4`, by `PROVISIONING.md` — it was never a decision.

---

## The blocking one

### D1 — Isolation substrate · **OPEN · BLOCKS EVERYTHING DOWNSTREAM OF THE SPINE**

*Raised:* `ARCHITECTURE.md §10` · *Pressurised:* `UX-STACK.md §7` · *Contained:* `SPINE.md §5`

Same-document and shadow-root are cheap and lie about responsive behaviour. iframes are honest and expensive — and under a continuously animating world transform they may be untenable at any useful density.

Live options: **(a)** iframes, accept low-density SANDBOX; **(b)** shadow-root, sacrifice real media queries, require container queries from components under test; **(c)** hybrid promote-on-focus, which needs a written exception to `ARCHITECTURE.md §8`'s same-substrate rule.

*Mitigated by:* `SPINE.md §5` — cards declare traits, `policy/substrate.toml` maps traits to strategy. When this resolves, one file changes and no card is touched. **The spine is therefore buildable before D1 resolves.**

*Reframed by `PROVISIONING.md §6`, not resolved:* the three options are now **providers** of one requirement, ranked by one conformance suite. They stop competing as arguments and start being measured. What does not change: nobody knows yet whether *any* provider clears 120fps under continuous transform. That question is empirical and still blocks.

*Resolution gate:* the spike. Pass/fail on: honest media queries at forced widths, HMR through the boundary, and N specimens at 120fps under continuous `matrix3d()`.

---

## Reclassified

### D4 — Runner · **NOT A DECISION** · *pending sign-off*

> `ARCHITECTURE.md §10` still carries D4 as open. That is correct until `PROVISIONING.md §9` is approved — the proposal does not get to edit other docs before it is accepted. Same for `TESTING.md`'s "blocked on D4". Known, tracked, not drift.

*Was:* Vitest browser mode vs Playwright CT vs Playwright driving the harness.

*Now:* a **binding**. Runners are providers of the "execute a test plan" requirement, selected per profile by conformance evidence, replaceable by a refactor procedure. `PROVISIONING.md §1 F4, §6`.

The same-substrate constraint from `ARCHITECTURE.md §8` survives as a **conformance requirement**, which is stronger than it was as prose: a runner that mounts specimens differently from the canvas fails the suite rather than being caught in review.

---

## Resolved

| | Decision | Resolution |
|---|---|---|
| **D3** | Card authorship | CEM skeleton + `*.card.ts` overlay, merged at the overlay stage. Cards are pure data; builders emit plain documents. `SPINE.md §4, §7`. **Contingent on O2.** |
| **D6** | Specimen identity | Opaque ULIDs minted once into `vitrine.lock`; names are labels; `SpecimenId = hash(CardId, StateId, canonical(AxisVector))`. Renames are free, rebinds are proposed and never silent. `SPINE.md §2`. **Contingent on O1.** |

Both resolutions have a live objection against them. Neither is safe to treat as settled.

---

## Open — scope

Answer these before build order matters, because they change what gets built.

**V3 — Is GAUNTLET in v1?** As written this is three products in a trenchcoat. Honest minimum: BENCH + CANVAS + rungs through `RENDERS`, with the test runner deferred. *Interacts with D4, S5.*

**S5 — Is the engine ambition real?** The cheapest honest answer is: build the sandbox with wgpu and let the native engine earn its existence later, or never. The risk is that engine ambition makes every decision three times more expensive for a future that does not arrive. *Interacts with S2, S3.*

**V1 — Seven rungs or three?** `RENDERS / BEHAVES / PINNED` is the defensible minimum. Seven may be ceremony that produces a pretty canvas and no information. *Cheap to defer — the fold is a pure function over evidence; add rungs later without migration.*

**V4 — Is the agent persona real work now?** Or is it a manifest-format constraint that costs nothing to honour and everything to build for? *Currently costs nothing: the spine is already serialisable data.*

---

## Open — architecture

**D2 — Layout persistence.** Committed (reviewable, merge-hostile) vs local-only (frictionless, kills "concept in a PR") vs hybrid named-concepts-plus-scratch. Hybrid is probably right and is the most work. *Partially eased by D6: opaque ids mean layout survives renames.*

**D5 — Rung computation locus.** Client-side fold (live, degrades with ledger size) vs SCRIBE-computed on write (fast, breaks I5 for static builds). *Leaning client-side with a serialised snapshot for static builds — probably decidable now, cheaply.*

**O3 — Axis expansion blowup.** Four states × five viewports × two themes × two densities is eighty specimens per component. Evidence, baselines and canvas cost all scale with that product. Sparse per-state axes, sampling policy, or on-demand expansion with cached rungs. *Unspecified. Will bite in week two.*

**O5 — Provenance cost.** Provenance on every resolved value is correct and possibly expensive in a hot path. Wants resolve-once-cache-hard, but then session overrides need precise invalidation.

---

## Open — objections to things marked resolved

**O1 — Is minted identity over-engineering?** Buys rename-safety; costs a SCRIBE write path, a merge-conflict surface, and a rebind ritual. Alternative: renames nuke baselines, don't rename. *If this falls, D6 falls with it.*

**O2 — Does CEM carry real weight?** If CEM gives tag names and attribute types while the overlay carries all states, port schemas, traits and fixtures, then "zero-config adoption" gets you an empty card at `DECLARED`. **This is the assumption most likely to be wrong, and it is cheap to check.** *If this falls, D3's premise falls and VISION's success criterion needs rewording.*

**O4 — Fixtures as escape hatch.** "Cards are pure data" holds only while fixtures stay small. Nothing currently stops a fixture becoming the actual configuration, at which point purity is theatre and the static build breaks. *Needs a constraint that is not yet written.*

---

## Open — provisioning

Raised by `PROVISIONING.md §10`. P1 gates the rest.

**P1 — Is negotiated provisioning justified at this scale?** Terraform-grade machinery for a solo tool may be the most over-engineered thing in the doc set. Counter: without it, `UX-STACK.md` is a set of welds and the stated philosophy is implementation-agnostic-until-inconvenient. *Argue before building anything under `PROVISIONING`.*

**P2 — Requirement granularity.** Too coarse and providers are unswappable monoliths; too fine and the project dies of interfaces. Working suspicion — a requirement is worth declaring only where a conformance suite is worth writing — is a nice test and possibly circular.

**P3 — Does negotiation purity survive npm?** Pure only while probes are cached and no version resolution happens during it. May force providers to pin exact versions and never ranges.

**P4 — Cross-ecosystem locks.** Does the binding lock reference, contain, or generate the Rust and Node locks? Referencing is cheapest and leaves two sources of truth.

**P5 — `PROVISIONAL` decay.** Nothing currently forces a provisional binding to clear. Expiry that fails CI is honest and will be hated on the day it fires; the alternative is the state quietly becoming permanent, which is what it was invented to prevent.

---

## Open — stack

**S1 — Browser-first: cowardice or correctness?** Costs the native-feel story and filesystem access for a year. The alternative is eating WebKitGTK now and designing down to it, which probably means abandoning the FabFilter motion premise. *Evidence is on the browser-first side; this is here to be argued, not assumed.*

**S2 — `bevy_ecs` standalone vs hand-rolled entity store.** ECS for a few hundred entities is arguably ceremony. It is also what makes a native runtime a port rather than a rewrite. *Downstream of S5.*

**S3 — Command protocol vs direct wasm bindings.** Per-frame serialisation cost is real and paid today; the portability it buys is claimed for phase three. *Downstream of S5.*

**S4** — is D1 restated from the sandbox side. Tracked under D1, not separately.

**V2 — Does committed layout poison every diff?** Realistically: does `concepts/*.json` get `.gitignore`'d by week two? *Same question as D2 from the vision side.*

**Astro checkpoint** — not lettered, from `VISION.md §9` and `UX-STACK.md §3`. If CANVAS becomes one giant island, Astro is a shell server and this is a Vite app. Explicit review at v0.3, no sunk cost.

---

## Dependency order

```
O2 (survey CEM)  ──▶ D3 stands or falls        [cheap, do first, no code]
O1 (identity)    ──▶ D6 stands or falls        [argument, no code]
V3 + S5 (scope)  ──▶ what gets built at all    [argument, no code]
P1 (provisioning)──▶ how much machinery        [argument, no code]
        │
        ▼
   SPINE BUILD  ────────────────────────────── [D1-independent, per SPINE §5]
        │
   D1 SPIKE  ─────▶ substrate binding, D2      [throwaway code, hard gate]
        │            runner binding follows free
        │
   O3, O5, D5  ───▶ scale and perf             [decidable during build]
   P2..P5      ───▶ only if P1 lands yes
```

Five things above the line are arguments, not code. Three are settleable in an afternoon. **Nothing should be written until O2's survey is done and V3, S5 and P1 are called** — those change the shape of the thing, not just its details.
