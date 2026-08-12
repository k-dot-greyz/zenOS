# VITRINE — SPINE.md

> The manifest layer everything else hangs off. Supersedes `ARCHITECTURE.md §2`.
> Status: **v0.1 DRAFT — unroasted**. Resolves D3, D6. Deliberately does **not** resolve D1.

---

## 0. Two corrections to `ARCHITECTURE.md`

Owning these before building on them.

**C1 — I conflated card and specimen.** `ARCHITECTURE.md §2` declares `SpecimenCard { id: SpecimenId }`, which is wrong. A card declares a *family*; a specimen is one *point* in that family's space. Evidence, baselines, layout and wires all attach to points, not families. Authorship happens at the family. Getting this backwards would have put per-viewport evidence on a card with no place to live.

**C2 — `placement` does not belong in the card.** I had `placement?: PlacementRef` on the card. A specimen can appear on many canvases in different arrangements; placement is a property of a *concept*, keyed by specimen. Layout moves out of the spine entirely.

---

## 1. The core distinction

```
CARD  (family, authored)         "button, in these 4 states, with this contract"
  ×
AXES  (dimensions, referenced)   viewport × theme × density × motion
  ↓  expand
SPECIMEN (point, derived)        "button / disabled / viewport.sm / theme.dark / …"
```

**Everything downstream addresses specimens. Everything upstream authors cards.** The expansion is the only place the two meet, and it is pure and deterministic.

One consequence worth stating plainly: you cannot add a specimen by hand. Specimens exist because a card declared a state and an axis set contained a member. That *is* invariant I1 — mechanically, not aspirationally.

---

## 2. Identity

The D6 trap: content-addressed ids are stable across moves but detonate baselines on rename; human ids are stable but collide and require discipline. Both are wrong because both make *identity* a function of *naming*.

**Answer: mint opaque ids once, treat names as labels.**

```
CardId      ULID, minted on first discovery, recorded in vitrine.lock
StateId     ULID, minted on first discovery, recorded in vitrine.lock
AxisMemberId  authored (axes are hand-declared, ids are explicit)

Locator     { package, element, cardName }   derived, mutable, never load-bearing
SpecimenId  = hash(CardId, StateId, canonical(AxisVector))   deterministic
```

Renaming a card, a state, a file, or a package changes **nothing**. Deleting breaks things, which is correct.

**Rebinding.** When SCRIBE sees a state vanish and an unfamiliar one appear in the same card, it proposes a rebind and **stops**. Never silent, never heuristic-only — a wrong rebind silently poisons visual baseline history, which is worse than losing them. The confirmed rebind is recorded in the lock with provenance and timestamp.

`vitrine.lock` is git-tracked, human-diffable, and the single mutable thing SCRIBE writes to the spine.

---

## 3. The document set

Nine kinds of document. Each has exactly one job. Literals live in exactly one of them.

```
vitrine.toml           project policy: roots, resolver config, schema version
vitrine.lock           minted identities + rebind history   [SCRIBE-written]

tokens/*.toml          scalars. THE ONLY PLACE A LITERAL MAY EXIST.
axes/*.toml            axis sets: viewport, theme, density, locale, motion
policy/
  capabilities.toml    grants (Tier A/B) — card requests, policy grants
  budgets.toml         perf budgets
  a11y.toml            rule sets + contrast policy
  substrate.toml       traits → mount strategy      ← D1 LANDS HERE, ONLY HERE
fixtures/*.ts          impure/live values, referenced by id
**/*.card.ts           card overlays, colocated with components
concepts/*.json        canvas layouts, keyed by SpecimenId
ledger/*.jsonl         append-only evidence
```

`768` appears once, in `tokens/`, as `viewport.sm.width`. `axes/viewport.toml` references it. A card references the axis. Nothing else has an opinion. That is I2, enforced by there being nowhere else to put it.

---

## 4. The card

```ts
// NORMATIVE CONTRACT SKETCH — shapes only, no impl
interface Card {
  schemaVersion: SemVer;
  id?: CardId;              // omitted → minted into the lock on first sight
  element: TagName;
  source: ModuleRef;

  states: State[];          // named configurations
  axes: AxisRef[];          // which dimensions this card is expanded across

  ports: {                  // wire endpoints — see §6
    out: OutPort[];
    in:  InPort[];
  };

  contract: {
    a11y?:    PolicyRef;
    budgets?: PolicyRef;
    invariants?: InvariantRef[];
  };

  capabilities?: CapabilityRequest[];   // REQUESTS. Grants live in policy.
  traits?: Traits;                      // FACTS, not strategies — see §5
}

interface State {
  id?: StateId;             // omitted → minted
  name: string;             // label only, freely renameable
  props?:  Record<PropName, Value | FixtureRef>;
  attrs?:  Record<AttrName, Value | FixtureRef>;
  slots?:  Record<SlotName, MarkupRef | FixtureRef>;
  context?: Record<ContextKey, FixtureRef>;
  preconditions?: InteractionScriptRef[];   // "open the menu first"
}

type Value = TokenRef | Primitive;   // Primitive permitted ONLY where the
                                     // resolver proves no token could apply
```

**Cards are pure data.** `*.card.ts` is a *builder* evaluated at build/dev time that emits a plain document. No functions survive into the registry — the Rust core consumes it, and the static build serialises it (I5). Anything that must be live is a `FixtureRef`, resolved by the substrate at mount.

That constraint is load-bearing, not stylistic. The moment a card can contain a closure, the static build dies and the wasm boundary needs a JS callback channel.

---

## 5. Traits, not strategies — how the spine survives D1

The temptation is a card field like `mount: "iframe" | "shadow"`. That would weld the unresolved substrate decision into every card ever authored.

**Cards declare facts about the component. Policy maps facts to strategies.**

```ts
interface Traits {
  ownMediaQueries?: boolean;   // component ships its own @media
  statefulMount?:   boolean;   // rebuilding internal state is expensive
  heavyInit?:       boolean;   // first paint is costly
  globalSideEffects?: boolean; // touches document/window on connect
}
```

`policy/substrate.toml` maps trait combinations to mount strategy, LOD behaviour, and unmount-vs-freeze. When D1 resolves, **one file changes** and no card is touched. If D1 resolves differently for SANDBOX than for GAUNTLET, that's two profiles in one file — still no card churn.

This is the mechanism that makes "design the spine before D1" legitimate rather than reckless.

---

## 6. Ports and wire validity

Wires are `out.event → in.prop`. Validity needs structure, not names.

```ts
interface OutPort { event: EventName;  detail: SchemaRef; when?: TriggerNote; }
interface InPort  { prop:  PropName;   accepts: SchemaRef; }
```

Connection is legal iff `resolver.isAssignable(out.detail, in.accepts)`. The spine holds **references**, never schemas — whether they're JSON Schema, TS-derived, or something else is the resolver's business. Swapping schema systems must not touch a card.

CEM gives you event *names* and attribute types; it is thin on `detail` shapes. Expect the overlay to carry most port typing in practice — see §9, O2.

---

## 7. Resolution pipeline

Pure, staged, cacheable. Each stage's output is a function of its inputs only.

```
  discover ──▶ skeleton ──▶ overlay ──▶ resolve ──▶ expand ──▶ REGISTRY
     │            │            │           │          │
   CEM +       cards with   card.ts     tokens+     × axes
   globs       minted ids   merged      policy     = specimens
```

**Provenance is mandatory.** Resolving a value returns:

```ts
interface Resolved<T> { value: T; provenance: { layer: LayerId; key: string }[]; }
```

So the UI can answer *"why is this viewport 768?"* with the full chain — project default → package policy → card override. Config carries evidence too (I4). This is the same discipline as the ledger, applied one layer down, and it costs almost nothing if built in from the start and is agony to retrofit.

**Invalidation is scoped by stage.** Token change → re-resolve + re-expand, skip discovery. Card change → one card's overlay onward. CEM change → that package's skeleton onward. A token edit must never blow the whole registry; at realistic scale that's the difference between instant and unusable HMR.

---

## 8. What the ledger addresses

```ts
interface EvidenceRecord {
  specimenId: SpecimenId;      // the point, not the family
  checkId: CheckId;
  verdict: Pass | Fail | Skip;
  artefactRef?: ArtefactRef;   // screenshot, trace, axe result
  envHash: Hash;               // determinism envelope + token snapshot + substrate version
  toolVersion: SemVer;
  at: Timestamp;
  signer?: SignerRef;          // rung 6 only
}
```

**Rung folding:**
- specimen rung = highest rung whose checks all pass with a current `envHash`
- **card rung = min over its specimens**

The min-fold is the honest rule and will be unpopular: a button that fails contrast at `theme.dark` is not `ACCESSIBLE`, it is a button with a contrast bug. Averaging would produce a comfortable number and a false one.

Evidence from a stale `envHash` is **stale, not failed** — displayed differently, never silently trusted, never counted as a pass.

---

## 9. Open for roast

- **O1 — Minted ids in a lockfile.** Buys rename-safety, costs a SCRIBE write path, a merge-conflict surface, and a rebind ritual. Alternative: accept that renames nuke baselines and tell people not to rename. Cheaper, and arguably fine for a solo operator. Am I building multiplayer infrastructure for a single-player game?
- **O2 — CEM's real weight.** VISION promises zero-config adoption. If CEM carries tag names and attribute types but the overlay carries all states, port detail schemas, traits, and fixtures, then "zero-config" gets you an empty card and a `DECLARED` rung. That may be an honest floor or a hollow claim. **Survey real published packages before this ships** — this is the assumption most likely to be wrong.
- **O3 — Axis expansion blowup.** 4 states × 5 viewports × 2 themes × 2 densities = 80 specimens *per component*. Evidence, baselines and canvas cost all scale with that product. Options: sparse axes declared per-state, sampling policy, or expansion on demand with cached rungs. Currently unspecified and it will bite in week two.
- **O4 — Fixtures are an escape hatch.** "Cards are pure data" is only true if fixtures stay small. Nothing currently stops a fixture from becoming the actual configuration, at which point purity is theatre and the static build breaks. Needs a constraint I haven't written.
- **O5 — Provenance on every resolved value.** Correct, and possibly expensive per frame if resolution happens in the hot path. Probably wants resolve-once-cache-hard, but then session overrides need to invalidate precisely.

---

## 10. Build order

The spine is buildable now — D1 does not block it (§5).

1. tokens + axes + resolver with provenance — no cards yet, prove I2 in isolation
2. lock + identity minting + rebind proposal
3. card schema + `*.card.ts` builder → plain document
4. CEM ingest → skeleton (**do O2's survey first**)
5. expansion → registry, serialisable
6. ledger addressing + rung fold

Nothing above touches the substrate, the canvas, or a renderer. If any step needs to know how a specimen mounts, the spine has been designed wrong and it's a stop-work.
