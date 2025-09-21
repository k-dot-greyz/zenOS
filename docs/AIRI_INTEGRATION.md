# 🌉 airi-zenOS Integration Guide

## Overview

The airi-zenOS bridge system creates a seamless integration between airi (mobile AI assistant) and zenOS (AI workflow orchestration) on Pixel 9a with Termux. This creates the ultimate mobile AI experience.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Pixel 9a      │    │     Termux      │    │   zenOS Core    │
│                 │    │                 │    │                 │
│  ┌───────────┐  │    │  ┌───────────┐  │    │  ┌───────────┐  │
│  │   airi    │◄─┼────┼──┤  Bridge   │◄─┼────┼──┤   Agent   │  │
│  │ (mobile)  │  │    │  │  System   │  │    │  │  System   │  │
│  └───────────┘  │    │  └───────────┘  │    │  └───────────┘  │
│                 │    │                 │    │                 │
│  ┌───────────┐  │    │  ┌───────────┐  │    │  ┌───────────┐  │
│  │Termux API │  │    │  │  Voice    │  │    │  │  Mobile   │  │
│  │(voice,etc)│  │    │  │  Bridge   │  │    │  │  Adapter  │  │
│  └───────────┘  │    │  └───────────┘  │    │  └───────────┘  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Quick Setup

### One-Line Installation

```bash
# Complete setup in one command
curl -sSL https://raw.githubusercontent.com/kasparsgreizis/zenOS/main/scripts/ultimate-bridge-setup.sh | bash
```

### Manual Setup

1. **Install zenOS**:
   ```bash
   curl -sSL https://raw.githubusercontent.com/kasparsgreizis/zenOS/main/scripts/termux-install.sh | bash
   ```

2. **Install airi**:
   ```bash
   pkg install proot-distro
   proot-distro install airi
   ```

3. **Install offline models**:
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ollama pull phi-2 tinyllama qwen:0.5b
   ```

## Usage

### Basic Commands

```bash
# Main bridge interface
zen "your question"

# Voice input
zen voice "speak your question"

# Offline processing
zen offline "work without internet"

# airi integration
zen airi "enhanced mobile processing"

# Interactive mode
zen interactive
```

### Mobile-Specific Features

```bash
# Voice shortcuts
zen-voice "quick voice question"
zen-clip  # Process clipboard content

# Battery-aware mode
zen-eco "optimize for battery"

# Context-aware processing
zen-context  # Show mobile context
zen-status   # Check system status
```

## Bridge Components

### 1. Main Bridge (`airi-zenos-bridge.sh`)
- Seamless airi-zenOS integration
- Mobile context awareness
- Smart caching and error handling
- Interactive and command-line modes

### 2. Voice Bridge (`voice-bridge.sh`)
- Voice input/output handling
- Termux API integration
- Continuous voice mode
- Quick voice commands

### 3. Offline Bridge (`offline-bridge.sh`)
- Local AI model processing
- Ollama integration
- Mobile-optimized models
- Smart caching system

### 4. Mobile Adapter (`zen/ai/mobile_adapter.py`)
- Python class for mobile AI processing
- Termux API integration
- Context-aware processing
- Voice processing pipeline

## Configuration

### Environment Variables

```bash
# Mobile optimizations
export COMPACT_MODE=1
export ZEN_CACHE_DIR=~/.zen-cache
export ZEN_MAX_TOKENS=800

# Offline mode
export ZEN_PREFER_OFFLINE=true
export ZEN_OFFLINE_MODEL=phi-2

# Voice settings
export ZEN_VOICE_ENABLED=true
export ZEN_TTS_ENABLED=true
```

### Mobile Context

The system automatically detects:
- Battery level
- Device location
- Clipboard content
- Internet connectivity
- Charging status

## Troubleshooting

### Common Issues

1. **"Permission Denied"**:
   ```bash
   chmod +x ~/zen-mobile
   chmod +x ~/zenOS/scripts/*.sh
   ```

2. **"Module Not Found"**:
   ```bash
   cd ~/zenOS
   pip install --upgrade -e .
   ```

3. **"API Key Invalid"**:
   ```bash
   nano ~/zenOS/.env
   # Add your OpenRouter API key
   ```

4. **Voice not working**:
   ```bash
   pkg install termux-api
   # Install Termux:API app from F-Droid
   ```

### Performance Issues

```bash
# Use lighter model
export ZEN_DEFAULT_MODEL="claude-3-haiku"

# Reduce context
export ZEN_MAX_CONTEXT_TOKENS=2000

# Enable eco mode
zen --eco "your question"
```

## Advanced Usage

### Custom Mobile Procedures

Create mobile-specific procedures in `procedures/mobile/`:

```yaml
procedure:
  id: "zen.mobile.voice_note"
  name: "Voice Note Taking"
  description: "Take voice notes with mobile optimization"
  
  mobile_optimizations:
    voice_input: true
    battery_aware: true
    offline_capable: true
    
  steps:
    - id: "voice_input"
      action: "termux.speech_to_text"
    - id: "process_note"
      action: "zenos.process"
      params:
        input: "${steps.voice_input.output}"
    - id: "save_note"
      action: "mobile.save_note"
```

### Integration with Other Tools

```bash
# SSH access from desktop
ssh u0_aXXX@<phone-ip> -p 8022

# Remote zenOS access
export ZEN_REMOTE_HOST="192.168.1.100:7777"
zen "using desktop compute"
```

## Best Practices

1. **Battery Management**: Use eco mode when battery is low
2. **Offline First**: Pre-download models on WiFi
3. **Voice Commands**: Use voice for quick interactions
4. **Context Awareness**: Let the system adapt to your environment
5. **Caching**: Enable response caching for offline access

## Support

- **Issues**: [GitHub Issues](https://github.com/kasparsgreizis/zenOS/issues)
- **Discussions**: [GitHub Discussions](https://github.com/kasparsgreizis/zenOS/discussions)
- **Documentation**: [zenOS Docs](https://zenos.ai/docs)

---

**Welcome to the future of mobile AI! 🧘🤖📱**
