# 🧘 zenOS - The Zen of AI Workflow Orchestration

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**zenOS** is a powerful, modular AI agent orchestration framework that brings zen-like simplicity to complex AI workflows.

## ✨ Features

- 🚀 **Simple CLI**: One command to rule them all - `zen`
- 📱 **Mobile-First**: Native Termux support with voice & gesture integration
- 🤖 **Modular Agents**: Composable, reusable AI agents
- 🔒 **Security First**: Built-in defense against prompt injection
- 🎯 **Auto-Critique**: Every prompt automatically upgraded for better results
- 🔋 **Battery-Aware**: Automatic eco mode for mobile devices
- 📦 **Zero Config**: Works out of the box, extensible when needed
- 🌈 **Beautiful Output**: Rich terminal interface with progress indicators
- 💾 **Smart Caching**: Offline access to previous AI responses

## 🚀 Quick Start

### Installation

```bash
# Mobile (Termux) - One-line installer 📱
curl -sSL https://raw.githubusercontent.com/kasparsgreizis/zenOS/main/scripts/termux-install.sh | bash

# Desktop - One-line installer (coming soon)
curl -sSL https://get.zenos.ai | bash

# Or via pip (coming soon)
pip install zenos

# Or from source
git clone https://github.com/kasparsgreizis/zenOS.git
cd zenOS
pip install -e .
```

📱 **[Full Mobile Setup Guide](QUICKSTART_TERMUX.md)** | 🖥️ **[Desktop Guide](QUICKSTART_WINDOWS.md)**

### Basic Usage

```bash
# Run an agent
zen troubleshoot "fix my git commit issue"

# Mobile voice input (Termux)
zen-voice "explain quantum computing"

# Mobile clipboard input
zen-clip  # Processes clipboard content

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

- [Quick Start Guide](docs/quickstart.md)
- [Agent Development](docs/agents.md)
- [Configuration](docs/configuration.md)
- [API Reference](docs/api.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

zenOS is MIT licensed. See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

zenOS is the evolution of PromptOS, rebuilt from the ground up with a focus on simplicity, security, and developer experience.

---

**"The path to AI enlightenment begins with a single command: `zen`"** 🧘
