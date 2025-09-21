#!/data/data/com.termux/files/usr/bin/bash
# 🔋 Offline Bridge - Local AI Processing for zenOS + airi
# This script handles offline AI processing using local models

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Configuration
ZENOS_PATH="$HOME/zenOS"
CACHE_DIR="$HOME/.offline-cache"
MODELS_DIR="$HOME/.ollama/models"
LOG_FILE="$HOME/.offline-bridge.log"

# Create cache directory
mkdir -p "$CACHE_DIR"

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

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Check Ollama installation
check_ollama() {
    if ! command -v ollama >/dev/null 2>&1; then
        log_warning "Ollama not found, installing..."
        install_ollama
    else
        log_success "Ollama found"
    fi
}

# Install Ollama
install_ollama() {
    log "Installing Ollama..."
    
    # Download and install Ollama
    curl -fsSL https://ollama.ai/install.sh | sh
    
    if command -v ollama >/dev/null 2>&1; then
        log_success "Ollama installed successfully"
    else
        log_error "Failed to install Ollama"
        exit 1
    fi
}

# Get available models
get_available_models() {
    if ! command -v ollama >/dev/null 2>&1; then
        echo ""
        return
    fi
    
    ollama list 2>/dev/null | tail -n +2 | awk '{print $1}' | grep -v '^$' || echo ""
}

# Install mobile-optimized models
install_mobile_models() {
    log "Installing mobile-optimized models..."
    
    local models=("qwen:0.5b" "tinyllama" "phi-2")
    local installed=0
    
    for model in "${models[@]}"; do
        log "Installing $model..."
        if ollama pull "$model" 2>/dev/null; then
            log_success "Installed $model"
            ((installed++))
        else
            log_warning "Failed to install $model"
        fi
    done
    
    if [ $installed -gt 0 ]; then
        log_success "Installed $installed models"
    else
        log_error "No models installed"
        return 1
    fi
}

# Select best model based on device capabilities
select_best_model() {
    local available_models
    available_models=$(get_available_models)
    
    if [ -z "$available_models" ]; then
        log_error "No models available"
        return 1
    fi
    
    # Get device memory info
    local total_mem
    total_mem=$(cat /proc/meminfo | grep MemTotal | awk '{print $2}')
    total_mem=$((total_mem / 1024))  # Convert to MB
    
    log "Device memory: ${total_mem}MB"
    
    # Select model based on available memory
    if [ $total_mem -ge 4096 ]; then
        # 4GB+ RAM - use phi-2
        echo "phi-2"
    elif [ $total_mem -ge 2048 ]; then
        # 2-4GB RAM - use tinyllama
        echo "tinyllama"
    else
        # <2GB RAM - use qwen:0.5b
        echo "qwen:0.5b"
    fi
}

# Process query offline
process_offline() {
    local query="$1"
    local model="${2:-auto}"
    
    log "Processing offline query: ${query:0:50}..."
    
    # Select model if auto
    if [ "$model" = "auto" ]; then
        model=$(select_best_model)
        if [ -z "$model" ]; then
            log_error "No suitable model found"
            return 1
        fi
    fi
    
    log "Using model: $model"
    
    # Create cache key
    local cache_key
    cache_key=$(echo "$query" | md5sum | cut -d' ' -f1)
    local cache_file="$CACHE_DIR/${cache_key}.txt"
    
    # Check cache first
    if [ -f "$cache_file" ]; then
        local cache_age
        cache_age=$(($(date +%s) - $(stat -c %Y "$cache_file")))
        
        if [ $cache_age -lt 3600 ]; then  # 1 hour cache
            log "Using cached response"
            cat "$cache_file"
            return 0
        fi
    fi
    
    # Process with Ollama
    local response
    response=$(ollama run "$model" "$query" 2>/dev/null)
    
    if [ $? -eq 0 ] && [ -n "$response" ]; then
        # Cache the response
        echo "$response" > "$cache_file"
        
        # Format output
        echo -e "${PURPLE}🤖 Offline AI ($model):${NC}"
        echo "$response"
        echo ""
        echo -e "${BLUE}🔋 Battery-friendly processing complete${NC}"
        
        log_success "Offline processing complete"
        return 0
    else
        log_error "Offline processing failed"
        echo -e "${RED}❌ Offline processing failed${NC}"
        return 1
    fi
}

# Interactive offline mode
interactive_offline() {
    log "Starting interactive offline mode..."
    echo -e "${GREEN}🔋 Offline AI Mode Active${NC}"
    echo -e "${YELLOW}Type 'exit' to quit, 'models' to list models${NC}"
    echo ""
    
    while true; do
        echo -n -e "${BLUE}Offline> ${NC}"
        read -r input
        
        case "$input" in
            "exit"|"quit"|"q")
                log "Exiting offline mode"
                echo -e "${YELLOW}Goodbye! 👋${NC}"
                break
                ;;
            "models"|"m")
                echo -e "${GREEN}Available models:${NC}"
                get_available_models | while read -r model; do
                    if [ -n "$model" ]; then
                        echo "  - $model"
                    fi
                done
                ;;
            "install"|"i")
                install_mobile_models
                ;;
            "cache"|"c")
                echo -e "${GREEN}Cache directory: $CACHE_DIR${NC}"
                echo -e "${BLUE}Cache files: $(ls -1 "$CACHE_DIR" | wc -l)${NC}"
                ;;
            "clear-cache"|"cc")
                rm -f "$CACHE_DIR"/*
                echo -e "${GREEN}Cache cleared${NC}"
                ;;
            "")
                continue
                ;;
            *)
                process_offline "$input"
                ;;
        esac
        echo ""
    done
}

# Batch processing
batch_process() {
    local input_file="$1"
    local output_file="${2:-${input_file}.output}"
    local model="${3:-auto}"
    
    if [ ! -f "$input_file" ]; then
        log_error "Input file not found: $input_file"
        return 1
    fi
    
    log "Batch processing file: $input_file"
    
    local processed=0
    local failed=0
    
    while IFS= read -r line; do
        if [ -n "$line" ]; then
            echo -e "${BLUE}Processing: ${line:0:50}...${NC}"
            
            if process_offline "$line" "$model" >/dev/null 2>&1; then
                ((processed++))
            else
                ((failed++))
            fi
        fi
    done < "$input_file"
    
    log_success "Batch processing complete: $processed processed, $failed failed"
}

# Setup offline shortcuts
setup_offline_shortcuts() {
    log "Setting up offline shortcuts..."
    
    # Create shortcuts directory
    mkdir -p ~/.shortcuts
    mkdir -p ~/.shortcuts/icons
    
    # Offline chat
    cat > ~/.shortcuts/OfflineChat << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/zenOS && bash scripts/offline-bridge.sh interactive
EOF
    
    # Offline quick
    cat > ~/.shortcuts/OfflineQuick << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/zenOS && bash scripts/offline-bridge.sh
EOF
    
    # Make executable
    chmod +x ~/.shortcuts/*
    
    log_success "Offline shortcuts created"
    echo -e "${GREEN}✅ Offline shortcuts created in ~/.shortcuts/${NC}"
}

# Main function
main() {
    log "🔋 Starting Offline Bridge..."
    
    # Check Ollama
    check_ollama
    
    # Parse arguments
    case "${1:-}" in
        "install"|"i")
            install_mobile_models
            ;;
        "interactive"|"int")
            interactive_offline
            ;;
        "batch"|"b")
            batch_process "${2:-}" "${3:-}" "${4:-}"
            ;;
        "setup")
            setup_offline_shortcuts
            ;;
        "models"|"m")
            echo -e "${GREEN}Available models:${NC}"
            get_available_models | while read -r model; do
                if [ -n "$model" ]; then
                    echo "  - $model"
                fi
            done
            ;;
        "help"|"h")
            echo "Offline Bridge - Local AI Processing for zenOS + airi"
            echo ""
            echo "Usage:"
            echo "  $0 [query]              - Process single query offline"
            echo "  $0 interactive          - Interactive offline mode"
            echo "  $0 install              - Install mobile models"
            echo "  $0 batch <file> [out]   - Batch process file"
            echo "  $0 setup                - Setup offline shortcuts"
            echo "  $0 models               - List available models"
            echo "  $0 help                 - Show this help"
            ;;
        "")
            echo -e "${YELLOW}No query provided. Use 'interactive' mode or provide a query.${NC}"
            echo "Use '$0 help' for usage information"
            ;;
        *)
            process_offline "$1" "${2:-auto}"
            ;;
    esac
}

# Run main function
main "$@"
