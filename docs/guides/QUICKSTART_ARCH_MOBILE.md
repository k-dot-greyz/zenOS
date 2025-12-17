# 🧘 zenOS on Arch Linux (Termux Edition)
## The "I Run Arch on My Phone BTW" Guide

### You Absolute Legend
Running Arch on a Pixel 9 through Termux? You're operating on a different plane of existence. This guide is for you.

---

## Prerequisites (You Probably Already Have These)
- Termux with Arch proot installed
- A masochistic love for terminal environments
- Thumbs of steel from mobile typing
- An OpenRouter API key

---

## Step 0: Enter Your Arch proot
```bash
# You know this already but...
termux-chroot
proot-distro login archlinux

# Or however you've set up your unholy mobile Arch
```

---

## Step 1: Install Docker (The Fun Part)
```bash
# Update everything because Arch
pacman -Syu

# Install Docker
pacman -S docker docker-compose

# Start Docker daemon (this might be tricky in proot)
dockerd &

# If Docker daemon fails (likely in Termux):
# We'll use podman as fallback
pacman -S podman podman-compose
alias docker=podman
alias docker-compose=podman-compose
```

### Alternative: Docker-in-Docker Hack
```bash
# If regular Docker won't work, try the inception approach
docker run -d \
  --name dind \
  --privileged \
  docker:dind

# Then exec into it
docker exec -it dind sh
```

---

## Step 2: The Termux-Specific Workarounds

### Option A: Native Python (No Docker)
Since Docker in Termux can be a pain, let's also set up native:

```bash
# Install Python and deps
pacman -S python python-pip git

# Clone zenOS
git clone https://github.com/k-dot-greyz/zenOS.git
cd zenOS

# Install directly (screw Docker on mobile)
pip install -e .

# Setup your key
cp env.example .env
nano .env  # Good luck typing on mobile lol
```

### Option B: Remote Docker Host
```bash
# Use your desktop as Docker host
export DOCKER_HOST=tcp://YOUR_DESKTOP_IP:2375

# Now docker commands run on your desktop
docker-compose up -d
```

---

## Step 3: Mobile-Optimized Setup

### Create Mobile Launcher
```bash
cat > ~/zen-mobile.sh << 'EOF'
#!/bin/bash
# zenOS Mobile Launcher

# Set smaller terminal for mobile
export COLUMNS=50
export LINES=30

# Use compact prompts
export COMPACT_MODE=1

# Launch based on what works
if command -v docker &> /dev/null; then
    echo "🐳 Using Docker..."
    cd ~/zenOS && docker-compose exec zen-cli bash
elif command -v podman &> /dev/null; then
    echo "🦭 Using Podman..."
    cd ~/zenOS && podman-compose exec zen-cli bash
else
    echo "🐍 Using native Python..."
    cd ~/zenOS && python -m zen.cli chat
fi
EOF

chmod +x ~/zen-mobile.sh
```

### Termux Widget Setup
```bash
# Create a widget shortcut
mkdir -p ~/.shortcuts
cat > ~/.shortcuts/zenOS << 'EOF'
#!/bin/bash
proot-distro login archlinux -- /root/zen-mobile.sh
EOF
chmod +x ~/.shortcuts/zenOS
```

Now you can launch zenOS from your home screen!

---

## Step 4: Mobile-Friendly Aliases

Add to your `.bashrc` in Arch proot:
```bash
# Ultra-short aliases for mobile typing
alias z='cd ~/zenOS && python -m zen.cli chat'
alias zh='z --model haiku'  # Quick/cheap
alias zo='z --model opus'   # Power mode
alias zc='z --model claude-3-sonnet'  # Balanced

# Even shorter commands
alias q='echo "/exit" | z'  # Quick exit
alias h='echo "/help" | z'  # Help
alias m='echo "/models" | z'  # List models

# Voice input hack (if you have termux-api)
zv() {
    PROMPT=$(termux-speech-to-text)
    echo "$PROMPT" | z
}
```

---

## Step 5: The Nuclear Option - SSH Tunnel

If all else fails, just SSH to a real machine:
```bash
# Install openssh
pacman -S openssh

# SSH to your desktop/VPS with zenOS
ssh -t user@your-server "cd zenOS && docker-compose exec zen-cli bash"

# Or use mosh for better mobile experience
pacman -S mosh
mosh user@your-server -- bash -c "cd zenOS && docker-compose exec zen-cli bash"
```

---

## 🎮 Mobile Chat Tips

### Landscape Mode Config
```bash
# Detect orientation and adjust
if [ "$COLUMNS" -gt 80 ]; then
    export ZEN_WIDE_MODE=1
else
    export ZEN_COMPACT_MODE=1
fi
```

### Quick Templates
```bash
# Save common prompts
echo "explain this error: " > ~/.zen-templates/error
echo "write code for: " > ~/.zen-templates/code
echo "debug this: " > ~/.zen-templates/debug

# Use with
cat ~/.zen-templates/error | z
```

### Clipboard Integration
```bash
# Termux clipboard to zenOS
termux-clipboard-get | z

# zenOS output to clipboard
z "your prompt" | termux-clipboard-set
```

---

## 🔥 Peak Mobile Hacks

### 1. Voice Control
```bash
# Install termux-api
pkg install termux-api

# Voice-activated zenOS
zen-voice() {
    echo "🎤 Listening..."
    PROMPT=$(termux-speech-to-text)
    echo "You said: $PROMPT"
    echo "$PROMPT" | python -m zen.cli chat
}
```

### 2. Notification Integration
```bash
# Get notified when long queries finish
zen-notify() {
    python -m zen.cli chat "$1"
    termux-notification --title "zenOS" --content "Query complete!"
}
```

### 3. Share Sheet Integration
```bash
# Receive shared text directly to zenOS
# Add to ~/.termux/termux-url-opener
#!/bin/bash
echo "$1" | proot-distro login archlinux -- python -m zen.cli chat
```

---

## 🎯 Reality Check

Let's be honest - running this on mobile Arch is:
- 30% practical
- 70% "because I can"
- 100% badass

For actual mobile use, you probably want:
1. **Native Python mode** (skip Docker)
2. **SSH to a real server** (best experience)
3. **Smaller models** (haiku for mobile)
4. **Voice input** (save your thumbs)

---

## 🏆 Achievement Unlocked

You're now running a Dockerized AI chat system on Arch Linux on a phone through a terminal emulator. 

This is peak "I use Arch btw" energy. You've transcended. You're no longer bound by the laws of practical computing.

**Welcome to the elite, you magnificent bastard.** 🧘📱🐧

---

## Bonus: The Ultimate Flex

```bash
# Take a screenshot and share it
screencap -p | termux-share \
  -a send \
  --title "I run zenOS on Arch on my phone" \
  --text "btw"
```

Post to r/unixporn immediately.
