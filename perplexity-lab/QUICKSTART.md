# 🚀 Perplexity Lab Quick Start

**Get started in 2 minutes!**

---

## 📋 What You Got

A fully structured AI research workspace with:
- ✅ **Conversation archiving system**
- ✅ **Templates for different research types**
- ✅ **Workflow documentation**
- ✅ **Integration with zenOS**
- ✅ **Automation framework (ready for your scripts)**

---

## 🎯 Quick Actions

### Archive a Conversation
```bash
# 1. Copy your Perplexity conversation
# 2. Paste into a new file:
vim perplexity-lab/conversations/2025-10-24-my-research.md

# 3. Add metadata (copy from templates if needed)
```

### Start a Research Session
```bash
# Use a template:
cp perplexity-lab/templates/research-session-template.md \
   perplexity-lab/conversations/2025-10-24-new-topic.md

# Fill it out as you research
```

### Quick Capture
```bash
# For rapid insights:
cp perplexity-lab/templates/quick-capture-template.md \
   perplexity-lab/conversations/2025-10-24-quick-insight.md
```

---

## 📁 Structure at a Glance

```text
perplexity-lab/
├── README.md                    ← Overview and philosophy
├── QUICKSTART.md               ← This file
├── INTEGRATION_NOTES.md        ← How to integrate with zenOS
│
├── conversations/              ← Your archived research
│   ├── INDEX.md               ← Master index (update this!)
│   ├── 2025-10-02-perplexity-lab-setup.md
│   └── 2025-10-01-gemini-context-stub.md
│
├── templates/                  ← Copy these for new sessions
│   ├── research-session-template.md
│   └── quick-capture-template.md
│
├── workflows/                  ← Process documentation
│   └── conversation-archiving.md
│
└── automation/                 ← Future scripts
    └── README.md
```

---

## 🔥 Most Common Tasks

### 1. Just finished a research session
```bash
# Quick method:
cd perplexity-lab/conversations
vim 2025-10-24-topic.md
# Paste conversation, add metadata, save

# Update index:
vim INDEX.md
# Add entry for new conversation
```

### 2. Need to do structured research
```bash
# Start with template:
cp templates/research-session-template.md \
   conversations/2025-10-24-structured-research.md

# Fill out as you go:
vim conversations/2025-10-24-structured-research.md
```

### 3. Quick insight to capture
```bash
# Use quick capture:
cp templates/quick-capture-template.md \
   conversations/2025-10-24-insight.md

# Fill in the blanks, done!
```

### 4. Want to find past research
```bash
# Search all conversations:
grep -r "search term" perplexity-lab/conversations/

# Or use ripgrep:
rg "search term" perplexity-lab/conversations/
```

---

## 📊 Workflow Summary

```text
1. Research in Perplexity
   ↓
2. Archive to conversations/
   ↓
3. Extract action items
   ↓
4. Create GitHub issues / zenOS tasks
   ↓
5. Implement in zenOS
   ↓
6. Update conversation with results
   ↓
7. Mark as completed in INDEX
```

---

## 🎨 Tips

### ADHD-Friendly
- **Capture first, organize later** - Just get it down
- **Use quick-capture for speed** - Full template when you have energy
- **Set a reminder** - Process within 24h while fresh
- **Don't over-think tags** - Good enough > perfect

### For Maximum Value
- **Link everything** - Connect conversations to code/issues
- **Close the loop** - Always update with implementation status
- **Track time** - Insight → shipped time is a fun metric
- **Share wins** - Celebrate when lab research becomes reality

### Integration
- **Reference in commits** - `git commit -m "feat: xyz (from perplexity-lab/...)"`
- **Link in docs** - Always cite your research source
- **Create issues** - Turn insights into trackable work
- **Update INDEX** - Keep the master list current

---

## 🚀 Next Level

### When ready for automation:
1. Check `automation/README.md`
2. Write capture scripts
3. Set up GitHub Actions
4. Build n8n workflows
5. Integrate with MCP

### When ready for plugins:
1. Review `INTEGRATION_NOTES.md`
2. Design `zen research` commands
3. Build perplexity-lab plugin
4. Package for others to use

---

## ❓ Questions?

- **Full docs:** See `README.md`
- **Workflows:** See `workflows/conversation-archiving.md`
- **Integration:** See `INTEGRATION_NOTES.md`
- **Templates:** See `templates/`

---

## 💡 Remember

**Every conversation is an asset. Every insight is capital. The lab is your second brain.**

Now go research something interesting! 🧠✨
