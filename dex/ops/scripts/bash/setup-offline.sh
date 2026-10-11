#!/bin/bash
#
# zenOS Offline Setup Script
# Sets up local AI models for true offline operation
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
cat << "EOF"
    ╔═══════════════════════════════════╗
    ║   🧘 zenOS Offline Mode Setup 🔌  ║
    ║   True AI - No Internet Required  ║
    ╔═══════════════════════════════════╝
EOF
echo -e "${NC}"

# Detect platform
detect_platform() {
    if [ -n "$TERMUX_VERSION" ] || [ -d "/data/data/com.termux" ]; then
        echo "termux"
    elif [ "$(uname)" == "Darwin" ]; then
        echo "macos"
    elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
        echo "linux"
    else
        echo "unknown"
    fi
}

PLATFORM=$(detect_platform)
echo -e "${BLUE}🔍 Detected platform: ${YELLOW}$PLATFORM${NC}"

# Function to install Ollama
install_ollama() {
    echo -e "${YELLOW}📦 Installing Ollama...${NC}"
    
    case $PLATFORM in
        termux)
            # Termux installation (experimental but works!)
            echo -e "${CYAN}Setting up Ollama for Termux...${NC}"
            
            # Install Go if not present
            if ! command -v go &> /dev/null; then
                pkg install -y golang
            fi
            
            # Clone and build Ollama
            if [ ! -d "$HOME/ollama" ]; then
                cd $HOME
                git clone https://github.com/ollama/ollama
                cd ollama
                
                # Build with mobile optimizations
                CGO_ENABLED=1 go build -tags "mobile" .
                
                # Create symlink
                ln -sf $HOME/ollama/ollama $PREFIX/bin/ollama
            fi
            
            # Start Ollama service in background
            nohup $HOME/ollama/ollama serve > /dev/null 2>&1 &
            echo $! > $HOME/.ollama.pid
            
            echo -e "${GREEN}✅ Ollama installed for Termux!${NC}"
            ;;
            
        linux|macos)
            # Standard installation
            if ! command -v ollama &> /dev/null; then
                echo "Installing Ollama..."
                curl -fsSL https://ollama.com/install.sh | sh
            else
                echo -e "${GREEN}✅ Ollama already installed${NC}"
            fi
            
            # Start Ollama service
            ollama serve > /dev/null 2>&1 &
            ;;
            
        *)
            echo -e "${RED}❌ Unsupported platform${NC}"
            exit 1
            ;;
    esac
    
    # Wait for Ollama to start
    echo -e "${YELLOW}⏳ Waiting for Ollama to start...${NC}"
    for i in {1..30}; do
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Ollama is running!${NC}"
            break
        fi
        sleep 1
    done
}

# Function to install llama.cpp as fallback
install_llamacpp() {
    echo -e "${YELLOW}📦 Installing llama.cpp (fallback)...${NC}"
    
    case $PLATFORM in
        termux)
            # Termux build
            pkg install -y clang make
            
            if [ ! -d "$HOME/llama.cpp" ]; then
                cd $HOME
                git clone https://github.com/ggerganov/llama.cpp
                cd llama.cpp
                
                # Build with Android optimizations
                make LLAMA_PORTABLE=1 LLAMA_OPENBLAS=1
                
                # Create symlinks
                ln -sf $HOME/llama.cpp/main $PREFIX/bin/llama
                ln -sf $HOME/llama.cpp/quantize $PREFIX/bin/llama-quantize
            fi
            
            echo -e "${GREEN}✅ llama.cpp installed!${NC}"
            ;;
            
        linux|macos)
            if [ ! -d "$HOME/llama.cpp" ]; then
                cd $HOME
                git clone https://github.com/ggerganov/llama.cpp
                cd llama.cpp
                make
                
                # Add to PATH
                echo 'export PATH="$HOME/llama.cpp:$PATH"' >> ~/.bashrc
            fi
            ;;
    esac
}

# Function to download mobile-friendly models
download_models() {
    echo -e "${CYAN}"
    echo "═══════════════════════════════════════"
    echo "  📱 Select Models to Download"
    echo "═══════════════════════════════════════"
    echo -e "${NC}"
    
    # Get available RAM
    if [ "$PLATFORM" == "termux" ]; then
        AVAILABLE_RAM=$(cat /proc/meminfo | grep MemAvailable | awk '{print int($2/1024)}')
    else
        AVAILABLE_RAM=8000
    fi
    
    echo -e "${BLUE}Available RAM: ${YELLOW}${AVAILABLE_RAM}MB${NC}"
    echo ""
    
    # Model options based on RAM
    if [ $AVAILABLE_RAM -lt 2000 ]; then
        echo -e "${YELLOW}⚠️  Limited RAM - Recommending ultra-light models:${NC}"
        MODELS=("qwen:0.5b" "tinyllama")
    elif [ $AVAILABLE_RAM -lt 4000 ]; then
        echo -e "${GREEN}✅ Mobile models recommended:${NC}"
        MODELS=("tinyllama" "phi-2" "gemma:2b" "stablelm2:1.6b")
    else
        echo -e "${GREEN}✅ All models available:${NC}"
        MODELS=("tinyllama" "phi-2" "gemma:2b" "mistral:7b" "llama3:8b")
    fi
    
    echo "Available models:"
    for i in "${!MODELS[@]}"; do
        echo "  $((i+1)). ${MODELS[$i]}"
    done
    echo "  0. Skip model download"
    echo ""
    
    read -p "Select models to download (space-separated numbers): " -a selections
    
    for selection in "${selections[@]}"; do
        if [ "$selection" == "0" ]; then
            echo "Skipping model download"
            break
        elif [ "$selection" -ge 1 ] && [ "$selection" -le "${#MODELS[@]}" ]; then
            MODEL="${MODELS[$((selection-1))]}"
            echo -e "${YELLOW}📥 Downloading $MODEL...${NC}"
            
            if command -v ollama &> /dev/null; then
                ollama pull "$MODEL"
                echo -e "${GREEN}✅ $MODEL ready!${NC}"
            else
                echo -e "${RED}❌ Ollama not available${NC}"
            fi
        fi
    done
}

# Function to create offline launcher
create_launcher() {
    echo -e "${YELLOW}🚀 Creating offline launcher...${NC}"
    
    cat > $HOME/zen-offline << 'EOF'
#!/bin/bash
# zenOS Offline Mode Launcher

# Force offline mode
export ZEN_PREFER_OFFLINE=true
export OLLAMA_HOST=${OLLAMA_HOST:-http://localhost:11434}

# Start Ollama if not running
if ! curl -s $OLLAMA_HOST/api/tags > /dev/null 2>&1; then
    echo "Starting Ollama..."
    if [ -f $HOME/.ollama.pid ]; then
        kill $(cat $HOME/.ollama.pid) 2>/dev/null || true
    fi
    nohup ollama serve > /dev/null 2>&1 &
    echo $! > $HOME/.ollama.pid
    sleep 3
fi

# List available models
echo "🤖 Available offline models:"
curl -s $OLLAMA_HOST/api/tags | grep -o '"name":"[^"]*"' | cut -d'"' -f4 | sed 's/^/  - /'

echo ""
echo "🧘 Starting zenOS in offline mode..."

# Run zenOS with offline provider
cd $HOME/zenOS
python -m zen.cli chat --offline "$@"
EOF
    
    chmod +x $HOME/zen-offline
    
    # Add to PATH if not already there
    if ! grep -q 'export PATH="$HOME:$PATH"' $HOME/.bashrc; then
        echo 'export PATH="$HOME:$PATH"' >> $HOME/.bashrc
    fi
    
    echo -e "${GREEN}✅ Offline launcher created!${NC}"
    echo "   Run 'zen-offline' to start in offline mode"
}

# Function to test offline setup
test_offline() {
    echo -e "${YELLOW}🧪 Testing offline setup...${NC}"
    
    # Check if Ollama is running
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Ollama server is running${NC}"
        
        # List models
        MODELS=$(curl -s http://localhost:11434/api/tags | grep -o '"name":"[^"]*"' | cut -d'"' -f4)
        
        if [ -z "$MODELS" ]; then
            echo -e "${YELLOW}⚠️  No models installed yet${NC}"
        else
            echo -e "${GREEN}✅ Installed models:${NC}"
            echo "$MODELS" | sed 's/^/  - /'
            
            # Test generation
            FIRST_MODEL=$(echo "$MODELS" | head -n1)
            echo -e "${YELLOW}Testing generation with $FIRST_MODEL...${NC}"
            
            RESPONSE=$(curl -s http://localhost:11434/api/generate \
                -d "{\"model\":\"$FIRST_MODEL\",\"prompt\":\"Say hello\",\"stream\":false}" \
                | grep -o '"response":"[^"]*"' | cut -d'"' -f4)
            
            if [ -n "$RESPONSE" ]; then
                echo -e "${GREEN}✅ Response: $RESPONSE${NC}"
            else
                echo -e "${RED}❌ Generation failed${NC}"
            fi
        fi
    else
        echo -e "${RED}❌ Ollama is not running${NC}"
    fi
}

# Main installation flow
main() {
    echo -e "${CYAN}Starting offline setup...${NC}"
    echo ""
    
    # Step 1: Install Ollama
    if [ "$1" != "--skip-install" ]; then
        install_ollama
        
        # Fallback: Install llama.cpp if Ollama fails
        if ! command -v ollama &> /dev/null; then
            echo -e "${YELLOW}Ollama not available, installing llama.cpp as fallback...${NC}"
            install_llamacpp
        fi
    fi
    
    # Step 2: Download models
    if [ "$1" != "--skip-models" ]; then
        download_models
    fi
    
    # Step 3: Create launcher
    create_launcher
    
    # Step 4: Test setup
    test_offline
    
    echo ""
    echo -e "${GREEN}"
    echo "════════════════════════════════════════"
    echo "    🎉 Offline Setup Complete! 🎉"
    echo "════════════════════════════════════════"
    echo -e "${NC}"
    echo -e "${CYAN}Quick Start:${NC}"
    echo "  • Run ${YELLOW}zen-offline${NC} to start in offline mode"
    echo "  • Run ${YELLOW}ollama list${NC} to see installed models"
    echo "  • Run ${YELLOW}ollama pull <model>${NC} to add more models"
    echo ""
    echo -e "${BLUE}Recommended mobile models:${NC}"
    echo "  • ${GREEN}tinyllama${NC} - Ultra fast (637MB)"
    echo "  • ${GREEN}phi-2${NC} - Best quality/size (1.6GB)"
    echo "  • ${GREEN}qwen:0.5b${NC} - Tiny but capable (395MB)"
    echo ""
    echo -e "${YELLOW}You now have AI that works anywhere, anytime!${NC}"
    echo -e "${GREEN}No internet? No problem! 🧘${NC}"
}

# Handle arguments
case "$1" in
    --test)
        test_offline
        ;;
    --models)
        download_models
        ;;
    --help)
        echo "Usage: $0 [OPTIONS]"
        echo "Options:"
        echo "  --test         Test offline setup"
        echo "  --models       Download models only"
        echo "  --skip-install Skip installation"
        echo "  --skip-models  Skip model download"
        echo "  --help         Show this help"
        ;;
    *)
        main "$@"
        ;;
esac
