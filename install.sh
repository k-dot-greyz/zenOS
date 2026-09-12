#!/bin/bash
# zenOS Universal Installer - One Command to Rule Them All!
# Usage (from a checkout): bash install.sh
# Bootstrap: ZENOS_GITHUB_OWNER=YOUR_GITHUB_USERNAME curl -sSL https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/zenOS/main/install.sh | bash

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

zenos_github_owner() {
    if [[ -n "${ZENOS_GITHUB_OWNER:-}" ]]; then
        printf '%s' "$ZENOS_GITHUB_OWNER"
        return 0
    fi
    if [[ -n "${GITHUB_OWNER:-}" ]]; then
        printf '%s' "$GITHUB_OWNER"
        return 0
    fi
    if [[ -n "${GITHUB_USERNAME:-}" ]]; then
        printf '%s' "$GITHUB_USERNAME"
        return 0
    fi
    printf '%s' "YOUR_GITHUB_USERNAME"
}

zenos_clone_url() {
    local owner
    owner="$(zenos_github_owner)"
    if [[ -z "$owner" || "$owner" == "YOUR_GITHUB_USERNAME" ]]; then
        echo -e "${RED}No GitHub owner is baked into this template.${NC}"
        echo "Clone your fork and rerun from the checkout, or set ZENOS_GITHUB_OWNER."
        exit 1
    fi
    echo "https://github.com/${owner}/${ZENOS_REPO_NAME:-zenOS}.git"
}

is_zenos_checkout() {
    [[ -f pyproject.toml && -d zen ]]
}

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
    restore_setup() {
        if [ -f _setup.py.bak ]; then
            mv _setup.py.bak setup.py
        fi
    }
    trap restore_setup EXIT
    if [ -f setup.py ]; then
        mv setup.py _setup.py.bak
    fi
    "$PYTHON_BIN" -m pip install --upgrade pip setuptools wheel
    if ! "$PYTHON_BIN" -m pip install -e ".[dev]"; then
        echo -e "${YELLOW}Retrying with --break-system-packages...${NC}"
        "$PYTHON_BIN" -m pip install --break-system-packages -e ".[dev]"
    fi
    restore_setup
    trap - EXIT
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

# main orchestrates the zenOS installation: uses the current checkout when present,
# otherwise clones via ZENOS_GITHUB_OWNER, then installs dependencies.
main() {
    if is_zenos_checkout; then
        echo "📂 Using existing zenOS checkout at $PWD"
    elif [[ ! -d "zenOS" ]]; then
        echo "📥 Cloning zenOS repository..."
        git clone "$(zenos_clone_url)"
        cd zenOS
    else
        cd zenOS
    fi

    if ! is_zenos_checkout; then
        echo -e "${RED}Could not find a zenOS checkout (expected pyproject.toml + zen/).${NC}"
        exit 1
    fi
    
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
    echo "📚 Full guides (in this checkout):"
    echo "  Mobile:  docs/guides/QUICKSTART_MOBILE.md"
    echo "  Windows: docs/guides/QUICKSTART_WINDOWS.md"
    echo "  Linux:   docs/guides/QUICKSTART_LINUX.md"
    echo ""
    echo "Welcome to zenOS! Enjoy the zen!"
}

# Run main function
main "$@"
