# VITRINE — VISION.md

> Codename placeholder. A *vitrine* is a glass display case for specimens. Rename at will.
> Status: **v0.1 DRAFT — unroasted**. No code exists. No code will exist until this is signed off.

---

## 1. One-liner

A sovereign, canvas-first workbench where a web component is **specified, rendered, exercised, measured, and attested** — with the specimen manifest as the single spine feeding dev view, test runner, and progress dashboard alike.

---

## 2. The problem

Component development today is three disconnected surfaces:

| Surface | Tool | What it knows | What it forgets |
|---|---|---|---|
| Isolation dev | Storybook | props/args | whether it passes anything |
| Test | Vitest / Playwright | assertions | what the component looks like |
| Progress | Jira / a spreadsheet | ticket status | reality |

The gap: **the thing you look at and the thing you assert on are described twice**, by hand, in two vocabularies, and they drift. Then a third human writes a status update that is fiction.

Second gap: **linear story lists are the wrong topology for concept validation.** When you're deciding whether a UI idea holds up, you don't want a sidebar tree and one specimen at a time. You want twelve variants on a surface at once, at different widths, in different themes, in different states, side by side, and you want to drag them around and squint. That's a canvas, not a list.

---

## 3. Thesis / core bet

**One artifact — the Specimen Card — drives everything.**

```
                 ┌──> canvas render (visual truth)
Specimen Card ───┼──> test case generation (behavioural truth)
                 ├──> a11y + contrast gate (accessibility truth)
                 └──> attestation ledger (progress truth)
```

If the card is the only place a component's states are declared, then "what we look at", "what we assert", and "what we report" cannot diverge. Progress stops being self-reported and becomes **derived**.

Secondary bet: **native custom elements + Astro is a genuinely zero-runtime harness.** No framework adapter layer, no `@storybook/web-components` shim, no hydration directives. Astro emits static shell HTML; the custom element upgrades itself; Vite provides HMR. The harness owns no rendering opinion whatsoever.

---

## 4. Who it's for

- **P0 — the operator (me).** Solo/small-team component work across projects, offline-capable, no cloud, no telemetry, no account.
- **P1 — a reviewer.** Someone handed a URL or a static build who needs to judge a UI concept without running a dev server.
- **P2 — a machine.** Agents that read the manifest, render specimens, diff snapshots, and write attestations without a human in the loop.

Explicitly **not** for: design-system marketing sites, public documentation portals, non-technical stakeholder theatre.

---

## 5. The three modes

One app, one manifest, three lenses over it.

### BENCH — isolate
Single specimen, full viewport, controls panel, live event log, DOM/shadow inspector, computed-style readout. This is the "I am building the thing" mode. Nothing novel here; it must simply be fast and not lie.

### CANVAS — compose & compare
Infinite pan/zoom surface. Specimens are **live DOM**, not screenshots. Drop the same component at 320/768/1440 side by side. Drop three variants of a button next to each other. Draw a frame around a set of specimens and call it a *concept*. Annotate. Arrange. The layout is a committed artifact, not local ephemera — **layout is reviewable in a PR**.

This is the differentiating mode and the reason the project exists.

### GAUNTLET — prove
Every specimen is a test case whether you wrote assertions or not. Baseline gauntlet, free of charge, from the card alone:
- renders without throwing
- upgrades as a custom element
- emits its declared events
- passes automated a11y rules
- meets contrast policy
- matches its visual baseline
- respects declared perf budget

Author-written interaction assertions layer on top. The gauntlet runs in CI **and** on the canvas — a specimen on the canvas wears its own pass/fail state as a visible aura.

---

## 6. Maturity ladder (the "progress" part)

A specimen's status is **computed from evidence**, never typed by a human.

| Rung | Name | Earned when |
|---|---|---|
| 0 | `DECLARED` | card exists, no implementation resolves |
| 1 | `STUB` | element resolves, renders something |
| 2 | `RENDERS` | renders without error across all declared viewports |
| 3 | `BEHAVES` | declared events fire; interaction assertions pass |
| 4 | `ACCESSIBLE` | a11y rules + contrast policy pass |
| 5 | `PINNED` | visual baseline captured and stable |
| 6 | `ATTESTED` | all of the above + human sign-off recorded with provenance |

The canvas rendered at rung-colour = a live kanban of component maturity that **cannot** be gamed by moving a ticket. Component-level progress percentage is arithmetic, not vibes.

---

## 7. Non-goals (hard)

1. **Not a component library.** Ships zero components of its own beyond its own chrome.
2. **Not framework-agnostic-by-adapter.** Custom elements are the contract. React/Vue/Svelte components are supported exactly to the degree they're wrapped as custom elements. No adapter zoo.
3. **Not a design tool.** The canvas arranges and annotates live components. It does not draw shapes, does not do vector editing, is not Figma, will never round-trip to Figma.
4. **No cloud, no account, no telemetry, no analytics, no phone-home.** Ever. The harness runs offline from a folder.
5. **Not a docs site generator.** A static export exists for review, not for publishing.
6. **No visual card editor in v1.** Cards are authored as code, reviewed as code.

---

## 8. Success criteria

Ship gate for v1 — all must hold:

- **Adoption cost:** a component with an existing custom-elements manifest appears on the canvas with **zero** hand-written config.
- **Honesty:** deleting a component's implementation drops its rung within one HMR cycle, visibly, without a rebuild.
- **Speed:** N specimens on canvas stays interactive at pan/zoom; degradation is graceful (virtualisation/freeze), never a cliff.
- **Portability:** `build` produces a static bundle that opens from `file://` or any dumb static host, canvas included, no server.
- **Single-spine proof:** it is impossible to add a specimen state to the canvas that the gauntlet does not see.

## 9. Kill criteria

Abandon or hard-pivot if:

- Isolation cost (whatever substrate wins, see ARCHITECTURE D1) makes a realistic canvas unusable and no virtualisation strategy recovers it.
- HMR cannot be made to work through the isolation boundary — a harness that requires manual refresh is dead on arrival.
- Astro's role collapses to "serves an SPA", in which case drop Astro and admit it's a Vite app.

---

## 10. Open for roast

Vision-level only — architecture decisions live in `ARCHITECTURE.md §Open Decisions`.

- **V1.** Is the maturity ladder over-engineered? The honest minimal version is three rungs: `RENDERS` / `BEHAVES` / `PINNED`. Seven rungs may be ceremony that produces a pretty canvas and no information.
- **V2.** Is "layout as a committed artifact" right, or does canvas layout churn poison every diff and get `.gitignore`'d by week two?
- **V3.** Should GAUNTLET be in scope for v1 at all, or is v1 "BENCH + CANVAS with an honest maturity ladder" and the test runner is v2? Scope is currently three products in a trenchcoat.
- **V4.** Is the P2 "agent as user" persona real work now, or is it a manifest-format constraint that costs nothing to honour and everything to build for?
