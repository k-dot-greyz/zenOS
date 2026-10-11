# zenOS Tools

Utilities and automation tools for the zenOS ecosystem.

## Post Template Selector

**🎭 Interactive CLI tool for AI-generated social media post templates**

### Quick Start

```bash
cd tools/
python3 post_template_selector.py
```

### Features

- **Cross-platform clipboard support** (macOS, Linux, Windows)
- **Interactive template selection** with live preview
- **Three persona templates** from the AI post template library
- **Graceful error handling** with manual copy fallback
- **zenOS integration** ready

### Templates Available

1. **Engineer's Log** - Classic humble brag style
2. **Alchemist's Field Notes** - Philosophical reflection approach
3. **Overlord's Decree** - Pure, unfiltered confidence

### Prerequisites

- Python 3.6+
- PyYAML (`pip install pyyaml`)
- Clipboard utilities (auto-detected):
  - **macOS**: `pbcopy` (built-in)
  - **Linux**: `xclip` or `xsel`
  - **Windows**: `clip` (built-in)

### Linux Setup

```bash
# Ubuntu/Debian
sudo apt install xclip

# Fedora/RHEL
sudo dnf install xclip

# Arch
sudo pacman -S xclip
```

### Usage Examples

#### Basic Usage

```bash
$ python3 post_template_selector.py
🚀 Loading zenOS AI Post Templates...

🎭 zenOS AI Post Template Selector
==================================================
1. Engineer's Log
   📝 Classic Humble Brag

2. Alchemist's Field Notes
   📝 Philosophical Flex

3. Overlord's Decree
   📝 Pure, Unfiltered Chaos

Select template (1-3) or 'q' to quit: 1
```

#### Integration with zenOS Workflows

```bash
# Generate daily briefing and select post template
./daily_briefing.sh && python3 tools/post_template_selector.py
```

### Customization

Edit `../ai_post_templates.yaml` to add new personas or modify existing templates:

```yaml
ai_post_templates:
  your_custom_persona:
    title: Your Custom Persona
    vibe: Your Custom Vibe
    template: Your template text here...
```

### Troubleshooting

**Clipboard not working?**
- Install platform-specific clipboard utility
- Use manual copy mode (script will display text)

**YAML file not found?**
- Ensure `ai_post_templates.yaml` exists in the parent directory
- Check file permissions

**Python dependencies?**
```bash
pip install pyyaml
```

### Integration Ideas

- **GitHub Actions**: Auto-generate posts from repository activity
- **Cron Jobs**: Daily/weekly automated social media content
- **n8n Workflows**: Connect to social media APIs
- **Slack/Discord Bots**: Share templates in team channels

---

*Part of the zenOS ecosystem - where work becomes play* 🧘✨