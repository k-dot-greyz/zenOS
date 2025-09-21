# 🚀 Development Environment Setup Guide

**Your One Anchor Point for All Development Setups**

This guide consolidates all the best practices from `promptOS`, `mcp-config`, and `zenOS` into a single, comprehensive reference for setting up development environments anywhere.

## 🎯 Quick Reference

### **One-Command Setup (Any Environment)**
```bash
# Clone and setup zenOS (includes everything)
git clone https://github.com/kasparsgreizis/zenOS.git && cd zenOS && python setup.py

# Or if you already have zenOS
cd zenOS && python setup.py
```

### **Essential Commands Cheat Sheet**
```bash
# Environment validation
python setup.py --validate-only

# Specific setup phases
python setup.py --phase git_setup
python setup.py --phase mcp_setup

# Full automated setup
python setup.py --unattended
```

## 📋 Complete Setup Checklist

### **Phase 1: Environment Detection**
- [ ] **OS Detection**: Windows, Linux, macOS, Termux
- [ ] **Shell Detection**: PowerShell, Bash, Zsh, CMD
- [ ] **Python Version**: 3.7+ (3.8+ recommended)
- [ ] **Git Availability**: Git installed and configured
- [ ] **Node.js**: For MCP servers (optional but recommended)
- [ ] **Internet Connectivity**: For package installation

### **Phase 2: Git Setup**
- [ ] **Repository Initialization**: `git init` if needed
- [ ] **User Configuration**: Name and email set
- [ ] **Gitignore Creation**: Comprehensive .gitignore for project type
- [ ] **Cleanup**: Remove unwanted tracked files
- [ ] **Initial Commit**: Setup changes committed
- [ ] **Git Aliases**: Development shortcuts configured

### **Phase 3: MCP Setup** (Optional)
- [ ] **Node.js Installation**: LTS version recommended
- [ ] **MCP Servers**: Global installation of required servers
- [ ] **Configuration Linking**: Symlinks to central config
- [ ] **Health Checks**: Verify MCP servers working

### **Phase 4: Project Dependencies**
- [ ] **Python Dependencies**: `pip install -r requirements.txt`
- [ ] **Node Dependencies**: `npm install` (if applicable)
- [ ] **System Packages**: Platform-specific requirements
- [ ] **Environment Variables**: API keys, paths, etc.

### **Phase 5: Development Tools**
- [ ] **IDE Configuration**: VS Code, Cursor, etc.
- [ ] **Linting Setup**: Python, JavaScript, etc.
- [ ] **Testing Framework**: pytest, jest, etc.
- [ ] **Debugging Tools**: Breakpoints, logging, etc.

## 🔧 Platform-Specific Procedures

### **Windows (PowerShell)**
```powershell
# 1. Install Git (if not installed)
winget install Git.Git

# 2. Install Python (if not installed)
winget install Python.Python.3.11

# 3. Install Node.js (if needed)
winget install OpenJS.NodeJS

# 4. Clone and setup
git clone https://github.com/kasparsgreizis/zenOS.git
cd zenOS
python setup.py --unattended
```

### **Linux/macOS (Bash/Zsh)**
```bash
# 1. Install Git (if not installed)
# Ubuntu/Debian
sudo apt update && sudo apt install git

# macOS
brew install git

# 2. Install Python (if not installed)
# Ubuntu/Debian
sudo apt install python3 python3-pip

# macOS
brew install python

# 3. Install Node.js (if needed)
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# macOS
brew install node

# 4. Clone and setup
git clone https://github.com/kasparsgreizis/zenOS.git
cd zenOS
python setup.py --unattended
```

### **Termux (Android)**
```bash
# 1. Update packages
pkg update && pkg upgrade

# 2. Install essential tools
pkg install git python nodejs

# 3. Clone and setup
git clone https://github.com/kasparsgreizis/zenOS.git
cd zenOS
python setup.py --unattended
```

## 🛠️ Git Best Practices

### **Repository Setup**
```bash
# Initialize repository
git init

# Configure user (if not set globally)
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Create comprehensive .gitignore
# (Handled automatically by zenOS setup)

# Initial commit
git add .
git commit -m "feat: initial project setup"
```

### **Development Workflow**
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Push to remote
git push origin feature/your-feature-name

# Create pull request (via GitHub/GitLab)
# Merge after review

# Clean up
git checkout main
git pull origin main
git branch -d feature/your-feature-name
```

### **Git Aliases (Auto-configured by zenOS)**
```bash
# Safe multiline commits
gcommit "feat" "add new feature" "detailed description"

# Quick commits
gfeat "add new feature"
gfix "fix bug"
gdocs "update documentation"

# Commit and push
gcp "feat" "add feature"

# Interactive commit
gicommit

# Common operations
gs          # git status
ga          # git add
gaa         # git add -A
gl          # git log --oneline -10
gd          # git diff
gp          # git push
gpu         # git pull
```

## 🔍 Troubleshooting Common Issues

### **Git Issues**
```bash
# Commit hanging
git config --global core.editor "code --wait"

# Missing user config
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Not in git repo
git init

# Permission denied
# Check SSH keys or use HTTPS
```

### **Python Issues**
```bash
# Wrong Python version
# Use pyenv or conda to manage versions

# Package not found
pip install --upgrade pip
pip install -r requirements.txt

# Virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### **Node.js Issues**
```bash
# Wrong Node version
# Use nvm to manage versions
nvm install --lts
nvm use --lts

# Permission issues
# Use npx or configure npm properly
```

### **MCP Issues**
```bash
# MCP server not found
npm install -g @cyanheads/git-mcp-server

# Configuration not linked
# Run zenOS setup again
python setup.py --phase mcp_setup
```

## 📱 Mobile Development (Termux)

### **Essential Setup**
```bash
# 1. Install Termux from F-Droid
# 2. Update and install essentials
pkg update && pkg upgrade
pkg install git python nodejs

# 3. Setup storage access
termux-setup-storage

# 4. Clone and setup zenOS
git clone https://github.com/kasparsgreizis/zenOS.git
cd zenOS
python setup.py --unattended
```

### **Mobile-Specific Commands**
```bash
# Check battery status
termux-battery-status

# Share files
termux-share file.txt

# Open in browser
termux-open-url https://github.com

# Clipboard operations
termux-clipboard-set "text"
termux-clipboard-get
```

## 🔄 Environment Switching

### **Quick Environment Switch**
```bash
# 1. Save current work
git add .
git commit -m "wip: save current work"

# 2. Push to remote
git push origin main

# 3. On new machine
git clone https://github.com/your-repo.git
cd your-repo
python setup.py --unattended

# 4. Continue development
git pull origin main
```

### **Environment Sync**
```bash
# Sync all changes
git add .
git commit -m "sync: environment changes"
git push origin main

# Pull on other machine
git pull origin main
```

## 🎯 One-Liner Setup Commands

### **Fresh Environment**
```bash
# All platforms
git clone https://github.com/kasparsgreizis/zenOS.git && cd zenOS && python setup.py
```

### **Existing Project**
```bash
# Update and setup
git pull origin main && python setup.py --unattended
```

### **Validation Only**
```bash
# Check if environment is ready
python setup.py --validate-only
```

## 📚 Additional Resources

- **[zenOS Setup Guide](SETUP_GUIDE.md)** - Detailed setup documentation
- **[Mobile Setup](QUICKSTART_MOBILE.md)** - Termux-specific guide
- **[Windows Setup](QUICKSTART_WINDOWS.md)** - PowerShell installation
- **[Linux Setup](QUICKSTART_LINUX.md)** - Terminal installation

## 🆘 Emergency Recovery

### **If Setup Fails**
```bash
# 1. Check logs
cat setup.log

# 2. Run validation only
python setup.py --validate-only

# 3. Run specific phases
python setup.py --phase detection
python setup.py --phase git_setup

# 4. Manual recovery
# Follow platform-specific procedures above
```

### **Reset Environment**
```bash
# Remove setup artifacts
rm -rf .git
rm setup.log
rm -rf node_modules
rm -rf __pycache__

# Start fresh
python setup.py --unattended
```

---

**This guide is your anchor point for all development environment setups. Bookmark it, share it, and never struggle with environment setup again!** 🚀
