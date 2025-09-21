#!/bin/bash
# zenOS Universal Installer - One Command to Rule Them All! 🧘
# Usage: curl -sSL https://raw.githubusercontent.com/kasparsgreizis/zenOS/main/install.sh | bash

set -e

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

# Function to install dependencies
install_deps() {
    case $PLATFORM in
        "termux")
            echo "📦 Installing Termux packages..."
            pkg update -y && pkg upgrade -y
            pkg install -y python python-pip git curl
            
            echo "🐍 Installing Python packages..."
            pip install --user rich click aiohttp aiofiles psutil pyyaml textblob nltk
            
            echo "📥 Downloading NLTK data..."
            python3 -m textblob.download_corpora
            ;;
        "linux")
            echo "🐍 Installing Python packages..."
            pip3 install --user rich click aiohttp aiofiles psutil pyyaml textblob nltk
            
            echo "📥 Downloading NLTK data..."
            python3 -m textblob.download_corpora
            ;;
        "macos")
            echo "🐍 Installing Python packages..."
            pip3 install --user rich click aiohttp aiofiles psutil pyyaml textblob nltk
            
            echo "📥 Downloading NLTK data..."
            python3 -m textblob.download_corpora
            ;;
        "windows")
            echo "🐍 Installing Python packages..."
            pip install rich click aiohttp aiofiles psutil pyyaml textblob nltk
            
            echo "📥 Downloading NLTK data..."
            python -m textblob.download_corpora
            ;;
        *)
            echo "❌ Unsupported platform: $OSTYPE"
            echo "Please install manually: https://github.com/kasparsgreizis/zenOS"
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

# Main installation
main() {
    # Clone repository if not already present
    if [[ ! -d "zenOS" ]]; then
        echo "📥 Cloning zenOS repository..."
        git clone https://github.com/kasparsgreizis/zenOS.git
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
    echo "  Mobile: https://github.com/kasparsgreizis/zenOS/blob/main/QUICKSTART_MOBILE.md"
    echo "  Windows: https://github.com/kasparsgreizis/zenOS/blob/main/QUICKSTART_WINDOWS.md"
    echo "  Linux: https://github.com/kasparsgreizis/zenOS/blob/main/QUICKSTART_LINUX.md"
    echo ""
    echo "🧘 Welcome to zenOS! Enjoy the zen! ✨"
}

# Run main function
main "$@"
