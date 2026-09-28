# Launch readiness checklist

Maintain this matrix in-repo **before any staging deployment or production traffic cutover**. Treat it as an engineering specification, not a legal memo. Status checkboxes are the living record; leave an item `[ ]` until the structural fix is in the shipped surface, or mark it `N/A` with a one-line reason when that surface does not exist yet.

This document is an architectural invariant spec derived from public statutes, regulations, and case law. It is not a substitute for counsel on a specific launch.

---

## Core insight

Legal compliance for software applications is rarely a legal wording problem—it is an **architectural state machine and boundary enforcement** problem.

When compliance is treated as post-hoc legal boilerplate (copy-pasting a privacy policy or adding a passive "By signing up you agree" footer), systems leak liability because the code itself remains unaware of regulatory invariants. If, instead, compliance constraints are designed directly into the protocol, schema, network boundary, and lifecycle layers—via zero-egress asset bundling, immutable contract ledgers, deterministic consent state machines, and symmetric subscription primitives—the application becomes legally compliant **by construction**.

This matches zenOS's existing GlitchWorks rules in `CONTRIBUTING.md`: boundary validation, state hydration, graceful degradation, and agnostic telemetry (domain logic emits events; the host decides whether a sink is stdout, a file, or a remote endpoint).

---

## Launch readiness matrix

Copy and keep this table current. Fill **Status** with `[x]` when the invariant is enforced in code, CI, or ops—not when copy exists on a marketing page.

| # | Verification item | Regulatory / financial hazard | Structural fix / architectural invariant | Status |
| --- | --- | --- | --- | --- |
| 1 | Zero-egress static assets | GDPR / ePrivacy (Munich LG: €100/visit IP leak) | Bundle all fonts, glyphs, and libraries locally; enforce strict Content Security Policy (`default-src 'self'`). | [ ] |
| 2 | Affirmative clickwrap ledger | Contract nullification (Berman v. Freedom Financial) | Require an active, un-ticked binary check; store an immutable event log with a hash of the exact terms version. | [ ] |
| 3 | Hardened age gate | COPPA ($53,088/child under 16 CFR § 1.98) | Neutral DOB input or explicit age declaration **prior** to profile initialization or identifier storage. | [ ] |
| 4 | Default-deny telemetry and replay | CIPA wiretapping ($5k/session under Cal. Penal Code § 631) | Gate analytics on an opt-in state machine; inject client-side DOM sanitizers to mask keystrokes/inputs at source. | [ ] |
| 5 | RFC 8058 outbound mail pipeline | CAN-SPAM ($53,088/email) and deliverability | Inject `List-Unsubscribe-Post`, `List-Unsubscribe` headers, and physical postal address template tokens into all bulk mailers. | [ ] |
| 6 | Symmetric click-to-cancel | FTC Negative Option (16 CFR Part 425) and CA ARL (AB 2863) | Expose 1-click self-service cancellation in the account dashboard matching onboarding complexity; no retention walls. | [ ] |
| 7 | Pre-checkout renewal notice | California ARL "unconditional gift" restitution | Display billing cadence, recurring price, and cancellation mechanism immediately contiguous to the primary checkout CTA. | [ ] |
| 8 | Merchant of Record (MoR) isolation | Economic nexus liability and MATCH list placement | Delegate payment ingestion to a Merchant of Record to insulate against multi-state tax nexus and card network fines. | [ ] |
| 9 | DMCA safe harbor agent | Statutory copyright infringement ($150k/work) | Pay $6 to register a Designated Agent with the U.S. Copyright Office; expose a public notice URL. | [ ] |
| 10 | Accessibility navigation model | ADA Title III / Unruh Civil Rights Act litigation | Enforce semantic HTML, keyboard focus traps/rings, and screen-reader accessibility meeting W3C WCAG 2.2 AA. | [ ] |
| 11 | Programmatic DSAR pipelines | GDPR Art. 17 / CCPA deletion failures | Provide self-service data export (JSON/archive) and hard cascading purge hooks across all data stores. | [ ] |

### How to record status

- `[ ]` — invariant not yet enforced for a surface that exists or is about to ship
- `[x]` — invariant is enforced in the shipped path (link the PR, schema, or header in the implementation notes below)
- `N/A` — surface does not exist (for example: no payments yet). Re-open the item the moment that surface is designed, not after it is live

---

## zenOS surface mapping

Use this table to decide which rows are in-scope for a given cutover. CLI-only local use does not skip item 4 (telemetry) or item 11 (PKM / inbox personal data) if those stores hold identifiers.

| Item | Current zenOS surface | Becomes blocking when |
| --- | --- | --- |
| 1. Zero-egress assets | Docs sites, future web UI, plugin web entry points | Any first-party HTML/CSS/JS is served to a browser |
| 2. Clickwrap ledger | Not present (no hosted accounts) | Signup, ToS, or "you agree" copy is added |
| 3. Age gate | Not present | Any profile, email, or persistent identifier is collected from a human user |
| 4. Default-deny telemetry | Architecture already sketches `Enable telemetry? [y/N]: n`; CONTRIBUTING requires agnostic sinks | Any analytics, crash reporter, session replay, or remote event sink ships |
| 5. RFC 8058 mail | Not present | Waitlist, launch, or lifecycle email is sent |
| 6. Click-to-cancel | Not present | Paid or free-trial subscriptions exist |
| 7. Pre-checkout notice | Not present | Checkout / subscribe CTA exists |
| 8. MoR isolation | Not present | zenOS (or a hosted sibling) takes payment as seller of record |
| 9. DMCA agent | Not present (MIT-licensed code; no public UGC host) | Users can upload or publish files, images, or posts visible to others |
| 10. Accessibility | CLI/TUI today; future visual workspace / mobile / web | Any graphical or web UI is offered as a public product |
| 11. DSAR pipelines | PKM notes, inbox, local context, `.env` identifiers | Personal data is stored, synced, or processed beyond the local machine |

**Cutover rule:** a row moves from `N/A` to `[ ]` in the same PR that introduces the surface—not in a follow-up "legal pass."

---

## Structural implementation: eliminating pitfalls by design

### 1. Client-side egress, fonts, and asset isolation (GDPR / ePrivacy)

**Root pitfall:** Hotlinking resources (Google Fonts, unhosted CDNs, external script tags) causes the client browser to transmit the visitor's IP address and user-agent string to third-party servers on page render—an unauthorized personal data transfer under EU jurisprudence (Landgericht München I, 3 O 17493/20).

**Implementation blueprint:**

- **Zero external calls.** Package all web fonts (`.woff2`) and vendor dependencies as first-party assets distributed from the zenOS origin or reverse proxy.
- **Content Security Policy.** Serve a strict HTTP header that prevents dynamic runtime egress:

```http
Content-Security-Policy: default-src 'self'; font-src 'self'; img-src 'self' data:; script-src 'self'; connect-src 'self';
```

- **Result:** Because no network packet leaves the client to an external host on static page loads, IP leakage is physically impossible.

**zenOS note:** This applies to any hosted docs, plugin `web` entry, or visual workspace. Third-party model APIs (OpenRouter and similar) are *user-initiated* `connect-src` exceptions and must be documented in the CSP and privacy notice—they are not an excuse to hotlink fonts or analytics.

### 2. Signup contracts and age gating (clickwrap, COPPA, GDPR Art. 8)

**Root pitfall:** "Browsewrap" (for example "By continuing, you agree...") fails the legal test of mutual assent (*Berman v. Freedom Financial Network, LLC*). Courts void mandatory arbitration and limitation-of-liability clauses. Failing to screen age leaves you strictly liable for COPPA violations ($53,088 per violation).

**Implementation blueprint:**

- **Schema-enforced audit ledger.** Do not rely on a boolean `agreed_to_terms: true`. Design an append-only agreement ledger:

```sql
CREATE TABLE legal_agreements (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    document_type VARCHAR(32) NOT NULL, -- 'terms_of_service', 'privacy_policy'
    document_version_hash CHAR(64) NOT NULL, -- SHA-256 of the exact text served
    interaction_type VARCHAR(16) NOT NULL, -- 'explicit_checkbox'
    ip_hash CHAR(64) NOT NULL, -- Salted SHA-256 (privacy-preserving audit)
    user_agent_snippet VARCHAR(255) NOT NULL,
    agreed_at_utc TIMESTAMP WITH TIME ZONE NOT NULL
);
```

- **Neutral age verification.** Place a neutral birthdate or age-gate selector **before** collecting identifiable user information (email, phone, name). If age is < 13 (or < 16 in the EU under GDPR Art. 8), terminate the session client-side and block registration **without persisting identifiers**.

**zenOS note:** Local CLI config (`OPENROUTER_API_KEY` in `.env`) is not a child-directed signup. The gate becomes mandatory the moment a hosted identity, cloud PKM sync, or social profile is designed.

### 3. Client telemetry and session replays (CIPA wiretapping)

**Root pitfall:** Session-recording scripts intercept client-side input events (DOM mutation, keystrokes, clipboard paste). Plaintiffs in California sue under Cal. Penal Code § 631, claiming that real-time event streaming to a third-party analytics vendor is illegal electronic eavesdropping without two-party consent.

**Implementation blueprint:**

- **Default-off state machine.** Telemetry scripts must not execute until an explicit consent state resolves to `true` (privacy-first preferences). The CLI sketch already defaults to `n`; keep that default in every new sink.
- **Client-side obfuscation.** If recording sessions for debugging, apply absolute input masking at the DOM serialization layer, not on the server:
  - Mask all form input fields (`<input>`, `<textarea>`, `contenteditable`).
  - Apply structural CSS masking classes to any element displaying user-generated data or PII **before** sending payload deltas over the wire.

**zenOS note:** CONTRIBUTING already requires agnostic telemetry—domain logic emits events; the host chooses the sink. A remote sink is a product decision gated by this row. PKM capture, inbox ingestion, and chat logs are **content stores**, not analytics; they still need consent and DSAR coverage if they leave the machine.

### 4. Outbound marketing and lifecycle messaging (CAN-SPAM, CASL)

**Root pitfall:** Sending "We launched!" blasts to waitlist signups without an instantaneous unsubscribe mechanism or physical address violates the CAN-SPAM Act and triggers automated spam scoring.

**Implementation blueprint:**

- **Dual-mechanism unsubscribe.** Support both HTTP GET and RFC-standard headers in every bulk email payload:

```http
List-Unsubscribe: <https://api.yourdomain.com/v1/mail/unsubscribe?token=...>, <mailto:unsubscribe@yourdomain.com?subject=unsubscribe>
List-Unsubscribe-Post: List-Unsubscribe=One-Click
```

This satisfies RFC 8058 and RFC 2369, enabling native one-click unsubscribe in mail clients (Gmail, Apple Mail).

- **Template injection guard.** Make the transactional template engine **fail hard in CI** if the footer does not render the registered legal entity's physical postal address or valid PO Box.

**zenOS note:** Transactional mail that is a direct response to a user request (password reset, magic link) is not the same as a launch blast, but the unsubscribe headers and postal address still belong on commercial messages. Do not reuse waitlist emails as a marketing list without this pipeline.

### 5. Payments, automatic renewals, and fiscal boundaries (FTC Negative Option and MoR)

**Root pitfall:**

- **FTC Negative Option Rule (16 CFR Part 425) and California ARL:** Disallowing self-service cancellation, burying subscription terms, or making cancellation harder than enrollment classifies the service as deceptive, rendering billed amounts an illegal gift requiring complete refund.
- **Sales tax nexus and MATCH list:** Selling globally via a naked payment gateway (for example raw Stripe API) without remitting sales tax triggers personal tax liabilities once you cross economic nexus thresholds ($100k / 200 transactions in many US states; immediately in the EU via OSS). High dispute rates trigger placement on the Mastercard MATCH list, blacklisting principals from acquiring merchant accounts.

**Implementation blueprint:**

- **Symmetric cancellation interface.** The cancellation flow must require equal or fewer clicks than checkout. If a user subscribed with two clicks, they must be able to cancel with two clicks from `/settings/billing` without chat prompts or phone calls.
- **Checkout proximity copy.** Display the recurring price, renewal frequency, and immediate cancellation URL in clear, contrasting typography within 100 pixels of the checkout submit button.
- **Merchant of Record layer.** For early launches, avoid running as the direct seller of record. Route through a Merchant of Record abstraction (for example Lemon Squeezy, Paddle, Polar). The MoR acts as the legal reseller, assuming liability for calculating, collecting, and remitting global sales tax/VAT, and insulating the core entity from processor chargeback thresholds.

**zenOS note:** Do not wire a raw Stripe (or similar) charge in a plugin or hosted sibling without an explicit MoR / nexus decision recorded in this matrix.

### 6. User-generated content and safe harbor (DMCA 17 U.S.C. § 512)

**Root pitfall:** If the application accepts file uploads, image posts, or text sharing, third parties can upload copyrighted material. Without a formally registered Designated Agent, you are directly liable for contributory infringement (statutory damages up to $150,000 per infringed work).

**Implementation blueprint:**

- **Statutory registration.** File a designated agent registration electronically at the U.S. Copyright Office Directory ($6 fee).
- **Expose a protocol endpoint.** Publish `/dmca` or `/legal/copyright` with the agent's name, physical address, and dedicated email (`dmca@yourdomain.com`).
- **Takedown pipeline.** Build a deterministic internal status flag on user assets: `ACTIVE`, `TAKEDOWN_PENDING`, `REMOVED`. On a compliant notice, programmatically transition the asset to `REMOVED` and notify the uploader to preserve safe harbor immunity.

**zenOS note:** Local PKM notes are not a public UGC host. Shared/synced workspaces, plugin marketplaces, and social "AI network" features **are**. Register the agent before those surfaces accept uploads.

### 7. Accessibility navigation model (ADA Title III / Unruh / WCAG 2.2 AA)

**Root pitfall:** A public web or GUI product that cannot be used with a keyboard or screen reader is a litigation target under ADA Title III and California's Unruh Civil Rights Act.

**Implementation blueprint:**

- Semantic HTML (`button`, `nav`, `main`, labeled inputs)—not clickable `div`s.
- Visible keyboard focus rings; focus traps only inside modal dialogs, released on close.
- Meet [W3C WCAG 2.2 AA](https://www.w3.org/TR/WCAG22/).
- CLI/TUI: respect terminal accessibility (no color-only status, screen-reader-friendly tables where the host supports it).

### 8. Programmatic DSAR pipelines (GDPR Art. 17 / CCPA)

**Root pitfall:** A "contact us to delete your data" mailbox that cannot actually purge replicas, logs, backups, and vendor copies is a deletion failure.

**Implementation blueprint:**

- Self-service export: JSON or archive of all personal data associated with the identity.
- Cascading purge hooks across primary stores, search indexes, object storage, and third-party processors (model providers, mail, analytics).
- Record the deletion event; do not keep the underlying PII "just in case."

**zenOS note:** PKM, inbox, context sync, and any cloud memory feature need an export/purge path the moment they store personal data off-box.

---

## Socratic exploration: hardening the surface

Dial this architecture in for the specific cutover:

1. **Telemetry boundary.** When an anonymous visitor arrives at a landing page (or a first-run CLI), what is the exact lifecycle of their session? Are any scripts or sinks allowed to capture data before an explicit choice is registered in the consent state machine?
2. **Liability perimeter.** In the envisioned billing architecture, does zenOS act as the direct merchant of record, or does the operational roadmap benefit from offloading multi-jurisdiction VAT/sales tax registration to an intermediary?
3. **Identifier timing.** What is the first byte of personal data written to disk or a remote store—and does the age gate run before that write?
4. **Assent evidence.** If a court asked for the exact terms text a user agreed to on date *T*, can you produce the SHA-256 of that version plus an append-only ledger row—or only a boolean?
5. **Cancel symmetry.** Count the clicks from "I want this" to charged, then from "I don't" to not charged. Are they equal or is cancel longer?
6. **Processor map.** Which third parties (OpenRouter, TTS, n8n, object storage, email) receive personal data, under what legal role (processor vs controller), and how does a DSAR cascade to each?

---

## Addendum: official standards and regulatory references

- [FTC civil penalty adjustments (16 CFR § 1.98)](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-A/part-1/subpart-L) — federal register statutory penalty escalations
- [FTC Negative Option Rule (16 CFR Part 425)](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-D/part-425) — click-to-cancel regulations
- [FTC CAN-SPAM Act compliance guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) — Bureau of Consumer Protection business rules
- [California Automatic Renewal Law (AB 2863)](https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=202320240AB2863) — Bus. & Prof. Code § 17600–17606
- [California Invasion of Privacy Act (CIPA)](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PEN&sectionNum=631) — Penal Code § 631
- [DMCA designated agent directory](https://www.copyright.gov/dmca-directory/) — U.S. Copyright Office DMCA registry
- [DMCA safe harbor statute](https://www.law.cornell.edu/uscode/text/17/512) — 17 U.S.C. § 512
- [RFC 8058: One-Click List-Unsubscribe](https://www.rfc-editor.org/rfc/rfc8058) and [RFC 2369: mailing list headers](https://www.rfc-editor.org/rfc/rfc2369)
- Affirmative assent: *Berman v. Freedom Financial Network, LLC*, 30 F.4th 849 (9th Cir. 2022)
- Pre-checked consent: *Planet49 GmbH*, CJEU Case C-673/17
- [W3C Web Content Accessibility Guidelines (WCAG) 2.2](https://www.w3.org/TR/WCAG22/)

---

## Maintenance

- **Owners:** reviewers of any PR that introduces hosted UI, telemetry, mail, billing, accounts, or UGC (see `.github/PULL_REQUEST_TEMPLATE.md`).
- **Cadence:** re-walk the matrix on every staging or production cutover, not once per year.
- **Edits:** change the invariant or the status in this file in the same PR as the surface. Do not keep a shadow spreadsheet.
