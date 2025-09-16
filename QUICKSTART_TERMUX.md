# 🚀 zenOS on Termux - Native Mobile Power
## Because Your Phone IS a Computer

### Why Termux Native?
Forget the proot/Arch complexity. Let's run zenOS directly on Termux - fast, native, and powerful. Your Pixel/Samsung/Whatever is basically a Linux box with a touchscreen.

---

## 🎯 One-Line Install (The Dream)
```bash
curl -sSL https://raw.githubusercontent.com/kasparsgreizis/zenOS/main/scripts/termux-install.sh | bash
```

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

## 🚀 Advanced: Local Models

### Install Ollama on Termux
```bash
# This is experimental but works!
pkg install golang
git clone https://github.com/ollama/ollama
cd ollama
go build .
./ollama serve &

# Pull a small model
./ollama pull phi-2

# Configure zenOS to use it
export ZEN_LOCAL_MODEL="ollama:phi-2"
```

---

## 🎉 You're Done!

Your phone is now a portable AI powerhouse. You can:
- 💬 Chat with AI anywhere
- 🎤 Use voice input
- 📋 Integrate with clipboard
- 🔔 Get notifications
- ⚡ Run offline with local models
- 🌐 Connect to remote backends

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
