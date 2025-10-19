# 🤝 Contributing to zenOS

Welcome to the zenOS community! We're excited that you want to contribute to making AI workflows more zen. This guide will help you get started.

## 🧘 Philosophy

Before contributing, please understand our core philosophy:
- **Simplicity over complexity** - If it can be simpler, make it simpler
- **Automation over manual work** - Automate repetitive tasks
- **Mobile-first thinking** - Always consider mobile users
- **Progressive disclosure** - Show complexity only when needed
- **Community-driven** - Your ideas and feedback matter

## 🚀 Quick Start

1. **Fork the repository**
   ```bash
   gh repo fork k-dot-greyz/zenOS --clone
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/your-awesome-idea
   ```

3. **Make your changes**
   - Write clean, readable code
   - Add tests if applicable
   - Update documentation

4. **Commit with conventional commits** (see below)
   ```bash
   npm run commit
   # or
   git commit -m "feat(mobile): add gesture support"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-awesome-idea
   gh pr create
   ```

## 📝 Commit Message Guidelines

We use **Conventional Commits** to maintain a clean history and automate releases.

### Format
```
<type>(<scope>): <subject>

[optional body]

[optional footer(s)]
```

### Quick Examples
```bash
# Feature
feat(cli): add voice input support

# Bug fix
fix(mobile): resolve Termux compatibility issue

# Documentation
docs: update installation instructions

# Breaking change
feat(api)!: redesign plugin interface

BREAKING CHANGE: Plugin manifest v2 required
```

### Types

| Type | When to use | Example |
|------|-------------|---------|
| `feat` | New feature | `feat: add offline mode` |
| `fix` | Bug fix | `fix: resolve crash on startup` |
| `docs` | Documentation only | `docs: clarify setup steps` |
| `style` | Formatting (no logic change) | `style: fix indentation` |
| `refactor` | Code restructuring | `refactor: simplify context manager` |
| `perf` | Performance improvement | `perf: optimize API calls` |
| `test` | Adding/fixing tests | `test: add unit tests for plugins` |
| `build` | Build/dependency changes | `build: update dependencies` |
| `ci` | CI/CD changes | `ci: add GitHub Actions workflow` |
| `chore` | Maintenance | `chore: update .gitignore` |

**zenOS-specific types:**
| Type | When to use | Example |
|------|-------------|---------|
| `mobile` | Mobile-specific changes | `mobile: add Termux gestures` |
| `ai` | AI/ML features | `ai: integrate GPT-4 vision` |
| `plugin` | Plugin system | `plugin: add discovery API` |
| `zen` | Workflow improvements | `zen: simplify onboarding` |

### Interactive Commit Helper

For an interactive commit experience:
```bash
npm run commit
```

This will guide you through creating a properly formatted commit message.

## 🏗️ Development Setup

### Prerequisites
- Python 3.8+
- Node.js 16+ (for tooling)
- Git

### Setup
```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/zenOS.git
cd zenOS

# Install Python dependencies
pip install -e ".[dev]"

# Install commit tools (optional but recommended)
npm install

# Set up git commit template
git config commit.template .gitmessage
```

### Running Tests
```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_core.py

# Run with coverage
pytest --cov=zen tests/
```

### Code Style
We use:
- **Black** for Python formatting
- **isort** for import sorting
- **flake8** for linting

```bash
# Format code
black zen/
isort zen/

# Check linting
flake8 zen/
```

## 📦 Project Structure

```
zenOS/
├── zen/                 # Core package
│   ├── core/           # Core functionality
│   ├── cli/            # CLI interface
│   ├── ui/             # UI components
│   ├── mobile/         # Mobile-specific
│   ├── plugins/        # Plugin system
│   └── providers/      # AI providers
├── docs/               # Documentation
├── scripts/            # Helper scripts
├── tests/              # Test suite
└── examples/           # Example code
```

## 🧪 Testing

### Writing Tests
- Place tests in `tests/` directory
- Mirror the structure of `zen/` package
- Use descriptive test names

Example test:
```python
def test_plugin_discovery_finds_github_repos():
    """Test that plugin discovery can find GitHub repositories."""
    discovery = PluginDiscovery()
    plugins = discovery.search("text-processing")
    assert len(plugins) > 0
    assert all(p.has_manifest() for p in plugins)
```

## 📚 Documentation

### Where to document:
- **Code**: Inline docstrings (Google style)
- **Features**: Update relevant `.md` files in `docs/`
- **API changes**: Update API documentation
- **Breaking changes**: Note in commit message

### Documentation style:
- Use clear, simple language
- Include examples
- Explain the "why" not just the "what"
- Add emojis sparingly for clarity 😊

## 🎯 What to Work On

### Good First Issues
Look for issues labeled `good first issue` - these are perfect for getting started.

### Areas We Need Help
- 📱 **Mobile optimization** - Termux, gestures, battery efficiency
- 🔌 **Plugins** - Create new plugins, improve plugin system
- 📚 **Documentation** - Tutorials, examples, translations
- 🧪 **Testing** - Unit tests, integration tests, mobile tests
- 🎨 **UI/UX** - CLI improvements, web interface, mobile UI
- 🌐 **Internationalization** - Translations, locale support

### Feature Ideas
Have an idea? Open an issue to discuss it! We love:
- Workflow improvements
- Mobile features
- AI integrations
- Plugin ideas
- Performance optimizations

## 🐛 Reporting Issues

### Before reporting:
1. Check existing issues
2. Try the latest version
3. Check documentation

### Issue template:
```markdown
**Description**
Clear description of the issue

**Steps to Reproduce**
1. Step one
2. Step two
3. ...

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g., Android 13/Termux]
- Python version: [e.g., 3.11]
- zenOS version: [e.g., 0.1.0]
```

## 🚢 Pull Request Process

1. **Update documentation** for any API changes
2. **Add tests** for new functionality
3. **Ensure all tests pass**
4. **Update CHANGELOG.md** (in Unreleased section)
5. **Use conventional commits**
6. **Keep PRs focused** - one feature/fix per PR

### PR Title Format
Use the same format as commit messages:
```
feat(mobile): add gesture support for navigation
```

## 💬 Communication

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: General questions, ideas
- **Pull Requests**: Code contributions

## 📜 Code of Conduct

Be kind, be helpful, be zen. We're all here to make AI workflows better together.

- Respect all contributors
- Welcome newcomers
- Give constructive feedback
- Focus on what's best for the community

## 🙏 Recognition

All contributors are recognized in our:
- GitHub contributors page
- Release notes
- Special thanks in documentation

## ❓ Questions?

Not sure about something? 
- Check the [documentation](docs/)
- Open a [discussion](https://github.com/k-dot-greyz/zenOS/discussions)
- Ask in your PR - we're here to help!

---

Thank you for contributing to zenOS! Your efforts help make AI workflows more accessible and zen for everyone. 🧘✨