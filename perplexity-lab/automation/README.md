# 🤖 Perplexity Lab Automation

**Status:** Planned  
**Goal:** Fully automated conversation capture, processing, and integration

---

## 🎯 Automation Goals

### Phase 1: Basic Scripts (Current)
- [ ] `capture-conversation.py` - Manual URL input, formatted output
- [ ] `extract-insights.py` - Parse markdown, extract action items
- [ ] `create-github-issues.py` - Auto-create issues from insights

### Phase 2: API Integration
- [ ] Perplexity API client
- [ ] Auto-detect new conversations
- [ ] Scheduled archiving (daily/weekly)

### Phase 3: AI-Powered Processing
- [ ] LLM-based insight extraction
- [ ] Smart categorization and tagging
- [ ] Automated task prioritization

### Phase 4: Full Integration
- [ ] MCP tool integration
- [ ] n8n workflow automation
- [ ] Voice-activated archiving
- [ ] Slack/Discord notifications

---

## 📁 Script Stubs

### capture-conversation.py
```python
#!/usr/bin/env python3
"""
Capture Perplexity conversation and format for archiving.

Usage:
    python capture-conversation.py --url [perplexity-url]
    python capture-conversation.py --clipboard
"""

# TODO: Implement
```

### extract-insights.py
```python
#!/usr/bin/env python3
"""
Extract actionable insights from archived conversation.

Usage:
    python extract-insights.py conversations/[file].md
"""

# TODO: Implement with LLM for smart extraction
```

### create-github-issues.py
```python
#!/usr/bin/env python3
"""
Auto-create GitHub issues from conversation insights.

Usage:
    python create-github-issues.py conversations/[file].md
"""

# TODO: Use GitHub API
```

---

## 🔗 Integration Ideas

### n8n Workflow
- Webhook trigger when conversation is saved
- Parse markdown for action items
- Create GitHub issues automatically
- Send notification to Discord/Slack
- Update project board

### GitHub Actions
- On push to `perplexity-lab/conversations/`
- Validate markdown format
- Auto-tag conversation
- Create issues if flagged
- Update conversation index

### MCP Tools
- `perplexity.archive` - Save current conversation
- `perplexity.extract` - Get insights from conversation
- `perplexity.integrate` - Create tasks and issues

---

## 📊 Future Tools

- **Smart Tagging:** AI categorizes conversations automatically
- **Duplicate Detection:** Finds similar past conversations
- **Trend Analysis:** Identifies research patterns over time
- **Knowledge Graph:** Maps relationships between conversations
- **Auto-summarization:** TL;DR for long sessions

---

*Automation makes the workflow disappear - that's the goal!*
