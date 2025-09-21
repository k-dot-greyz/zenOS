#!/data/data/com.termux/files/usr/bin/bash
# 🎤 Voice Bridge - Seamless Voice Integration for zenOS + airi
# This script handles voice input/output for the mobile AI stack

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
ZENOS_PATH="$HOME/zenOS"
BRIDGE_SCRIPT="$ZENOS_PATH/scripts/airi-zenos-bridge.sh"
LOG_FILE="$HOME/.voice-bridge.log"

# Logging
log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

# Check Termux API availability
check_termux_api() {
    if ! command -v termux-speech-to-text >/dev/null 2>&1; then
        log_error "Termux:API not installed"
        log "Installing Termux:API..."
        pkg install -y termux-api
        
        if ! command -v termux-speech-to-text >/dev/null 2>&1; then
            log_error "Failed to install Termux:API"
            log "Please install Termux:API from F-Droid"
            exit 1
        fi
    fi
    log_success "Termux:API available"
}

# Voice input function
voice_input() {
    log "🎤 Listening for voice input..."
    
    # Show listening indicator
    echo -e "${YELLOW}🎤 Listening... (speak now)${NC}"
    
    # Get voice input
    local voice_text
    voice_text=$(termux-speech-to-text 2>/dev/null)
    
    if [ -z "$voice_text" ]; then
        log_error "No voice input received"
        echo -e "${RED}❌ No voice input received${NC}"
        return 1
    fi
    
    log "Voice input: $voice_text"
    echo -e "${GREEN}You said: $voice_text${NC}"
    
    # Process through bridge
    local response
    response=$(bash "$BRIDGE_SCRIPT" "$voice_text" 2>/dev/null)
    
    if [ -n "$response" ]; then
        echo -e "${BLUE}Response:${NC}"
        echo "$response"
        
        # Text-to-speech output
        if command -v termux-tts-speak >/dev/null 2>&1; then
            log "🔊 Converting response to speech..."
            echo "$response" | termux-tts-speak
        fi
        
        return 0
    else
        log_error "No response from bridge"
        echo -e "${RED}❌ No response received${NC}"
        return 1
    fi
}

# Continuous voice mode
continuous_voice() {
    log "🎤 Starting continuous voice mode..."
    echo -e "${GREEN}🎤 Continuous voice mode active${NC}"
    echo -e "${YELLOW}Say 'exit' to quit${NC}"
    echo ""
    
    while true; do
        echo -n -e "${BLUE}Voice> ${NC}"
        
        # Get voice input
        local voice_text
        voice_text=$(termux-speech-to-text 2>/dev/null)
        
        if [ -z "$voice_text" ]; then
            echo -e "${RED}❌ No voice input${NC}"
            continue
        fi
        
        echo -e "${GREEN}You said: $voice_text${NC}"
        
        # Check for exit command
        if [[ "$voice_text" =~ ^(exit|quit|stop|end)$ ]]; then
            log "Exiting continuous voice mode"
            echo -e "${YELLOW}Goodbye! 👋${NC}"
            break
        fi
        
        # Process through bridge
        local response
        response=$(bash "$BRIDGE_SCRIPT" "$voice_text" 2>/dev/null)
        
        if [ -n "$response" ]; then
            echo -e "${BLUE}Response:${NC}"
            echo "$response"
            
            # Text-to-speech
            if command -v termux-tts-speak >/dev/null 2>&1; then
                echo "$response" | termux-tts-speak
            fi
        else
            echo -e "${RED}❌ No response received${NC}"
        fi
        
        echo ""
    done
}

# Voice with specific mode
voice_mode() {
    local mode="$1"
    local query="$2"
    
    case "$mode" in
        "offline")
            log "🎤 Voice input in offline mode"
            echo -e "${YELLOW}🎤 Listening for offline query...${NC}"
            
            local voice_text
            voice_text=$(termux-speech-to-text 2>/dev/null)
            
            if [ -n "$voice_text" ]; then
                echo -e "${GREEN}You said: $voice_text${NC}"
                bash "$BRIDGE_SCRIPT" offline "$voice_text"
            else
                echo -e "${RED}❌ No voice input received${NC}"
            fi
            ;;
        "quick")
            log "🎤 Voice input in quick mode"
            echo -e "${YELLOW}🎤 Listening for quick query...${NC}"
            
            local voice_text
            voice_text=$(termux-speech-to-text 2>/dev/null)
            
            if [ -n "$voice_text" ]; then
                echo -e "${GREEN}You said: $voice_text${NC}"
                bash "$BRIDGE_SCRIPT" "$voice_text" --quick
            else
                echo -e "${RED}❌ No voice input received${NC}"
            fi
            ;;
        *)
            log_error "Unknown voice mode: $mode"
            echo -e "${RED}❌ Unknown mode: $mode${NC}"
            echo "Available modes: offline, quick"
            ;;
    esac
}

# Setup voice shortcuts
setup_voice_shortcuts() {
    log "Setting up voice shortcuts..."
    
    # Create voice shortcuts directory
    mkdir -p ~/.shortcuts
    mkdir -p ~/.shortcuts/icons
    
    # Quick voice chat
    cat > ~/.shortcuts/VoiceChat << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/zenOS && bash scripts/voice-bridge.sh
EOF
    
    # Voice offline mode
    cat > ~/.shortcuts/VoiceOffline << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/zenOS && bash scripts/voice-bridge.sh offline
EOF
    
    # Voice quick mode
    cat > ~/.shortcuts/VoiceQuick << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/zenOS && bash scripts/voice-bridge.sh quick
EOF
    
    # Make executable
    chmod +x ~/.shortcuts/*
    
    log_success "Voice shortcuts created"
    echo -e "${GREEN}✅ Voice shortcuts created in ~/.shortcuts/${NC}"
    echo -e "${BLUE}Add Termux widgets to your home screen for quick access!${NC}"
}

# Main function
main() {
    log "🎤 Starting Voice Bridge..."
    
    # Check dependencies
    check_termux_api
    
    # Check if bridge script exists
    if [ ! -f "$BRIDGE_SCRIPT" ]; then
        log_error "Bridge script not found at $BRIDGE_SCRIPT"
        exit 1
    fi
    
    # Parse arguments
    case "${1:-}" in
        "setup")
            setup_voice_shortcuts
            ;;
        "continuous"|"c")
            continuous_voice
            ;;
        "offline")
            voice_mode "offline" "${@:2}"
            ;;
        "quick")
            voice_mode "quick" "${@:2}"
            ;;
        "help"|"h")
            echo "Voice Bridge - zenOS + airi Voice Integration"
            echo ""
            echo "Usage:"
            echo "  $0                    - Single voice input"
            echo "  $0 continuous         - Continuous voice mode"
            echo "  $0 offline            - Voice input in offline mode"
            echo "  $0 quick              - Voice input in quick mode"
            echo "  $0 setup              - Setup voice shortcuts"
            echo "  $0 help               - Show this help"
            ;;
        "")
            voice_input
            ;;
        *)
            log_error "Unknown command: $1"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
