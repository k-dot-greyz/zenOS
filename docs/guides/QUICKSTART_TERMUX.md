# 🚀 zenOS on Termux - Native Mobile Power
## Because Your Phone IS a Computer

### Why Termux Native?
Forget the proot/Arch complexity. Let's run zenOS directly on Termux - fast, native, and powerful. Your Pixel/Samsung/Whatever is basically a Linux box with a touchscreen.

---

## 🎯 One-Line Install (The Dream)
```bash
# Complete airi-zenOS bridge setup
curl -sSL https://raw.githubusercontent.com/kasparsgreizis/zenOS/main/scripts/ultimate-bridge-setup.sh | bash
```

**What this installs:**
- ✅ zenOS core system
- ✅ airi integration
- ✅ Voice bridge system
- ✅ Offline AI models
- ✅ Mobile optimizations
- ✅ All shortcuts and aliases

---

## 📱 Manual Setup (5 Minutes Max)

### Step 1: Update Termux
```bash
# Get the latest packages
pkg update && pkg upgrade -y

# Install essentials
pkg install -y python git termux-api termux-tools openssh
```

### Step 2: Clone & Setup zenOS
```bash
# Clone the repo
git clone https://github.com/kasparsgreizis/zenOS.git
cd zenOS

# Install Python dependencies
pip install -e .

# Setup your API key
cp env.example .env
# Use nano or vim to add your OpenRouter key
nano .env
```

### Step 2.5: Install airi (Mobile AI Assistant)
```bash
# Install airi for mobile AI integration
pkg install proot-distro
proot-distro install airi
```

### Step 2.6: Install Offline Models
```bash
# Install Ollama for local AI processing
curl -fsSL https://ollama.ai/install.sh | sh

# Download mobile-optimized models
ollama pull phi-2        # 1.6GB - Perfect for Pixel 9a
ollama pull tinyllama    # 637MB - Ultra-lightweight
ollama pull qwen:0.5b    # 395MB - Minimal but capable
```

### Step 3: Termux Optimizations
```bash
# Enable wake lock (keep running when screen off)
termux-wake-lock

# Setup storage access
termux-setup-storage

# Optional: Setup SSH for remote access
sshd
# Now you can SSH from your laptop: ssh u0_aXXX@<phone-ip> -p 8022
```

---

## ⚡ Quick Launch Scripts

### Create the Ultimate Launcher
```bash
cat > ~/zen << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
# zenOS Mobile Launcher

# Auto-detect best mode
if [ -n "$1" ]; then
    # Direct command mode
    cd ~/zenOS && python -m zen.cli chat "$@"
else
    # Interactive mode with mobile UI
    export COMPACT_MODE=1
    export TERMUX_VERSION=1
    cd ~/zenOS && python -m zen.cli chat
fi
EOF

chmod +x ~/zen
```

### Add to PATH
```bash
echo 'export PATH="$HOME:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Now just type 'zen' from anywhere!
zen "explain quantum computing"

# New bridge system commands!
zen voice "speak your question"     # Voice input
zen offline "work without internet" # Offline mode
zen airi "enhanced processing"      # airi integration
zen interactive                     # Full bridge mode
```

---

## 🔥 Termux API Integration

### Voice Input
```bash
# Install Termux:API app from F-Droid first!
pkg install termux-api

# Voice-to-zenOS
zen-voice() {
    echo "🎤 Listening..."
    TEXT=$(termux-speech-to-text)
    echo "You said: $TEXT"
    zen "$TEXT"
}
```

### Clipboard Integration
```bash
# Send clipboard to zenOS
zen-clip() {
    termux-clipboard-get | zen
}

# Copy zenOS output
zen "$1" | termux-clipboard-set
```

### Notification When Done
```bash
# Long-running queries with notification
zen-notify() {
    RESULT=$(zen "$1")
    echo "$RESULT"
    termux-notification \
        --title "🧘 zenOS Complete" \
        --content "${RESULT:0:100}..." \
        --action "termux-clipboard-set '$RESULT'"
}
```

### Share Sheet Integration
```bash
# Add to ~/.termux/termux-url-opener
#!/data/data/com.termux/files/usr/bin/bash
# Send shared URLs/text to zenOS
echo "$1" | ~/zen "summarize this: $1"
```

---

## 📊 Performance Optimizations

### 1. Use Lighter Models on Mobile
```bash
# Add to ~/.bashrc
alias zenh='zen --model claude-3-haiku'  # Fast & cheap
alias zens='zen --model claude-3-sonnet'  # Balanced
alias zeno='zen --model claude-3-opus'    # When you need power
```

### 2. Response Caching
```bash
# Cache responses locally for offline access
mkdir -p ~/.zen-cache
export ZEN_CACHE_DIR=~/.zen-cache
```

### 3. Background Processing
```bash
# Run in background with tmux
pkg install tmux

# Start background session
tmux new -d -s zen "zen 'your long query here'"

# Check later
tmux attach -t zen
```

---

## 🎮 Widget & Shortcuts

### Termux:Widget Setup
```bash
# Create shortcuts folder
mkdir -p ~/.shortcuts
mkdir -p ~/.shortcuts/icons

# Quick Chat
cat > ~/.shortcuts/ZenChat << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/zenOS && python -m zen.cli chat
EOF

# Voice Input
cat > ~/.shortcuts/ZenVoice << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
TEXT=$(termux-speech-to-text)
cd ~/zenOS && python -m zen.cli chat "$TEXT"
EOF

chmod +x ~/.shortcuts/*
```

Now add Termux widgets to your home screen!

---

## 🔋 Battery & Data Optimizations

### Aggressive Power Saving
```bash
# Use local models when on battery
zen-eco() {
    if [ $(termux-battery-status | grep percentage | cut -d: -f2) -lt 30 ]; then
        echo "⚠️ Low battery - using cheap model"
        zen --model claude-3-haiku "$@"
    else
        zen "$@"
    fi
}
```

### Data Saver Mode
```bash
# Compress responses for mobile data
export ZEN_COMPRESS_RESPONSES=1
export ZEN_MAX_TOKENS=500  # Shorter responses on mobile
```

---

## 🌐 Remote zenOS Access

### Option 1: Use Your Desktop as Backend
```bash
# On desktop, expose zenOS API
cd ~/zenOS
python -m zen.core.api --host 0.0.0.0 --port 7777

# On phone, connect to desktop
export ZEN_REMOTE_HOST="192.168.1.100:7777"
zen "now using desktop compute!"
```

### Option 2: Reverse SSH Tunnel
```bash
# Access home zenOS from anywhere
ssh -R 7777:localhost:7777 your-vps.com

# Now on phone
ssh your-vps.com -L 7777:localhost:7777
export ZEN_REMOTE_HOST="localhost:7777"
```

---

## 🎯 The Ultimate Mobile Setup

### All-in-One Config
```bash
cat > ~/.zenrc << 'EOF'
# zenOS Mobile Config

# Performance
export COMPACT_MODE=1
export ZEN_CACHE_DIR=~/.zen-cache
export ZEN_MAX_TOKENS=800

# Aliases
alias z='zen'
alias zh='zen --model claude-3-haiku'
alias zs='zen --model claude-3-sonnet'
alias zo='zen --model claude-3-opus'

# Functions
zv() { termux-speech-to-text | zen "$@"; }
zc() { termux-clipboard-get | zen "$@"; }
zn() { zen "$@" && termux-notification --title "zenOS" --content "Done!"; }

# Auto-complete
complete -W "chat help models context save reset exit" zen

echo "🧘 zenOS Mobile Ready!"
EOF

echo "source ~/.zenrc" >> ~/.bashrc
```

---

## 📱 Touch-Friendly Tips

### Swipe Gestures (in Termux)
- **Two-finger swipe up/down**: Scroll history
- **Pinch zoom**: Adjust font size
- **Long press**: Copy mode
- **Volume down + Q**: Quick escape

### Quick Commands
```bash
# Single letters for common tasks
alias q='zen "quick question: "'
alias e='zen "explain: "'
alias d='zen "debug this: "'
alias c='zen "write code for: "'
```

---

## 🚀 True Offline Mode - No Internet Required!

### One-Line Offline Setup
```bash
# Automatic offline setup with model download
curl -sSL https://raw.githubusercontent.com/kasparsgreizis/zenOS/main/scripts/setup-offline.sh | bash
```

### What This Does
1. ✅ Installs Ollama (or llama.cpp as fallback)
2. ✅ Downloads mobile-optimized models
3. ✅ Creates offline launcher (`zen-offline`)
4. ✅ Configures automatic fallback

### Recommended Models by Device

#### Low-End Phones (< 2GB RAM)
```bash
ollama pull qwen:0.5b    # 395MB - Tiny but capable
ollama pull tinyllama     # 637MB - Best tiny model
```

#### Mid-Range Phones (2-4GB RAM)  
```bash
ollama pull phi-2         # 1.6GB - Best quality/size ratio
ollama pull gemma:2b      # 1.4GB - Google's efficient model
ollama pull stablelm2:1.6b # 980MB - Good balance
```

#### Flagship Phones (4GB+ RAM)
```bash
ollama pull llama3:3b     # 2GB - Powerful
ollama pull mistral:7b-q4 # 4GB - Desktop quality
```

### Usage Examples

#### Fully Offline Mode
```bash
# Force offline mode (no internet used)
zen --offline "explain quantum computing"

# Use specific local model
zen --offline --model phi-2 "write a python function"

# Offline with voice
zen-voice --offline "tell me a joke"
```

#### Smart Hybrid Mode
```bash
# Uses online when available, falls back to offline
zen "your question"

# Prefer offline when available (saves data)
export ZEN_PREFER_OFFLINE=true
zen "your question"
```

#### Battery-Aware Mode
```bash
# Automatically uses lighter models when battery is low
zen --eco "your question"

# Combines with offline for ultimate efficiency
zen --offline --eco "quick question"
```

### Managing Offline Models

#### List Installed Models
```bash
ollama list

# Or via zenOS
zen --offline --list-models
```

#### Remove Models (Save Space)
```bash
ollama rm model-name
```

#### Update Models
```bash
ollama pull model-name
```

### Offline Performance Tips

1. **Pre-download models on WiFi**
   ```bash
   # Download all mobile models at once
   for model in qwen:0.5b tinyllama phi-2; do
       ollama pull $model
   done
   ```

2. **Use quantized versions**
   ```bash
   # Q4 = 4-bit quantization (smaller, faster)
   ollama pull llama3:7b-q4_0
   ```

3. **Cache responses locally**
   ```bash
   export ZEN_CACHE_DIR=~/.zen-cache
   export ZEN_CACHE_TTL_HOURS=168  # 1 week
   ```

4. **Batch process when online**
   ```bash
   # Process multiple queries when connected
   zen --batch queries.txt > responses.txt
   ```

---

## 🎉 You're Done!

Your phone is now a portable AI powerhouse. You can:
- 💬 Chat with AI anywhere
- 🎤 Use voice input with Termux API
- 📋 Integrate with clipboard
- 🔔 Get notifications
- ⚡ Run offline with local models
- 🌐 Connect to remote backends
- 🌉 Use airi-zenOS bridge system
- 🤖 Process with mobile-optimized AI

**Available Commands:**
```bash
zen                    # Main AI interface
zen voice             # Voice input mode
zen offline           # Offline processing
zen airi              # airi integration
zen interactive       # Full bridge mode
zen status            # Check system status
zen context           # Show mobile context
```

**Welcome to the future, where your phone IS your computer!** 🧘📱

---

## Troubleshooting

### "Permission Denied"
```bash
# Fix permissions
chmod +x ~/zen
chmod -R 755 ~/zenOS
```

### "Module Not Found"
```bash
# Reinstall dependencies
cd ~/zenOS
pip install --upgrade -e .
```

### "API Key Invalid"
```bash
# Check your .env
cat ~/zenOS/.env
# Make sure no quotes around the key!
```

### Performance Issues
```bash
# Use lighter model
export ZEN_DEFAULT_MODEL="claude-3-haiku"

# Reduce context
export ZEN_MAX_CONTEXT_TOKENS=2000
```

---

**Pro Tip**: Star the repo if this made your phone cooler! ⭐
