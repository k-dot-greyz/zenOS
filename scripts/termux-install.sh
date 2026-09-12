#!/data/data/com.termux/files/usr/bin/bash
#
# zenOS Termux Native Installer
# One-liner installer for zenOS on Termux
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Fancy banner
echo -e "${CYAN}"
cat << "EOF"
    ███████╗███████╗███╗   ██╗ ██████╗ ███████╗
    ╚══███╔╝██╔════╝████╗  ██║██╔═══██╗██╔════╝
      ███╔╝ █████╗  ██╔██╗ ██║██║   ██║███████╗
     ███╔╝  ██╔══╝  ██║╚██╗██║██║   ██║╚════██║
    ███████╗███████╗██║ ╚████║╚██████╔╝███████║
    ╚══════╝╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝
                    Mobile Edition
EOF
echo -e "${NC}"

echo -e "${BLUE}🚀 Installing zenOS on Termux...${NC}\n"

# Check if running on Termux
if [ ! -d "/data/data/com.termux" ]; then
    echo -e "${RED}❌ This script is designed for Termux!${NC}"
    echo "Please run this on your Android device with Termux installed."
    exit 1
fi

# Update packages
echo -e "${YELLOW}📦 Updating Termux packages...${NC}"
pkg update -y && pkg upgrade -y

# Install required packages
echo -e "${YELLOW}📦 Installing dependencies...${NC}"
pkg install -y python git nano curl wget openssh termux-api termux-tools

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo -e "${YELLOW}📦 Installing pip...${NC}"
    pkg install -y python-pip
fi

# Clone zenOS
echo -e "${YELLOW}📥 Cloning zenOS...${NC}"
if [ -d "$HOME/zenOS" ]; then
    echo -e "${BLUE}Found existing zenOS installation, updating...${NC}"
    cd $HOME/zenOS
    git pull
else
    cd $HOME
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    # shellcheck source=zenos-origin.sh
    . "$SCRIPT_DIR/zenos-origin.sh"
    clone_url="$(zenos_github_clone_url)" || {
        echo "GitHub origin is not configured. Clone this repo or set ZENOS_GITHUB_OWNER in .env."
        exit 1
    }
    git clone "$clone_url" zenOS
fi

cd $HOME/zenOS
# Always load origin from the checkout so key writes work on update AND first clone.
# shellcheck source=zenos-origin.sh
. "$HOME/zenOS/scripts/zenos-origin.sh"

# Install Python dependencies
echo -e "${YELLOW}🐍 Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -e .

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}📝 Creating .env file...${NC}"
    cp env.example .env
    
    echo -e "${CYAN}"
    echo "================================================================"
    echo "  IMPORTANT: You need to add your OpenRouter API key!"
    echo "================================================================"
    echo -e "${NC}"
    echo "Get your key at: https://openrouter.ai/keys"
    echo ""
    echo "Would you like to add it now? (y/n)"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "Please enter your OpenRouter API key:"
        read -r api_key
        zenos_set_dotenv_value OPENROUTER_API_KEY "$api_key" .env
        echo -e "${GREEN}✅ API key saved!${NC}"
    else
        echo -e "${YELLOW}⚠️  Remember to add your API key to ~/zenOS/.env later!${NC}"
    fi
else
    echo -e "${GREEN}✅ .env file already exists${NC}"
fi

# Create the launcher script
echo -e "${YELLOW}🚀 Creating launcher script...${NC}"
cat > $HOME/zen << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
# zenOS Mobile Launcher

# Set mobile optimizations
export COMPACT_MODE=1
export TERMUX_VERSION=1
export COLUMNS=$(tput cols)
export LINES=$(tput lines)

# Cache directory for offline access
export ZEN_CACHE_DIR=$HOME/.zen-cache
mkdir -p $ZEN_CACHE_DIR

# Handle arguments
if [ -n "$1" ]; then
    # Direct command mode
    cd $HOME/zenOS && python -m zen.cli chat "$@"
else
    # Interactive mode
    cd $HOME/zenOS && python -m zen.cli chat
fi
EOF

chmod +x $HOME/zen

# Add to PATH
if ! grep -q 'export PATH="$HOME:$PATH"' $HOME/.bashrc; then
    echo 'export PATH="$HOME:$PATH"' >> $HOME/.bashrc
fi

# Create shortcuts directory
echo -e "${YELLOW}📱 Setting up Termux widgets...${NC}"
mkdir -p $HOME/.shortcuts
mkdir -p $HOME/.shortcuts/icons

# Chat widget
cat > $HOME/.shortcuts/ZenChat << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd $HOME/zenOS && python -m zen.cli chat
EOF
chmod +x $HOME/.shortcuts/ZenChat

# Voice widget
cat > $HOME/.shortcuts/ZenVoice << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
TEXT=$(termux-speech-to-text)
if [ -n "$TEXT" ]; then
    cd $HOME/zenOS && python -m zen.cli chat "$TEXT"
fi
EOF
chmod +x $HOME/.shortcuts/ZenVoice

# Clipboard widget
cat > $HOME/.shortcuts/ZenClipboard << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
TEXT=$(termux-clipboard-get)
if [ -n "$TEXT" ]; then
    cd $HOME/zenOS && python -m zen.cli chat "$TEXT"
fi
EOF
chmod +x $HOME/.shortcuts/ZenClipboard

# Create mobile config
echo -e "${YELLOW}⚙️  Setting up mobile configuration...${NC}"
cat > $HOME/.zenrc << 'EOF'
# zenOS Mobile Configuration

# Performance optimizations
export COMPACT_MODE=1
export TERMUX_VERSION=1
export ZEN_CACHE_DIR=$HOME/.zen-cache
export ZEN_MAX_TOKENS=800
export ZEN_DEFAULT_MODEL="claude-3-haiku"  # Fast on mobile

# Aliases for quick access
alias z='zen'
alias zh='zen --model claude-3-haiku'    # Fast mode
alias zs='zen --model claude-3-sonnet'   # Balanced
alias zo='zen --model claude-3-opus'     # Power mode
alias zg='zen --model gpt-3.5-turbo'     # GPT mode

# Quick functions
zv() {
    # Voice input
    echo "🎤 Listening..."
    TEXT=$(termux-speech-to-text)
    if [ -n "$TEXT" ]; then
        echo "You said: $TEXT"
        zen "$TEXT"
    fi
}

zc() {
    # Clipboard input
    TEXT=$(termux-clipboard-get)
    if [ -n "$TEXT" ]; then
        zen "$TEXT"
    fi
}

zn() {
    # With notification
    RESULT=$(zen "$@")
    echo "$RESULT"
    termux-notification \
        --title "🧘 zenOS" \
        --content "Query complete" \
        --action "termux-share"
}

# Battery-aware mode
zen-eco() {
    BATTERY=$(termux-battery-status | grep percentage | sed 's/[^0-9]//g')
    if [ "$BATTERY" -lt 30 ]; then
        echo "⚠️  Low battery ($BATTERY%) - using efficient mode"
        zen --model claude-3-haiku "$@"
    else
        zen "$@"
    fi
}

# Welcome message
echo "🧘 zenOS Mobile Ready! Type 'z' to start chatting."
echo "   Quick tips: zv = voice, zc = clipboard, zh = fast mode"
EOF

# Add to bashrc if not already there
if ! grep -q 'source $HOME/.zenrc' $HOME/.bashrc; then
    echo 'source $HOME/.zenrc' >> $HOME/.bashrc
fi

# Setup storage access
echo -e "${YELLOW}📱 Setting up storage access...${NC}"
termux-setup-storage 2>/dev/null || true

# Enable wake lock
echo -e "${YELLOW}🔋 Enabling wake lock...${NC}"
termux-wake-lock 2>/dev/null || true

# Test the installation
echo -e "${YELLOW}🧪 Testing installation...${NC}"
if python -c "import zen" 2>/dev/null; then
    echo -e "${GREEN}✅ Python module installed correctly${NC}"
else
    echo -e "${RED}❌ Python module installation failed${NC}"
    echo "Trying to fix..."
    cd $HOME/zenOS && pip install --force-reinstall -e .
fi

# Final message
echo -e "\n${GREEN}"
echo "================================================================"
echo "                    🎉 Installation Complete! 🎉"
echo "================================================================"
echo -e "${NC}"
echo -e "${CYAN}Quick Start:${NC}"
echo "  1. Restart Termux or run: ${YELLOW}source ~/.bashrc${NC}"
echo "  2. Type: ${YELLOW}zen${NC} to start chatting"
echo "  3. Or use shortcuts:"
echo "     ${YELLOW}z${NC}  = Quick chat"
echo "     ${YELLOW}zv${NC} = Voice input" 
echo "     ${YELLOW}zc${NC} = Clipboard input"
echo "     ${YELLOW}zh${NC} = Fast mode (Haiku)"
echo ""
echo -e "${CYAN}Widgets:${NC}"
echo "  Add Termux:Widget to your home screen for quick access!"
echo ""
echo -e "${CYAN}API Key:${NC}"
if ! (cd "$HOME/zenOS" && zenos_openrouter_key >/dev/null); then
    echo -e "  ${YELLOW}⚠️  Don't forget to add your OpenRouter API key!${NC}"
    echo "  Edit: ${YELLOW}nano ~/zenOS/.env${NC}"
    echo "  Get key at: https://openrouter.ai/keys"
else
    echo -e "  ${GREEN}✅ API key configured${NC}"
fi
echo ""
echo -e "${GREEN}Enjoy zenOS on mobile! 🧘📱${NC}"
echo ""

# Offer to start immediately
echo "Would you like to start zenOS now? (y/n)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    source $HOME/.bashrc
    exec $HOME/zen
fi
