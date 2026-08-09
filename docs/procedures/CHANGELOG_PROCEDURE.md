# 📋 zenOS Changelog & Release Procedure

## Overview

This document defines how we maintain version history, create releases, and communicate changes in zenOS.

## 🎯 Philosophy

In keeping with the Zen philosophy:
- **Automate everything possible** - Let tools handle the tedious parts
- **Clear communication** - Make changes discoverable and understandable
- **Minimal cognitive load** - Simple, memorable conventions
- **Progressive disclosure** - Details when needed, simplicity by default

---

## 📝 Commit Message Convention

We use **Conventional Commits** with zenOS-specific extensions.

### Format
```
<type>(<scope>): <subject>

[optional body]

[optional footer(s)]
```

### Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | ✨ New feature or capability | `feat(cli): add voice input support` |
| `fix` | 🐛 Bug fix | `fix(mobile): resolve Termux compatibility issue` |
| `docs` | 📚 Documentation changes | `docs(readme): update installation instructions` |
| `style` | 💎 Formatting (no code change) | `style(cli): align output columns` |
| `refactor` | ♻️ Code restructuring | `refactor(core): simplify context management` |
| `perf` | ⚡ Performance improvement | `perf(providers): optimize API batching` |
| `test` | 🧪 Test changes | `test(plugins): add integration tests` |
| `build` | 🔧 Build/dependency changes | `build(deps): upgrade openrouter-py to 2.0` |
| `ci` | 🤖 CI/CD changes | `ci(github): add automated testing` |
| `chore` | 🧹 Maintenance tasks | `chore: update .gitignore` |
| **zenOS-Specific Types** | | |
| `mobile` | 📱 Mobile-specific changes | `mobile(termux): add gesture support` |
| `ai` | 🧠 AI/ML related changes | `ai(gemini): implement flash-2.0 model` |
| `plugin` | 🔌 Plugin system changes | `plugin(discovery): add GitHub search` |
| `zen` | 🧘 Workflow improvements | `zen: simplify onboarding flow` |

### Scopes

Common scopes (optional, can use custom):
- `core` - Core framework
- `cli` - Command-line interface
- `ui` - User interface
- `mobile` - Mobile features
- `plugins` - Plugin system
- `providers` - AI providers
- `context` - Context management
- `setup` - Setup/installation
- `docs` - Documentation
- `test` - Testing
- `deps` - Dependencies

### Examples

```bash
# Simple feature
feat: add offline mode support

# Scoped bug fix
fix(mobile): resolve battery optimization in Termux

# Breaking change
feat(api)!: redesign plugin interface

BREAKING CHANGE: Plugin manifest v2 required

# Multiple issues
fix(cli): improve error messages

Fixes #123, #456
```

---

## 🔄 Versioning Strategy

We follow **Semantic Versioning** (SemVer): `MAJOR.MINOR.PATCH`

- **MAJOR** (1.0.0): Breaking changes, major milestones
- **MINOR** (0.1.0): New features, backwards compatible
- **PATCH** (0.0.1): Bug fixes, minor improvements

### Version Bumping Rules

| Commit Type | Version Bump |
|-------------|--------------|
| `fix` | PATCH |
| `feat` | MINOR |
| `BREAKING CHANGE` | MAJOR |
| `perf` | PATCH |
| `docs`, `style`, `refactor`, `test`, `build`, `ci`, `chore` | No bump (unless grouped with release) |

---

## 📋 Changelog Management

### Structure

The `CHANGELOG.md` follows [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
## [Unreleased]
### Added
- New features

### Changed
- Changes to existing features

### Deprecated
- Features marked for removal

### Removed
- Removed features

### Fixed
- Bug fixes

### Security
- Security fixes
```

### Updating the Changelog

#### Option 1: Manual (During Development)
1. Add changes to `[Unreleased]` section as you work
2. Group by category (Added, Changed, Fixed, etc.)
3. Write user-facing descriptions

#### Option 2: Automated (At Release)
```bash
# Generate changelog from commits
npm run changelog

# Or with standard-version
npm run release
```

---

## 🚀 Release Procedure

### Quick Release (Automated)

```bash
# Dry run to preview
npm run release -- --dry-run

# Patch release (0.1.0 -> 0.1.1)
npm run release:patch

# Minor release (0.1.1 -> 0.2.0)
npm run release:minor

# Major release (0.2.0 -> 1.0.0)
npm run release:major

# Custom version
npm run release -- --release-as 2.0.0
```

### Manual Release Process

1. **Update Version**
   ```bash
   # Update pyproject.toml
   # Update package.json (if applicable)
   # Update zen/__init__.py
   ```

2. **Update Changelog**
   - Move `[Unreleased]` items to new version section
   - Add version number and date
   - Add comparison link

3. **Commit Changes**
   ```bash
   git add -A
   git commit -m "chore(release): 🚀 v0.2.0"
   ```

4. **Create Tag**
   ```bash
   git tag -a v0.2.0 -m "Release version 0.2.0"
   ```

5. **Push to Remote**
   ```bash
   git push origin main --tags
   ```

6. **Create GitHub Release**
   - Go to GitHub releases page
   - Create release from tag
   - Copy changelog section as description
   - Attach any binaries if needed

---

## 🤖 Automation Tools

### Commitizen (Interactive Commits)

```bash
# Install globally
npm install -g commitizen
npm install -g cz-conventional-changelog

# Use for commits
git cz
# or
npm run commit
```

### Standard Version (Automated Releases)

```bash
# Install
npm install --save-dev standard-version

# Configure in package.json
"scripts": {
  "release": "standard-version",
  "release:patch": "standard-version --release-as patch",
  "release:minor": "standard-version --release-as minor",
  "release:major": "standard-version --release-as major"
}
```

### Release Please (GitHub Action)

```yaml
# .github/workflows/release-please.yml
name: Release Please

on:
  push:
    branches:
      - main

jobs:
  release-please:
    runs-on: ubuntu-latest
    steps:
      - uses: google-github-actions/release-please-action@v3
        with:
          release-type: python
          package-name: zenos
```

---

## 🎨 Customization Points

These are the areas you can customize to match your preferences:

### 1. Commit Types
Edit `.czrc` to modify:
- Type names and descriptions
- Emoji associations
- Custom types for zenOS

### 2. Changelog Format
- Section headers
- Grouping strategy
- Description style

### 3. Version Strategy
- When to bump major/minor/patch
- Pre-release naming (alpha, beta, rc)
- Release branch strategy

### 4. Automation Level
Choose your preferred approach:
- **Full Manual**: Complete control
- **Semi-Automated**: Tool-assisted, human-reviewed
- **Fully Automated**: CI/CD handles everything

---

## 📚 Quick Reference

### Daily Development
```bash
# Make changes
git add .

# Interactive commit
npm run commit
# OR conventional commit
git commit -m "feat(mobile): add gesture support"

# Push to branch
git push origin feature/my-feature
```

### Release Time
```bash
# Check what would happen
npm run release -- --dry-run

# Create release
npm run release

# Push with tags
git push --follow-tags origin main
```

### Emergency Fixes
```bash
# Hotfix commit
git commit -m "fix(critical): resolve data loss issue"

# Fast patch release
npm run release:patch
git push --follow-tags origin main
```

---

## 🔗 Resources

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Semantic Versioning](https://semver.org/)
- [Commitizen](https://github.com/commitizen/cz-cli)
- [Standard Version](https://github.com/conventional-changelog/standard-version)
- [Release Please](https://github.com/googleapis/release-please)

---

## 🧘 The Zen Way

Remember: The best changelog procedure is the one that gets used. Start simple, automate gradually, and adjust based on what actually helps your workflow.

"Perfection is achieved not when there is nothing more to add, but when there is nothing left to take away." - Antoine de Saint-Exupéry