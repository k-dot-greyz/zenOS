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

PYTHON_BIN=""

require_python_314() {
    local candidate
    for candidate in python3.14 python3 python; do
        if command -v "$candidate" >/dev/null 2>&1; then
            if "$candidate" -c 'import sys; raise SystemExit(0 if sys.version_info[:2] >= (3, 14) else 1)' 2>/dev/null; then
                PYTHON_BIN="$candidate"
                echo -e "${GREEN}Using ${PYTHON_BIN} ($("$PYTHON_BIN" -c 'import sys; print("%d.%d.%d" % sys.version_info[:3])'))${NC}"
                return 0
            fi
        fi
    done
    echo -e "${RED}zenOS requires Python 3.14+${NC}"
    echo "Install CPython 3.14 (https://www.python.org/downloads/ or: uv python install 3.14)"
    echo "Then recreate your venv and rerun this installer."
    exit 1
}

# install_deps installs current stable zenOS dependencies via pyproject.toml on Python 3.14+.
install_deps() {
    require_python_314
    echo -e "${YELLOW}🐍 Installing zenOS (Python 3.14+, current stables from pyproject.toml)...${NC}"
    if [ -f setup.py ]; then
        mv setup.py _setup.py.bak
    fi
    "$PYTHON_BIN" -m pip install --upgrade pip setuptools wheel
    if ! "$PYTHON_BIN" -m pip install -e ".[dev]"; then
        echo -e "${YELLOW}Retrying with --break-system-packages...${NC}"
        "$PYTHON_BIN" -m pip install --break-system-packages -e ".[dev]"
    fi
    if [ -f _setup.py.bak ]; then
        mv _setup.py.bak setup.py
    fi
}

# Function to setup environment
setup_env() {
    echo "🔧 Setting up environment..."
    
    case $PLATFORM in
        "termux"|"linux"|"macos")
            echo 'export PYTHONPATH="$PWD:$PYTHONPATH"' >> ~/.bashrc
            echo "alias zenos=\"${PYTHON_BIN} -m zen.cli\"" >> ~/.bashrc
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
            "$PYTHON_BIN" -m zen.cli --help > /dev/null 2>&1
            ;;
        "windows")
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
            "$PYTHON_BIN" -m zen.cli plugins install ./examples/sample-plugin --local
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
            echo "  zen --help"
            echo "  zen env-doctor"
            ;;
        "windows")
            echo "  \$env:PYTHONPATH = \"\$PWD\""
            echo "  zen --help"
            echo "  zen env-doctor"
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