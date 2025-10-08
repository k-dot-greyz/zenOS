#!/usr/bin/env python3
"""
GitHub Repository Cloner - Enhanced Version
Clones or updates all repositories from specified GitHub accounts

Features:
- Multiple GitHub accounts support
- Configurable destination directory
- Dry-run mode for preview
- JSON output option
- Safe confirmation prompts
- Environment variable support
"""

import os
import sys
import subprocess
import requests
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

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

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Clone or update all repositories from GitHub accounts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python clone_all_repos.py                          # Clone repos for default user to default dir
  python clone_all_repos.py -u k-dot-greyz -d ./repos # Specific user and directory
  python clone_all_repos.py -u user1 -u user2 --dry-run # Multiple users, preview mode
  python clone_all_repos.py --json results.json      # Save results to JSON
  python clone_all_repos.py --yes                     # Skip confirmation prompts

Environment Variables:
  GITHUB_TOKEN     - GitHub personal access token
  GITHUB_USERNAME  - Default GitHub username
  REPO_DEST_DIR    - Default destination directory
        """
    )

    parser.add_argument(
        '-u', '--username',
        action='append',
        help='GitHub username(s) to clone from (can be used multiple times)'
    )

    parser.add_argument(
        '-d', '--destination',
        type=Path,
        help='Destination directory for repositories'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview actions without making changes'
    )

    parser.add_argument(
        '--json',
        type=Path,
        help='Save results to JSON file'
    )

    parser.add_argument(
        '--yes', '-y',
        action='store_true',
        help='Skip confirmation prompts'
    )

    parser.add_argument(
        '--include-private',
        action='store_true',
        help='Include private repositories'
    )

    parser.add_argument(
        '--exclude-forks',
        action='store_true',
        help='Exclude forked repositories'
    )

    return parser.parse_args()

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

def get_configuration(args) -> Dict:
    """Get configuration from arguments and environment variables"""
    config = {}

    # Get usernames
    usernames = args.username or []
    if not usernames:
        # Try environment variable
        env_user = os.environ.get('GITHUB_USERNAME')
        if env_user:
            usernames = [env_user]
        else:
            # Default fallback
            usernames = ['k-dot-greyz']

    config['usernames'] = usernames

    # Get destination directory
    destination = args.destination
    if not destination:
        # Try environment variable
        env_dest = os.environ.get('REPO_DEST_DIR')
        if env_dest:
            destination = Path(env_dest)
        else:
            # Default fallback based on platform
            if sys.platform == "win32":
                destination = Path(r"E:\Vault\Code")
            else:
                destination = Path.home() / "repos"

    config['destination'] = destination
    config['dry_run'] = args.dry_run
    config['auto_confirm'] = args.yes
    config['include_private'] = args.include_private
    config['exclude_forks'] = args.exclude_forks
    config['json_output'] = args.json

    return config

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
        response = requests.get('https://api.github.com/user', headers=headers, timeout=10)
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

def ensure_destination_dir(destination: Path, dry_run: bool = False) -> bool:
    """Create destination directory if it doesn't exist"""
    try:
        if not dry_run:
            destination.mkdir(parents=True, exist_ok=True)
        print_colored(f"✅ Destination directory: {destination}", Colors.GREEN)
        return True
    except Exception as e:
        print_colored(f"❌ Failed to create destination directory: {e}", Colors.RED)
        return False

def confirm_action(message: str, auto_confirm: bool = False) -> bool:
    """Get user confirmation for an action"""
    if auto_confirm:
        return True

    try:
        response = input(f"{message} (y/N): ").strip().lower()
        return response in ['y', 'yes']
    except KeyboardInterrupt:
        print_colored("\n❌ Operation cancelled by user", Colors.RED)
        return False

def fetch_all_repos(token: str, username: str, include_private: bool = False, exclude_forks: bool = False) -> List[Dict]:
    """Fetch all repositories from GitHub API for a specific user with pagination"""
    print_colored(f"🔍 Fetching repositories for user: {username}", Colors.BLUE)

    repos = []
    page = 1
    per_page = 100

    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    while True:
        # Use different endpoints for different users
        if username == 'authenticated_user':
            url = f'https://api.github.com/user/repos?page={page}&per_page={per_page}&sort=updated'
        else:
            url = f'https://api.github.com/users/{username}/repos?page={page}&per_page={per_page}&sort=updated'

        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            page_repos = response.json()
            if not page_repos:
                break

            # Filter repositories based on criteria
            filtered_repos = []
            for repo in page_repos:
                # Skip private repos if not requested
                if not include_private and repo.get('private', False):
                    continue

                # Skip forks if requested
                if exclude_forks and repo.get('fork', False):
                    continue

                filtered_repos.append(repo)

            repos.extend(filtered_repos)
            print_colored(f"  📄 Fetched page {page} ({len(filtered_repos)} repos)", Colors.CYAN)
            page += 1

        except requests.RequestException as e:
            print_colored(f"❌ Failed to fetch repos for {username} (page {page}): {e}", Colors.RED)
            break

    print_colored(f"✅ Found {len(repos)} repositories for {username}", Colors.GREEN)
    return repos

def repo_exists_locally(repo_name: str, destination: Path) -> bool:
    """Check if repository exists locally"""
    repo_path = destination / repo_name
    return repo_path.exists() and (repo_path / '.git').exists()

def clone_repository(repo: Dict, destination: Path, dry_run: bool = False) -> Tuple[bool, str]:
    """Clone a repository"""
    repo_name = repo['name']
    clone_url = repo['clone_url']
    repo_path = destination / repo_name

    action = "DRY RUN: Would clone" if dry_run else "Cloning"
    print_colored(f"📥 {action}: {repo_name}", Colors.BLUE)

    if dry_run:
        print_colored(f"  📁 Would create: {repo_path}", Colors.CYAN)
        return True, "dry_run"

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
            cwd=destination
        )

        if result.returncode == 0:
            print_colored(f"  ✅ Cloned: {repo_name}", Colors.GREEN)
            return True, "cloned"
        else:
            print_colored(f"  ❌ Failed to clone {repo_name}: {result.stderr}", Colors.RED)
            return False, "clone_failed"

    except Exception as e:
        print_colored(f"  ❌ Error cloning {repo_name}: {e}", Colors.RED)
        return False, "error"

def update_repository(repo_name: str, destination: Path, dry_run: bool = False) -> Tuple[bool, str]:
    """Pull latest changes for existing repository"""
    repo_path = destination / repo_name

    action = "DRY RUN: Would update" if dry_run else "Updating"
    print_colored(f"🔄 {action}: {repo_name}", Colors.YELLOW)

    if dry_run:
        print_colored(f"  📁 Would update: {repo_path}", Colors.CYAN)
        return True, "dry_run"

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
            return False, "not_git_repo"

        # Pull latest changes
        result = subprocess.run(
            ['git', 'pull'],
            capture_output=True,
            text=True,
            cwd=repo_path
        )

        if result.returncode == 0:
            print_colored(f"  ✅ Updated: {repo_name}", Colors.GREEN)
            return True, "updated"
        else:
            print_colored(f"  ❌ Failed to update {repo_name}: {result.stderr}", Colors.RED)
            return False, "pull_failed"

    except Exception as e:
        print_colored(f"  ❌ Error updating {repo_name}: {e}", Colors.RED)
        return False, "error"

def save_results_to_json(config: Dict, all_results: List[Dict], json_file: Path) -> None:
    """Save operation results to JSON file"""
    data = {
        'timestamp': datetime.now().isoformat(),
        'configuration': {
            'usernames': config['usernames'],
            'destination': str(config['destination']),
            'dry_run': config['dry_run'],
            'include_private': config['include_private'],
            'exclude_forks': config['exclude_forks']
        },
        'results': all_results
    }

    try:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print_colored(f"💾 Results saved to: {json_file}", Colors.GREEN)
    except Exception as e:
        print_colored(f"❌ Failed to save results: {e}", Colors.RED)

def main():
    """Main execution function"""
    args = parse_arguments()

    print_colored("🚀 zenOS GitHub Repository Manager", Colors.BOLD)
    print_colored("=" * 60, Colors.BLUE)

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Get configuration
    config = get_configuration(args)
    print_colored(f"👤 Users: {', '.join(config['usernames'])}", Colors.CYAN)
    print_colored(f"📁 Destination: {config['destination']}", Colors.CYAN)
    print_colored(f"🔧 Mode: {'DRY RUN' if config['dry_run'] else 'LIVE'}", Colors.YELLOW if config['dry_run'] else Colors.GREEN)

    # Get GitHub token
    token = get_github_token()
    if not token:
        sys.exit(1)

    # Ensure destination directory exists
    if not ensure_destination_dir(config['destination'], config['dry_run']):
        sys.exit(1)

    # Confirm action if not auto-confirmed
    if not config['auto_confirm']:
        total_users = len(config['usernames'])
        mode_desc = "DRY RUN (preview only)" if config['dry_run'] else "LIVE (will make changes)"
        message = f"Process {total_users} user(s) in {mode_desc} mode?"
        if not confirm_action(message, config['auto_confirm']):
            print_colored("❌ Operation cancelled", Colors.RED)
            sys.exit(0)

    # Process each user
    all_results = []
    total_stats = {
        'users_processed': 0,
        'repos_found': 0,
        'cloned': 0,
        'updated': 0,
        'dry_run': 0,
        'failed': 0,
        'skipped': 0
    }

    for username in config['usernames']:
        print_colored(f"\n{'='*60}", Colors.BLUE)
        print_colored(f"👤 Processing user: {username}", Colors.BOLD)
        print_colored(f"{'='*60}", Colors.BLUE)

        # Fetch repositories for this user
        repos = fetch_all_repos(
            token,
            username,
            config['include_private'],
            config['exclude_forks']
        )

        if not repos:
            print_colored(f"⚠️  No repositories found for {username}", Colors.YELLOW)
            continue

        total_stats['users_processed'] += 1
        total_stats['repos_found'] += len(repos)

        # Process repositories
        print_colored(f"\n📦 Processing {len(repos)} repositories...", Colors.BLUE)

        user_results = []
        user_stats = {'cloned': 0, 'updated': 0, 'dry_run': 0, 'failed': 0, 'skipped': 0}

        for repo in repos:
            repo_name = repo['name']
            is_private = repo.get('private', False)
            is_fork = repo.get('fork', False)
            visibility = "🔒" if is_private else "🌐"
            fork_indicator = " (fork)" if is_fork else ""

            print_colored(f"\n{visibility} {repo_name}{fork_indicator} ({repo.get('language', 'Unknown')})", Colors.WHITE)

            repo_result = {
                'username': username,
                'repo_name': repo_name,
                'is_private': is_private,
                'is_fork': is_fork,
                'action': None,
                'success': False,
                'message': None
            }

            if repo_exists_locally(repo_name, config['destination']):
                success, action = update_repository(repo_name, config['destination'], config['dry_run'])
                repo_result['action'] = 'update'
            else:
                success, action = clone_repository(repo, config['destination'], config['dry_run'])
                repo_result['action'] = 'clone'

            repo_result['success'] = success
            repo_result['message'] = action

            user_results.append(repo_result)

            # Update stats
            if action == 'dry_run':
                user_stats['dry_run'] += 1
                total_stats['dry_run'] += 1
            elif success:
                if action == 'cloned':
                    user_stats['cloned'] += 1
                    total_stats['cloned'] += 1
                elif action == 'updated':
                    user_stats['updated'] += 1
                    total_stats['updated'] += 1
            else:
                user_stats['failed'] += 1
                total_stats['failed'] += 1

        # User summary
        print_colored(f"\n{'='*40}", Colors.CYAN)
        print_colored(f"📊 User Summary: {username}", Colors.BOLD)
        print_colored(f"{'='*40}", Colors.CYAN)
        print_colored(f"✅ Cloned: {user_stats['cloned']}", Colors.GREEN)
        print_colored(f"🔄 Updated: {user_stats['updated']}", Colors.YELLOW)
        print_colored(f"👁️  Dry Run: {user_stats['dry_run']}", Colors.BLUE)
        print_colored(f"❌ Failed: {user_stats['failed']}", Colors.RED)

        all_results.extend(user_results)

    # Final summary
    print_colored(f"\n{'='*60}", Colors.BLUE)
    print_colored("🎯 FINAL SUMMARY", Colors.BOLD)
    print_colored(f"{'='*60}", Colors.BLUE)
    print_colored(f"👥 Users processed: {total_stats['users_processed']}", Colors.CYAN)
    print_colored(f"📚 Repositories found: {total_stats['repos_found']}", Colors.CYAN)
    print_colored(f"✅ Cloned: {total_stats['cloned']}", Colors.GREEN)
    print_colored(f"🔄 Updated: {total_stats['updated']}", Colors.YELLOW)
    print_colored(f"👁️  Dry Run: {total_stats['dry_run']}", Colors.BLUE)
    print_colored(f"❌ Failed: {total_stats['failed']}", Colors.RED)

    # Save results if requested
    if config['json_output']:
        save_results_to_json(config, all_results, config['json_output'])

    # Exit with appropriate code
    if total_stats['failed'] > 0:
        print_colored(f"\n⚠️  {total_stats['failed']} operations failed. Check the output above for details.", Colors.YELLOW)
        sys.exit(1)
    elif config['dry_run']:
        print_colored("\n👁️  Dry run completed successfully!", Colors.BLUE)
    else:
        print_colored("\n🎉 All operations completed successfully!", Colors.GREEN)

if __name__ == "__main__":
    main()
