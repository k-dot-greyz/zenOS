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

### One Command Installation! ⚡

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

### Manual Installation (if you prefer)

**📱 Mobile (Android/Termux)**
```bash
git clone https://github.com/kasparsgreizis/zenOS.git
cd zenOS
chmod +x install_termux.sh
./install_termux.sh
```
📱 **[Full Mobile Guide](QUICKSTART_MOBILE.md)**

**🖥️ Windows**
```bash
git clone https://github.com/kasparsgreizis/zenOS.git
cd zenOS
pip install rich click aiohttp aiofiles psutil pyyaml textblob nltk
python -m textblob.download_corpora
```
🖥️ **[Full Windows Guide](QUICKSTART_WINDOWS.md)**

**🐧 Linux**
```bash
git clone https://github.com/kasparsgreizis/zenOS.git
cd zenOS
pip3 install --user rich click aiohttp aiofiles psutil pyyaml textblob nltk
python3 -m textblob.download_corpora
```
🐧 **[Full Linux Guide](QUICKSTART_LINUX.md)**

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

- [Quick Start Guide](QUICKSTART.md)
- [Mobile Setup (Termux)](QUICKSTART_TERMUX.md)
- [airi Integration](docs/AIRI_INTEGRATION.md)
- [Mobile UI Framework](MOBILE_UI_FRAMEWORK.md)
- [Plugin System](PLUGIN_SYSTEM_SPECIFICATION.md)
- [AI Integration Blueprint](AI_INTEGRATION_BLUEPRINT.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

zenOS is MIT licensed. See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

zenOS is the evolution of PromptOS, rebuilt from the ground up with a focus on simplicity, security, and developer experience.

---

**"The path to AI enlightenment begins with a single command: `zen`"** 🧘
