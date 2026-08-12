# VITRINE — TESTING.md

> The harness that must exist before implementation does.
> Status: **v0.1 DRAFT — unroasted**. Partially blocked by D1 and D4; §2–§5 are not.

---

## 0. The recursion, named

VITRINE is a test harness. Its own tests are therefore in constant danger of becoming a second, worse test harness that duplicates the first.

**The rule that prevents this:**

> VITRINE's own components are tested *by VITRINE*, through the public spine, once VITRINE can render anything at all. Everything below the spine is tested conventionally and never sees a browser.

Concretely: `core-*` crates are Rust unit and property tests. The resolver is a pure-function test suite. VITRINE's own chrome — the tool strip, the disclosure surfaces, the port pips — are custom elements with cards in `packages/chrome/`, and they are dogfooded specimens. If the chrome cannot be expressed as cards, the card model is inadequate and that is a finding, not an inconvenience.

**Bootstrap order matters:** the spine's tests must pass before any chrome exists, because the chrome's tests depend on the spine working.

---

## 1. Layers

| Layer | Kind | Runs where | Needs D1? |
|---|---|---|---|
| Tokens / axes / resolver | pure unit + property | Rust, no DOM | no |
| Identity + lock | unit + scenario | Rust, temp fs | no |
| Card parse + merge | golden-file | Rust | no |
| Expansion | property | Rust | no |
| Ledger + rung fold | property | Rust | no |
| Interaction model | deterministic simulation | Rust, headless | no |
| Substrate contract | conformance suite | browser | **yes** |
| Chrome components | dogfooded specimens | VITRINE | yes |
| End-to-end lens behaviour | e2e | browser | yes |

Six of nine layers are D1-independent and buildable now. This is the argument for writing tests before the substrate question is settled — most of the surface does not touch it.

---

## 2. Properties, not examples

The spine is a set of pure transformations. Example-based tests will miss the interesting failures. Properties worth stating as executable invariants:

**Resolver**
- resolution is deterministic: same inputs, same output, always
- resolution is monotone in override strength — a stronger layer never loses to a weaker one
- every resolved value carries a non-empty provenance chain
- **no primitive escapes the resolver without either a token reference or a resolver-proven exemption** (this is I2, executable)

**Identity**
- renaming any card, state, file or package leaves every `SpecimenId` unchanged
- deleting a state and adding an unrelated one produces a rebind *proposal* and never a silent rebind
- `SpecimenId` is a pure function of its inputs and independent of axis-member ordering

**Expansion**
- `|specimens| == |states| × ∏|axis members|`, exactly, no dedup surprises
- expansion is order-independent and idempotent
- every specimen traces back to exactly one card and one state

**Ledger**
- fold is monotone: adding a passing record never lowers a rung
- adding a failing record never raises one
- card rung equals the minimum over its specimens (`SPINE.md §8`)
- a stale `envHash` never counts as a pass, and is distinguishable from a fail
- rung six decays when any lower-rung evidence is invalidated — **human sign-off never outranks a failing test**

That last property is the one worth writing first. It is the entire honesty claim, expressed as an assertion.

---

## 3. The substrate conformance suite

D1's answer is not yet known. **The suite that judges it can be written now**, and writing it is how D1 gets decided rather than argued.

Any substrate must pass, identically:

- mount and teardown leave no residue in the host document
- forced viewport width is honoured by the component's own `@media` queries
- injected determinism holds: seeded RNG, frozen clock, pinned locale and timezone, `prefers-*` overrides
- declared events reach the tap with intact detail and composed path
- undeclared capability use is recorded, not silently swallowed
- HMR re-mount preserves scroll position and, where possible, interaction state
- style isolation: host styles do not leak in, specimen styles do not leak out
- **N specimens remain interactive at 120fps under continuous world transform** — N from tokens, not a literal

The last one is the gate `UX-STACK.md §7` demanded. Options (a), (b) and (c) each run this suite; the results decide, and the suite outlives the decision as a regression net.

---

## 4. Interaction, tested without a browser

`core-interact` is a state machine plus a spring integrator. Both are deterministic and both can be tested headlessly at a fixed timestep — which matters, because interaction bugs found by clicking are found late and reproduced never.

- gesture → intent mapping is total: every (input, modifier, tool mode) triple maps somewhere, including explicit no-ops
- disclosure levels are interruptible: L1→L3 mid-flight retargets, never queues
- the spring is critically damped for the token-declared constants and never overshoots past tolerance
- **the disclosure superset law is executable:** for every entity, the set of visible affordances at level N is a superset of level N−1, and the position of every shared affordance is identical across levels

That last check is worth more than any amount of design review. It turns `UX-STACK.md §5`'s law from a promise into a failing test.

---

## 5. Golden files and what they cost

Card parse, merge and expansion are golden-file tested: fixture inputs, committed expected outputs, diff on change.

Cheap, high-coverage, and quietly corrosive — golden files get regenerated when they fail, and a regenerated golden is a test that has stopped testing. Mitigation: goldens are small and hand-written, regeneration is a separate explicit command that is never part of the normal loop, and a regenerated golden must be reviewed as a diff.

Visual baselines are **not** golden files and are not committed as truth. They are ledger artefacts with an `envHash`, and they are stale rather than wrong when the environment moves.

---

## 6. What is deliberately not tested

- **wgpu output pixels.** Shader correctness is judged by eye and by the frame budget. Pixel-comparing GPU output across drivers is a full-time job that produces flakes and no information.
- **Astro's rendering.** Framework behaviour is the framework's problem.
- **The canvas transform maths beyond its invariants.** Round-trip world↔viewport and camera-matrix agreement between the DOM and GPU planes are tested; specific pan and zoom sequences are not.
- **Third-party components under test.** VITRINE tests that its harness is honest about them, not that they are correct.

---

## 7. CI shape

| Stage | Gate | Runs |
|---|---|---|
| Rust unit + property | must pass | every push |
| Golden files | must pass, no auto-regen | every push |
| Interaction simulation | must pass | every push |
| Substrate conformance | must pass | every push, once D1 lands |
| Perf gate | budget from tokens | every push, once D1 lands |
| Dogfood specimens | rung must not regress | every push |
| Static build | must produce a `file://`-openable bundle | every push — this is I5, and it will rot silently otherwise |

**The dogfood gate is the interesting one.** CI computes VITRINE's own component rungs from the ledger and fails if any card drops. The project's honesty claim is enforced against the project itself, which is either elegant or insufferable depending on the week.

---

## 8. Open

- **T1.** Does the dogfood gate deadlock at the start? Chrome components cannot be dogfooded until VITRINE renders, and VITRINE needs chrome to render. Probable answer: a minimal chrome bootstrap that is exempt and stays exempt, which is an exemption list that will grow if unwatched.
- **T2.** Property tests need a card generator. Writing a generator that produces *valid* cards means encoding the schema twice — once as the schema, once as the generator. Is a constrained generator over real fixtures enough?
- **T3.** The perf gate's N (§3) is a token, so it can be lowered when it fails. That is exactly how perf gates die. Should N be a token at all, or is this the one place a committed literal is correct?
- **T4.** Blocked on D4: whether the conformance suite runs under the same runner as everything else, or is its own thing.
