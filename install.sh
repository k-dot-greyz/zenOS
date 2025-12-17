#!/bin/bash
# zenOS Universal Installer - One Command to Rule Them All!
# Usage: curl -sSL https://raw.githubusercontent.com/k-dot-greyz/zenOS/main/install.sh | bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo "🧘 zenOS Universal Installer"
echo "=========================="
echo ""

# Detect platform
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macos"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
    PLATFORM="windows"
else
    PLATFORM="unknown"
fi

# Check if we're in Termux
if [[ -n "$PREFIX" && "$PREFIX" == "/data/data/com.termux/files/usr" ]]; then
    PLATFORM="termux"
fi

echo "🔍 Detected platform: $PLATFORM"
echo ""

# install_deps installs required system packages and Python dependencies for the detected platform (termux, linux, macos, windows) and attempts to download NLTK corpora.
install_deps() {
    case $PLATFORM in
        "termux")
            echo -e "${YELLOW}📦 Installing Termux packages...${NC}"
            pkg update -y && pkg upgrade -y
            pkg install -y python python-pip git curl
            
            echo -e "${YELLOW}🐍 Installing Python packages...${NC}"
            pip install --user rich click aiohttp aiofiles psutil pyyaml textblob nltk || {
                echo -e "${RED}❌ Failed to install Python packages${NC}"
                echo "Trying alternative installation..."
                pip install --user --break-system-packages rich click aiohttp aiofiles psutil pyyaml textblob nltk
            }
            
            echo -e "${YELLOW}📥 Downloading NLTK data...${NC}"
            python3 -m textblob.download_corpora || echo -e "${YELLOW}⚠️ NLTK data download failed, continuing...${NC}"
            ;;
        "linux")
            echo -e "${YELLOW}🐍 Installing Python packages...${NC}"
            pip3 install --user rich click aiohttp aiofiles psutil pyyaml textblob nltk || {
                echo -e "${RED}❌ Failed to install Python packages${NC}"
                echo "Trying with sudo..."
                sudo pip3 install rich click aiohttp aiofiles psutil pyyaml textblob nltk
            }
            
            echo -e "${YELLOW}📥 Downloading NLTK data...${NC}"
            python3 -m textblob.download_corpora || echo -e "${YELLOW}⚠️ NLTK data download failed, continuing...${NC}"
            ;;
        "macos")
            echo -e "${YELLOW}🐍 Installing Python packages...${NC}"
            pip3 install --user rich click aiohttp aiofiles psutil pyyaml textblob nltk || {
                echo -e "${RED}❌ Failed to install Python packages${NC}"
                echo "Trying with sudo..."
                sudo pip3 install rich click aiohttp aiofiles psutil pyyaml textblob nltk
            }
            
            echo -e "${YELLOW}📥 Downloading NLTK data...${NC}"
            python3 -m textblob.download_corpora || echo -e "${YELLOW}⚠️ NLTK data download failed, continuing...${NC}"
            ;;
        "windows")
            echo -e "${YELLOW}🐍 Installing Python packages...${NC}"
            pip install rich click aiohttp aiofiles psutil pyyaml textblob nltk || {
                echo -e "${RED}❌ Failed to install Python packages${NC}"
                exit 1
            }
            
            echo -e "${YELLOW}📥 Downloading NLTK data...${NC}"
            python -m textblob.download_corpora || echo -e "${YELLOW}⚠️ NLTK data download failed, continuing...${NC}"
            ;;
        *)
            echo -e "${RED}❌ Unsupported platform: $OSTYPE${NC}"
            echo "Please install manually: https://github.com/k-dot-greyz/zenOS"
            exit 1
            ;;
    esac
}

# Function to setup environment
setup_env() {
    echo "🔧 Setting up environment..."
    
    case $PLATFORM in
        "termux"|"linux"|"macos")
            echo 'export PYTHONPATH="$PWD:$PYTHONPATH"' >> ~/.bashrc
            echo 'alias zenos="python3 zen/cli.py"' >> ~/.bashrc
            ;;
        "windows")
            echo 'Add to your PowerShell profile:'
            echo '$env:PYTHONPATH = "$PWD"'
            echo 'Set-Alias -Name zenos -Value "python zen/cli.py"'
            ;;
    esac
}

# Function to test installation
test_install() {
    echo "🧪 Testing installation..."
    
    case $PLATFORM in
        "termux"|"linux"|"macos")
            export PYTHONPATH="$PWD:$PYTHONPATH"
            python3 zen/cli.py --help > /dev/null 2>&1
            ;;
        "windows")
            $env:PYTHONPATH = "$PWD"
            python zen/cli.py --help > /dev/null 2>&1
            ;;
    esac
    
    echo "✅ Installation test passed!"
}

# Function to install sample plugin
install_sample() {
    echo "🔌 Installing sample plugin..."
    
    case $PLATFORM in
        "termux"|"linux"|"macos")
            export PYTHONPATH="$PWD:$PYTHONPATH"
            python3 zen/cli.py plugins install ./examples/sample-plugin --local
            ;;
        "windows")
            $env:PYTHONPATH = "$PWD"
            python zen/cli.py plugins install ./examples/sample-plugin --local
            ;;
    esac
    
    echo "✅ Sample plugin installed!"
}

# main orchestrates the zenOS installation: clones the repository if missing, installs dependencies, configures the environment, verifies the installation, installs a sample plugin, and prints quick-start and guide links.
main() {
    # Clone repository if not already present
    if [[ ! -d "zenOS" ]]; then
        echo "📥 Cloning zenOS repository..."
        git clone https://github.com/k-dot-greyz/zenOS.git
    fi
    
    cd zenOS
    
    # Install dependencies
    install_deps
    
    # Setup environment
    setup_env
    
    # Test installation
    test_install
    
    # Install sample plugin
    install_sample
    
    echo ""
    echo "🎉 zenOS installation complete!"
    echo "=============================="
    echo ""
    echo "🚀 Quick start:"
    case $PLATFORM in
        "termux"|"linux"|"macos")
            echo "  export PYTHONPATH=\"\$PWD:\$PYTHONPATH\""
            echo "  python3 zen/cli.py --help"
            echo "  python3 zen/cli.py plugins list"
            echo "  python3 zen/cli.py plugins execute com.example.text-processor text.summarize \"Hello world!\""
            ;;
        "windows")
            echo "  \$env:PYTHONPATH = \"\$PWD\""
            echo "  python zen/cli.py --help"
            echo "  python zen/cli.py plugins list"
            echo "  python zen/cli.py plugins execute com.example.text-processor text.summarize \"Hello world!\""
            ;;
    esac
    echo ""
    echo "📚 Full guides:"
    echo "  Mobile: https://github.com/k-dot-greyz/zenOS/blob/main/QUICKSTART_MOBILE.md"
    echo "  Windows: https://github.com/k-dot-greyz/zenOS/blob/main/QUICKSTART_WINDOWS.md"
    echo "  Linux: https://github.com/k-dot-greyz/zenOS/blob/main/QUICKSTART_LINUX.md"
    echo ""
    echo "Welcome to zenOS! Enjoy the zen!"
}

# Run main function
main "$@"