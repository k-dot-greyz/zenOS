# zenOS 🧘🤖

**The Zen of AI Workflow Orchestration**

A revolutionary operating system for human-AI collaboration where biological and artificial intelligence work together as equal partners. 
zenOS transforms your terminal into a living, breathing workspace where humans and AI agents collaborate seamlessly.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

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

### 1. **PCC (Pokédex Control Center)**
Discover, catalog, and manage AI models and procedures:
```bash
zen pokedex models          # Browse available AI models
zen pokedex procedures      # Explore procedure library
zen pokedex sync            # Update from OpenRouter and other sources
```

### 2. **Bender (Multi-Agent Framework)**
Orchestrate multiple AI agents for complex tasks:
```bash
zen swarm "analyze security vulnerabilities"  # Multi-AI collaboration
zen delegate "refactor auth module"           # Single AI takes over
zen chat --copilot                           # AI assists you
```

### 3. **PKM (Personal Knowledge Management)**
Capture, organize, and evolve your knowledge:
```bash
zen notes capture           # Quick note taking
zen notes search "topic"    # Find relevant information
zen context sync            # Update working context
```

### 4. **Repo Management**
Intelligent repository analysis and organization:
```bash
zen repo analyze            # Deep dive into codebase
zen repo health             # Check project status
zen repo optimize          # Suggest improvements
```

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
   pip install -e .
   ```

4. **Start exploring:**
   ```bash
   zen chat
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
│  🎮 Pokédex    🤖 Bender    📚 PKM    📦 Repo   │
│  Control       Multi-Agent  Knowledge Management │
│  Center        Framework    System     Analyzer  │
├─────────────────────────────────────────────────┤
│              AI Adapter Layer                    │
│  ┌──────────┬──────────┬──────────┬──────────┐ │
│  │Protocol  │Context   │Learning  │Social    │ │
│  │Parser    │Manager   │Engine    │Network   │ │
│  └──────────┴──────────┴──────────┴──────────┘ │
├─────────────────────────────────────────────────┤
│                 Interfaces                       │
│  ┌──────────┬──────────┬──────────┬──────────┐ │
│  │Human     │AI Agent  │Hybrid    │Swarm     │ │
│  │Terminal  │API       │Mode      │Mode      │ │
│  └──────────┴──────────┴──────────┴──────────┘ │
└─────────────────────────────────────────────────┘
```

---

## 🎯 Use Cases

### Development Workflows
```bash
# Start a coding session
zen chat "I need to add user authentication"

# Analyze codebase
zen repo analyze --focus security

# Get AI assistance
zen delegate "implement OAuth2 flow"

# Multi-agent review
zen swarm "review my PR for security issues"
```

### Knowledge Management
```bash
# Capture quick notes
zen notes capture "Meeting: discussed API redesign"

# Search your knowledge base
zen notes search "API design patterns"

# Sync context for AI
zen context sync
```

### Model Discovery
```bash
# Find the right model
zen pokedex models --capability "code generation"

# Explore procedures
zen pokedex procedures --rarity legendary

# Sync latest models
zen pokedex sync
```

---

## 📖 Documentation

- **[Quick Start Guide](docs/guides/QUICKSTART.md)** - Get started in minutes
- **[AI Instructions](docs/AI_INSTRUCTIONS.md)** - For AI agents
- **[Integration Blueprint](docs/planning/AI_INTEGRATION_BLUEPRINT.md)** - Architecture deep dive
- **[Setup Guides](docs/guides/)** - Platform-specific instructions
- **[Genesis Log](docs/zenOS-genesis-log.md)** - The origin story

### Platform-Specific Guides
- [Windows Setup](docs/guides/QUICKSTART_WINDOWS.md)
- [Linux Setup](docs/guides/QUICKSTART_LINUX.md)
- [Termux/Mobile Setup](docs/guides/QUICKSTART_TERMUX.md)
- [Arch Linux Mobile](docs/guides/QUICKSTART_ARCH_MOBILE.md)

---

## 🗺️ Roadmap

### ✅ Current (v0.1.0)
- Core CLI functionality
- OpenRouter integration
- Basic Pokédex system
- Repository analysis
- Multi-agent framework (Bender)

### 🚧 In Progress (v0.2.0)
- Enhanced PKM system
- Advanced context management
- AI-to-AI collaboration protocols
- Mobile optimization

### 🔮 Future (v1.0.0)
- Visual workspace interface
- Plugin ecosystem
- Decentralized AI network
- Real-time collaboration
- Advanced learning engine

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
zen doctor              # Run diagnostics
zen doctor --ai-mode   # AI-specific checks
```

### Common Issues

**API Key Not Working?**
```bash
# Check your .env file
cat .env | grep OPENROUTER_API_KEY

# Test connection
zen chat "hello"
```

**Installation Failed?**
```bash
# Update pip first
python -m pip install --upgrade pip

# Retry installation
pip install -e .
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
