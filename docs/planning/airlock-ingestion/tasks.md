# TASK_AIRLOCK-001 — PR-style LLM ingest (MVP)

**Status:** REVIEW  
**Protocol:** `0x20.00.11` (draft)  
**Hub:** `projects/airlock-ingestion/`  
**Verify:** `pytest dex/10-tests/test_airlock_ingestion_signature.py`

## Main user story

As greyZ reviewing a streamed LLM transcript (Grok / Gemini / Perplexity / OpenAI) in a zenOS review surface, I see typed blocks, I can redact or reject anything sketchy, and **merge cannot put model HTML on the app origin**. Hostile SVG and widgets stay quarantined as source until I approve them into an isolated frame with no `eval`.

UX flow (keep this as the alignment bar):

1. Paste / stream transcript.
2. Blocks appear as prose (host components), code (text), JSON (your tree), images (decoded bitmap or quarantine).
3. SVG/Mermaid/widgets default to source + `QUARANTINED`.
4. Approve / redact / reject per block. Override of high risk requires an explicit justification.
5. Merge writes only approved/redacted blocks. Raw bytes stay unmounted.

## Checklist

- [x] Archive submitted spec (not law)
- [x] Signed architecture review
- [x] Binding protocol (fail-closed, host HMAC, no `unsafe-eval`)
- [ ] Worker lexer with carry-over + quotas + terminate-on-timeout
- [ ] Host-owned markdown/JSON render
- [ ] Isolated-origin SVG after approve
- [ ] Governance FSM including `REJECTED`
