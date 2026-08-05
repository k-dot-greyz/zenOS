# zenOS 🧘🤖

**The Zen of AI Workflow Orchestration**

A revolutionary operating system for human-AI collaboration where biological and artificial intelligence work together as equal partners. 
zenOS transforms your terminal into a living, breathing workspace where humans and AI agents collaborate seamlessly.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![Rust](https://img.shields.io/badge/rust-first--class-orange.svg)](https://www.rust-lang.org/)

---

## 🌟 What is zenOS?

zenOS is not just another AI CLI tool—it's a complete paradigm shift in how we interact with artificial intelligence:

- **🤝 True Collaboration**: Humans and AIs as equal participants
- **🎮 Dex System**: Discover and catalog AI models and procedures
- **🔄 Multi-Agent Orchestration**: Multiple AIs working together on complex tasks
- **📱 Universal Access**: Desktop, mobile (Termux), and offline modes
- **🧠 Living Knowledge**: Procedures that evolve through use
- **🌐 Repo Management**: Smart repository analysis and organization

---

## ✨ Core Components

### 1. **Dex** — model & procedure catalog
```bash
zen dex models
zen dex procedures --tier legendary
zen sync                         # top-level refresh (not zen dex sync)
```

### 2. **Agents**
```bash
zen run --list
zen run --chat
zen run troubleshoot "fix my git issue"
```

### 3. **PKM** — optional knowledge satellite
```bash
zen pkm setup
zen pkm extract --limit 20
zen pkm search "topic"
```

### 4. **Plugins & inbox**
```bash
zen plugins list
zen inbox add note "ship it"
```

### 5. **Visual Wiki** (external app — CLI in #48)
```bash
zen wiki setup && zen wiki sync
```

Full map: **[docs/guides/CLI.md](docs/guides/CLI.md)**.

---

## 🚀 Quick Start

### Instant Setup (One-Liners)

#### 🖥️ Desktop (Windows/Mac/Linux)
```bash
curl -sSL https://raw.githubusercontent.com/k-dot-greyz/zenOS/main/install.sh | bash
```

#### 📱 Mobile (Termux/Android)
```bash
curl -sSL https://raw.githubusercontent.com/k-dot-greyz/zenOS/main/install_termux.sh | bash
```

#### ✈️ Offline Mode (No Internet)
```bash
# First download while online:
git clone https://github.com/k-dot-greyz/zenOS.git
cd zenOS

# Then install offline:
python -m pip install -e .
```

### Manual Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/k-dot-greyz/zenOS.git
   cd zenOS
   ```

2. **Set up environment:**
   ```bash
   cp env.example .env
   # Edit .env with your API key (OpenRouter recommended)
   ```

3. **Install dependencies:**
   ```bash
   python3.14 -m pip install -e ".[dev]"
   ```

4. **Start exploring:**
   ```bash
   zen --help
   zen run --list
   zen dex models
   ```

---

## 💡 Features

### For Humans 👨‍💻
- **Interactive Chat**: Natural conversations with AI
- **Code Analysis**: Deep insights into your codebase
- **Task Delegation**: Let AI handle complex workflows
- **Knowledge Management**: Capture and organize thoughts
- **Multi-Platform**: Works everywhere—desktop, mobile, offline

### For AI Agents 🤖
- **AI-First Design**: Native support for AI autonomy
- **Machine-Readable Procedures**: Structured YAML workflows
- **Context Awareness**: Full project understanding
- **Learning & Evolution**: Procedures that improve over time
- **Social Network**: Collaborate with other AIs

### For Teams 🤝
- **Hybrid Workflows**: Seamless human-AI collaboration
- **Swarm Intelligence**: Multiple agents tackling problems together
- **Knowledge Sharing**: Team-wide context and procedures
- **Version Control**: Git-native, merge-friendly

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                   zenOS Core                     │
├─────────────────────────────────────────────────┤
│  🎮 Dex     🤖 Agents    📚 PKM    🔌 Plugins  │
│  catalog    run/chat     optional   Git VST     │
│             + critique                          │
├─────────────────────────────────────────────────┤
│  inbox pipe · wiki garden (external) · setup    │
├─────────────────────────────────────────────────┤
│  Python ≥3.14 glue  ·  Rust-bound dex path      │
└─────────────────────────────────────────────────┘
```

---

## 🎯 Use Cases

### Agents & chat
```bash
zen run --chat
zen run critic "tighten this system prompt" --upgrade-only
```

### Catalog
```bash
zen dex models --task "code generation"
zen dex procedures --tier legendary
zen sync
zen arena
```

### Knowledge pipes
```bash
zen inbox add note "ship dex"
zen pkm search "API patterns"
# zen wiki sync   # when visual-wiki CLI lands
```

### Plugins
```bash
zen plugins search summarizer
zen plugins install ./examples/sample-plugin --local
```

---

## 📖 Documentation

- **[CLI Reference](docs/guides/CLI.md)** — canonical command map
- **[Quick Start](docs/guides/QUICKSTART.md)** — install + first commands
- **[Rework sprint audit](docs/planning/REWORK_SPRINT_AUDIT.md)** — debt & track order
- **[AI Instructions](docs/AI_INSTRUCTIONS.md)** — for AI agents
- **[Setup Guides](docs/guides/)** — platform-specific
- **[Genesis Log (archive)](docs/archive/zenOS-genesis-log.md)** — historical

### Platform-Specific Guides
- [Windows Setup](docs/guides/QUICKSTART_WINDOWS.md)
- [Linux Setup](docs/guides/QUICKSTART_LINUX.md)
- [Termux/Mobile Setup](docs/guides/QUICKSTART_TERMUX.md)
- [Arch Linux Mobile](docs/guides/QUICKSTART_ARCH_MOBILE.md)

---

## 🗺️ Roadmap

### ✅ Current
- Live CLI: `run`, `setup`, `dex`, `sync`, `bench`, `arena`, `plugins`, `pkm`, `inbox`
- OpenRouter + offline hooks
- Python ≥ 3.14 CI floor

### 🚧 In Progress
- Wire `doctor` / `help` into root CLI
- Visual wiki CLI (#48)
- Real `tests/` + Rust `zen-dex` crate

### 🔮 Later
- Top-level `zen chat` / swarm verbs **only when implemented**
- Plugin marketplace contracts
- Termux mobile quarantine

---

## 🤝 Contributing

We welcome contributions from humans and AIs alike!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 🐛 Troubleshooting

### System Health Check
```bash
zen setup --validate-only   # available now
# zen doctor --ai-mode      # in source; wire to root CLI next
```

### Common Issues

**API Key Not Working?**
```bash
cat .env | grep OPENROUTER_API_KEY
zen run --chat
```

**Installation Failed?**
```bash
python3.14 -m pip install --upgrade pip
python3.14 -m pip install -e ".[dev]"
```

**Termux/Mobile Issues?**
See [Termux Setup Guide](docs/guides/QUICKSTART_TERMUX.md) for platform-specific fixes.

---

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🌟 Philosophy

> "The goal is not to replace human intelligence with artificial intelligence,
> but to create a harmonious system where both enhance each other."

zenOS embodies the principle of **zen** in software:
- **Simplicity**: Complex power through simple interfaces
- **Flow**: Seamless transitions between human and AI control
- **Balance**: Neither human nor AI dominates—both collaborate
- **Evolution**: Systems that learn and improve over time
- **Openness**: Knowledge freely shared and accessible

---

## 🙏 Acknowledgments

Built with love by humans and AIs working together.

Special thanks to:
- The OpenRouter team for model access
- The open-source AI community
- Every AI agent that has contributed to procedure evolution
- You, for being part of this journey

---

## 📬 Contact & Community

- **GitHub**: [k-dot-greyz/zenOS](https://github.com/k-dot-greyz/zenOS)
- **Issues**: [Report bugs or request features](https://github.com/k-dot-greyz/zenOS/issues)
- **Discussions**: [Join the conversation](https://github.com/k-dot-greyz/zenOS/discussions)

---

**Welcome to zenOS - Where Humans and AIs Collaborate in Balanced Zen** 🧘🤖
