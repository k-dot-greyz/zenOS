# 🧠 Neuro-Spicy DevKit

<p align="center">  
  <!-- Optional: ASCII Art or a simple banner image -->  
  <pre>🧠 Neuro-Spicy DevKit
═══════════════════════════════════════
Lean • Mean • Accessible • Cross-Platform</pre>  
</p>

<p align="center">  
  <!-- Badges: License, Platform, etc. -->  
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">  
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-blue.svg" alt="Platform">  
  <img src="https://img.shields.io/badge/Status-Ready%20for%20Release-green.svg" alt="Status">
</p>

> **A lean, mean development environment setup tool designed for ADHD/autism-friendly workflows.**

<!--   
  GIF DEMO: A short, silent GIF showing the init script and health check.  
  This is the most powerful part of the README.  
-->  
<!-- ![Demo GIF](link-to-your-demo.gif) -->

## ✨ Features

- 🚀 **One-Command Setup**: Interactive initialization with guided prompts
- 🔧 **Cross-Platform**: Windows (PowerShell) and Linux/macOS (Bash) support
- 📦 **Portable**: Easy to clone, customize, and share
- 🎯 **Lean & Mean**: Focused on essential tools only
- 🔒 **Secure**: MIT licensed with no personal data collection
- 🌈 **Customizable**: JSON-based profile system for different workflows
- 📚 **Well-Documented**: Clear guides for beginners and advanced users

## 🚀 Quick Start

### Prerequisites

- **Windows**: PowerShell 5.1+ or PowerShell Core
- **Linux/macOS**: Bash shell
- **Git**: For version control
- **Node.js**: For MCP servers (optional)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/neuro-spicy-devkit.git
cd neuro-spicy-devkit

# Run the interactive setup
# Windows
.\init.ps1

# Linux/macOS
./init.sh
```

The interactive setup will guide you through:
1. **Git Configuration** - Set up your name and email
2. **GitHub Token** - Configure GitHub authentication
3. **Cursor Setup** - Configure AI-powered development
4. **Health Check** - Verify all tools are working

## 📁 Project Structure

```
neuro-spicy-devkit/
├── init.ps1                     # Windows quick launcher
├── init.sh                      # Linux/macOS quick launcher
├── scripts/                     # Core setup scripts
│   ├── neuro-spicy-init.ps1     # Windows interactive setup
│   ├── neuro-spicy-init.sh     # Linux/macOS interactive setup
│   ├── health-check-core.ps1   # Windows health check
│   ├── health-check-core.sh    # Linux/macOS health check
│   └── ...
├── docs/                        # Documentation
│   ├── CORE_FOCUS_PLAN.md      # Core philosophy
│   ├── AESTHETICS_GUIDE.md     # Style guide and visual standards
│   ├── QUICK_REFERENCE.md      # Essential info for contributors
│   ├── BASH_LINUX_DEFAULT.md   # Bash/Linux guide
│   └── BEGINNER_JOURNEY.md      # Beginner's guide
├── portable-dev-env/            # Portable development environment
│   ├── cursor/                  # Cursor configuration
│   ├── vscode/                  # VSCode configuration
│   ├── profiles/                # Profile templates
│   └── docs/                    # Usage documentation
└── LICENSE                      # MIT License
```

## 🎯 Core Philosophy

The Neuro-Spicy DevKit follows these principles:

1. **Simplicity First**: Minimal setup, maximum productivity
2. **Portability**: Easy to share and customize
3. **Accessibility**: ADHD/autism-friendly workflows
4. **Cross-Platform**: Works everywhere
5. **Open Source**: MIT licensed, community-driven

## 📚 Documentation

- **[Core Focus Plan](docs/CORE_FOCUS_PLAN.md)** - Understanding the philosophy
- **[Aesthetics Guide](docs/AESTHETICS_GUIDE.md)** - Style guide and visual standards
- **[Quick Reference](docs/QUICK_REFERENCE.md)** - Essential info for contributors
- **[Bash/Linux Default](docs/BASH_LINUX_DEFAULT.md)** - Linux/macOS setup guide
- **[Beginner's Journey](docs/BEGINNER_JOURNEY.md)** - Step-by-step guide for new users
- **[Usage Guide](portable-dev-env/docs/USAGE_GUIDE.md)** - Advanced usage patterns

## 🔧 Customization

The devkit uses a profile-based system for customization:

```json
{
  "name": "frontend-developer",
  "description": "Frontend development profile",
  "tools": ["node", "npm", "git"],
  "mcp_servers": ["docker", "github"],
  "shell_config": "bash"
}
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

Neuro-Spicy DevKit is MIT licensed. See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

Built with ❤️ for the neurodivergent developer community.

---

**"Code with confidence, develop with purpose"** 🧠✨