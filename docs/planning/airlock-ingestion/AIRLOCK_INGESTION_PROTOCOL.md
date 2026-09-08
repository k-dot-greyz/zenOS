<!--
dex_id: "0x20.00.11"
dex_type: protocol
status: draft
tags: [security, llm, airlock, xss, csp, iframe, ingestion]
-->

# Airlock Ingestion Protocol

> Status: `draft`  
> Hub: [`projects/airlock-ingestion/`](../../projects/airlock-ingestion/)  
> Submitted spec (archive, not law): [`AIRLOCK_INGESTION_SPEC.md`](../03-docs/projects/airlock-ingestion/AIRLOCK_INGESTION_SPEC.md)  
> Signed review: [`REVIEW.md`](../03-docs/projects/airlock-ingestion/REVIEW.md)  
> Companion: [Embed Security Policy](EMBED_SECURITY_POLICY.md) (`0x20.00.0D`)

Untrusted LLM transcripts (Gemini, Grok, Perplexity, OpenAI, local) are hostile input. This protocol is the **binding v1** for ingesting them into zenOS / visual-wiki / any review surface. The submitted four-layer paper is evidence, not an implementation checklist.

Do not implement the submitted spec as-written. `unsafe-eval`, `X-Frame-Options: SAMEORIGIN` on the sandbox host, HMAC inside the untrusted worker, and host-origin HTML from the sanitizer are rejected.

## Law

1. **Host origin never mounts model markup.** No `innerHTML`, `dangerouslySetInnerHTML`, or HTML-string highlighters on pipeline output. Markdown becomes a token AST rendered by host-owned components. `rawPayload` is never mounted.
2. **Parse off the main thread.** Layer 1 runs in a worker. Byte, depth, and node quotas are numeric and fail-closed. A host watchdog **terminates** the worker on timeout; that payload is `QUARANTINED` and is never retried on the main thread.
3. **Allowlist via a real parser.** HTML/SVG sanitization is parse → allowlist → serialize → reparse until fixpoint. Regex is not a sanitizer. MathML is forbidden in v1. YAML is forbidden in v1.
4. **Bitmaps decode, they do not sniff.** Magic bytes are necessary and not sufficient. Decode with a dumb decoder (`createImageBitmap` or equivalent). Quarantine on failure. Never re-parse as HTML. Cap pixels and decoded bytes. `image/svg+xml` is a vector graphic, not a bitmap.
5. **Crypto lives on the privileged side.** Worker never sees `SessionKey`. Raw digest is SHA-256. Host HMAC covers `{blockId, type, sanitizedPayload}` with a canonical byte encoding. Reviewer Ed25519 is verified server-side against a registered pubkey. Client-supplied `reviewerSignature` strings are not authentication.
6. **Scripts and SVG execute only on an isolated origin after approve.** v1: SVG/Mermaid/widgets are quarantined by default; preview is source text. No `unsafe-eval`. No `allow-same-origin` combined with `allow-scripts` on our own origin ([Embed Security](EMBED_SECURITY_POLICY.md) Rule 1). CSP is response headers, not the iframe `csp` attribute.
7. **Sandbox headers must actually load in the parent.** Use `frame-ancestors` of the app origin. Do not set `X-Frame-Options: SAMEORIGIN` on a foreign sandbox host. App surfaces keep `X-Frame-Options: DENY` and `frame-src 'none'` unless this exception is documented in the PR.
8. **Fail closed.** Hash mismatch hides the block. `auditBatch.canMerge` is false unless every block is `APPROVED` or `REDACTED`. There is a `REJECTED` state. `OVERRIDE_FLAG` at score ≥ 75 is a two-person or explicit high-privilege action with justification.
9. **Default-deny capabilities.** MessagePort schema is size-capped. Widgets do not get `fetch`, clipboard, storage, or cookies unless granted. `connect-src 'none'` on the runner unless a named grant exists.
10. **Exceptions are isolated origins.** “It is sandboxed” is not a justification. Cite `layer:embed-security` and `layer:airlock-ingestion` in the PR.

## v1 types

`PROSE`, `CODE_SNIPPET`, `STRUCTURED_DATA` (JSON only), `VECTOR_GRAPHIC`, `CANVAS_EXPORT`. `DYNAMIC_WIDGET` is deferred: host-owned JSON cards (`zenos.entity/1`) only.

Streaming ingest is `AsyncIterable<CanonicalBlock>` with lexer carry-over across chunks. Batch `ingest(): Promise<…>` is a wrapper, not the contract.

## Tests

Binding tests are listed in [`REVIEW.md`](../03-docs/projects/airlock-ingestion/REVIEW.md) (rewired checklist) and [`tasks.md`](../../projects/airlock-ingestion/tasks.md). Signature integrity: `pytest dex/10-tests/test_airlock_ingestion_signature.py`.

```bash
python dex/04-scripts/check-layout-facade.py --merge-base origin/main
pytest dex/10-tests/test_airlock_ingestion_signature.py
```
