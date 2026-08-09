# 🚀 Dev Environment Setup - Cheat Sheet

## **One-Command Setup (Any Environment)**
```bash
git clone https://github.com/k-dot-greyz/zenOS.git && cd zenOS && python setup.py
```

## **Something broken? Diagnose first**
```bash
make doctor          # env-doctor.sh — OS/shell/tooling/git/creds discovery, read-only
python setup.py --validate-only   # zenOS-specific: Python 3.14 floor, pip-audit
```
See `CLAUDE.md`'s "Environment auto-healing protocol" for the full flow.

## **Essential Commands**
```bash
# Validation only
python setup.py --validate-only

# Specific phases
python setup.py --phase git_setup
python setup.py --phase mcp_setup

# Automated setup
python setup.py --unattended
```

## **Git Workflow**
```bash
# Safe commits
gcommit "feat" "add feature" "description"
gfeat "add feature"
gfix "fix bug"

# Common operations
gs          # git status
ga          # git add
gl          # git log --oneline -10
gp          # git push
gpu         # git pull
```

## **Platform-Specific**

### **Windows**
```powershell
winget install Git.Git Python.Python.3.11 OpenJS.NodeJS
```

### **Linux/macOS**
```bash
# Ubuntu/Debian
sudo apt install git python3 python3-pip nodejs

# macOS
brew install git python node
```

### **Termux (Android)**
```bash
pkg update && pkg upgrade
pkg install git python nodejs
```

## **Troubleshooting**
```bash
# Git hanging
git config --global core.editor "code --wait"

# Missing user config
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Python issues
pip install --upgrade pip
pip install -r requirements.txt

# Node issues
nvm install --lts
nvm use --lts
```

## **Environment Switching**
```bash
# Save work
git add . && git commit -m "wip: save work" && git push

# On new machine
git clone <repo> && cd <repo> && python setup.py --unattended
```

---
**Bookmark this! Your anchor point for all dev environment setups.** 🎯
