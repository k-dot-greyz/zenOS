#!/usr/bin/env python3
"""
Check PR status, conflicts, and mergeability for zenOS repository.

Usage:
    python scripts/check_prs.py                    # Check all open PRs
    python scripts/check_prs.py --pr 42            # Check specific PR
    python scripts/check_prs.py --json              # Output as JSON
    python scripts/check_prs.py --conflicts-only   # Show only PRs with conflicts
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, List, Optional

try:
    from github import Github
except ImportError:
    print("❌ PyGithub not installed. Install with: pip install PyGithub")
    sys.exit(1)


def get_github_token() -> Optional[str]:
    """Get GitHub token from environment."""
    return os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')


def check_pr(pr, json_output: bool = False) -> Dict:
    """Check a single PR's status."""
    data = {
        'number': pr.number,
        'title': pr.title,
        'author': pr.user.login,
        'branch': f"{pr.head.ref} → {pr.base.ref}",
        'state': pr.state,
        'created_at': pr.created_at.isoformat(),
        'updated_at': pr.updated_at.isoformat(),
        'mergeable': pr.mergeable,
        'mergeable_state': pr.mergeable_state,
        'draft': pr.draft,
        'url': pr.html_url,
    }
    
    # Get reviews
    reviews = pr.get_reviews()
    approvals = sum(1 for r in reviews if r.state == 'APPROVED')
    changes_requested = sum(1 for r in reviews if r.state == 'CHANGES_REQUESTED')
    
    data['reviews'] = {
        'approvals': approvals,
        'changes_requested': changes_requested,
        'total': reviews.totalCount
    }
    
    # Get CI status
    commits = pr.get_commits()
    ci_statuses = []
    if commits.totalCount > 0:
        last_commit = commits[commits.totalCount - 1]
        statuses = last_commit.get_statuses()
        for status in statuses:
            ci_statuses.append({
                'context': status.context,
                'state': status.state,
                'description': status.description
            })
    data['ci_statuses'] = ci_statuses
    
    # Get files changed
    files = pr.get_files()
    data['files_changed'] = files.totalCount
    data['files'] = [
        {'filename': f.filename, 'status': f.status, 'additions': f.additions, 'deletions': f.deletions}
        for f in files[:10]  # Limit to first 10 files
    ]
    
    # Determine readiness
    ready = (
        pr.mergeable is True and
        pr.mergeable_state == 'clean' and
        not pr.draft and
        approvals > 0
    )
    data['ready_to_merge'] = ready
    
    if json_output:
        return data
    
    # Pretty print
    print(f"\n{'='*60}")
    print(f"PR #{pr.number}: {pr.title}")
    print(f"{'='*60}")
    print(f"Author: {pr.user.login}")
    print(f"Branch: {pr.head.ref} → {pr.base.ref}")
    print(f"State: {pr.state}")
    print(f"Created: {pr.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Updated: {pr.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"URL: {pr.html_url}")
    
    # Merge status
    print(f"\n📊 Merge Status:")
    if pr.mergeable is True:
        print("  ✅ Mergeable: YES (no conflicts)")
    elif pr.mergeable is False:
        print("  ❌ Mergeable: NO (has conflicts)")
    else:
        print("  ⏳ Mergeable: CHECKING...")
    
    state_icons = {
        'clean': '✅',
        'dirty': '❌',
        'unstable': '⚠️',
        'blocked': '🚫',
        'behind': '⬇️',
        'unknown': '❓'
    }
    icon = state_icons.get(pr.mergeable_state, '❓')
    print(f"  {icon} Merge State: {pr.mergeable_state.upper()}")
    
    # CI status
    print(f"\n🔍 CI Status:")
    if ci_statuses:
        for status in ci_statuses:
            icon = '✅' if status['state'] == 'success' else '❌' if status['state'] == 'failure' else '⚠️'
            print(f"  {icon} {status['context']}: {status['state']}")
    else:
        print("  ⏳ No CI status checks found")
    
    # Reviews
    print(f"\n👥 Reviews:")
    print(f"  ✅ Approvals: {approvals}")
    print(f"  ❌ Changes Requested: {changes_requested}")
    print(f"  📝 Total Reviews: {reviews.totalCount}")
    
    # Status
    if pr.draft:
        print(f"\n📝 Status: DRAFT (not ready for review)")
    else:
        print(f"\n📝 Status: READY FOR REVIEW")
    
    # Labels
    labels = [label.name for label in pr.labels]
    if labels:
        print(f"\n🏷️  Labels: {', '.join(labels)}")
    
    # Files
    print(f"\n📁 Files Changed: {files.totalCount}")
    if files.totalCount <= 10:
        for file in files:
            status_icon = {
                'added': '➕',
                'modified': '✏️',
                'removed': '➖',
                'renamed': '🔄'
            }.get(file.status, '❓')
            print(f"  {status_icon} {file.status}: {file.filename} ({file.additions}+ {file.deletions}-)")
    
    # Summary
    print(f"\n{'='*60}")
    if ready:
        print("✅ READY TO MERGE")
    elif pr.mergeable is False:
        print("❌ HAS CONFLICTS - Needs resolution")
        print("\nTo resolve conflicts:")
        print(f"  1. git checkout {pr.head.ref}")
        print(f"  2. git fetch origin")
        print(f"  3. git merge origin/{pr.base.ref}")
        print("  4. Resolve conflicts manually")
        print("  5. git commit")
        print("  6. git push")
    elif pr.draft:
        print("📝 DRAFT - Not ready for review")
    elif pr.mergeable_state != 'clean':
        print(f"⚠️  NOT READY - Merge state: {pr.mergeable_state}")
    else:
        print("⏳ PENDING - Waiting for reviews/CI")
    print(f"{'='*60}\n")
    
    return data


def main():
    parser = argparse.ArgumentParser(description='Check PR status and conflicts')
    parser.add_argument('--pr', type=int, help='PR number to check (default: all open PRs)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--conflicts-only', action='store_true', help='Show only PRs with conflicts')
    parser.add_argument('--repo', default='k-dot-greyz/zenOS', help='Repository (owner/repo)')
    
    args = parser.parse_args()
    
    # Get token
    token = get_github_token()
    if not token:
        print("❌ GITHUB_TOKEN or GH_TOKEN environment variable not found")
        print("   Set it with: export GITHUB_TOKEN=your_token")
        print("   Or create one at: https://github.com/settings/tokens")
        sys.exit(1)
    
    # Connect to GitHub
    g = Github(token)
    repo = g.get_repo(args.repo)
    
    results = []
    
    if args.pr:
        # Check specific PR
        try:
            pr = repo.get_pull(args.pr)
            if args.conflicts_only and pr.mergeable is not False:
                if not args.json:
                    print(f"PR #{args.pr} does not have conflicts.")
                sys.exit(0)
            
            data = check_pr(pr, json_output=args.json)
            results.append(data)
        except Exception as e:
            print(f"❌ Error checking PR #{args.pr}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Check all open PRs
        if not args.json:
            print(f"🔍 Checking all open PRs for {args.repo}...\n")
        
        open_prs = repo.get_pulls(state='open', sort='updated', direction='desc')
        
        if open_prs.totalCount == 0:
            if args.json:
                print(json.dumps({'prs': [], 'summary': {'total': 0}}))
            else:
                print("✅ No open pull requests")
            return
        
        for pr in open_prs:
            if args.conflicts_only and pr.mergeable is not False:
                continue
            
            data = check_pr(pr, json_output=args.json)
            results.append(data)
        
        # Summary
        if not args.json:
            print(f"\n{'='*60}")
            print("SUMMARY")
            print(f"{'='*60}")
            
            ready_count = sum(1 for r in results if r.get('ready_to_merge'))
            conflict_count = sum(1 for r in results if r.get('mergeable') is False)
            draft_count = sum(1 for r in results if r.get('draft'))
            
            print(f"✅ Ready to merge: {ready_count}")
            print(f"❌ Has conflicts: {conflict_count}")
            print(f"📝 Draft PRs: {draft_count}")
            print(f"📊 Total checked: {len(results)}")
        else:
            summary = {
                'total': len(results),
                'ready_to_merge': sum(1 for r in results if r.get('ready_to_merge')),
                'has_conflicts': sum(1 for r in results if r.get('mergeable') is False),
                'drafts': sum(1 for r in results if r.get('draft'))
            }
            output = {'prs': results, 'summary': summary}
            print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()

