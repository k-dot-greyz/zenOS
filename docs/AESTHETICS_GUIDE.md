# 🎨 Neuro-Spicy Aesthetics & Documentation Guide

This document outlines the "look and feel" of the Neuro-Spicy DevKit. The goal is not to be restrictive, but to create a consistent, low-friction experience for both users and contributors. For us, good aesthetics are a core feature, directly supporting accessibility and reducing cognitive load.

## 🎯 Core Philosophy: Aesthetics as a Feature

1. **Clarity Over Clutter**: Every visual element should serve a purpose. If it doesn't clarify, it's clutter.
2. **Consistency Reduces Load**: By using the same patterns everywhere, we make the project predictable and easier to navigate.
3. **Information Hierarchy is Key**: Guide the user's eye to what's most important using headers, colors, and emojis.
4. **Celebrate Success**: Use visual cues (colors, summaries) to provide positive feedback and a sense of accomplishment.

## 🎨 Brand Identity

### Logo

The official logo is a simple, clean, text-based design. It's designed to be easily displayed in a terminal or markdown file.

```
🧠 Neuro-Spicy DevKit
═══════════════════════════════════════
Lean • Mean • Accessible • Cross-Platform
```

### Color Palette (for Script Output)

All scripts should use the following color scheme for terminal output. This is already implemented in scripts like health-check-core.sh.

| Color | ANSI Code | Usage |
| :---- | :---- | :---- |
| **Magenta** | \033[0;35m | Main headers and titles |
| **Cyan** | \033[0;36m | Section headers and informational messages |
| **Green** | \033[0;32m | Success messages, confirmations, "OK" |
| **Yellow** | \033[1;33m | Warnings, suggestions, user prompts |
| **Red** | \033[0;31m | Error messages, failures, "Not Found" |
| **White/NC** | \033[0m (No Color) | Standard text, details |

### Emoji Legend

Emojis are used as a visual shorthand to quickly convey the purpose of a section or message.

| Emoji | Meaning | Usage Example |
| :---- | :---- | :---- |
| 🧠 | Core Philosophy, Neuro-Spicy Concepts | 🧠 Neuro-Spicy Philosophy |
| 🚀 | Quick Start, Deployment, Performance | 🚀 Quick Start |
| 🔧 | Configuration, Scripts, Tooling | 🔧 Core Scripts |
| 🎯 | Goals, Principles, Focus | 🎯 Core Principles |
| 📚 | Documentation, Guides, Learning | 📚 Documentation Style Guide |
| ✅ | Success, Complete, Passed | ✅ Git: Installed |
| ❌ | Error, Failed, To-Do | ❌ Python: Not Installed |
| 💡 | Tip, Suggestion, Idea | 💡 Run health-check.sh --fix |
| 🔍 | Checking, Analysis, Health Check | 🔍 Checking Git... |

## 📚 Documentation Style Guide

### General File Structure (.md)

All markdown files in the /docs directory should follow this basic structure.

```markdown
# 🧠 [Emoji] Page Title

> A brief, one-sentence description of what this document is about. Keep it concise.

## 🎯 Section 1 Title

Text, code blocks, and lists for the first major topic.

### Sub-section (if needed)

Deeper details.

## 🚀 Section 2 Title

Text, code blocks, and lists for the second major topic.

---

*Optional closing thought or summary.*
```

## 🔧 Script Output Style Guide

The terminal is our UI. It should be clean, informative, and satisfying to use.

### Script Output Template (Bash)

This template provides a standardized way to structure shell scripts for consistent output.

```bash
#!/bin/bash

# --- Color Definitions ---
GREEN='\033[0;32m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# --- Logging Functions ---
log_info() {
    echo -e "${CYAN}INFO: $1${NC}"
}
log_success() {
    echo -e "${GREEN}SUCCESS: $1${NC}"
}
log_warning() {
    echo -e "${YELLOW}WARNING: $1${NC}"
}
log_error() {
    echo -e "${RED}ERROR: $1${NC}"
}

# --- Header Function ---
print_header() {
    echo -e "${MAGENTA}🧠 $1${NC}"
    echo -e "${MAGENTA}======================================${NC}"
    echo ""
}

# --- Main Execution ---
print_header "My Awesome Script"

log_info "Starting process..."

# TODO: Add a spinner for long-running tasks
sleep 2 # Simulating work

log_success "Process complete!"

echo ""
echo -e "${CYAN}Next steps:${NC}"
echo "1. Do the next thing."
```

### Script Output Template (PowerShell)

```powershell
# --- Color Definitions ---
$Green = "Green"
$Cyan = "Cyan"
$Magenta = "Magenta"
$Yellow = "Yellow"
$Red = "Red"
$White = "White"

# --- Logging Functions ---
function Write-Info {
    param([string]$Message)
    Write-Host "INFO: $Message" -ForegroundColor $Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "SUCCESS: $Message" -ForegroundColor $Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "WARNING: $Message" -ForegroundColor $Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "ERROR: $Message" -ForegroundColor $Red
}

# --- Header Function ---
function Write-Header {
    param([string]$Title)
    Write-Host "🧠 $Title" -ForegroundColor $Magenta
    Write-Host "======================================" -ForegroundColor $Magenta
    Write-Host ""
}

# --- Main Execution ---
Write-Header "My Awesome Script"

Write-Info "Starting process..."

# TODO: Add a spinner for long-running tasks
Start-Sleep -Seconds 2

Write-Success "Process complete!"

Write-Host ""
Write-Host "Next steps:" -ForegroundColor $Cyan
Write-Host "1. Do the next thing."
```

## 🎯 Implementation Checklist

- [ ] Update all existing scripts to use the color palette
- [ ] Standardize emoji usage across all documentation
- [ ] Create consistent header functions for all scripts
- [ ] Add demo GIF to README
- [ ] Update all markdown files to follow the style guide
- [ ] Create CONTRIBUTING.md with style guidelines

---

*"Good aesthetics are not just pretty - they're functional."* 🎨✨
