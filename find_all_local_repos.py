#!/usr/bin/env python3
"""
Local Git Repository Scanner for zenOS

Scans local filesystem for all git repositories and provides comprehensive
repository management capabilities.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import subprocess

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

def is_git_repository(path: Path) -> bool:
    """Check if a directory is a git repository"""
    git_dir = path / '.git'
    return git_dir.exists() and git_dir.is_dir()

def get_git_info(repo_path: Path) -> Dict:
    """Get git repository information"""
    info = {
        'path': str(repo_path),
        'name': repo_path.name,
        'status': 'unknown',
        'remote_url': None,
        'branch': None,
        'last_commit': None,
        'ahead_behind': None,
        'uncommitted_changes': False,
        'has_staged_changes': False
    }

    try:
        # Check if it's a valid git repo
        result = subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            info['status'] = 'invalid'
            return info

        info['status'] = 'valid'

        # Get remote URL
        result = subprocess.run(
            ['git', 'config', '--get', 'remote.origin.url'],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=3
        )
        if result.returncode == 0:
            info['remote_url'] = result.stdout.strip()

        # Get current branch
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=3
        )
        if result.returncode == 0:
            info['branch'] = result.stdout.strip()

        # Get last commit info
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%h %s %ad', '--date=short'],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=3
        )
        if result.returncode == 0:
            info['last_commit'] = result.stdout.strip()

        # Check status
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            changes = result.stdout.strip()
            info['uncommitted_changes'] = bool(changes)
            # Check for staged changes
            if changes:
                staged_lines = [line for line in changes.split('\n') if line.strip() and not line.startswith(' ')]
                info['has_staged_changes'] = bool(staged_lines)

        # Check ahead/behind status
        if info['remote_url']:
            result = subprocess.run(
                ['git', 'status', '-sb'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and '[' in result.stdout:
                status_line = result.stdout.split('\n')[0]
                if '[' in status_line and ']' in status_line:
                    ahead_behind = status_line.split('[')[1].split(']')[0]
                    info['ahead_behind'] = ahead_behind

    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, Exception) as e:
        info['status'] = f'error: {str(e)}'

    return info

def scan_for_repositories(root_paths: List[Path], max_depth: int = 10, exclude_patterns: List[str] = None) -> List[Dict]:
    """Scan filesystem for git repositories"""
    if exclude_patterns is None:
        exclude_patterns = ['node_modules', '.git', '__pycache__', '.venv', 'venv', 'env']

    repositories = []
    scanned_dirs = 0

    print_colored("🔍 Scanning for git repositories...", Colors.BLUE)

    for root_path in root_paths:
        if not root_path.exists():
            print_colored(f"⚠️  Warning: Path does not exist: {root_path}", Colors.YELLOW)
            continue

        print_colored(f"📁 Scanning: {root_path}", Colors.CYAN)

        try:
            # Walk through directory tree
            for current_path in root_path.rglob('.git'):
                if current_path.is_dir():
                    repo_path = current_path.parent

                    # Check if path should be excluded
                    should_exclude = False
                    for pattern in exclude_patterns:
                        if pattern in str(repo_path):
                            should_exclude = True
                            break

                    if should_exclude:
                        continue

                    # Check depth limit
                    try:
                        depth = len(repo_path.relative_to(root_path).parts)
                        if depth > max_depth:
                            continue
                    except ValueError:
                        # Can't calculate relative path, skip depth check
                        pass

                    scanned_dirs += 1
                    if scanned_dirs % 50 == 0:
                        print_colored(f"  📊 Scanned {scanned_dirs} directories...", Colors.CYAN)

                    if is_git_repository(repo_path):
                        info = get_git_info(repo_path)
                        repositories.append(info)

        except PermissionError:
            print_colored(f"  ❌ Permission denied: {root_path}", Colors.RED)
        except Exception as e:
            print_colored(f"  ❌ Error scanning {root_path}: {e}", Colors.RED)

    return repositories

def get_default_scan_paths() -> List[Path]:
    """Get default paths to scan based on platform"""
    paths = []

    if sys.platform == "win32":
        # Windows paths
        user_profile = os.environ.get('USERPROFILE', '')
        if user_profile:
            paths.extend([
                Path(user_profile) / 'Documents' / 'Code',
                Path(user_profile) / 'source' / 'repos',
                Path(user_profile) / 'Projects',
                Path(user_profile) / 'dev',
            ])

        # Check for common drive letters
        for drive in ['C:', 'D:', 'E:', 'F:']:
            dev_path = Path(f'{drive}/dev')
            code_path = Path(f'{drive}/code')
            projects_path = Path(f'{drive}/projects')

            if dev_path.exists():
                paths.append(dev_path)
            if code_path.exists():
                paths.append(code_path)
            if projects_path.exists():
                paths.append(projects_path)

    else:
        # Unix-like systems
        home = Path.home()
        paths.extend([
            home / 'Documents' / 'Code',
            home / 'Projects',
            home / 'dev',
            home / 'src',
            Path('/opt'),
            Path('/usr/local/src'),
        ])

    # Filter out non-existent paths
    existing_paths = [p for p in paths if p.exists()]
    return existing_paths

def print_repository_summary(repositories: List[Dict]) -> None:
    """Print a summary of found repositories"""
    print_colored(f"\n{'='*60}", Colors.BLUE)
    print_colored("📊 REPOSITORY SCAN SUMMARY", Colors.BOLD)
    print_colored(f"{'='*60}", Colors.BLUE)

    total = len(repositories)
    valid = len([r for r in repositories if r['status'] == 'valid'])
    invalid = len([r for r in repositories if r['status'] != 'valid'])
    with_remote = len([r for r in repositories if r['remote_url']])
    with_changes = len([r for r in repositories if r['uncommitted_changes']])

    print_colored(f"✅ Total repositories found: {total}", Colors.GREEN)
    print_colored(f"✅ Valid repositories: {valid}", Colors.GREEN)
    if invalid > 0:
        print_colored(f"❌ Invalid/problematic: {invalid}", Colors.RED)
    print_colored(f"🔗 With remote origin: {with_remote}", Colors.CYAN)
    if with_changes > 0:
        print_colored(f"📝 With uncommitted changes: {with_changes}", Colors.YELLOW)

def print_repository_details(repositories: List[Dict], show_details: bool = False) -> None:
    """Print detailed repository information"""
    if not repositories:
        print_colored("❌ No repositories found!", Colors.RED)
        return

    print_colored(f"\n{'='*80}", Colors.BLUE)
    print_colored("📋 REPOSITORY DETAILS", Colors.BOLD)
    print_colored(f"{'='*80}", Colors.BLUE)

    for i, repo in enumerate(repositories, 1):
        status_icon = "✅" if repo['status'] == 'valid' else "❌"
        name = repo['name']
        path = repo['path']
        branch = repo['branch'] or 'unknown'
        remote = repo['remote_url'] or 'local only'

        print_colored(f"{i:2d}. {status_icon} {name}", Colors.WHITE)
        print_colored(f"    📁 Path: {path}", Colors.CYAN)
        print_colored(f"    🌿 Branch: {branch}", Colors.GREEN)

        if remote != 'local only':
            # Extract repo name from URL
            if 'github.com' in remote:
                remote_name = remote.split('/')[-1].replace('.git', '')
            else:
                remote_name = remote.split('/')[-1] if '/' in remote else remote
            print_colored(f"    🔗 Remote: {remote_name}", Colors.BLUE)
        else:
            print_colored(f"    🔗 Remote: {remote}", Colors.GRAY)

        if repo['uncommitted_changes']:
            changes_icon = "📝" if repo['has_staged_changes'] else "📄"
            print_colored(f"    {changes_icon} Has uncommitted changes", Colors.YELLOW)

        if repo['ahead_behind']:
            print_colored(f"    📊 Status: {repo['ahead_behind']}", Colors.CYAN)

        if show_details and repo['last_commit']:
            print_colored(f"    🕒 Last commit: {repo['last_commit']}", Colors.GRAY)

        print()

def save_to_json(repositories: List[Dict], output_file: Path) -> None:
    """Save repository data to JSON file"""
    data = {
        'scan_timestamp': datetime.now().isoformat(),
        'total_repositories': len(repositories),
        'repositories': repositories
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print_colored(f"💾 Results saved to: {output_file}", Colors.GREEN)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Scan local filesystem for git repositories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python find_all_local_repos.py                          # Scan default locations
  python find_all_local_repos.py -p C:/dev -p D:/projects  # Scan specific paths
  python find_all_local_repos.py --json results.json      # Save to JSON file
  python find_all_local_repos.py --details                # Show detailed info
        """
    )

    parser.add_argument(
        '-p', '--path',
        action='append',
        type=Path,
        help='Path to scan (can be used multiple times)'
    )

    parser.add_argument(
        '--max-depth',
        type=int,
        default=10,
        help='Maximum directory depth to scan (default: 10)'
    )

    parser.add_argument(
        '--exclude',
        action='append',
        default=[],
        help='Patterns to exclude from scan'
    )

    parser.add_argument(
        '--json',
        type=Path,
        help='Save results to JSON file'
    )

    parser.add_argument(
        '--details',
        action='store_true',
        help='Show detailed repository information'
    )

    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress progress messages'
    )

    args = parser.parse_args()

    # Get scan paths
    if args.path:
        scan_paths = args.path
    else:
        scan_paths = get_default_scan_paths()

    if not scan_paths:
        print_colored("❌ No valid paths to scan. Please specify paths with -p option.", Colors.RED)
        sys.exit(1)

    print_colored("🚀 zenOS Local Repository Scanner", Colors.BOLD)
    print_colored("=" * 50, Colors.BLUE)
    print_colored(f"📁 Scanning paths: {', '.join(str(p) for p in scan_paths)}", Colors.CYAN)

    # Perform scan
    repositories = scan_for_repositories(
        scan_paths,
        max_depth=args.max_depth,
        exclude_patterns=args.exclude
    )

    # Print results
    print_repository_summary(repositories)

    if repositories:
        print_repository_details(repositories, show_details=args.details)

        # Save to JSON if requested
        if args.json:
            save_to_json(repositories, args.json)

    print_colored("\n🎉 Scan complete!", Colors.GREEN)

if __name__ == "__main__":
    main()
