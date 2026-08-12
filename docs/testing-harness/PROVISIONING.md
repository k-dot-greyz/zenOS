# VITRINE — PROVISIONING.md

**Stack negotiation, idempotent init, and refactor procedures.**

| | |
|---|---|
| Status | **PROPOSED — awaiting operator sign-off** |
| Normative | Yes. Amends `ARCHITECTURE.md`, `UX-STACK.md`, `TESTING.md`, `DECISIONS.md` — see §9. |
| Supersedes | Nothing. Reframes `UX-STACK.md` (see §1, F1). |
| Blocks | Any dependency being added to any manifest by any means. |
| Verified against | doc set as of 2026-07-27 |

---

## 1. Review findings — what this requirement breaks

Leading with the damage, because the requirement invalidates a framing I shipped two turns ago.

### F1 — `UX-STACK.md` is mis-framed and must be demoted

I wrote it as a decision record: Astro, React, wgpu, `bevy_ecs`, browser-first, not-Tauri. Those recommendations remain evidence-backed and I stand behind the *reasoning*. But the document presents them as **axioms**, and under a negotiated-stack model no dependency may be an axiom. It is a **resolved binding snapshot for one target profile** — `linux/wayland/chromium/dev` — and nothing more.

Concretely: nothing in `core-render` may name wgpu. Nothing in the shell may name Astro. Those names appear in exactly one place, the binding lock, and everything else addresses the *capability*.

This is the same mistake in a different coat as the card/specimen conflation owned in `SPINE.md §0`: I let a concrete choice sit where an abstraction belonged.

### F2 — Invariant I3 is too narrow

"The harness owns no rendering opinion" was written about component frameworks. The correct generalisation is **the harness owns no stack opinion**. Restated in §9 as I3′.

### F3 — I2 has an unhandled literal class

`tokens/` is declared the only place a literal may exist. Dependency versions, registry URLs and package names are literals and have no home. Left unaddressed, every manifest becomes an I2 violation the moment it exists. Resolved in §2 by making the binding lock a token space with a formal exemption, not by pretending versions aren't literals.

### F4 — D4 was never a decision

`DECISIONS.md` carries D4 as "pick a runner: Vitest browser mode vs Playwright CT vs Playwright driving the harness." Under this model that is not a decision — it is a **binding**, chosen per profile by evidence, replaceable by a refactor procedure. Reclassified in §9.

### F5 — D1 changes shape but does not go away

The substrate is a capability with three candidate providers and a conformance suite already specified (`TESTING.md §3`). Negotiation does not answer whether *any* provider clears 120fps under continuous transform. That question is empirical and still blocking. What changes: D1 stops being "choose one and weld it in" and becomes "run the suite, let evidence bind, keep the losers as providers."

### F6 — the honest risk, stated once

**The failure mode of this entire document is building a second, worse package manager.** If the negotiation engine starts resolving version ranges, walking dependency graphs, or fetching tarballs, it is dead and it has taken the project with it. The engine **plans and delegates**; npm and cargo do the work. Every design choice below is subordinate to that constraint. If a feature requires the engine to understand semver ranges, cut the feature.

---

## 2. The model — requirements, providers, bindings

The stack becomes a card. Same shape as `SPINE.md §5`, one layer up.

| Spine (runtime) | Provisioning (build) |
|---|---|
| card declares **traits** (facts) | component declares **requirements** (capabilities) |
| policy maps traits → **strategy** | negotiation maps requirements → **providers** |
| one file changes when D1 lands | one lock changes when a stack choice moves |

```
REQUIREMENT     a capability the system needs, with a conformance suite
                "isolate a specimen"  ·  "render a GPU world plane"
                "serve static chrome" ·  "execute a test plan"

PROVIDER        a concrete adapter that claims a requirement, declaring:
                dependency footprint · target profiles supported
                capability requests (network, fs, native toolchain)
                conformance evidence

BINDING         requirement × profile → provider, recorded with provenance
                lives in vitrine.stack.lock, git-tracked, human-diffable

PROFILE         a named target: linux/wayland/chromium/dev
                                ci/headless · static/file · native/vulkan
```

**Requirements are declared in documents; providers are discovered; bindings are negotiated and locked.** No source file imports a provider directly — it imports the requirement's interface, and the glue is generated at hydrate.

**F3's resolution:** `vitrine.stack.lock` is a token space. Package names, versions and registry URLs are literals *there* and nowhere else, exactly as `768` lives in `tokens/` and nowhere else. I2 holds by the same mechanism it already uses; it just gains a second store with an explicit, narrow exemption.

---

## 3. The handshake

Three phases, hard-separated. Phase boundaries are the only places state may change.

### DECLARE — pure, offline, no mutation

Both sides state facts.

- **System declares:** requirements, constraints (license policy, version floors, capability budget), target profile.
- **Environment declares:** probe results — OS, package managers present, toolchain versions, GPU adapters, browser availability, network reachability, existing manifests and locks.

Probes are read-only, cached with a TTL, and their results are provenance-tagged. **A probe that mutates anything is a bug, not a probe.**

### NEGOTIATE — pure, offline, produces a proposal

Resolution walks requirements against discovered providers under the profile and constraints, and emits a **Proposal**: a set of bindings, the dependency delta implied, capability requests raised, and full provenance for every choice.

```
Proposal {
  profile, bindings[], deltaAdd[], deltaRemove[], deltaChange[],
  capabilityRequests[], provenance[], conformanceStatus[], warnings[]
}
```

Negotiation is a **pure function** of declared inputs. Same inputs, same proposal, byte-identical. This is what makes the whole thing testable without a network and reviewable as a diff.

**Halt conditions — no silent fallback, ever:**

- no provider satisfies a requirement under the profile → **HALT**
- multiple providers tie with no policy tiebreak → **HALT**
- a provider lacks conformance evidence for this profile → **HALT** (or bind `PROVISIONAL`, see §6)
- the proposal changes an existing binding → **HALT for approval**, always, no exceptions
- a capability request is ungranted → **HALT**

Halt means: print the proposal with reasons, exit non-zero, change nothing. Degrading to a weaker provider without saying so is the exact failure this architecture exists to prevent.

### HYDRATE — the only mutating phase

Executes an approved plan. Everything in §4 applies.

---

## 4. Idempotence

Stated as properties, because "idempotent" without properties is a vibe.

| | Property |
|---|---|
| **P-conv** | `apply(plan)` run N times converges to the same state as N=1 |
| **P-noop** | applying to an already-converged state performs zero mutations and exits zero |
| **P-resume** | an interrupted apply, re-run, either completes or aborts cleanly — never half-state |
| **P-pure** | desired state is a pure function of declarations, probes and policy |
| **P-observe** | actual state is observable without mutation |
| **P-journal** | every mutation is journaled before it happens and confirmed after |

### Mechanism — plan/apply with a journal

```
desired = f(declarations, probes, policy)      pure
actual  = observe()                            read-only
plan    = diff(desired, actual)                pure, ordered, content-addressed
apply(plan)                                    journaled, step-idempotent
```

Each step declares its own **precondition**, **effect**, and **postcondition**. A step whose postcondition already holds is skipped, not repeated — that is where P-noop comes from, not from wrapping the whole thing in a flag file.

The **journal** is append-only JSONL with the same record shape as the evidence ledger. Not a coincidence and not reuse-for-its-own-sake: provisioning history is evidence, it wants provenance and `envHash`, and the ledger already does that. I1 paying rent a fourth time.

### The uncomfortable part

Package managers are not idempotent. `npm install` can produce different trees from identical inputs; `cargo add` mutates a manifest with formatting opinions.

Containment:

- the harness **never** invokes a resolving install. Lockfiles are desired state; installs are deterministic replays (`npm ci` and equivalents).
- manifest edits are performed by the harness against a parsed AST, deterministically formatted, and **verified by re-parse** before the step's postcondition passes.
- if a package manager produces a lock that disagrees with the plan, that is a **halt**, not a merge. The engine does not negotiate with the resolver — F6.

### Crash safety

Journal-before-mutate gives resumability. On start, an unterminated journal entry means the last apply was interrupted: re-observe, re-plan, and the plan naturally omits whatever already landed. **No rollback machinery.** Rollback of a partial dependency install is a fantasy; convergence is achievable and rollback is not.

---

## 5. Refactor procedures

A refactor is a **declared document**, never a script. "Swap the runner", "move the substrate from shadow-root to iframe pool", "add a native profile" are all the same kind of object.

```
Procedure {
  id, description
  preconditions[]        must hold or HALT
  bindingChanges[]       requirement → new provider
  migrations[]           codemods, config rewrites, evidence remapping
  postconditions[]       must hold or the procedure did not happen
  evidenceDisposition    preserve | stale | invalidate   ← mandatory, no default
  reversible             bool; irreversible procedures say so loudly
}
```

Rules:

- a procedure runs through the same plan/apply path as init. **There is one mutation path.** A second one would be a second source of truth about state, which is the thing this project is against.
- procedures are idempotent by the same properties. Running one twice is a no-op with a message.
- **`evidenceDisposition` has no default.** Changing the substrate invalidates every visual baseline; changing the runner probably does not; changing a token snapshot makes evidence stale rather than wrong. Getting this wrong silently is how a maturity ladder starts lying, so the procedure author must state it.
- a procedure that would drop any card's rung reports the drop in the proposal, before approval.

---

## 6. Conformance as the acceptance gate

This is the finding that makes the whole thing hold together, and it was already sitting in `TESTING.md §3` doing a smaller job.

**A requirement owns a conformance suite. A provider is bound only if it passes that suite under the target profile.**

Consequences, in order of how much I like them:

1. **The testing harness is the negotiation validator.** "A testing harness that can dynamically change stack dependencies" is not two features bolted together — the harness is the thing that licenses the change. There is no other mechanism by which a provider becomes trustworthy.
2. **Provider swaps become safe by construction.** Vitest and Playwright are interchangeable exactly insofar as both pass the runner conformance suite. If they diverge, the suite is the diff.
3. **The suite outlives the decision.** Written to settle D1, it becomes the permanent regression net for whatever wins, and the entry exam for anything proposed later.
4. **D1's three options stop competing and start being measured.** All three become providers; the suite ranks them; the binding records which won and why.

Binding states:

| State | Meaning |
|---|---|
| `VERIFIED` | conformance passed under this profile, current `envHash` |
| `PROVISIONAL` | bound with explicit operator override, suite not yet passed — **visible in every proposal until cleared** |
| `STALE` | passed under a different `envHash` |
| `FAILED` | cannot be bound |

`PROVISIONAL` exists because a bootstrap needs it. It must be loud, it must appear in CI output, and it must never quietly become the steady state.

---

## 7. Supply chain and capability

Dynamic dependency addition is a security surface. Justified Capability Attestation applies unchanged.

- a provider declares its capability requests with justifications; **the grant is policy's decision, never the provider's**
- negotiation performs **no network access** without an explicit grant. Offline negotiation against cached probes and locked registries is the default, and it is also what makes negotiation a pure function.
- new transitive dependencies surface in the proposal as a **diff of the resolved tree**, not as a count. "Adds one package" that pulls two hundred transitively is the lie this prevents.
- provider identity is content-addressed. A provider whose hash changes without a binding change is a halt.
- the proposal is the review artifact. **It is designed to be read before approval by a human who is tired**, which is the only realistic review condition.

---

## 8. The bootstrap floor

The negotiation engine has dependencies. That is the paradox, and it needs a stated floor.

**Irreducible core, fixed, never negotiated:** a Rust toolchain, one package manager per ecosystem in use, and a filesystem. Nothing else.

Everything above that floor is a provider. The engine itself must be buildable and runnable with zero negotiated dependencies, or the first `init` cannot run. This is a hard constraint on the engine's own implementation and it should be checked in CI: **build the engine with the network off and an empty cache.**

---

## 9. Normative amendments

Apply these to the existing set. Until applied, the docs disagree with each other and this file wins.

| Doc | Amendment |
|---|---|
| `ARCHITECTURE.md` | **I3′ replaces I3:** "The harness owns no stack opinion. It must never name a concrete framework, renderer, or runner outside the binding lock." |
| `ARCHITECTURE.md` | **New I7:** "One mutation path. All state change flows through plan/apply with a journal." |
| `UX-STACK.md` | Add status header: **"Resolved binding snapshot for profile `linux/wayland/chromium/dev`. Evidence-backed, not axiomatic. Names in this document appear in the binding lock and nowhere else in the system."** |
| `TESTING.md §3` | Generalise: the substrate conformance suite is one instance of a per-requirement pattern. Every requirement carries a suite; the suite is the provider acceptance gate (§6). |
| `TESTING.md §7` | Add CI stage: **offline bootstrap** — build the engine with network off and empty cache (§8). |
| `TESTING.md §2` | Add property class: negotiation is pure and deterministic; apply satisfies P-conv, P-noop, P-resume. |
| `DECISIONS.md` | **D4 reclassified** from decision to binding, resolved by conformance evidence, changeable by refactor procedure. |
| `DECISIONS.md` | **D1 reframed**, not resolved: three providers, one suite, empirical gate. Still blocking. |
| `SPINE.md §3` | Document set gains `vitrine.stack.lock` (binding lock, token space, git-tracked) and `procedures/*.toml`. |

---

## 10. Open

- **P1 — Is this justified at project scale?** Terraform-grade provisioning machinery for a solo tool is plausibly the most over-engineered thing in the doc set. The counter-argument: without it, `UX-STACK.md` is a set of welds, and the stated philosophy is implementation-agnostic-until-inconvenient. The honest question is whether "inconvenient" arrived already and I am building for a portability need that never materialises. **This is the one to argue first.**
- **P2 — Requirement granularity.** Too coarse ("a frontend") and providers are unswappable monoliths. Too fine ("a way to hash a string") and every dependency needs an adapter and the project dies of interfaces. No principle currently distinguishes them. Suspicion: a requirement is only worth declaring where a *conformance suite* is worth writing — which is a nice test and possibly circular.
- **P3 — Does purity survive contact with npm?** Negotiation is pure only while probes are cached and no resolution happens during it. The moment a version range must be resolved to satisfy a proposal, purity is gone and F6 is knocking. Possibly requires that providers pin exact versions and never ranges, which pushes work onto provider authors.
- **P4 — Cross-ecosystem locks.** Rust and Node have separate locks with separate semantics. Does the binding lock reference them, contain them, or generate them? Referencing is cheapest and leaves two sources of truth.
- **P5 — `PROVISIONAL` decay.** It is designed to be loud, but nothing forces it to clear. An expiry that fails CI after N days is honest and will be hated on the day it fires. Alternative is that `PROVISIONAL` quietly becomes permanent, which is the outcome the state was invented to prevent.

---

## Sign-off

This document is not in effect until the operator approves §9's amendments. Until then the existing docs stand as written and this file is a proposal.

- [ ] §1 review findings accepted (F1–F6)
- [ ] §9 amendments applied to the doc set
- [ ] P1 argued — scale justification
- [ ] `DECISIONS.md` register updated
