# VITRINE — UX-STACK.md

> Stack decision record + interaction architecture for the **SANDBOX** layer.
> Supersedes nothing in `ARCHITECTURE.md`; it *pressurises* D1 badly (see §7).
> Status: **v0.1 DRAFT — unroasted**. Versions verified 2026-07-25.

---

## 1. The hard constraint, up front

**You cannot render live web components inside a Vulkan swapchain.** Not with a trick, not with a shim. A custom element is a DOM node in a browser engine's layout tree; Vulkan is a triangle pipe. There is no bridge that preserves inspection, the a11y tree, text selection, or interaction.

So the ambition splits into two products, and you must know which one is load-bearing:

| | Web component sandbox | Native engine |
|---|---|---|
| Specimens | live DOM, inspectable | not possible |
| Chrome/panels | DOM + CSS | immediate-mode or custom |
| World layer | GPU | GPU |
| Runs on | Chromium / Wayland | Vulkan direct |

**Recommendation: keep them one codebase and two presentations.** Shared Rust core, forked render target. Same pattern as the keyboard IME — core + shims — which is why it'll feel right.

The move that makes this cheap is **wgpu**: one crate, one WGSL shader set, that runs natively on Vulkan/Metal/D3D12/GL *and* over WebGPU/WebGL2 in wasm. Write the world renderer once in Rust. Today it's a `<canvas>` in Chromium. Later it's a Vulkan surface via winit. **The renderer never gets rewritten.** That single fact is the spine of this whole recommendation.

---

## 2. The second hard truth: not Tauri on Linux. Not yet.

Tauri on Linux renders through WebKitGTK, and WebKitGTK is documented-bad for exactly the workload here:

- DMABuf framebuffer construction failures; blank/flickering windows, worst on NVIDIA
- WebGL renderer string masked for fingerprinting — you cannot even tell what's behind the context
- Tauri's own docs describe high input latency and low frame rates in WebGL-heavy views; community reports of ~40fps where Chromium hits 240
- Tauri maintainers have said they can't fully recommend Tauri for Linux; GTK4 and CEF work has started, plus a Servo-based webview with Igalia — none shipped

FabFilter feel is **120fps interruptible spring motion under a continuous drag**. WebKitGTK will not give you that on Omarchy. Shipping Tauri here would be choosing the pretty architecture diagram over the actual product.

**Ship v1 as a browser app.** Chromium on Wayland, Vulkan-backed WebGPU, full modern CSS, zero packaging, instant HMR. Revisit Tauri when CEF or Verso lands — the app stays portable because the Rust core doesn't care.

---

## 3. Stack

### Rust core — one cargo workspace, two targets

| Crate | Job | wasm | native |
|---|---|---|---|
| `core-scene` | entities, transforms, spatial index (bevy_ecs standalone, not full Bevy) | ✓ | ✓ |
| `core-render` | **wgpu 30** + WGSL: wires, gizmos, auras, analyzers, grid | → WebGPU | → Vulkan |
| `core-interact` | tool state machine, disclosure ladder, gesture→intent, spring integrator | ✓ | ✓ |
| `core-card` | specimen card resolution, token/policy chain | ✓ | ✓ |
| `core-ledger` | evidence, attestation, rungs | ✓ | ✓ |

Boundary is a **command/event protocol**, not direct wasm-bindgen calls. Same protocol later rides IPC to a native process. Costs a serialisation layer, buys the entire phase-3 story.

### Web shell — today

- **Astro 7** (7.0.9). Astro 6 moved the dev server onto Vite's Environment API, so dev and prod finally share one path — relevant because the harness *is* a dev server. Static chrome, routing, content collections as the card registry.
- **React 19** (19.2.x) — **panels and chrome only.** Formally banned from the interaction hot path (§5).
- **Vite** — HMR, wasm plugin, glob discovery.
- **CSS, the parts that actually earn their place:**
  - `@property` — animatable custom properties. This is what lets disclosure transitions run on the compositor with zero JS. Load-bearing, not decoration.
  - OKLCH + `color-mix()` — token-driven theming that stays APCA-checkable
  - container queries — specimen responsive testing without the D1 iframe tax, *where components opt in*
  - CSS anchor positioning + `popover` — disclosure surfaces tethered to world-space entities (Chromium-first; acceptable, we're Chromium-first anyway)
  - `content-visibility` / `contain` — canvas virtualisation assist
  - View Transitions — mode switching without a hard cut

### Native runtime — later

`winit` + `wgpu 30` → Vulkan. `core-render` unchanged.

**Bevy (0.19, June 2026)** is the alternative: you'd get ECS, asset pipeline, and an editor preview that landed in 0.18. Verdict: **use `bevy_ecs` standalone now, not the engine.** Full Bevy brings a UI layer (Feathers) you will never use because your UI is DOM, and its scene format is still code-driven with no asset loader. Take the ECS, leave the engine, keep the door open.

---

## 4. GMod × FabFilter, decomposed

Both refuse to leave the world. That's the whole thesis, and it's the same thesis twice.

**FabFilter's actual primitives:**
1. The display *is* the control — param space and screen space are one bijective projection, not "chart with sliders underneath"
2. Live measurement overlaid in the same coordinate space as the control — cause and effect in one glance
3. Disclosure by proximity and intent, rendered *at* the thing, never in a far-away panel
4. Modifier-graded precision — same gesture, different resolution
5. Interruptible spring motion — you can grab something mid-animation
6. Expert view is a **superset** of basic view *in the same spatial arrangement*
7. No modals, no confirmations; undo is the safety net

**GMod's primitives:**
1. Spawn menu — held-key palette over the world, never a mode change
2. Tool gun — one tool, N modes; the mode decides what a click *means*; mode owns a small HUD, not a sidebar
3. Physgun — direct grab with distance/rotation modifiers (this is FabFilter #4 wearing a hat)
4. Wiremod — node graph in **world space**, not a separate editor
5. Hold-C context menu — entity properties in place
6. Everything is an entity of a class, inspectable at runtime

### The mapping

| GMod | VITRINE |
|---|---|
| entity | specimen |
| spawn menu | component registry as held-key radial palette |
| tool gun modes | `PLACE / GRAB / WIRE / PROBE / MEASURE / ATTEST` |
| physgun | direct manipulation with modifier-graded precision |
| wiremod | **`component.event → component.prop`, drawn as live wire** |
| hold-C properties | L2/L3 inline disclosure |
| entity class | specimen card |

**The wire idea is the best thing in this design.** VITRINE already taps every `CustomEvent` crossing a specimen boundary (`ARCHITECTURE.md §6`). Render that tap as world geometry and you *watch events fire* — a pulse travels the wire from emitter to consumer. Behavioural truth becomes visible without opening a console. The event tap was already built for the test runner; the sandbox gets it for free. That's I1 (single spine) paying rent a third time.

---

## 5. Progressive disclosure — the ladder

| L | Name | Trigger | Shows |
|---|---|---|---|
| L0 | AMBIENT | default | entity + maturity aura only |
| L1 | PROXIMATE | cursor within radius | handles, name, rung, port stubs |
| L2 | FOCUSED | selected | gizmo, all ports, inline scalar controls |
| L3 | EDITING | active drag | live readout, snap guides, modifier hints |
| L4 | EXPERT | held modifier / pinned | full card, contract, evidence ledger, capability grants |

**The law (non-negotiable, this is what makes it FabFilter and not Storybook):**

> **L4 is a strict superset of L0–L3 in the same spatial arrangement. Nothing that was visible moves when you level up.**

Break this and you've built a tool with two personalities that users must learn twice. Every disclosure level is additive overlay on a fixed layout. This constrains the entity's visual design hard — you must lay out for L4 first and *subtract* down to L0, never the reverse.

Corollaries:
- Radius, timing, and spring constants come from tokens (I2). No magic numbers.
- Levels are **interruptible** — L1→L3 mid-flight must retarget, not queue. Requires springs with retargeting, not CSS keyframes. ~60 lines of critically-damped integrator in `core-interact`, no dependency, constants from tokens.
- Modifier→intent is a **map**, declared once, not `if (e.shiftKey)` scattered across handlers.

---

## 6. Render planes

```
 z+   DOM overlay      HUD, tool strip, pinned panels     [viewport space, React]
      DOM world        specimens                          [world transform]
      GPU world        wires, gizmos, auras, analyzers     [world transform, wgpu]
 z-   GPU backdrop     grid, ambient, vignette            [world transform, wgpu]
```

Two planes, one camera. **The camera matrix is owned by `core-scene` and published to both** — neither plane owns it, so they cannot desync. DOM world plane consumes it as a single `matrix3d()` on one containing element.

**React is banned below the overlay plane.** Drag loops write transforms imperatively via refs inside a rAF loop driven by the core. React reconciles panel *structure*; it never sees a pointermove. Non-negotiable at 120fps.

---

## 7. This breaks D1 and I need to say so

`ARCHITECTURE.md` D1 leaned toward **iframe-per-specimen with a recycling pool** — chosen for honest media queries.

The sandbox model makes that considerably worse:

- iframes are expensive to composite; dozens of them under a continuously animating `matrix3d()` will cost you the frame budget the whole design is premised on
- pointer events across iframe boundaries complicate grab/wire gestures at every step
- an iframe cannot be perspective-transformed or shader-affected, so it will always sit visually *apart* from the GPU world plane

Honest options:
- **(a)** Keep iframes, accept that SANDBOX is a low-density mode (tens, not hundreds of specimens) and lean harder on LOD
- **(b)** Shadow-root specimens, sacrifice real media queries, require container queries from components under test — cheap, fast, and a real capability loss
- **(c)** Hybrid: shadow-root by default, promote to iframe on focus. Two mount paths, which §8 of `ARCHITECTURE.md` explicitly forbids for the test runner. Would need a written exception.

I don't have a confident answer. **This is the decision to make before anything else gets built**, and the D1 spike (`ARCHITECTURE.md §12 step 1`) should now include "N specimens under continuous world transform at 120fps" as an explicit pass/fail.

---

## 8. Omarchy / Arch notes

- Chromium on Wayland: `--ozone-platform=wayland`, Vulkan-backed WebGPU. Mesa RADV/ANV are fine; NVIDIA proprietary is the usual coin flip.
- Hyprland tiling means **arbitrary window geometry, always** — no fixed layout may exist anywhere. Conveniently this is just I2 again.
- Keyboard-first is a gift: hold-key tool modality is already Hyprland muscle memory. Tool switching should be chorded and holdable, never a click target.
- Dev loop: `vite` + `cargo watch` + `wasm-pack` in three panes. No Node-side build of the Rust; wasm artefact is a Vite dependency.
- Native later: `vulkan-icd-loader` + vendor ICD, `winit` Wayland backend. No X11 path, don't build one.

---

## 9. Open for roast

- **S1.** Is the browser-first call cowardice or correctness? It costs the native-feel story and filesystem access for a year. Alternative: eat WebKitGTK now and design *down* to what it can do — which probably means abandoning the FabFilter motion premise entirely.
- **S2.** `bevy_ecs` standalone vs a hand-rolled entity store. ECS for a few hundred entities is arguably ceremony; but it's the thing that makes a future native runtime a port instead of a rewrite.
- **S3.** Command protocol over the wasm boundary vs direct bindings. Serialisation cost per frame is real. Is phase-3 portability worth paying for it every frame, today?
- **S4.** §7. The one that matters.
- **S5.** Is the engine ambition real, or is it the thing that kills the harness by making every decision 3× more expensive for a future that never arrives? Cheapest honest answer: build the sandbox with wgpu, and let the engine earn its existence later or not at all.
