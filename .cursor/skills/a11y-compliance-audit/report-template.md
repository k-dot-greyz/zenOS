# Report template (copy per spec)

Replace `{placeholders}` when writing `{spec.id}.md`.

---

```markdown
# {spec.title} — Accessibility audit

| Field | Value |
|-------|-------|
| **Spec** | [{spec.title}]({spec.normative_url}) |
| **Status** | {spec.status} |
| **Target** | {target} |
| **Date** | {ISO-8601 date} |
| **Conformance target** | {e.g. WCAG 2.2 AA} |
| **Overall** | {PASS \| PARTIAL \| FAIL \| ADVISORY ONLY} |

## Scope

What was tested (URLs, routes, components, states, AT assumptions).

## Normative references

- Primary: {spec.normative_url}
- Supplemental: {bulleted related URLs from manifest}

## Summary

2–4 sentences: outcome, blocker count, highest-risk gaps.

## Findings

| ID | Checkpoint / SC | Result | Severity | Evidence | Remediation | Official link |
|----|-----------------|--------|----------|----------|-------------|---------------|
| F-001 | {criterion} | fail | critical | `{selector}` / `file:line` | {fix} | [{SC title}]({exact URL with fragment if possible}) |

### Finding detail (blockers & critical only)

#### F-001 — {short title}

- **Result:** fail
- **Impact:** {who cannot use what}
- **Steps to reproduce:** 1. … 2. …
- **Remediation:** {specific code/markup change}
- **Normative:** [{SC}]({url})

## Passes worth noting

Brief list of strong patterns (helps reviewers prioritize).

## Not tested / N/A

| Item | Reason |
|------|--------|
| {checkpoint} | {no auth / out of scope / blocked} |

## Tooling appendix

| Tool | Output |
|------|--------|
| axe / Lighthouse / manual | `{path-to-raw.json}` |

## Extension criteria (if any)

Criteria merged from project extensions not in core manifest.

---

```
