# Airlock ingestion (zenOS copy)

SHA-256 attested 2026-09-08 review of the agnostic airlock / PR-style LLM ingest spec. Human sign-off of this zenOS copy is **pending**.

**SSOT is [`k-dot-greyz/dev-master`](https://github.com/k-dot-greyz/dev-master).** This directory is a byte-identical copy of the submitted spec, the signed analysis, and the binding protocol so the public zenOS repo carries the same fingerprints. Companion: [dev-master#1509](https://github.com/k-dot-greyz/dev-master/pull/1509).

| File | Role |
| :--- | :--- |
| [`AIRLOCK_INGESTION_SPEC.md`](./AIRLOCK_INGESTION_SPEC.md) | Submitted artifact (archive, **not** law) |
| [`REVIEW.md`](./REVIEW.md) | Signed analysis (Cursor Grok 4.6) |
| [`AIRLOCK_INGESTION_PROTOCOL.md`](./AIRLOCK_INGESTION_PROTOCOL.md) | Binding v1 (`0x20.00.11`, draft) |
| [`SIGNATURE.md`](./SIGNATURE.md) | SHA-256 attestation (human sign-off pending) |
| [`SIGNATURE.json`](./SIGNATURE.json) | Machine attestation |
| [`tasks.md`](./tasks.md) | MVP user story |

Archived spec / review / protocol keep their dex-tree relative links (`../../../02-protocols/...`, `../03-docs/...`). Those paths do **not** resolve in zenOS; follow them in `dev-master`. In this copy, the binding protocol is [`AIRLOCK_INGESTION_PROTOCOL.md`](./AIRLOCK_INGESTION_PROTOCOL.md). Do not rewrite archived bytes to “fix” those links — fingerprints would break.

Do not implement the submitted Layer 4 CSP. Host origin never mounts model HTML. No `unsafe-eval` in v1.
