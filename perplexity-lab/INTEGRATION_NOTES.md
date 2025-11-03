# 🔗 Perplexity Lab → zenOS Integration Notes

**Created:** 2025-10-24  
**Status:** Active Development  

---

## 🎯 Integration Vision

The Perplexity Lab isn't a standalone project—it's a **Product Engine** component that feeds directly into zenOS development. Every conversation here should translate into actionable zenOS improvements.

---

## 🔄 Integration Points

### 1. With zenOS Inbox System
**Location:** `/workspace/inbox/`

**Flow:**
```text
Perplexity Research → Lab Conversations → Extract Insights → zenOS Inbox → Implementation
```

**When to use inbox:**
- Conversation needs deeper processing
- Multiple zenOS components affected
- Requires team discussion or review
- Uncertain about implementation approach

**Command:**
```bash
# Move conversation to inbox for deeper processing
mv perplexity-lab/conversations/[file].md inbox/processing/
```

---

### 2. With Pokedex System
**Location:** `/workspace/pokedex/`

**Flow:**
```text
Research on procedures/models → Extract patterns → Update pokedex YAML files
```

**When to use pokedex:**
- Conversation defines new workflows
- AI model configuration insights
- Procedure or process documentation
- Template patterns discovered

**Files to update:**
- `pokedex/procedures.yaml` - Workflow procedures
- `pokedex/models.yaml` - AI model configurations

---

### 3. With Documentation
**Location:** `/workspace/docs/`

**Flow:**
```text
Technical/planning research → Update relevant docs → Link back to source
```

**Documentation targets:**
- `docs/planning/` - Roadmaps, implementation plans
- `docs/blueprints/` - Architecture and design plans
- `docs/guides/` - User guides and quickstarts
- `docs/AI_INSTRUCTIONS.md` - AI context and instructions

**Always include source:**
```markdown
> Research from: perplexity-lab/conversations/2025-10-24-topic.md
```

---

### 4. With Plugin System
**Location:** `/workspace/zen/plugins/` & `/workspace/examples/sample-plugin/`

**Flow:**
```text
Research plugin concepts → Prototype in lab → Develop in zen/plugins/ → Package for distribution
```

**Perplexity Lab could become a plugin itself:**
```yaml
# zenos-plugin.yaml
name: perplexity-lab
version: 1.0.0
description: AI research workspace with automated archiving
commands:
  - zen research archive
  - zen research extract
  - zen research search
```

---

### 5. With CLI Tools
**Location:** `/workspace/zen/cli.py` & `/workspace/tools/`

**Flow:**
```text
Identify workflow friction → Research better tools → Implement CLI enhancement
```

**Potential commands:**
```bash
zen research start [topic]      # Start new research session
zen research archive [url]      # Archive conversation
zen research extract [file]     # Extract insights
zen research search [query]     # Search past conversations
zen lab stats                   # Show lab statistics
```

---

### 6. With Automation (n8n, GitHub Actions)
**Location:** `/workspace/n8n/` & `.github/workflows/`

**Flow:**
```text
Research automation ideas → Document in lab → Implement in n8n/GitHub Actions
```

**Automation targets:**
- Auto-archive conversations on commit
- Create GitHub issues from insights
- Send Discord/Slack notifications
- Update project boards

---

### 7. With MCP Integration
**Location:** `/workspace/mcp-config/`

**Flow:**
```text
Research MCP tools → Configure in mcp-config/ → Use in Perplexity sessions
```

**MCP tool ideas for Perplexity:**
- `perplexity_search` - Direct search tool
- `conversation_archive` - Save current conversation
- `insight_extractor` - AI-powered extraction

---

## 🚀 Quick Integration Workflows

### From Lab to Implementation
```bash
# 1. Conduct research in Perplexity
# 2. Archive to lab
cp [conversation] perplexity-lab/conversations/YYYY-MM-DD-topic.md

# 3. Extract insights
python perplexity-lab/automation/extract-insights.py [file]

# 4. Create implementation branch
git checkout -b feature/lab-insight-[topic]

# 5. Implement in zenOS
# ... make changes ...

# 6. Commit with reference
git commit -m "feat: [feature] (from perplexity-lab/conversations/[file])"

# 7. Update conversation with results
echo "## Implementation Results" >> [conversation-file]
echo "- Implemented in: [PR or commit]" >> [conversation-file]
echo "- Status: Completed" >> [conversation-file]
```

---

### From Lab to Documentation
```bash
# 1. Research produces documentation insights
# 2. Update relevant docs
vim docs/planning/[relevant-file].md

# 3. Add source citation
echo "> Research source: perplexity-lab/conversations/[file].md" >> [doc-file]

# 4. Update conversation index
vim perplexity-lab/conversations/INDEX.md
```

---

### From Lab to Plugin
```bash
# 1. Research identifies plugin opportunity
# 2. Create plugin structure
mkdir -p zen/plugins/new-plugin
cp examples/sample-plugin/zenos-plugin.yaml zen/plugins/new-plugin/

# 3. Develop plugin
# ... implement ...

# 4. Document in conversation
echo "## Plugin Created: new-plugin" >> [conversation-file]
```

---

## 📊 Metrics & Tracking

### Success Metrics
- **Conversation → Implementation time:** Aim for < 7 days
- **Action item completion rate:** Target 80%+
- **GitHub issues created:** Track quality, not just quantity
- **Features shipped from insights:** Monthly count

### Track in Conversations
Always include outcome tracking:
```markdown
## Implementation Status

- **Created:** 2025-10-24
- **First Action:** 2025-10-25 (GitHub issue #123)
- **First Commit:** 2025-10-26 (feat: xyz)
- **Merged:** 2025-10-28 (PR #124)
- **Shipped:** 2025-10-30

**Time to Ship:** 6 days ✅
```

---

## 🎨 Philosophy

### "Work as Play"
Research should be fun. The lab removes friction between insight and implementation. No guilt about "research rabbit holes"—they're features, not bugs.

### Personal Sovereignty
Own your research. Own your insights. Own your knowledge graph. The lab is YOUR second brain, not scattered across platforms.

### Neurodivergent-Friendly
- **Clear process:** No ambiguity in workflow
- **Quick capture:** Get it down fast, process later
- **No pressure:** Research when inspired, implement when ready
- **Hyperfocus-friendly:** Deep dives are encouraged

---

## 🔮 Future Vision

### Phase 1: Foundation (✅ Current)
- Manual archiving
- Template system
- Basic workflow

### Phase 2: Automation
- API integrations
- Auto-extraction
- GitHub sync

### Phase 3: Intelligence
- AI-powered insights
- Conversation linking
- Knowledge graph

### Phase 4: Integration
- Full MCP support
- Voice activation
- Real-time collaboration

### Phase 5: Evolution
- Lab becomes a standalone product
- Multi-user support
- Marketplace for research templates

---

## 🧠 Remember

**Every conversation is an asset.** The lab turns ephemeral chat into permanent knowledge capital. That's the game.

---

*Integration is where the magic happens—research meets reality* ✨
