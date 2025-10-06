#!/bin/bash
# zenOS n8n Template Selector Setup Script

set -e

echo "🧠 zenOS n8n Integration Setup"
echo "=============================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_info() {
    echo -e "${BLUE}📝${NC} $1"
}

# Check if n8n is installed
if command -v n8n &> /dev/null; then
    n8n_version=$(n8n --version)
    print_status "n8n found (version: $n8n_version)"
else
    print_error "n8n not found. Please install n8n first:"
    echo ""
    echo "   # Global installation:"
    echo "   npm install n8n -g"
    echo ""
    echo "   # Or using Docker:"
    echo "   docker run -it --rm --name n8n -p 5678:5678 n8nio/n8n"
    echo ""
    echo "   # Or n8n Cloud:"
    echo "   Visit https://n8n.cloud"
    echo ""
    exit 1
fi

# Check if workflow file exists
if [ ! -f "zenOS_template_selector.json" ]; then
    print_error "Workflow file 'zenOS_template_selector.json' not found."
    echo "   Please ensure you're in the n8n directory of the zenOS repository."
    exit 1
fi

print_status "Workflow file found"

# Check if curl is available for testing
if command -v curl &> /dev/null; then
    print_status "curl found (for testing)"
else
    print_warning "curl not found. You won't be able to test the webhook automatically."
fi

# Check if jq is available for JSON processing
if command -v jq &> /dev/null; then
    print_status "jq found (for JSON processing)"
else
    print_info "jq not found but optional. Install with: apt install jq (Ubuntu) or brew install jq (macOS)"
fi

echo ""
print_info "Setup Instructions:"
echo ""
echo "1. 🌐 Open your n8n instance:"
echo "   - Local: http://localhost:5678"
echo "   - Cloud: https://app.n8n.cloud"
echo ""
echo "2. 📁 Import the workflow:"
echo "   - Go to 'Workflows' → 'Import from JSON'"
echo "   - Copy the contents of 'zenOS_template_selector.json'"
echo "   - Paste and import"
echo ""
echo "3. ▶️ Activate the workflow:"
echo "   - Click the toggle to activate"
echo "   - Note the webhook URL (usually /webhook/template-selector)"
echo ""
echo "4. 🚀 Access your template selector:"
echo "   - Navigate to: https://your-n8n-instance.com/webhook/template-selector"
echo "   - Or: http://localhost:5678/webhook/template-selector (local)"
echo ""
echo "5. 🎉 Test the interface:"
echo "   - Select a template persona"
echo "   - Copy to clipboard"
echo "   - Paste and dominate social media!"
echo ""

print_info "Additional Configuration:"
echo ""
echo "🔗 GitHub Integration:"
echo "   The workflow automatically fetches from:"
echo "   https://raw.githubusercontent.com/k-dot-greyz/zenOS/main/ai_post_templates.yaml"
echo ""
echo "🎨 Customization:"
echo "   - Edit the 'Generate Beautiful Web UI' node for styling changes"
echo "   - Modify colors, fonts, or layout as needed"
echo "   - Templates update automatically from your GitHub repo"
echo ""
echo "📊 Analytics:"
echo "   - Check browser console for usage logs"
echo "   - Extend workflow for advanced tracking"
echo "   - Connect to databases or notification systems"
echo ""

print_status "Setup script completed!"
echo ""
print_info "Next steps:"
echo "1. Import the workflow into n8n"
echo "2. Activate the workflow"
echo "3. Access the web interface"
echo "4. Start dominating social media with AI-generated content!"
echo ""
print_status "The Overlord approves. 👑"
echo ""
echo "Need help? Check the README.md or create an issue on GitHub."
echo "Happy automating! 🚀✨"