---
dex_id: "0x7E:0x02"
dex_type: "documentation"
midi_2_0_context:
  resource_type: "Documentation"
  property_exchange_id: "urn:zenos:runtime:dex-readme"
legacy_map:
  midi_1_0_bank: 126
  midi_1_0_prog: 2
status: "active"
tags: ["documentation", "dex", "zenos", "runtime"]
---

# zenOS dex integration

this directory implements the dex protocol for zenOS runtime resources.

## quick start

```bash
# generate/update the dex index
python3 dex/7E-01_dex-yoinker.py

# view the index
cat dex/7E-00_dex-index.md
```

## what's indexed

the yoinker scans zenOS for files with MIDI 2.0 frontmatter:
- zen/ modules and utilities
- scripts and tools
- documentation with dex annotations
- configuration files
- anything with a `dex_id` in frontmatter

## relationship to dev-master

**dev-master/dex/** - protocol specification and infrastructure procedures  
**zenOS/dex/** - runtime resources and operational catalog

both use the same protocol, different domains:
- dev-master: how to build (0x7F kernel, 0x7E ops, 0x7D dev)
- zenOS: what's running (0x7C agents, 0x7B audio, runtime resources)

## protocol reference

see the full dex protocol spec in dev-master (private repository):
- dex protocol spec (`dex/7F-7F_dex-protocol-spec.md`)
- architecture doc (`dex/7E-02_dex-architecture.md`)

## usage

### cli integration (future)
```bash
zen dex list                    # list all dex entries
zen dex get 0x7C:0x01          # get specific entry
zen dex search --tag agents    # search by tag
zen dex sync                    # regenerate index
```

### python api
```python
from zen.utils.dex import DexReader

dex = DexReader()
agents = dex.by_bank(0x7C)  # all agent resources
spec = dex.get("0x7F:0x7F")  # specific entry
```

---

*runtime resources, cataloged and discoverable*

