# 🧘 zenOS - The Zen of AI Workflow Orchestration

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**zenOS** is a powerful, modular AI agent orchestration framework that brings zen-like simplicity to complex AI workflows.

## ✨ Features

- 🚀 **Simple CLI**: One command to rule them all - `zen`
- 📱 **Mobile-First**: Native Termux support with voice & gesture integration
- 🌉 **Bridge System**: Seamless airi-zenOS integration for mobile AI
- 🎤 **Voice Interface**: Voice input/output with Termux API
- 🔋 **Offline Mode**: Local AI processing with Ollama integration
- 🤖 **Modular Agents**: Composable, reusable AI agents
- 🔒 **Security First**: Built-in defense against prompt injection
- 🎯 **Auto-Critique**: Every prompt automatically upgraded for better results
- 🔋 **Battery-Aware**: Automatic eco mode for mobile devices
- 📦 **Zero Config**: Works out of the box, extensible when needed
- 🌈 **Beautiful Output**: Rich terminal interface with progress indicators
- 💾 **Smart Caching**: Offline access to previous AI responses

## 🚀 Quick Start

### **One-Command Setup (All Platforms)** ⚡

```bash
# Clone and setup in one command - works everywhere!
git clone https://github.com/kasparsgreizis/zenOS.git && cd zenOS && python setup.py
```

### **Platform-Specific One-Liners**

**🖥️ Windows (PowerShell)**
```powershell
git clone https://github.com/kasparsgreizis/zenOS.git; cd zenOS; python setup.py
```

**🐧 Linux/macOS**
```bash
git clone https://github.com/kasparsgreizis/zenOS.git && cd zenOS && python setup.py
```

**📱 Mobile (Termux)**
```bash
git clone https://github.com/kasparsgreizis/zenOS.git && cd zenOS && python setup.py
```

### **Legacy Installers (Still Available)**

**📱 Mobile (Android/Termux)**
```bash
curl -sSL https://raw.githubusercontent.com/kasparsgreizis/zenOS/main/install.sh | bash
```

**🖥️ Windows (PowerShell)**
```powershell
iwr -useb https://raw.githubusercontent.com/kasparsgreizis/zenOS/main/install.ps1 | iex
```

**🐧 Linux/macOS**
```bash
curl -sSL https://raw.githubusercontent.com/kasparsgreizis/zenOS/main/install.sh | bash
```

### Detailed Guides

🚀 **[Dev Environment Setup](docs/guides/DEV_ENVIRONMENT_SETUP.md)** - **Your anchor point for all dev setups**  
📱 **[Full Mobile Guide](docs/guides/QUICKSTART_MOBILE.md)** - Complete Termux setup  
🖥️ **[Full Windows Guide](docs/guides/QUICKSTART_WINDOWS.md)** - PowerShell installation  
🐧 **[Full Linux Guide](docs/guides/QUICKSTART_LINUX.md)** - Terminal installation  
🚀 **[Setup Guide](docs/guides/SETUP_GUIDE.md)** - Unified setup system documentation

### Quick Reference

📋 **[Dev Setup Cheat Sheet](DEV_SETUP_CHEAT_SHEET.md)** - One-page reference for all platforms

### Basic Usage

```bash
# Run an agent
zen troubleshoot "fix my git commit issue"

# Mobile voice input (Termux)
zen-voice "explain quantum computing"

# Mobile clipboard input
zen-clip  # Processes clipboard content

# airi integration (mobile)
zen airi "enhanced mobile processing"

# Offline mode (local AI)
zen offline "work without internet"

# Bridge system (airi + zenOS)
zen interactive  # Full bridge mode

# Review a prompt
zen critic "analyze this prompt for improvements"

# List available agents
zen --list

# Create a new agent
zen --create my-agent

# Disable auto-critique for speed
zen --no-critique assistant "quick question"

# Battery-aware mode (auto on mobile)
zen --eco "run in low power mode"
```

## 🏗️ Architecture

zenOS is built on a modular architecture that separates concerns:

```
zenOS/
├── zen/                    # Core package
│   ├── cli.py             # CLI interface
│   ├── core/              # Core functionality
│   ├── agents/            # Built-in agents
│   └── utils/             # Utilities
├── agents/                # User-defined agents
├── modules/               # Modular components
│   ├── roles/            # Who you are
│   ├── tasks/            # What you do
│   ├── contexts/         # Where/why you operate
│   └── constraints/      # Rules and limits
└── configs/              # Configuration
```

## 🤖 Built-in Agents

- **troubleshooter**: System diagnostics and automated fixes
- **critic**: Prompt analysis and improvement
- **security**: Security analysis and threat detection
- **assistant**: General-purpose AI assistant
- More coming soon...

## 📚 Documentation

- [Quick Start Guide](docs/guides/QUICKSTART.md)
- [Mobile Setup (Termux)](docs/guides/QUICKSTART_MOBILE.md)
- [Windows Setup](docs/guides/QUICKSTART_WINDOWS.md)
- [Linux Setup](docs/guides/QUICKSTART_LINUX.md)
- [AI Integration Blueprint](docs/planning/AI_INTEGRATION_BLUEPRINT.md)
- [Plugin System](docs/planning/PLUGIN_SYSTEM_SPECIFICATION.md)
- [Mobile UI Framework](docs/planning/MOBILE_UI_FRAMEWORK.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

zenOS is MIT licensed. See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

zenOS is the evolution of PromptOS, rebuilt from the ground up with a focus on simplicity, security, and developer experience.

---

**"The path to AI enlightenment begins with a single command: `zen`"** 🧘
