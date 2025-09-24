# 🎨 Neuro-Spicy Quick Reference

> **Quick access to the most important information for contributors and users**

## 🎯 Core Philosophy

**"Aesthetics as a Feature"** - Good aesthetics aren't just pretty, they're functional. They directly support accessibility and reduce cognitive load.

## 🎨 Color Palette (Terminal Output)

| Color | ANSI Code | Usage |
| :---- | :---- | :---- |
| **Magenta** | `\033[0;35m` | Main headers and titles |
| **Cyan** | `\033[0;36m` | Section headers and info |
| **Green** | `\033[0;32m` | Success messages |
| **Yellow** | `\033[1;33m` | Warnings and prompts |
| **Red** | `\033[0;31m` | Error messages |

## 📝 Emoji Legend

| Emoji | Meaning | Example |
| :---- | :---- | :---- |
| 🧠 | Core Philosophy | 🧠 Neuro-Spicy Concepts |
| 🚀 | Quick Start | 🚀 Installation |
| 🔧 | Configuration | 🔧 Scripts & Tools |
| 🎯 | Goals & Focus | 🎯 Core Principles |
| 📚 | Documentation | 📚 Guides |
| ✅ | Success | ✅ Completed |
| ❌ | Error/Failed | ❌ Not Found |
| 💡 | Tips | 💡 Suggestions |
| 🔍 | Checking | 🔍 Health Check |

## 🔧 Script Template (Bash)

```bash
#!/bin/bash

# --- Color Definitions ---
GREEN='\033[0;32m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# --- Logging Functions ---
log_info() { echo -e "${CYAN}INFO: $1${NC}"; }
log_success() { echo -e "${GREEN}SUCCESS: $1${NC}"; }
log_warning() { echo -e "${YELLOW}WARNING: $1${NC}"; }
log_error() { echo -e "${RED}ERROR: $1${NC}"; }

# --- Header Function ---
print_header() {
    echo -e "${MAGENTA}🧠 $1${NC}"
    echo -e "${MAGENTA}======================================${NC}"
    echo ""
}
```

## 📚 Documentation Structure

```markdown
# 🧠 [Emoji] Page Title

> Brief description of what this document is about.

## 🎯 Section 1 Title

Content here.

## 🚀 Section 2 Title

More content.

---

*Optional closing thought.*
```

## 🎯 Quick Commands

```bash
# Health check
./scripts/health-check-core.sh

# Interactive setup
./init.sh          # Linux/macOS
.\init.ps1          # Windows

# Make scripts executable
chmod +x scripts/*.sh
```

---

**For complete details, see [AESTHETICS_GUIDE.md](AESTHETICS_GUIDE.md)** 📚✨
