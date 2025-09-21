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

# Clone zenOS if not already present
if [ ! -d "zenOS" ]; then
    echo "📥 Cloning zenOS repository..."
    git clone https://github.com/kasparsgreizis/zenOS.git
fi

cd zenOS

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
