#!/bin/bash
#
# zenOS Private Development Workflow
# Manages private development branch and syncing
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
PRIVATE_REPO="https://github.com/k-dot-greyz/zenOS-dev.git"
DEVELOPMENT_BRANCH="development"
MAIN_BRANCH="main"

# Functions
show_help() {
    echo -e "${CYAN}zenOS Private Development Workflow${NC}"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  setup     - Set up private remote and development branch"
    echo "  sync      - Sync development branch to private repo"
    echo "  pull      - Pull latest from private repo"
    echo "  promote   - Promote development to main (public)"
    echo "  status    - Show current status"
    echo "  help      - Show this help"
    echo ""
}

setup_private() {
    echo -e "${YELLOW}🔧 Setting up private development workflow...${NC}"
    
    # Check if private remote exists
    if git remote get-url private >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Private remote already configured${NC}"
    else
        echo -e "${YELLOW}📝 Adding private remote...${NC}"
        git remote add private "$PRIVATE_REPO"
        echo -e "${GREEN}✅ Private remote added${NC}"
    fi
    
    # Ensure we're on development branch
    if [ "$(git branch --show-current)" != "$DEVELOPMENT_BRANCH" ]; then
        echo -e "${YELLOW}📝 Switching to development branch...${NC}"
        git checkout -b "$DEVELOPMENT_BRANCH" 2>/dev/null || git checkout "$DEVELOPMENT_BRANCH"
    fi
    
    # Push development branch to private repo
    echo -e "${YELLOW}📤 Pushing development branch to private repo...${NC}"
    git push -u private "$DEVELOPMENT_BRANCH"
    
    echo -e "${GREEN}✅ Private development setup complete!${NC}"
    echo ""
    echo -e "${CYAN}Workflow:${NC}"
    echo "  • Work on 'development' branch"
    echo "  • Use '$0 sync' to push to private repo"
    echo "  • Use '$0 promote' to merge to public main"
}

sync_to_private() {
    echo -e "${YELLOW}📤 Syncing development to private repo...${NC}"
    
    # Ensure we're on development branch
    if [ "$(git branch --show-current)" != "$DEVELOPMENT_BRANCH" ]; then
        echo -e "${RED}❌ Not on development branch. Switch to development first.${NC}"
        exit 1
    fi
    
    # Add all changes
    git add -A
    
    # Commit if there are changes
    if ! git diff --cached --quiet; then
        git commit -m "Development: $(date '+%Y-%m-%d %H:%M:%S')"
    fi
    
    # Push to private repo
    git push private "$DEVELOPMENT_BRANCH"
    
    echo -e "${GREEN}✅ Synced to private repo${NC}"
}

pull_from_private() {
    echo -e "${YELLOW}📥 Pulling latest from private repo...${NC}"
    
    git pull private "$DEVELOPMENT_BRANCH"
    
    echo -e "${GREEN}✅ Pulled from private repo${NC}"
}

promote_to_public() {
    echo -e "${YELLOW}🚀 Promoting development to public main...${NC}"
    
    # Switch to main
    git checkout "$MAIN_BRANCH"
    
    # Merge development
    git merge "$DEVELOPMENT_BRANCH" --no-ff -m "Merge development: $(date '+%Y-%m-%d %H:%M:%S')"
    
    # Push to public
    git push origin "$MAIN_BRANCH"
    
    echo -e "${GREEN}✅ Promoted to public main${NC}"
    echo -e "${CYAN}💡 You can now continue development on the development branch${NC}"
}

show_status() {
    echo -e "${CYAN}📊 zenOS Development Status${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Current branch
    CURRENT_BRANCH=$(git branch --show-current)
    echo -e "Current Branch: ${YELLOW}$CURRENT_BRANCH${NC}"
    
    # Remote status
    echo -e "\n${BLUE}Remotes:${NC}"
    git remote -v | sed 's/^/  /'
    
    # Uncommitted changes
    if ! git diff --quiet || ! git diff --cached --quiet; then
        echo -e "\n${YELLOW}⚠️  Uncommitted changes:${NC}"
        git status --porcelain | sed 's/^/  /'
    else
        echo -e "\n${GREEN}✅ Working directory clean${NC}"
    fi
    
    # Branch status
    echo -e "\n${BLUE}Branch Status:${NC}"
    if [ "$CURRENT_BRANCH" = "$DEVELOPMENT_BRANCH" ]; then
        echo -e "  ${GREEN}✓ On development branch${NC}"
    else
        echo -e "  ${YELLOW}⚠ Not on development branch${NC}"
    fi
    
    # Check if private remote exists
    if git remote get-url private >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓ Private remote configured${NC}"
    else
        echo -e "  ${RED}✗ Private remote not configured${NC}"
    fi
}

# Main script logic
case "${1:-help}" in
    setup)
        setup_private
        ;;
    sync)
        sync_to_private
        ;;
    pull)
        pull_from_private
        ;;
    promote)
        promote_to_public
        ;;
    status)
        show_status
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        show_help
        exit 1
        ;;
esac
