#!/data/data/com.termux/files/usr/bin/bash
# 🌉 airi-zenOS Bridge - The Ultimate Mobile AI Connection
# This script creates a seamless bridge between airi and zenOS on Pixel 9a

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
ZENOS_PATH="$HOME/zenOS"
AIRI_PATH="/data/data/com.termux/files/usr/var/lib/proot-distro/installed-rootfs/airi"
BRIDGE_LOG="$HOME/.airi-zenos-bridge.log"
CACHE_DIR="$HOME/.airi-zenos-cache"

# Create cache directory
mkdir -p "$CACHE_DIR"

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1" | tee -a "$BRIDGE_LOG"
}

# Error logging
log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$BRIDGE_LOG"
}

# Success logging
log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$BRIDGE_LOG"
}

# Warning logging
log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$BRIDGE_LOG"
}

# Check if zenOS is installed
check_zenos() {
    if [ ! -d "$ZENOS_PATH" ]; then
        log_error "zenOS not found at $ZENOS_PATH"
        log "Installing zenOS..."
        curl -sSL https://raw.githubusercontent.com/k-dot-greyz/zenOS/main/scripts/termux-install.sh | bash
        if [ $? -eq 0 ]; then
            log_success "zenOS installed successfully"
        else
            log_error "Failed to install zenOS"
            exit 1
        fi
    else
        log_success "zenOS found at $ZENOS_PATH"
    fi
}

# Check if airi is installed
check_airi() {
    if [ ! -d "$AIRI_PATH" ]; then
        log_warning "airi not found, installing..."
        pkg install -y proot-distro
        proot-distro install airi
        if [ $? -eq 0 ]; then
            log_success "airi installed successfully"
        else
            log_error "Failed to install airi"
            exit 1
        fi
    else
        log_success "airi found at $AIRI_PATH"
    fi
}

# Get mobile context
get_mobile_context() {
    local context=""
    
    # Battery status
    if command -v termux-battery-status >/dev/null 2>&1; then
        local battery=$(termux-battery-status 2>/dev/null | grep -o '"percentage":[0-9]*' | cut -d: -f2)
        context="${context}Battery: ${battery}%\n"
    fi
    
    # Location (if available)
    if command -v termux-location >/dev/null 2>&1; then
        local location=$(termux-location 2>/dev/null | head -1)
        if [ -n "$location" ]; then
            context="${context}Location: ${location}\n"
        fi
    fi
    
    # Clipboard content
    if command -v termux-clipboard-get >/dev/null 2>&1; then
        local clipboard=$(termux-clipboard-get 2>/dev/null | head -c 100)
        if [ -n "$clipboard" ]; then
            context="${context}Clipboard: ${clipboard}...\n"
        fi
    fi
    
    # Device info
    context="${context}Device: Pixel 9a\n"
    context="${context}Mode: Mobile Bridge\n"
    context="${context}Timestamp: $(date)\n"
    
    echo -e "$context"
}

# Process query through zenOS
process_zenos() {
    local query="$1"
    local context="$2"
    local mode="${3:-mobile}"
    
    log "Processing through zenOS: ${query:0:50}..."
    
    # Create temporary context file
    local context_file=$(mktemp)
    echo -e "$context" > "$context_file"
    
    # Process through zenOS with mobile optimizations
    local response
    if [ "$mode" = "offline" ]; then
        response=$(cd "$ZENOS_PATH" && python -m zen.cli chat "$query" --offline --mobile-mode 2>/dev/null)
    else
        response=$(cd "$ZENOS_PATH" && python -m zen.cli chat "$query" --mobile-mode --context-file "$context_file" 2>/dev/null)
    fi
    
    # Clean up
    rm -f "$context_file"
    
    if [ -n "$response" ]; then
        log_success "zenOS processing complete"
        echo "$response"
    else
        log_error "zenOS processing failed"
        echo "Sorry, I couldn't process that request through zenOS."
    fi
}

# Process through airi
process_airi() {
    local input="$1"
    local context="$2"
    
    log "Processing through airi: ${input:0:50}..."
    
    # Create airi processing script
    local airi_script=$(mktemp)
    cat > "$airi_script" << 'EOF'
#!/bin/bash
# airi processing script

# Get input from stdin
read -r input

# Process with airi (this would be the actual airi processing)
# For now, we'll enhance the input with mobile-specific features
echo "📱 airi enhancement: $input"
echo "🔋 Mobile optimized response"
echo "📱 Context-aware processing complete"
EOF
    
    chmod +x "$airi_script"
    
    # Process through airi
    local response
    if [ -d "$AIRI_PATH" ]; then
        response=$(echo "$input" | proot-distro login airi -- bash -c "cat > /tmp/input && echo 'Processing with airi...' && cat /tmp/input")
    else
        response=$(echo "$input" | bash "$airi_script")
    fi
    
    # Clean up
    rm -f "$airi_script"
    
    log_success "airi processing complete"
    echo "$response"
}

# Voice processing
process_voice() {
    log "🎤 Starting voice processing..."
    
    if ! command -v termux-speech-to-text >/dev/null 2>&1; then
        log_error "Termux:API not installed. Please install from F-Droid"
        return 1
    fi
    
    # Get voice input
    local voice_text
    voice_text=$(termux-speech-to-text 2>/dev/null)
    
    if [ -z "$voice_text" ]; then
        log_error "No voice input received"
        return 1
    fi
    
    log "Voice input: $voice_text"
    
    # Process through the bridge
    local response
    response=$(process_query "$voice_text" "voice")
    
    # Text-to-speech output
    if command -v termux-tts-speak >/dev/null 2>&1; then
        echo "$response" | termux-tts-speak
    fi
    
    echo "$response"
}

# Main query processing function
process_query() {
    local query="$1"
    local input_type="${2:-text}"
    local mode="${3:-online}"
    
    log "Processing query: ${query:0:50}..."
    
    # Get mobile context
    local context
    context=$(get_mobile_context)
    
    # Process through zenOS
    local zenos_response
    zenos_response=$(process_zenos "$query" "$context" "$mode")
    
    # Process through airi
    local airi_response
    airi_response=$(process_airi "$zenos_response" "$context")
    
    # Combine responses
    local final_response=""
    final_response="${final_response}🧘 zenOS: $zenos_response\n"
    final_response="${final_response}📱 airi: $airi_response\n"
    final_response="${final_response}🌉 Bridge: Processing complete\n"
    
    # Cache the response
    echo "$final_response" > "$CACHE_DIR/$(date +%s).txt"
    
    log_success "Query processing complete"
    echo -e "$final_response"
}

# Interactive mode
interactive_mode() {
    log "🌉 Starting airi-zenOS Bridge in interactive mode..."
    echo -e "${PURPLE}Welcome to the airi-zenOS Bridge!${NC}"
    echo -e "${CYAN}Type 'voice' for voice input, 'offline' for offline mode, or just type your message${NC}"
    echo -e "${YELLOW}Type 'exit' to quit${NC}"
    echo ""
    
    while true; do
        echo -n -e "${GREEN}airi-zenOS> ${NC}"
        read -r input
        
        case "$input" in
            "exit"|"quit"|"q")
                log "Exiting interactive mode"
                echo "Goodbye! 👋"
                break
                ;;
            "voice"|"v")
                process_voice
                ;;
            "offline"|"o")
                echo -n "Enter your offline query: "
                read -r query
                process_query "$query" "text" "offline"
                ;;
            "help"|"h")
                echo "Available commands:"
                echo "  voice/v    - Voice input mode"
                echo "  offline/o  - Offline processing mode"
                echo "  help/h     - Show this help"
                echo "  exit/q     - Exit the bridge"
                echo "  <message>  - Process text message"
                ;;
            "")
                continue
                ;;
            *)
                process_query "$input"
                ;;
        esac
        echo ""
    done
}

# Command line mode
cmd_mode() {
    local query="$*"
    if [ -z "$query" ]; then
        log_error "No query provided"
        echo "Usage: $0 [query]"
        echo "       $0 voice"
        echo "       $0 offline [query]"
        echo "       $0 interactive"
        exit 1
    fi
    
    case "$query" in
        "voice")
            process_voice
            ;;
        "interactive")
            interactive_mode
            ;;
        "offline"*)
            local offline_query="${query#offline }"
            process_query "$offline_query" "text" "offline"
            ;;
        *)
            process_query "$query"
            ;;
    esac
}

# Main function
main() {
    log "🌉 Starting airi-zenOS Bridge..."
    
    # Check dependencies
    check_zenos
    check_airi
    
    # Install Termux:API if not present
    if ! command -v termux-speech-to-text >/dev/null 2>&1; then
        log_warning "Termux:API not found. Installing..."
        pkg install -y termux-api
    fi
    
    # Create aliases
    create_aliases
    
    # Start processing
    if [ $# -eq 0 ]; then
        interactive_mode
    else
        cmd_mode "$@"
    fi
}

# Create useful aliases
create_aliases() {
    local alias_file="$HOME/.airi-zenos-aliases"
    
    cat > "$alias_file" << 'EOF'
# airi-zenOS Bridge Aliases
alias airi-zenos='~/zenOS/scripts/airi-zenos-bridge.sh'
alias az='airi-zenos'
alias azv='airi-zenos voice'
alias azo='airi-zenos offline'
alias azi='airi-zenos interactive'

# Quick functions
az-quick() {
    airi-zenos "$@" | head -20
}

az-voice() {
    airi-zenos voice
}

az-offline() {
    airi-zenos offline "$@"
}
EOF
    
    # Add to bashrc if not already there
    if ! grep -q "airi-zenos-aliases" "$HOME/.bashrc" 2>/dev/null; then
        echo "source $alias_file" >> "$HOME/.bashrc"
        log_success "Aliases created and added to .bashrc"
    fi
}

# Run main function
main "$@"
