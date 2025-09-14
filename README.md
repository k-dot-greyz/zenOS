# 🧘 zenOS - The Zen of AI Workflow Orchestration

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**zenOS** is a powerful, modular AI agent orchestration framework that brings zen-like simplicity to complex AI workflows.

## ✨ Features

- 🚀 **Simple CLI**: One command to rule them all - `zen`
- 🤖 **Modular Agents**: Composable, reusable AI agents
- 🔒 **Security First**: Built-in defense against prompt injection
- 🎯 **Auto-Critique**: Every prompt automatically upgraded for better results
- 📦 **Zero Config**: Works out of the box, extensible when needed
- 🌈 **Beautiful Output**: Rich terminal interface with progress indicators

## 🚀 Quick Start

### Installation

```bash
# One-line installer (coming soon)
curl -sSL https://get.zenos.ai | bash

# Or via pip (coming soon)
pip install zenos

# Or from source
git clone https://github.com/kasparsgreizis/zenOS.git
cd zenOS
pip install -e .
```

### Basic Usage

```bash
# Run an agent
zen troubleshoot "fix my git commit issue"

# Review a prompt
zen critic "analyze this prompt for improvements"

# List available agents
zen --list

# Create a new agent
zen --create my-agent

# Disable auto-critique for speed
zen --no-critique assistant "quick question"
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
