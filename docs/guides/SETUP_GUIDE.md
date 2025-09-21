# 🧘 zenOS Setup Guide

**The Ultimate Development Environment Setup - Never Get Lost Again!**

This guide covers the **bulletproof setup system** that combines the best procedures from promptOS and mcp-config to create an environment-agnostic development environment that works everywhere.

## 🚀 **One-Command Setup**

### **Quick Start (All Platforms)**

```bash
# Clone and setup in one command
git clone https://github.com/kasparsgreizis/zenOS.git && cd zenOS && python setup.py
```

### **Platform-Specific One-Liners**

**Windows (PowerShell):**
```powershell
git clone https://github.com/kasparsgreizis/zenOS.git; cd zenOS; python setup.py
```

**macOS/Linux:**
```bash
git clone https://github.com/kasparsgreizis/zenOS.git && cd zenOS && python setup.py
```

**Termux (Mobile):**
```bash
git clone https://github.com/kasparsgreizis/zenOS.git && cd zenOS && python setup.py
```

## 🎯 **What Gets Set Up**

### **✅ Environment Detection & Validation**
- **Cross-platform compatibility** (Windows, macOS, Linux, Termux)
- **AI-powered troubleshooting** with automatic issue resolution
- **Progressive failure recovery** with manual intervention fallback
- **Comprehensive validation** (Python, Git, shell, permissions, internet)

### **✅ Git Repository Setup**
- **Automated .gitignore creation** with project type detection
- **Git aliases and workflow optimization**
- **User configuration** and repository initialization
- **Tracked file cleanup** and repository maintenance

### **✅ MCP Server Configuration**
- **Model Context Protocol servers** installation and linking
- **Cross-tool integration** (Cursor, Warp, Claude Desktop)
- **Configuration symlinking** and environment setup
- **Health checks and validation**

### **✅ zenOS Core Setup**
- **Python dependencies** installation
- **CLI aliases** and shell integration
- **Workspace directories** creation
- **Configuration files** generation

### **✅ Integration & Linking**
- **promptOS integration** setup
- **MCP configuration** linking
- **Workspace organization**
- **Tool integration**

## 🔧 **Advanced Setup Options**

### **Unattended Setup**
```bash
python setup.py --unattended
```
Runs setup without user interaction - perfect for automation.

### **Validation Only**
```bash
python setup.py --validate-only
```
Just validates the environment without making changes.

### **Phase-Specific Setup**
```bash
# Start from specific phase
python setup.py --phase git_setup
python setup.py --phase mcp_setup
python setup.py --phase zenos_setup
```

### **Using zenOS CLI**
```bash
# Setup via zenOS CLI
zen setup
zen setup --unattended
zen setup --validate-only
zen setup --phase git_setup
```

## 🛠️ **Manual Setup (If Needed)**

If automated setup fails, you can manually set up zenOS:

### **1. Prerequisites**
```bash
# Python 3.7+ (required)
python --version

# Git (recommended)
git --version

# Node.js (for MCP integration)
node --version
```

### **2. Installation**
```bash
# Clone repository
git clone https://github.com/kasparsgreizis/zenOS.git
cd zenOS

# Install Python dependencies
pip install -r requirements.txt

# Setup git (if not already done)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Create .gitignore
python zen/setup/git_setup.py

# Setup MCP servers (optional)
npm install -g @modelcontextprotocol/server-filesystem
```

### **3. Verify Setup**
```bash
# Test zenOS CLI
python zen/cli.py --help

# Test plugins
python zen/cli.py plugins list

# Test inbox
python zen/cli.py receive add "test" "Hello world"
```

## 🔍 **Troubleshooting**

### **Common Issues**

**Python Version Too Old:**
```bash
# macOS
brew install python@3.9

# Ubuntu/Debian
sudo apt install python3.9

# Windows
# Download from https://python.org/downloads/
```

**Git Not Found:**
```bash
# macOS
brew install git

# Ubuntu/Debian
sudo apt install git

# Windows
# Download from https://git-scm.com/download/win
```

**Permission Issues:**
```bash
# Fix ownership
sudo chown -R $USER:$USER .

# Fix permissions
chmod -R 755 .
```

**Network Connectivity:**
```bash
# Test connectivity
ping google.com

# Check DNS
nslookup github.com
```

### **Validation Script**
```bash
# Run validation
python validate_setup.py

# Check setup log
cat setup.log
```

### **Getting Help**
1. **Run validation**: `python validate_setup.py`
2. **Check setup log**: `cat setup.log`
3. **Re-run setup**: `python setup.py`
4. **Check troubleshooting guide**: `cat TROUBLESHOOTING.md`

## 🎉 **After Setup**

### **Available Commands**
```bash
# zenOS CLI
zen --help                    # Show all commands
zen chat                      # Interactive chat mode
zen troubleshoot "your issue" # AI troubleshooting
zen plugins list              # List available plugins
zen receive list              # List inbox items

# Setup commands
zen setup                     # Re-run setup
zen setup --validate-only     # Validate environment
zen setup --phase git_setup   # Run specific phase
```

### **Workspace Structure**
```
zenOS/
├── zen/                      # Core zenOS code
├── docs/                     # Documentation
├── inbox/                    # Inbox system
├── workspace/                # Your workspace
├── config/                   # Configuration files
├── setup.py                  # Setup script
└── validate_setup.py         # Validation script
```

### **Configuration Files**
- **zenOS config**: `config/zenos.json`
- **Git config**: `.gitignore`, git aliases
- **MCP config**: `mcp-config/configs/mcp.json`
- **Shell aliases**: Added to your shell profile

## 🔄 **Environment Switching**

The setup system is designed to work across different environments:

### **Switching Between Machines**
1. **Clone repository**: `git clone https://github.com/kasparsgreizis/zenOS.git`
2. **Run setup**: `python setup.py`
3. **Everything works**: All procedures are restored automatically

### **Different Platforms**
- **Windows**: PowerShell integration
- **macOS**: Homebrew and zsh integration
- **Linux**: apt and bash integration
- **Termux**: Mobile-optimized setup

### **Backup & Restore**
```bash
# Backup your setup
git add . && git commit -m "backup setup" && git push

# Restore on new machine
git clone https://github.com/kasparsgreizis/zenOS.git
cd zenOS && python setup.py
```

## 🚀 **Pro Tips**

### **1. Use Aliases**
After setup, you'll have these aliases available:
```bash
zen                    # zenOS CLI
zen-receive           # Inbox management
zen-plugins           # Plugin management
```

### **2. Mobile Development**
On Termux, zenOS automatically detects mobile mode and optimizes for:
- Battery usage
- Screen size
- Touch interface
- Limited resources

### **3. Offline Mode**
```bash
# Force offline mode
zen chat --offline

# Eco mode for battery saving
zen chat --eco
```

### **4. Custom Models**
```bash
# Use specific model
zen chat --model "gpt-4"

# Use local model
zen chat --offline --model "llama2"
```

## 🎯 **Why This Setup is Bulletproof**

### **1. Environment Agnostic**
- Works on Windows, macOS, Linux, and Termux
- Automatically detects and adapts to your environment
- No platform-specific dependencies

### **2. AI-Powered Troubleshooting**
- Automatically diagnoses and fixes common issues
- Provides intelligent suggestions for complex problems
- Learns from your environment and adapts

### **3. Progressive Recovery**
- If one step fails, it continues with the next
- Provides manual intervention options
- Never leaves you in a broken state

### **4. Comprehensive Validation**
- Validates Python, Git, shell, permissions, and network
- Provides detailed error messages and solutions
- Creates validation scripts for future use

### **5. Integration Ready**
- Sets up MCP servers for tool integration
- Configures shell aliases and environment variables
- Links configurations across different tools

## 🧘 **The Zen of Setup**

This setup system embodies the zenOS philosophy:

- **Simplicity**: One command sets up everything
- **Reliability**: Works consistently across environments
- **Intelligence**: AI-powered problem resolution
- **Flexibility**: Adapts to your specific needs
- **Recovery**: Never leaves you stranded

**Your development environment should never be a source of friction. With zenOS, it becomes a source of flow.**

---

**Happy coding! 🧘✨**
