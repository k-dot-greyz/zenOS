#!/bin/bash
# zenOS Termux Installation Script
# Optimized for Termux's package management system

echo "🧘 Installing zenOS on Termux..."
echo "================================="

# Update package lists
echo "📦 Updating package lists..."
pkg update && pkg upgrade -y

# Install Python and essential packages
echo "🐍 Installing Python and dependencies..."
pkg install -y python python-pip git curl

# Install Python packages using pip (Termux-compatible)
echo "📚 Installing Python packages..."
pip install --user rich click aiohttp aiofiles psutil pyyaml

# Install NLTK and TextBlob for the sample plugin
echo "🤖 Installing AI/NLP packages..."
pip install --user textblob nltk

# Download NLTK data
echo "📥 Downloading NLTK data..."
python3 -m textblob.download_corpora

# Use this checkout when present (pyproject.toml + zen/), otherwise clone into ./zenOS.
if [[ -f pyproject.toml && -d zen ]]; then
    echo "📂 Using existing zenOS checkout at $PWD"
elif [[ ! -d "zenOS" ]]; then
    echo "📥 Cloning zenOS repository..."
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    if [ -f "$SCRIPT_DIR/scripts/zenos-origin.sh" ]; then
        # shellcheck source=scripts/zenos-origin.sh
        . "$SCRIPT_DIR/scripts/zenos-origin.sh"
    elif [ -f scripts/zenos-origin.sh ]; then
        . scripts/zenos-origin.sh
    fi
    clone_url="$(zenos_github_clone_url)" || {
        echo "GitHub origin is not configured. Clone this repo or set ZENOS_GITHUB_OWNER in .env."
        exit 1
    }
    git clone "$clone_url" zenOS
    cd zenOS
else
    cd zenOS
fi

if [[ ! -f pyproject.toml || ! -d zen ]]; then
    echo "Could not find a zenOS checkout (expected pyproject.toml + zen/)."
    exit 1
fi

# Set up environment
echo "🔧 Setting up environment..."
export PYTHONPATH="$PWD:$PYTHONPATH"

# Test the installation
echo "🧪 Testing installation..."
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from zen.plugins import PluginRegistry
    print('✅ Plugin system working!')
except Exception as e:
    print(f'❌ Error: {e}')
"

# Install sample plugin
echo "🔌 Installing sample plugin..."
python3 zen/cli.py plugins install ./examples/sample-plugin --local

# Show plugin list
echo "📋 Installed plugins:"
python3 zen/cli.py plugins list

echo ""
echo "🎉 zenOS installation complete!"
echo "================================="
echo "To use zenOS:"
echo "  cd zenOS"
echo "  export PYTHONPATH=\"\$PWD:\$PYTHONPATH\""
echo "  python3 zen/cli.py --help"
echo ""
echo "To test plugins:"
echo "  python3 zen/cli.py plugins list"
echo "  python3 zen/cli.py plugins execute com.example.text-processor text.summarize \"Hello world!\""
echo ""
echo "🚀 Ready to rock on mobile! 📱"
