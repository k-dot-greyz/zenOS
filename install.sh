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

# install_deps: Python 3.14.7+ FIRST, then pip. Never ignore requires-python.
install_deps() {
    local root
    root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    echo -e "${YELLOW}🐍 Python-first coldstart (3.14.7+ then .[dev])...${NC}"
    if ! bash "$root/scripts/python-first-coldstart.sh" "$root"; then
        echo -e "${RED}FLOOR_UNMET: python3.14 >= 3.14.7 required before pip${NC}"
        exit 2
    fi
    if [[ -x "$root/.venv/bin/python" ]]; then
        PYTHON_BIN="$root/.venv/bin/python"
    else
        require_python_314
    fi
}
setup_env() {
    echo "🔧 Setting up environment..."
    
    case $PLATFORM in
        "termux"|"linux"|"macos")
            echo 'export PYTHONPATH="$PWD:$PYTHONPATH"' >> ~/.bashrc
            echo "alias zenos=\"${PYTHON_BIN} -m zen.cli\"" >> ~/.bashrc
            ;;
        "windows")
            echo 'Add to your PowerShell profile:'
            echo "\$env:PYTHONPATH = \"\$PWD\""
            echo "Set-Alias -Name zenos -Value \"${PYTHON_BIN} -m zen.cli\""
            ;;
    esac
}

# Function to test installation
test_install() {
    echo "🧪 Testing installation..."
    export PYTHONPATH="$PWD:$PYTHONPATH"
    "$PYTHON_BIN" -m zen.cli --help > /dev/null 2>&1
    echo "✅ Installation test passed!"
}

# Function to install sample plugin
install_sample() {
    echo "🔌 Installing sample plugin..."
    export PYTHONPATH="$PWD:$PYTHONPATH"
    "$PYTHON_BIN" -m zen.cli plugins install ./examples/sample-plugin --local
    echo "✅ Sample plugin installed!"
}

# main orchestrates the zenOS installation. If already in a checkout, do not nest-clone.
main() {
    local root
    root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    if [[ -f "$root/pyproject.toml" && -d "$root/zen" ]]; then
        cd "$root"
    else
        if [[ ! -d "zenOS" ]]; then
            echo "📥 Cloning zenOS repository..."
            git clone https://github.com/k-dot-greyz/zenOS.git
        fi
        cd zenOS
    fi

    # Install dependencies (python-first)
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