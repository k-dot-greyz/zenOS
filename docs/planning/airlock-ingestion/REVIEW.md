# Review: Airlock Ingestion Spec

**Status:** findings recorded; spec is **not** implementation law  
**Reviewed:** 2026-09-08  
**Reviewer:** Cursor Grok 4.6 (SpaceXAI × Cursor)  
**Operator:** Kaspars Greizis (greyZ / `k-dot-greyz`)  
**Submitted artifact:** [`AIRLOCK_INGESTION_SPEC.md`](./AIRLOCK_INGESTION_SPEC.md)  
**Binding v1:** [`AIRLOCK_INGESTION_PROTOCOL.md`](../../../02-protocols/AIRLOCK_INGESTION_PROTOCOL.md) (`0x20.00.11`, draft)  
**Companion law:** [`EMBED_SECURITY_POLICY.md`](../../../02-protocols/EMBED_SECURITY_POLICY.md) (`0x20.00.0D`)  
**Signature:** [`SIGNATURE.md`](./SIGNATURE.md)

---

## Verdict

The threat model and four-layer shape are right. The spec as written would not deliver the guarantees it claims. Several of the named “security controls” are self-contradictory, and the highest-risk path — LLM HTML/JS ending up in the host document — is unspecified.

Treat the submitted paper as a design sketch. Binding constraints for any implementation live in the protocol. Language in the spec that “guarantees strict isolation” or “eliminates main-thread degradation” should read **mitigates** and **bounds**. Browsers will not keep those promises.

This review is the signed analysis for the 2026-09-08 ingest. It is not a rubber stamp.

---

## What is solid

Most “render the model output” UIs skip isolation and then act shocked when SVG `onload` or markdown `javascript:` links fire. The useful bones:

- Unidirectional ingest. Nothing skips a layer.
- Parse off the main thread. Giant markdown/SVG/JSON will freeze a tab long before XSS matters.
- Allowlists, not regex blacklists, for HTML/SVG.
- Human review modeled as merge, not a toast that says “looks safe.”
- Capability-based `MessageChannel` instead of `window.parent.postMessage` soup.
- `sandbox="allow-scripts"` **without** `allow-same-origin` is the right default if scripts must run.
- Fail-closed on hash mismatch, instead of “show raw as fallback.”
- Audit events with a hash chain and Ed25519 — directionally correct.

If you stop there, you are already ahead of typical chat UIs.

---

## Critical

### 1. Sanitized prose still runs in the host origin

Layer 4 isolation is only specified for `DYNAMIC_WIDGET` and `VECTOR_GRAPHIC`. `PROSE`, `CODE_SNIPPET`, and `STRUCTURED_DATA` are implied to render in `https://core.app.domain` after Layer 2.

One sanitizer bug is then stored XSS on the **app origin**, with cookies, tokens, and reviewer credentials. DOMPurify-class bugs and mutation XSS (mXSS) are a yearly event. The threat model lists DOM clobbering and XSS, then parks the most common payload type (markdown/HTML) outside the sandbox.

**Required:**

- The host document never does `innerHTML` / `dangerouslySetInnerHTML` on pipeline output.
- All HTML (including “safe” markdown) renders as host-owned components from a token AST, in a closed shadow root, or in the same iframe sandbox as widgets.
- Syntax highlighting (Prism, highlight.js + `innerHTML`) is a known sink. Highlight inside the sandbox or with a text-node highlighter.
- `rawPayload` is radioactive. Persist it if you must; never mount it. Review UI shows it as text.

Until that is explicit, Layers 1–3 are a speed bump, not an airlock.

### 2. Layer 4 CSP and frame policy fight each other

Three landmines in one iframe:

**`script-src 'self' 'unsafe-eval'`**  
Four layers forbid execution, then the runner gets `eval`. If widgets need to run model-generated JS, say that out loud and isolate it (QuickJS/WASM, SES/Realms, or a tiny DSL). `unsafe-eval` is containment theater unless origin isolation is airtight. It is not a sanitizer. v1 does not ship `unsafe-eval`.

**`X-Frame-Options: SAMEORIGIN` on `sandbox.isolated.domain`**  
Parent is `core.app.domain`. That header **blocks** the parent from framing the runner. Use `frame-ancestors https://core.app.domain` and drop `X-Frame-Options`. This also contradicts [`EMBED_SECURITY_POLICY.md`](../../../02-protocols/EMBED_SECURITY_POLICY.md) (`X-Frame-Options: DENY` on app surfaces; sandbox hosts are an isolated-origin exception with `frame-ancestors`, not SAMEORIGIN).

**“null origin” vs `https://sandbox.isolated.domain`**  
These are not interchangeable:

| Pattern | What you get |
| :--- | :--- |
| `sandbox` without `allow-same-origin` | Opaque unique origin. `script-src 'self'` gets weird. |
| Stable `sandbox.isolated.domain` + `allow-same-origin` | Shared origin across widgets/users. One break infects the origin. |
| Unique per-session subdomain + `allow-scripts allow-same-origin` | Predictable CSP, origin isolation per session. |

The spec mixes all three. Pick one.

The `csp` attribute on `<iframe>` is not a thing you can rely on. CSP lives on the **response headers** of the framed document.

`COOP: same-origin` on an iframe document is mostly a no-op (COOP is a top-level window thing). `COEP: require-corp` without `Cross-Origin-Resource-Policy` on the runner (and matching parent policy if the parent also uses COEP) is incomplete. Spec the parent headers too.

### 3. Algorithm 1 cannot parse real markdown and does not neutralize ReDoS

The fence regex `/^```([a-zA-Z0-9_-]+)?\n([\s\S]*?)```$/gm` with the `m` flag makes `$` end-of-**line**. That only matches fences that open and close on the same line. Normal code blocks never match. Everything falls through as `PROSE`.

Streaming makes it worse: a fence split across chunks is dropped or glued into prose. `ingest()` returning `Promise<CanonicalBlock[]>` is a batch API. Streaming intake needs a lexer with carry-over state and `AsyncIterable<CanonicalBlock>`.

The 50ms “guarantee” is not a guarantee in JS. A worker stuck in native regex / `JSON.parse` cannot be preempted; you **terminate and recycle** the worker. Watchdog in the host, `worker.terminate()`, payload → `QUARANTINED`, never retry that payload on the main thread.

Fence-splitting regex is not where ReDoS usually lives. The real killers are markdown parsers, SVG/`path` parsers, YAML, and syntax highlighters. Ban YAML bombs or do not accept YAML. Put a node/depth/byte cap on JSON and SVG **before** parse.

### 4. HMAC is named SHA-256, computed in the wrong place, and does not mean what the checklist says

Three ideas smashed into one field:

- `contentSha256` — content digest of raw bytes (SHA-256, keyless, for addressing)
- `sanitizedSha256` — digest of sanitizer output (SHA-256, for cache/equality)
- HMAC with `SessionKey` — authenticity of “this session’s pipeline emitted this”

HMAC inside Layer 2 (the same worker that touched untrusted bytes) is signing your own homework. Worker compromise ⇒ key + forged “clean” blocks.

**Model:**

1. Worker never sees `SessionKey`.
2. Worker returns `{ rawDigest, sanitizedPayload, type, … }`.
3. Host (or a privileged worker) HMACs `{blockId, type, sanitizedPayload}`.
4. Reviewer Ed25519 signs governance events, not the sanitizer output.

Canonical serialization for signatures is mandatory (byte-stable, not `JSON.stringify` insertion order). The checklist line about “one whitespace invalidates `contentSha256`” is fine for the raw digest and has nothing to do with HMAC.

### 5. SVG allowlist is both too tight and too loose; Mermaid is a trap

Default `risk.score = 50` for every SVG means SVG **never** auto-quarantines (threshold 75).

Banned `use`, `foreignObject`, `script`, `animate`, `set` — good start.

Still dangerous / missing: `<a>`, `<image>`, `<style>`, `<defs>`, `<filter>`, `pattern`, `marker`, `mask`, `clipPath`, gradients, `symbol`, nested `<svg>`, presentation attributes that take `url(#…)` or `url(https://…)`, SVG 1.2 `handler`/`listener`, `animateTransform`.

`text` without a real SVG sanitizer (DOM parse → allowlist → serialize → **reparse until fixpoint**) will mXSS.

Mermaid is classified as `VECTOR_GRAPHIC` but is source that compiles through a JS library with a CVE history. It must go through Layer 4 as a widget, never `innerHTML` of mermaid output on the host.

### 6. `DYNAMIC_WIDGET` is a type name with no product

Unspecified: artifact format (HTML bundle? React tree? custom elements? JSON-UI?), how reviewers PR-review minified JS, which `postMessage` capabilities exist (default deny), and the “64MB hard limit” (not a web platform feature on an iframe).

v1 widgets are **data + a host-owned renderer** (JSON cards, a canvas protocol you own). Not `eval` of the model’s mini-app.

---

## Important

**Magic bytes ≠ polyglot defense.** PNG `89 50 4E 47…` still allows trailing garbage and extra chunks. JPEG `FF D8 FF` is too short. The checklist’s “PNG + bash” case **passes** magic-byte checks. Once classified as bitmap: decode with `createImageBitmap` / a dumb decoder, render as `<img>` created via DOM APIs, never re-sniff, never parse as HTML. Quarantine on decode failure. Cap pixels and decoded bytes.

**Links.** Banning relative URLs breaks normal docs. Footguns are `javascript:`, `data:`, `vbscript:`, and protocol-relative `//evil.test`. Allow `https:` and in-app routes you control. Drop `http:` in production. `target="_blank"` + `rel="noopener noreferrer"` is correct.

**`id` banned, prose still in the parent DOM.** Clobbering is about where the nodes live. Ban `id`/`name` anyway; isolation beats allowlists. `metadata: Record<string, unknown>` is a smuggling bag — schema it or drop it.

**MathML** is named in Layer 2 and absent from the matrix. Forbid it in v1.

**FSM holes:** no `REJECTED` / `DROPPED`; no two-person rule for `OVERRIDE_FLAG` on score ≥ 75; no rule that `rawPayload` cannot be what got `MERGED` if a redaction exists; streaming sequenceIndex collisions; `commitTransaction` vs per-block `APPROVED`. `auditBatch` is fail-closed: any `QUARANTINED` / `INGESTED` / `IN_REVIEW` ⇒ `canMerge: false`.

**Signatures are not auth.** `redactBlock(..., reviewerSignature: string)` as a client-supplied field is theater. Server holds the event, verifies Ed25519 against a registered pubkey for `operatorId`.

**Quotas are named, not numbered.** Need concrete `L_max`, max blocks/session, max JSON depth, max SVG elements, max table cells, max base64 decoded size.

**CSS exfil test is the wrong test.** Iframes do not inherit parent CSS variables. Real test: sandbox cannot initiate any HTTP(S) request, and host tokens are never `postMessage`’d into the frame. `style-src 'unsafe-inline'` in the runner re-opens CSS probes *inside* the widget.

**Layer 1 “token block” vs LLM tokens.** 50ms per *token* is nonsense at stream rate. Per fenced chunk or per N KB, with a kill switch.

---

## Medium / nits

- Threat model lists CSS `expression()` — dead IE. Keep CSS `url()` / attribute selectors.
- No GIF/AVIF/`image/svg+xml`. Treat SVG-as-image as `VECTOR_GRAPHIC`, never as a bitmap.
- `CANVAS_EXPORT` as base64 in a JSON envelope will wreck memory. Prefer `ArrayBuffer` + hash.
- Review UI can DoS the main thread with a 2MB diff. Virtualize and truncate.
- Standards section should cite the HTML sanitizer algorithm (parse → allowlist → serialize → reparse) and the sandbox flags you **must not** set. RFC 4648 is the least interesting citation here.

---

## v1 MVP (matches the guiding user story)

One story: a reviewer opens an untrusted LLM transcript, sees typed blocks, and can merge only what they approved — without the host origin ever executing model markup.

Ship this first:

1. Lexer in a worker with byte caps. No markdown-in-regex HTML parse. Fence + prose + JSON only.
2. No model HTML in the host. Markdown → AST → host-owned components from **tokens**, not HTML strings. Links rewritten by you.
3. Code blocks as text + optional sandboxed highlighter.
4. JSON as `JSON.parse` with depth/size caps, rendered by **your** table/tree, keys as text.
5. SVG/Mermaid/widgets: **quarantined by default**, preview as source text, render only after approve, and only in the iframe.
6. Bitmaps: magic **and** decode, then `<img>` from a `blob:` you created.
7. Review FSM with `REJECTED`, no silent merge, HMAC on the host, Ed25519 on the server.
8. Widgets: json cards you already own (`zenos.entity/1`), not `unsafe-eval`.

That is an airlock. The submitted Layer 4 is a future appendix.

---

## Suggested contracts (shape)

```typescript
ingest(raw: ReadableStream<Uint8Array>): AsyncIterable<CanonicalBlock>;

type CanonicalBlock = {
  blockId: string;
  sequenceIndex: number;
  type: BlockClassification;
  rawRef: { sha256: string; byteSize: number };
  sanitized: { sha256: string; payload: string };
  hostMac: string;
  status: QuarantineStatus;
  risk: BlockRiskProfile;
};
```

Sandbox runner headers (parent frames it):

```http
Content-Security-Policy: default-src 'none'; script-src 'nonce-…'; style-src 'nonce-…'; img-src blob:; connect-src 'none'; frame-ancestors https://core.app.domain;
Cross-Origin-Resource-Policy: cross-origin
X-Content-Type-Options: nosniff
```

No `unsafe-eval` unless you have explicitly accepted “this frame runs hostile JS.”

---

## Compliance checklist — keep, rewire

| Submitted test | Verdict |
| :--- | :--- |
| ReDoS / 50ms | Keep, but test by **killing the worker**. Include markdown parser + JSON depth bombs. |
| Polyglot PNG | Magic-byte pass is **not** success. Decode-or-quarantine is the test. |
| `parent.location` | Keep. Also test `top.location`, `<a target=_top>`, absence of `allow-top-navigation-by-user-activation`. |
| CSS variable probe | Replace with “sandbox cannot initiate any HTTP(S) request.” |
| Whitespace hash | Split into raw SHA-256 vs host HMAC vs reviewer signature. Three tests. |

Add: mXSS (sanitize → parse in iframe → DOM not equal to expected), highlighter XSS, mermaid in host, `X-Frame-Options` actually allows the parent, worker terminate on timeout, `rawPayload` never in `innerHTML`.

---

## Bottom line

Keep the four layers and the PR metaphor. Rewrite Layer 1’s lexer, move crypto to the host, put **all** HTML in a sandbox (or do not use HTML), delete `unsafe-eval` from v1, fix the frame headers, and do not call SVG risk `50` if quarantine starts at `75`.
