# Audit extensions

Drop extension files here or pass arbitrary paths to `merge-manifest.py --extension`.

## YAML extension

```yaml
# extensions/example-product.yaml
specs:
  - id: product-karaoke-toolbar
    title: "Product — karaoke edit toolbar"
    normative_url: https://www.w3.org/WAI/ARIA/apg/patterns/toolbar/
    checkpoints:
      - id: toolbar-roving-tabindex
        summary: "Roving tabindex; Home/End; arrow keys per APG toolbar"
        severity: critical
      - id: stamp-shortcut
        summary: "Stamp action exposed in accessible name and aria-keyshortcuts"
        severity: serious
```

## Markdown extension (frontmatter)

```markdown
---
specs:
  - id: latvia-public-sector
    title: "LV — Cabinet Reg. 445 alignment"
    normative_url: https://www.w3.org/WAI/policies/
    checkpoints:
      - id: accessibility-statement
        summary: "Published accessibility statement with contact + enforcement"
        severity: serious
---

Additional prose for auditors: map EN 301 549 clauses cited in procurement docs.
```

## Merge

```bash
python ../scripts/merge-manifest.py \
  --output-dir ../../a11y-reports/demo \
  --target ./src \
  --extension ./example-product.yaml
```

Merged manifest is written to `{output-dir}/manifest.merged.yaml`.
