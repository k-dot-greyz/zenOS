#!/data/data/com.termux/files/usr/bin/bash
# 🌉 Ultimate Bridge Setup - Complete airi-zenOS Integration
# This script sets up the complete mobile AI stack on Pixel 9a

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Configuration
ZENOS_PATH="$HOME/zenOS"
BRIDGE_LOG="$HOME/.ultimate-bridge-setup.log"
CACHE_DIR="$HOME/.airi-zenos-cache"

# Create cache directory
mkdir -p "$CACHE_DIR"

# Logging
log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1" | tee -a "$BRIDGE_LOG"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$BRIDGE_LOG"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$BRIDGE_LOG"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$BRIDGE_LOG"
}

# Banner
show_banner() {
    echo -e "${PURPLE}"
    echo "🌉 ============================================= 🌉"
    echo "   Ultimate airi-zenOS Bridge Setup"
    echo "   Pixel 9a + Termux + airi + zenOS"
    echo "🌉 ============================================= 🌉"
    echo -e "${NC}"
}

# Check Termux environment
check_termux() {
    log "Checking Termux environment..."
    
    if [ ! -d "/data/data/com.termux" ]; then
        log_error "Not running in Termux environment"
        exit 1
    fi
    
    log_success "Termux environment detected"
}

# Update Termux packages
update_termux() {
    log "Updating Termux packages..."
    
    pkg update -y
    pkg upgrade -y
    
    log_success "Termux packages updated"
}

# Install essential packages
install_essentials() {
    log "Installing essential packages..."
    
    local packages=(
        "python"
        "git"
        "curl"
        "wget"
        "nano"
        "vim"
        "tmux"
        "openssh"
        "termux-api"
        "termux-tools"
        "proot-distro"
        "nodejs"
        "jq"
    )
    
    for package in "${packages[@]}"; do
        log "Installing $package..."
        pkg install -y "$package" || log_warning "Failed to install $package"
    done
    
    log_success "Essential packages installed"
}

# Install zenOS
install_zenos() {
    log "Installing zenOS..."
    
    if [ -d "$ZENOS_PATH" ]; then
        log_warning "zenOS already exists, updating..."
        cd "$ZENOS_PATH"
        git pull origin main
    else
        log "Cloning zenOS repository..."
        git clone https://github.com/k-dot-greyz/zenOS.git "$ZENOS_PATH"
    fi
    
    cd "$ZENOS_PATH"
    
    # Install Python dependencies
    log "Installing Python dependencies..."
    pip install -e .
    
    # Setup environment
    if [ ! -f ".env" ]; then
        log "Setting up environment file..."
        cp env.example .env
        log_warning "Please edit .env file with your API keys"
    fi
    
    log_success "zenOS installed successfully"
}

# Install airi
install_airi() {
    log "Installing airi..."
    
    # Check if airi is already installed
    if proot-distro list | grep -q "airi"; then
        log_warning "airi already installed, skipping..."
        return 0
    fi
    
    # Install airi
    proot-distro install airi
    
    if proot-distro list | grep -q "airi"; then
        log_success "airi installed successfully"
    else
        log_error "Failed to install airi"
        return 1
    fi
}

# Install Ollama for offline processing
install_ollama() {
    log "Installing Ollama for offline processing..."
    
    if command -v ollama >/dev/null 2>&1; then
        log_warning "Ollama already installed, skipping..."
        return 0
    fi
    
    # Install Ollama
    curl -fsSL https://ollama.ai/install.sh | sh
    
    if command -v ollama >/dev/null 2>&1; then
        log_success "Ollama installed successfully"
        
        # Install mobile-optimized models
        log "Installing mobile-optimized models..."
        local models=("qwen:0.5b" "tinyllama" "phi-2")
        
        for model in "${models[@]}"; do
            log "Installing model: $model..."
            ollama pull "$model" || log_warning "Failed to install $model"
        done
        
        log_success "Mobile models installed"
    else
        log_error "Failed to install Ollama"
        return 1
    fi
}

# Setup bridge scripts
setup_bridge_scripts() {
    log "Setting up bridge scripts..."
    
    # Make scripts executable
    chmod +x "$ZENOS_PATH/scripts"/*.sh
    
    # Create main launcher
    cat > ~/zen-mobile << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
# Ultimate mobile AI launcher

case "$1" in
    "voice"|"v")
        ~/zenOS/scripts/voice-bridge.sh "${@:2}"
        ;;
    "offline"|"o")
        ~/zenOS/scripts/offline-bridge.sh "${@:2}"
        ;;
    "airi"|"a")
        ~/zenOS/scripts/airi-zenos-bridge.sh "${@:2}"
        ;;
    "interactive"|"i")
        ~/zenOS/scripts/airi-zenos-bridge.sh interactive
        ;;
    "help"|"h")
        echo "zenOS Mobile AI Commands:"
        echo "  zen voice     - Voice input mode"
        echo "  zen offline   - Offline processing mode"
        echo "  zen airi      - airi integration mode"
        echo "  zen interactive - Interactive mode"
        echo "  zen help      - Show this help"
        ;;
    *)
        ~/zenOS/scripts/airi-zenos-bridge.sh "$@"
        ;;
esac
EOF
    
    chmod +x ~/zen-mobile
    
    log_success "Bridge scripts setup complete"
}

# Setup aliases and shortcuts
setup_aliases() {
    log "Setting up aliases and shortcuts..."
    
    # Create alias file
    cat > ~/.zenos-aliases << 'EOF'
# zenOS Mobile AI Aliases

# Main commands
alias zen='zen-mobile'
alias z='zen'
alias zv='zen voice'
alias zo='zen offline'
alias za='zen airi'
alias zi='zen interactive'

# Quick functions
zen-quick() {
    zen "$@" --quick
}

zen-deep() {
    zen "$@" --deep
}

zen-voice() {
    zen voice "$@"
}

zen-offline() {
    zen offline "$@"
}

# Mobile context
zen-context() {
    echo "🔋 Battery: $(termux-battery-status | grep percentage | cut -d: -f2)%"
    echo "📱 Device: Pixel 9a"
    echo "🌐 Internet: $(ping -c 1 8.8.8.8 >/dev/null 2>&1 && echo "✅" || echo "❌")"
    echo "🤖 Models: $(ollama list 2>/dev/null | wc -l) installed"
}

# Status check
zen-status() {
    echo "🌉 airi-zenOS Bridge Status:"
    echo "  zenOS: $(test -d ~/zenOS && echo "✅" || echo "❌")"
    echo "  airi: $(proot-distro list | grep -q airi && echo "✅" || echo "❌")"
    echo "  Ollama: $(command -v ollama >/dev/null && echo "✅" || echo "❌")"
    echo "  Termux API: $(command -v termux-speech-to-text >/dev/null && echo "✅" || echo "❌")"
}

echo "🧘 zenOS Mobile AI Ready!"
EOF
    
    # Add to bashrc
    if ! grep -q "zenos-aliases" ~/.bashrc 2>/dev/null; then
        echo "source ~/.zenos-aliases" >> ~/.bashrc
    fi
    
    # Create shortcuts
    mkdir -p ~/.shortcuts
    mkdir -p ~/.shortcuts/icons
    
    # Voice shortcut
    cat > ~/.shortcuts/ZenVoice << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/zenOS && bash scripts/voice-bridge.sh
EOF
    
    # Offline shortcut
    cat > ~/.shortcuts/ZenOffline << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/zenOS && bash scripts/offline-bridge.sh interactive
EOF
    
    # Interactive shortcut
    cat > ~/.shortcuts/ZenInteractive << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/zenOS && bash scripts/airi-zenos-bridge.sh interactive
EOF
    
    chmod +x ~/.shortcuts/*
    
    log_success "Aliases and shortcuts setup complete"
}

# Setup Termux API
setup_termux_api() {
    log "Setting up Termux API..."
    
    # Enable wake lock
    termux-wake-lock
    
    # Setup storage access
    termux-setup-storage
    
    # Start SSH server
    sshd
    
    log_success "Termux API setup complete"
    log "SSH server started on port 8022"
}

# Test installation
test_installation() {
    log "Testing installation..."
    
    local tests_passed=0
    local total_tests=5
    
    # Test zenOS
    if [ -d "$ZENOS_PATH" ] && [ -f "$ZENOS_PATH/zen/cli.py" ]; then
        log_success "zenOS test passed"
        ((tests_passed++))
    else
        log_error "zenOS test failed"
    fi
    
    # Test airi
    if proot-distro list | grep -q "airi"; then
        log_success "airi test passed"
        ((tests_passed++))
    else
        log_error "airi test failed"
    fi
    
    # Test Ollama
    if command -v ollama >/dev/null 2>&1; then
        log_success "Ollama test passed"
        ((tests_passed++))
    else
        log_error "Ollama test failed"
    fi
    
    # Test Termux API
    if command -v termux-speech-to-text >/dev/null 2>&1; then
        log_success "Termux API test passed"
        ((tests_passed++))
    else
        log_error "Termux API test failed"
    fi
    
    # Test bridge scripts
    if [ -x "$ZENOS_PATH/scripts/airi-zenos-bridge.sh" ]; then
        log_success "Bridge scripts test passed"
        ((tests_passed++))
    else
        log_error "Bridge scripts test failed"
    fi
    
    log "Tests passed: $tests_passed/$total_tests"
    
    if [ $tests_passed -eq $total_tests ]; then
        log_success "All tests passed! Installation complete!"
        return 0
    else
        log_warning "Some tests failed. Check the logs for details."
        return 1
    fi
}

# Show completion message
show_completion() {
    echo -e "${GREEN}"
    echo "🎉 ============================================= 🎉"
    echo "   Ultimate airi-zenOS Bridge Setup Complete!"
    echo "🎉 ============================================= 🎉"
    echo -e "${NC}"
    
    echo -e "${CYAN}Your Pixel 9a is now a mobile AI powerhouse!${NC}"
    echo ""
    echo -e "${YELLOW}Available commands:${NC}"
    echo "  zen                    - Main AI interface"
    echo "  zen voice             - Voice input mode"
    echo "  zen offline           - Offline processing"
    echo "  zen airi              - airi integration"
    echo "  zen interactive       - Interactive mode"
    echo "  zen status            - Check system status"
    echo "  zen context           - Show mobile context"
    echo ""
    echo -e "${YELLOW}Shortcuts available in Termux widgets!${NC}"
    echo -e "${BLUE}Add Termux widgets to your home screen for quick access.${NC}"
    echo ""
    echo -e "${PURPLE}Welcome to the future of mobile AI! 🧘🤖📱${NC}"
}

# Main setup function
main() {
    show_banner
    
    # Check environment
    check_termux
    
    # Update system
    update_termux
    
    # Install packages
    install_essentials
    
    # Install components
    install_zenos
    install_airi
    install_ollama
    
    # Setup scripts
    setup_bridge_scripts
    setup_aliases
    setup_termux_api
    
    # Test installation
    if test_installation; then
        show_completion
    else
        log_error "Installation completed with warnings. Check logs for details."
    fi
}

# Run main function
main "$@"
