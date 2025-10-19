#!/bin/bash

# zenOS Release Script
# Automates the release process with safeguards

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Emoji for zen vibes
ZEN="🧘"
ROCKET="🚀"
CHECK="✅"
WARN="⚠️"
INFO="ℹ️"

echo -e "${BLUE}${ZEN} zenOS Release Manager ${ZEN}${NC}"
echo "================================"

# Check if we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo -e "${YELLOW}${WARN} Warning: Not on main branch (currently on: $CURRENT_BRANCH)${NC}"
    read -p "Continue anyway? (y/N): " confirm
    if [ "$confirm" != "y" ]; then
        echo "Release cancelled."
        exit 1
    fi
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo -e "${RED}❌ Error: Uncommitted changes detected${NC}"
    echo "Please commit or stash your changes before releasing."
    exit 1
fi

# Pull latest changes
echo -e "${INFO} Pulling latest changes..."
git pull origin main

# Determine release type
if [ -z "$1" ]; then
    echo "Select release type:"
    echo "1) patch (bug fixes)"
    echo "2) minor (new features)"
    echo "3) major (breaking changes)"
    echo "4) custom version"
    read -p "Enter choice [1-4]: " choice
    
    case $choice in
        1) RELEASE_TYPE="patch" ;;
        2) RELEASE_TYPE="minor" ;;
        3) RELEASE_TYPE="major" ;;
        4) 
            read -p "Enter version (e.g., 1.2.3): " CUSTOM_VERSION
            RELEASE_TYPE="custom"
            ;;
        *) 
            echo "Invalid choice"
            exit 1
            ;;
    esac
else
    RELEASE_TYPE=$1
fi

# Get current version from pyproject.toml
CURRENT_VERSION=$(grep -E "^version = " pyproject.toml | sed 's/version = "\(.*\)"/\1/')
echo -e "${INFO} Current version: ${BLUE}v${CURRENT_VERSION}${NC}"

# Calculate new version
if [ "$RELEASE_TYPE" = "custom" ]; then
    NEW_VERSION=$CUSTOM_VERSION
else
    # Use Python to calculate new version
    NEW_VERSION=$(python -c "
import sys
current = '$CURRENT_VERSION'.split('.')
major, minor, patch = int(current[0]), int(current[1]), int(current[2])

if '$RELEASE_TYPE' == 'major':
    major += 1
    minor = 0
    patch = 0
elif '$RELEASE_TYPE' == 'minor':
    minor += 1
    patch = 0
elif '$RELEASE_TYPE' == 'patch':
    patch += 1

print(f'{major}.{minor}.{patch}')
")
fi

echo -e "${INFO} New version will be: ${GREEN}v${NEW_VERSION}${NC}"

# Confirmation
echo ""
echo "Release Summary:"
echo "----------------"
echo "From: v${CURRENT_VERSION}"
echo "To:   v${NEW_VERSION}"
echo "Type: ${RELEASE_TYPE}"
echo ""
read -p "Proceed with release? (y/N): " confirm

if [ "$confirm" != "y" ]; then
    echo "Release cancelled."
    exit 0
fi

echo ""
echo -e "${ROCKET} Starting release process..."

# Update version in pyproject.toml
echo -e "${INFO} Updating pyproject.toml..."
sed -i "s/version = \"${CURRENT_VERSION}\"/version = \"${NEW_VERSION}\"/" pyproject.toml

# Update version in __init__.py if it exists
if [ -f "zen/__init__.py" ]; then
    echo -e "${INFO} Updating zen/__init__.py..."
    sed -i "s/__version__ = \"${CURRENT_VERSION}\"/__version__ = \"${NEW_VERSION}\"/" zen/__init__.py 2>/dev/null || true
fi

# Update CHANGELOG.md
echo -e "${INFO} Updating CHANGELOG.md..."
TODAY=$(date +%Y-%m-%d)

# Create new version section in CHANGELOG
sed -i "/## \[Unreleased\]/a\\
\\
## [${NEW_VERSION}] - ${TODAY}" CHANGELOG.md

# Update links at bottom of CHANGELOG
sed -i "s|\[Unreleased\]:.*|\[Unreleased\]: https://github.com/k-dot-greyz/zenOS/compare/v${NEW_VERSION}...HEAD\\
[${NEW_VERSION}]: https://github.com/k-dot-greyz/zenOS/compare/v${CURRENT_VERSION}...v${NEW_VERSION}|" CHANGELOG.md

# Commit version bump
echo -e "${INFO} Committing version bump..."
git add pyproject.toml CHANGELOG.md zen/__init__.py 2>/dev/null || true
git commit -m "chore(release): 🚀 v${NEW_VERSION}

- Bump version from ${CURRENT_VERSION} to ${NEW_VERSION}
- Update CHANGELOG.md"

# Create tag
echo -e "${INFO} Creating tag v${NEW_VERSION}..."
git tag -a "v${NEW_VERSION}" -m "Release version ${NEW_VERSION}"

# Push changes
echo -e "${INFO} Pushing to remote..."
git push origin main
git push origin "v${NEW_VERSION}"

echo ""
echo -e "${CHECK} ${GREEN}Release v${NEW_VERSION} completed successfully!${NC}"
echo ""
echo "Next steps:"
echo "1. Go to: https://github.com/k-dot-greyz/zenOS/releases/new"
echo "2. Select tag: v${NEW_VERSION}"
echo "3. Copy the CHANGELOG section for this version"
echo "4. Publish the release"
echo ""
echo -e "${ZEN} Stay zen, my friend ${ZEN}"