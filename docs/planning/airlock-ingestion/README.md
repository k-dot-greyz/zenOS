# Airlock ingestion (zenOS copy)

Signed 2026-09-08 review of the agnostic airlock / PR-style LLM ingest spec.

**SSOT is `k-dot-greyz/dev-master`.** This directory is a byte-identical copy of the submitted spec, the signed analysis, and the binding protocol so the public zenOS repo carries the same fingerprints.

| File | Role |
| :--- | :--- |
| [`AIRLOCK_INGESTION_SPEC.md`](./AIRLOCK_INGESTION_SPEC.md) | Submitted artifact (archive, **not** law) |
| [`REVIEW.md`](./REVIEW.md) | Signed analysis (Cursor Grok 4.6) |
| [`AIRLOCK_INGESTION_PROTOCOL.md`](./AIRLOCK_INGESTION_PROTOCOL.md) | Binding v1 (`0x20.00.11`, draft) |
| [`SIGNATURE.md`](./SIGNATURE.md) | Human sign-off + SHA-256 |
| [`SIGNATURE.json`](./SIGNATURE.json) | Machine attestation |
| [`tasks.md`](./tasks.md) | MVP user story |

Relative links inside the protocol point at the dex tree. Use them in `dev-master`.

Do not implement the submitted Layer 4 CSP. Host origin never mounts model HTML. No `unsafe-eval` in v1.
