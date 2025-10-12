# zenOS: The Zen of AI Workflow Orchestration 🧘

[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Alpha](https://img.shields.io/badge/status-alpha-orange)](https://github.com/k-dot-greyz/zenOS)

**zenOS** is a personal context operating system designed to transform disparate thoughts, conversations, and data points into a unified, intelligent workflow. It's not just software—it's a philosophy for interacting with your own intellectual and creative landscape.

## What is zenOS?

zenOS aims to squeeze every last drop of human cognition and creativity by establishing a seamless interface with your constantly evolving **Personal Context Core (PCC)**. It reduces cognitive load, fosters semantic connections, and enables effortless exploration of your personal universe of ideas.

### Core Philosophy

- **Effortless Capture**: Ingest context with minimal friction
- **Semantic Flow**: Surface latent connections across your knowledge graph
- **Minimal Cognitive Load**: Act as an intelligent extension of memory
- **Playful Exploration**: Encourage divergent thinking and experimental branches
- **Personal Sovereignty**: Your data, your control, always

## Architecture

```
┌─────────────────────────────────────────────────┐
│             Personal Context Core (PCC)          │
│  Living database of knowledge & conversations    │
│  Vector embeddings • Semantic retrieval          │
└────────────────┬────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │   Bender 🤖     │
        │  AI Assistant   │
        └────────┬────────┘
                 │
    ┌────────────┴────────────┐
    │                         │
┌───▼────┐              ┌─────▼─────┐
│  CLI   │              │  Plugins  │
│ Tools  │              │  System   │
└────────┘              └───────────┘
```

### Core Components

1. **Personal Context Core (PCC)**
   - Central database of your knowledge, conversations, and creative output
   - Advanced text embeddings and vector search
   - Your ultimate long-term memory

2. **Bender 🤖**
   - Primary AI interface and "consciousness" of zenOS
   - Manages context ingestion and retrieval
   - Synthesizes answers and draws semantic connections

3. **Repository Management**
   - Comprehensive git repository organization
   - Multi-account GitHub integration
   - Automated health auditing and maintenance

4. **Plugin System**
   - Extensible architecture for custom workflows
   - PKM (Personal Knowledge Management) integration
   - MCP server support for AI assistants

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/k-dot-greyz/zenOS.git
cd zenOS

# Install dependencies
pip install -r requirements.txt

# Or install as a package
pip install -e .
```

### Basic Usage

```bash
# Start zenOS CLI
zen

# Chat with Bender
zen chat "Help me organize my thoughts"

# Manage repositories
zen repo scan
zen repo audit

# View available procedures
zen procedures list

# Get help
zen help
```

### Configuration

Copy the example environment file and configure:

```bash
cp env.example .env
# Edit .env with your settings
```

## Features

### 🧠 Personal Knowledge Management
- Semantic search across your knowledge base
- Context-aware retrieval and synthesis
- Automatic link discovery between ideas

### 📦 Repository Management
- Local repository discovery and cataloging
- GitHub integration with multi-account support
- Automated health scoring and recommendations
- Unified CLI interface for all operations

### 🔌 Plugin System
- Extensible architecture
- Custom workflow integration
- MCP server support
- Easy plugin development

### 🤖 AI Integration
- Multiple AI provider support
- Context-aware responses
- Conversation history management
- Swarm collaboration mode

### 📱 Mobile Support
- React Native mobile app (in development)
- Cross-platform sync
- Offline-first design

## Development

### Project Structure

```
zenOS/
├── zen/                    # Core Python package
│   ├── cli.py             # CLI interface
│   ├── agents/            # AI agent implementations
│   ├── pkm/               # Personal knowledge management
│   ├── plugins/           # Plugin system
│   └── core/              # Core utilities
├── docs/                   # Documentation
├── scripts/               # Utility scripts
├── workspace/             # Mobile app workspace
└── tests/                 # Test suite
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=zen --cov-report=term-missing

# Run specific test file
pytest test_zenos.py -v
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Documentation

- [Genesis & Philosophy](docs/GENESIS.md) - Project origin and core principles
- [AI Instructions](docs/AI_INSTRUCTIONS.md) - Guide for AI agents
- [Setup Guide](docs/guides/SETUP_GUIDE.md) - Detailed setup instructions
- [Quickstart Guide](docs/guides/QUICKSTART.md) - Get started quickly
- [Repository Management](docs/REPOSITORY_MANAGEMENT.md) - Repo tools documentation

## Use Cases

- **Developers**: Manage multiple projects, codebases, and documentation
- **Researchers**: Connect ideas across papers, notes, and conversations
- **Creatives**: Track projects, inspiration, and creative evolution
- **ADHD/Neurodiverse Users**: Reduce cognitive load with intelligent memory extension

## Roadmap

- [x] Core CLI framework
- [x] Repository management system
- [x] Plugin architecture
- [x] PKM integration
- [ ] Vector database implementation
- [ ] Mobile app beta
- [ ] GlitchBlow hardware integration
- [ ] Multi-user collaboration features

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- [GitHub Issues](https://github.com/k-dot-greyz/zenOS/issues)
- [Documentation](https://zenos.ai/docs)
- [Discord Community](https://discord.gg/zenos) (coming soon)

## Acknowledgments

Built with ❤️ by [Kaspars Greizis](https://github.com/k-dot-greyz) and the zenOS community.

---

*"In the chaos of information, find your zen."* 🧘✨
