---
name: a11y-compliance-audit
description: Audits web UIs and markup for WCAG 2.2/3, WAI-ARIA, HTML accessibility, EN 301 549, and cognitive/ND-friendly patterns; emits one markdown report per spec with official normative citations. Use when the user asks for accessibility, a11y, WCAG, ARIA, compliance audit, axe, or per-spec audit reports.
---

# Accessibility compliance audit

Run a **multi-spec audit** and write **one markdown report per spec** under a single output directory. Always cite **official W3C/WAI/ETSI** sources in each finding — never paraphrase success criteria from memory without linking the normative URL.

## Quick start

1. **Scope** — Confirm target: URL(s), repo path(s), component name(s), conformance target (default **WCAG 2.2 AA**).
2. **Compose manifest** — Merge core + extensions (expandable pipe). Resolve skill root once (repo **or** mirrored `~/.cursor/skills`):

   ```bash
   A11Y_SKILL="$(bash dex/04-scripts/sync-cursor-skills.sh --print a11y-compliance-audit)"
   python "$A11Y_SKILL/scripts/merge-manifest.py" \
     --target "<path-or-url>" \
     --output-dir "a11y-reports/<audit-slug>" \
     --extension path/to/extra-rules.yaml \
     --extension path/to/team-a11y.md
   ```

   Outside dev-master, after a prior sync: `A11Y_SKILL="$HOME/.cursor/skills/a11y-compliance-audit"`.

3. **Audit** — For each spec in the merged manifest: inspect target, map findings to criterion IDs, record evidence (selector, screenshot path, or file:line).
4. **Emit reports** — One file per spec: `{output-dir}/{spec.id}.md` using [report-template.md](report-template.md).
5. **Summary** — Write `{output-dir}/README.md` with rollup status, blockers, and links to all spec reports.

If automated tools exist in the project (`axe`, Playwright `@axe-core/playwright`, Lighthouse), run them first and **fold results into** the relevant spec reports — do not replace manual WCAG/ARIA reasoning with tool output alone.

## Expandable piping (extensions)

| Layer | Source | Role |
|-------|--------|------|
| **Core** | [core-manifest.yaml](core-manifest.yaml) | Always-on specs + official doc URLs + default checkpoints |
| **Extensions** | User-supplied `.yaml` / `.md` | Extra criteria, product rules, locale law, design-system tokens |
| **Territory** | Target codebase | Components, routes, framework a11y APIs |

**Extension YAML** (merge into manifest `specs[].checkpoints` or add new `specs[]` entries):

```yaml
specs:
  - id: design-system-acme
    title: "Acme DS — focus & motion"
    normative_url: "https://design.acme.example/a11y"
    checkpoints:
      - id: acme-focus-ring
        summary: "Focus ring ≥ 2px, contrast ≥ 3:1 against adjacent colors"
        severity: serious
```

**Extension markdown** — Use YAML frontmatter + bullet checkpoints; paths ending in `.md` are parsed by `merge-manifest.py` when frontmatter contains `specs:` or `checkpoints:`.

See [extensions/README.md](extensions/README.md) for examples.

## Audit workflow (per spec)

```
Task Progress:
- [ ] Manifest composed (core + extensions)
- [ ] Target inventoried (pages, components, states: default/hover/focus/error)
- [ ] Automated scan captured (if available)
- [ ] Manual review against spec checkpoints
- [ ] One {spec.id}.md written with official links per finding
- [ ] README.md rollup written
```

For each **checkpoint** in the manifest:

1. State **pass / fail / partial / not applicable / not tested**.
2. On fail/partial: **finding** (what breaks), **impact** (who is affected), **remediation** (concrete fix), **evidence**, **normative link** (exact criterion or pattern URL from manifest).
3. Prefer criterion IDs (`1.4.3`, `2.4.7`, `toolbar` pattern) in headings and tables.

## Core specs (always include unless manifest `--specs` filter excludes)

Loaded from [core-manifest.yaml](core-manifest.yaml):

| ID | Report file | Normative basis |
|----|-------------|-----------------|
| `wcag-22` | `wcag-22.md` | WCAG 2.2 (W3C Rec) — default level AA |
| `wcag-3` | `wcag-3.md` | WCAG 3.0 draft — gap/readiness only (not legal baseline) |
| `wai-aria-12` | `wai-aria-12.md` | WAI-ARIA 1.2 |
| `aria-apg` | `aria-apg.md` | ARIA Authoring Practices Guide patterns |
| `html-a11y` | `html-a11y.md` | HTML + accessibility mapping (native semantics first) |
| `en-301-549` | `en-301-549.md` | EN 301 549 V3.2.1 (EU ICT accessibility) |
| `cognitive-nd` | `cognitive-nd.md` | Cognitive / neurodivergent-friendly heuristics (informative; ties to WCAG 2.2 SC where applicable) |

Optional core add-ons (enable via extension or `--specs`):

- `atag-20` — authoring tool accessibility
- `section-508` — US federal (maps to WCAG 2.0/2.2 via 508 Refresh)

## Official documentation (canonical URLs)

Always use these as primary references in reports (versions pinned in core-manifest):

- WCAG 2.2: https://www.w3.org/TR/WCAG22/
- WCAG 3.0 (draft): https://www.w3.org/TR/wcag-3.0/
- Understanding WCAG 2.2: https://www.w3.org/WAI/WCAG22/Understanding/
- Techniques for WCAG 2.2: https://www.w3.org/WAI/WCAG22/Techniques/
- WAI-ARIA 1.2: https://www.w3.org/TR/wai-aria-1.2/
- ARIA in HTML: https://www.w3.org/TR/html-aria/
- APG: https://www.w3.org/WAI/ARIA/apg/
- EN 301 549: https://www.etsi.org/deliver/etsi_en/301500_301599/301549/
- Web Accessibility Laws & Policies: https://www.w3.org/WAI/policies/

When a criterion moved or is draft-only (WCAG 3), label severity as **advisory** and state clearly it is not yet a W3C Recommendation.

## Common suspects checklist (spot-check every audit)

Cross-cut failures — assign each to the **most specific** spec report:

- Missing or duplicate accessible name (`aria-label`, `aria-labelledby`, native label)
- Keyboard trap or unreachable control
- Focus not visible or focus order illogical
- Color-only state / insufficient contrast (text + UI components + focus indicator)
- Missing language (`lang`), title, or page heading structure
- Live region misuse (`aria-live` polite/assertive spam)
- Incorrect role or redundant ARIA on native elements
- Custom widget without APG keyboard model
- Motion without `prefers-reduced-motion` respect
- Form errors not programmatically associated (`aria-describedby`, `aria-invalid`)
- Touch target too small (mobile); reflow broken at 320px width
- Autoplay audio/video without user control
- Time limits without extension/warning
- Cognitive load: wall of text, no chunking, no skip link, surprise context shifts

## Tooling (optional, project-dependent)

```bash
# Playwright + axe (if installed in project)
npx playwright test --grep @a11y

# axe CLI (if @axe-core/cli present)
npx axe <url> --save a11y-reports/<audit-slug>/axe-raw.json

# Lighthouse accessibility category
npx lighthouse <url> --only-categories=accessibility --output=json
```

Attach raw tool JSON paths in the relevant spec report appendix.

## Output layout

```
a11y-reports/<audit-slug>/
├── README.md              # rollup
├── manifest.merged.yaml   # composed pipe (written by merge script)
├── wcag-22.md
├── wcag-3.md
├── wai-aria-12.md
├── aria-apg.md
├── html-a11y.md
├── en-301-549.md
└── cognitive-nd.md
```

## Severity scale (use consistently)

| Label | Meaning |
|-------|---------|
| **blocker** | Illegal/barrier risk; blocks task completion for AT users |
| **critical** | WCAG A/AA failure on primary flow |
| **serious** | Major friction; workaround painful |
| **moderate** | Secondary flow or edge state |
| **minor** | Best practice / draft WCAG 3 advisory |

## Additional resources

- Report body template: [report-template.md](report-template.md)
- Core pipe definition: [core-manifest.yaml](core-manifest.yaml)
- Extension examples: [extensions/README.md](extensions/README.md)
