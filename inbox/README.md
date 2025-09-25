# 📥 zenOS Inbox System

The zenOS inbox is where all incoming items get processed before being integrated into the system.

## 📁 Structure

- **`incoming/`** - Raw incoming items (tools, context, ideas)
- **`processing/`** - Items currently being worked on
- **`processed/`** - Completed and archived items
- **`tools/`** - Incoming tools/plugins to be integrated
- **`context/`** - Context updates and conversations
- **`ideas/`** - Random ideas and concepts

## 🔄 Processing Workflow

1. **Incoming** → Items land here automatically
2. **Processing** → Move items here when working on them
3. **Processed** → Archive completed items here

## 🎯 Types of Items

- 🔧 **Tools/Plugins** - New GitHub repos with zenos-plugin.yaml
- 📝 **Context** - Conversation updates, new procedures
- 💡 **Ideas** - Random thoughts, feature requests
- 🐛 **Issues** - Bug reports, problems to solve
- 📊 **Analytics** - Usage data, performance metrics

## 🚀 Quick Commands

```bash
# Process a new tool
zen receive add tool "https://github.com/user/tool-repo"

# Add a new idea
zen receive add idea "Voice-controlled plugin management"

# Process context update
zen receive add context "New conversation about mobile UI"

# List all items
zen receive list

# Move item to processing
zen receive move item-id processing
```

## 📋 Status Tracking

Each item gets a status:
- `new` - Just arrived
- `processing` - Being worked on
- `review` - Needs review
- `integrated` - Successfully integrated
- `rejected` - Not suitable
- `archived` - Completed and stored

---

**The inbox keeps zenOS organized and ensures nothing gets lost!** 🧘✨
