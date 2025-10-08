#!/usr/bin/env python3
"""
GitHub Repository Cloner
Clones all repositories from k-dot-greyz GitHub account to E:\Vault\Code\
"""

import os
import sys
import subprocess
import requests
import json
from pathlib import Path
from typing import List, Dict, Optional

# Configuration
GITHUB_USERNAME = 'k-dot-greyz'
DESTINATION_DIR = r'E:\Vault\Code'
GITHUB_API_BASE = 'https://api.github.com'

# Colors for output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_colored(message: str, color: str = Colors.WHITE) -> None:
    """Print colored output"""
    # Remove emojis for Windows compatibility
    clean_message = message.encode('ascii', 'ignore').decode('ascii')
    print(f"{color}{clean_message}{Colors.END}")

def check_dependencies() -> bool:
    """Check if required dependencies are available"""
    missing = []
    
    # Check if requests is available
    try:
        import requests
    except ImportError:
        missing.append("requests")
    
    # Check if git is available
    try:
        subprocess.run(['git', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing.append("git")
    
    if missing:
        print_colored(f"❌ Missing dependencies: {', '.join(missing)}", Colors.RED)
        print_colored("Install with: pip install requests", Colors.YELLOW)
        return False
    
    return True

def get_github_token() -> Optional[str]:
    """Get GitHub token from environment variables"""
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print_colored("❌ GITHUB_TOKEN environment variable not found", Colors.RED)
        print_colored("Please set your GitHub token:", Colors.YELLOW)
        print_colored("  PowerShell: $env:GITHUB_TOKEN='your_token_here'", Colors.CYAN)
        print_colored("  CMD: set GITHUB_TOKEN=your_token_here", Colors.CYAN)
        print_colored("  Create token at: https://github.com/settings/tokens", Colors.CYAN)
        print_colored("  Required scopes: repo (for private repos)", Colors.CYAN)
        return None
    
    # Test token
    headers = {'Authorization': f'token {token}'}
    try:
        response = requests.get(f'{GITHUB_API_BASE}/user', headers=headers, timeout=10)
        if response.status_code == 200:
            user_data = response.json()
            print_colored(f"✅ Authenticated as: {user_data.get('login', 'Unknown')}", Colors.GREEN)
            return token
        else:
            print_colored(f"❌ Invalid token (status: {response.status_code})", Colors.RED)
            return None
    except requests.RequestException as e:
        print_colored(f"❌ Token validation failed: {e}", Colors.RED)
        return None

def ensure_destination_dir() -> bool:
    """Create destination directory if it doesn't exist"""
    dest_path = Path(DESTINATION_DIR)
    try:
        dest_path.mkdir(parents=True, exist_ok=True)
        print_colored(f"✅ Destination directory: {DESTINATION_DIR}", Colors.GREEN)
        return True
    except Exception as e:
        print_colored(f"❌ Failed to create destination directory: {e}", Colors.RED)
        return False

def fetch_all_repos(token: str) -> List[Dict]:
    """Fetch all repositories from GitHub API with pagination"""
    print_colored("🔍 Fetching repositories from GitHub...", Colors.BLUE)
    
    repos = []
    page = 1
    per_page = 100
    
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    while True:
        url = f'{GITHUB_API_BASE}/user/repos?page={page}&per_page={per_page}&sort=updated'
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            page_repos = response.json()
            if not page_repos:
                break
                
            repos.extend(page_repos)
            print_colored(f"  📄 Fetched page {page} ({len(page_repos)} repos)", Colors.CYAN)
            page += 1
            
        except requests.RequestException as e:
            print_colored(f"❌ Failed to fetch repos (page {page}): {e}", Colors.RED)
            break
    
    print_colored(f"✅ Found {len(repos)} total repositories", Colors.GREEN)
    return repos

def repo_exists_locally(repo_name: str) -> bool:
    """Check if repository exists locally"""
    repo_path = Path(DESTINATION_DIR) / repo_name
    return repo_path.exists() and (repo_path / '.git').exists()

def clone_repository(repo: Dict) -> bool:
    """Clone a repository"""
    repo_name = repo['name']
    clone_url = repo['clone_url']
    repo_path = Path(DESTINATION_DIR) / repo_name
    
    print_colored(f"📥 Cloning: {repo_name}", Colors.BLUE)
    
    try:
        # Use token for authentication if it's a private repo
        if repo.get('private', False):
            # Replace https://github.com with token-based auth
            auth_url = clone_url.replace('https://github.com/', f'https://{os.environ.get("GITHUB_TOKEN")}@github.com/')
        else:
            auth_url = clone_url
        
        result = subprocess.run(
            ['git', 'clone', auth_url, str(repo_path)],
            capture_output=True,
            text=True,
            cwd=DESTINATION_DIR
        )
        
        if result.returncode == 0:
            print_colored(f"  ✅ Cloned: {repo_name}", Colors.GREEN)
            return True
        else:
            print_colored(f"  ❌ Failed to clone {repo_name}: {result.stderr}", Colors.RED)
            return False
            
    except Exception as e:
        print_colored(f"  ❌ Error cloning {repo_name}: {e}", Colors.RED)
        return False

def update_repository(repo_name: str) -> bool:
    """Pull latest changes for existing repository"""
    repo_path = Path(DESTINATION_DIR) / repo_name
    
    print_colored(f"🔄 Updating: {repo_name}", Colors.YELLOW)
    
    try:
        # Check if we're on a branch (not detached HEAD)
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            capture_output=True,
            text=True,
            cwd=repo_path
        )
        
        if result.returncode != 0:
            print_colored(f"  ⚠️  Not a git repository: {repo_name}", Colors.YELLOW)
            return False
        
        # Pull latest changes
        result = subprocess.run(
            ['git', 'pull'],
            capture_output=True,
            text=True,
            cwd=repo_path
        )
        
        if result.returncode == 0:
            print_colored(f"  ✅ Updated: {repo_name}", Colors.GREEN)
            return True
        else:
            print_colored(f"  ❌ Failed to update {repo_name}: {result.stderr}", Colors.RED)
            return False
            
    except Exception as e:
        print_colored(f"  ❌ Error updating {repo_name}: {e}", Colors.RED)
        return False

def main():
    """Main execution function"""
    print_colored("🚀 GitHub Repository Cloner", Colors.BOLD)
    print_colored("=" * 50, Colors.BLUE)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Get GitHub token
    token = get_github_token()
    if not token:
        sys.exit(1)
    
    # Ensure destination directory exists
    if not ensure_destination_dir():
        sys.exit(1)
    
    # Fetch all repositories
    repos = fetch_all_repos(token)
    if not repos:
        print_colored("❌ No repositories found", Colors.RED)
        sys.exit(1)
    
    # Process repositories
    print_colored("\n📦 Processing repositories...", Colors.BLUE)
    print_colored("=" * 50, Colors.BLUE)
    
    stats = {
        'cloned': 0,
        'updated': 0,
        'failed': 0,
        'skipped': 0
    }
    
    for repo in repos:
        repo_name = repo['name']
        is_private = repo.get('private', False)
        visibility = "🔒" if is_private else "🌐"
        
        print_colored(f"\n{visibility} {repo_name} ({repo.get('language', 'Unknown')})", Colors.WHITE)
        
        if repo_exists_locally(repo_name):
            if update_repository(repo_name):
                stats['updated'] += 1
            else:
                stats['failed'] += 1
        else:
            if clone_repository(repo):
                stats['cloned'] += 1
            else:
                stats['failed'] += 1
    
    # Print summary
    print_colored("\n" + "=" * 50, Colors.BLUE)
    print_colored("📊 SUMMARY", Colors.BOLD)
    print_colored("=" * 50, Colors.BLUE)
    print_colored(f"✅ Cloned: {stats['cloned']}", Colors.GREEN)
    print_colored(f"🔄 Updated: {stats['updated']}", Colors.YELLOW)
    print_colored(f"❌ Failed: {stats['failed']}", Colors.RED)
    print_colored(f"📁 Total processed: {sum(stats.values())}", Colors.CYAN)
    
    if stats['failed'] > 0:
        print_colored(f"\n⚠️  {stats['failed']} repositories failed. Check the output above for details.", Colors.YELLOW)
        sys.exit(1)
    else:
        print_colored("\n🎉 All repositories processed successfully!", Colors.GREEN)

if __name__ == "__main__":
    main()
