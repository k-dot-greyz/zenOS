# 🧘 zenOS Quick Start for Linux/WSL
## The "Linux Chad" Edition

### What You Need
- Linux/WSL with Docker installed
- An OpenRouter API key
- A terminal that doesn't suck (so... any Linux terminal)

---

## Step 0: Make Sure Docker Works (WSL only)
```bash
# Check if Docker is running
docker --version

# If not, install it (Ubuntu/Debian)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add yourself to docker group (no more sudo!)
sudo usermod -aG docker $USER
newgrp docker
```

---

## Step 1: Get Your AI Key (2 min)
```bash
# Open browser from terminal like a boss
xdg-open https://openrouter.ai/keys 2>/dev/null || echo "Go to https://openrouter.ai/keys"
```
1. Sign up (free $5 credit)
2. Create a key
3. Copy the `sk-or-v1-...` key

---

## Step 2: One-Line Install (30 seconds)
```bash
# Clone and enter
git clone https://github.com/kasparsgreizis/zenOS.git && cd zenOS

# Setup your key (replace YOUR_KEY_HERE with your actual key)
cp env.example .env && sed -i 's/sk-or-v1-your-api-key-here/YOUR_KEY_HERE/' .env

# Or if you want to edit manually
nano .env  # or vim if you're hardcore
```

---

## Step 3: Launch (1 minute)
```bash
# Make script executable and run
chmod +x start.sh
./start.sh

# Or just docker-compose directly
docker-compose up -d
```

---

## Step 4: Enter the Zen Zone 🧘
```bash
# Jump straight into chat
docker-compose exec zen-cli bash

# Or even better - alias it!
alias zen='docker-compose -f ~/zenOS/docker-compose.yml exec zen-cli bash'
```

Now you're chatting! No bullshit, just AI.

---

## 🚀 Power User Setup (Optional)

### Add to your `.bashrc` or `.zshrc`:
```bash
# zenOS aliases
alias zen='cd ~/zenOS && docker-compose exec zen-cli bash'
alias zen-up='cd ~/zenOS && docker-compose up -d'
alias zen-down='cd ~/zenOS && docker-compose down'
alias zen-logs='cd ~/zenOS && docker-compose logs -f zen-cli'
alias zen-cost='cd ~/zenOS && docker-compose exec zen-cli python -c "print(\"Check /cost in chat\")"'

# Quick model switcher
zen-opus() {
    cd ~/zenOS && docker-compose exec zen-cli bash -c "echo '/model opus' | python -m zen.cli chat"
}
```

### Even Faster Setup Script:
```bash
# Save this as setup-zen.sh
#!/bin/bash
set -e

echo "🧘 Setting up zenOS..."

# Clone
git clone https://github.com/kasparsgreizis/zenOS.git ~/zenOS
cd ~/zenOS

# Get API key
echo "Enter your OpenRouter API key (sk-or-v1-...):"
read -s API_KEY

# Setup env
cp env.example .env
sed -i "s/sk-or-v1-your-api-key-here/$API_KEY/" .env

# Start
docker-compose up -d

echo "✨ Ready! Run: docker-compose exec zen-cli bash"
```

---

## 🎮 Inside Chat Commands

| Command | What it Does | Cost |
|---------|-------------|------|
| `/model haiku` | Fast & cheap | $0.001/msg |
| `/model sonnet` | Balanced (default) | $0.01/msg |
| `/model opus` | Big brain mode | $0.05/msg |
| `/context file.py` | Add file to convo | Free |
| `/cost` | See damage to wallet | Free |
| `/save` | Save conversation | Free |
| `Ctrl+D` | GTFO | Free |

---

## 🔥 WSL-Specific Tips

### Docker Desktop Integration
If using Docker Desktop on Windows with WSL2:
```bash
# Check if Docker Desktop is integrated
docker context ls

# Should show "default" pointing to Docker Desktop
```

### File Access from Windows
```bash
# Your zenOS is at:
# Windows: \\wsl$\Ubuntu\home\YOUR_USER\zenOS
# WSL: ~/zenOS

# Open in Windows Explorer from WSL
explorer.exe .
```

### Performance Boost
```bash
# Add to .wslconfig in Windows user folder
[wsl2]
memory=8GB
processors=4
swap=2GB
```

---

## 🛠️ Troubleshooting

### "Cannot connect to Docker daemon"
```bash
# Start Docker service
sudo service docker start

# Or if using Docker Desktop, make sure it's running on Windows
```

### "Permission denied"
```bash
# Fix docker permissions
sudo usermod -aG docker $USER
newgrp docker
```

### "Port already in use"
```bash
# Kill whatever's using the ports
docker-compose down
docker system prune -a  # Nuclear option
```

---

## 🎯 That's It!

You now have a LOCAL AI that:
- Runs in Docker (no Python dependency hell)
- Uses ANY model via OpenRouter
- Costs pennies instead of $20/month
- Works offline (after first pull)
- Has a beautiful terminal UI

**Linux/WSL Master Race!** 🐧✨

---

## Bonus: Make it Even Better

```bash
# Install rich terminal stuff
pip install rich prompt-toolkit

# Get better terminal (if on WSL)
sudo apt install zsh oh-my-zsh terminator

# Peak aesthetics
echo "Welcome to zenOS 🧘" | cowsay | lolcat
```
