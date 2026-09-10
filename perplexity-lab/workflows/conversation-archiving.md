# 📦 Conversation Archiving Workflow

**Purpose:** Systematic process for capturing, processing, and integrating Perplexity AI conversations into zenOS.

---

## 🔄 Full Workflow

### Step 1: Research Phase
**Tool:** Perplexity AI  
**Action:** Conduct research session

- Use connected services (GitHub, Drive, Outlook)
- Keep focus on actionable outcomes
- Tag conversations mentally for later categorization

**Pro tip:** Use Perplexity's `/` commands and collections to organize as you go.

---

### Step 2: Capture Phase
**Action:** Export conversation

**Manual Method (Current):**
```bash
# 1. Copy conversation from Perplexity
# 2. Save to perplexity-lab/conversations/
# 3. Use naming convention: YYYY-MM-DD-topic-description.md
```

**Automated Method (Future):**
```bash
# Run capture script
python perplexity-lab/automation/capture-conversation.py --url [perplexity-url]
```

---

### Step 3: Process Phase
**Action:** Extract insights and create tasks

```bash
# 1. Read the conversation
# 2. Identify actionable items
# 3. Create GitHub issues for significant items
# 4. Update zenOS documentation if needed
# 5. Tag conversation with metadata
```

**Metadata to Add:**
```markdown
---
date: 2025-10-24
type: [technical/business/design/general]
tags: [ai, research, promptos, integration]
status: [processed/archived/active]
actionable_items: 5
github_issues: [#123, #124]
related_docs: [/docs/planning/AI_INTEGRATION.md]
---
```

---

### Step 4: Integration Phase
**Action:** Implement insights

- Create branches for code changes
- Update documentation
- Build out new features/plugins
- Close loop with testing

**Git Workflow:**
```bash
# Create feature branch from insights
git checkout -b feature/perplexity-insight-[topic]

# Make changes
# Commit with reference to conversation
git commit -m "feat: [feature] (from perplexity-lab/[conversation-file])"
```

---

### Step 5: Reflection Phase
**Action:** Update the lab

- Mark conversation as processed
- Update templates if workflow improved
- Document lessons learned
- Archive completed items

---

## 🤖 Automation Opportunities

### Current State
- ✅ Manual conversation capture
- ✅ Git-based archiving
- ⏳ Manual insight extraction
- ⏳ Manual task creation

### Future State (Goals)
- 🎯 **API Integration:** Direct Perplexity API access
- 🎯 **Auto-tagging:** AI-powered conversation categorization
- 🎯 **Smart Extraction:** Automated actionable item detection
- 🎯 **GitHub Sync:** Auto-create issues from insights
- 🎯 **MCP Integration:** Tool-level integration with Perplexity
- 🎯 **n8n Workflows:** Visual automation builder
- 🎯 **Voice Commands:** "Hey zenOS, archive this conversation"

---

## 🛠️ Tools & Scripts

### capture-conversation.py (Future)
```python
# Automated conversation capture
# Usage: python capture-conversation.py --url [url]
# Outputs: Formatted markdown in conversations/
```

### extract-insights.py (Future)
```python
# AI-powered insight extraction
# Usage: python extract-insights.py conversations/[file]
# Outputs: Structured insights with actionable items
```

### create-tasks.py (Future)
```python
# Auto-create GitHub issues from insights
# Usage: python create-tasks.py conversations/[file]
# Outputs: GitHub issues with proper tagging
```

---

## 📊 Metrics to Track

- Conversations archived per week
- Actionable items extracted
- GitHub issues created
- Features implemented from insights
- Time from insight to implementation

---

## 🎯 Success Criteria

**A well-processed conversation has:**
- ✅ Clear metadata header
- ✅ Identified actionable items
- ✅ Created GitHub issues (if applicable)
- ✅ Updated relevant docs
- ✅ Linked to related resources
- ✅ Archived in proper location

---

## 🧠 Best Practices

### During Research
- Start with clear objectives
- Use templates for consistency
- Keep conversations focused
- Note integration opportunities

### During Processing
- Process within 24 hours (ADHD-friendly)
- Don't over-analyze - extract and move on
- Create tasks immediately while context is fresh
- Link everything for future reference

### During Integration
- One conversation → one focus area
- Don't try to implement everything at once
- Test and validate insights
- Close the feedback loop

---

## 🚨 Anti-Patterns to Avoid

❌ **Archive Hoarding:** Saving everything without processing  
✅ **Active Processing:** Quick review and extract within 24h

❌ **Analysis Paralysis:** Over-thinking the categorization  
✅ **Quick Decisions:** Tag it, file it, move on

❌ **Broken Links:** Creating tasks without linking to source  
✅ **Full Context:** Always link issues back to conversation

❌ **Orphaned Insights:** Great ideas never implemented  
✅ **Action Bias:** If it's worth capturing, it's worth doing

---

## 📝 Template Usage

Choose the right template:

- **Full Research Session:** Complex multi-query research
- **Quick Capture:** Single question, quick insight
- **Technical Deep Dive:** API/code investigation
- **Business Research:** Market/legal/financial
- **Design Exploration:** UI/UX/aesthetic research

---

## 🔗 Integration Points

### With zenOS Inbox
```bash
# If conversation needs deeper processing
mv perplexity-lab/conversations/[file].md inbox/processing/
```

### With Dex
```bash
# If conversation defines new procedures or models
# Extract to dex/procedures.yaml or models.yaml
```

### With Documentation
```bash
# If conversation updates planning or blueprints
# Reference in docs/planning/ or docs/blueprints/
```

---

*This workflow is a living document - update as process evolves!*
