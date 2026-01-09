#!/usr/bin/env python3
"""
zenOS Repository Manager - Unified Git Repository Management Tool

Comprehensive repository management combining local scanning, GitHub operations,
status monitoring, and maintenance tasks.

Features:
- Local repository discovery and inventory
- GitHub repository cloning/updating
- Repository health auditing
- Status monitoring and reporting
- Maintenance operations
- Multi-user support
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from clone_all_repos import (clone_repository, confirm_action,
                             ensure_destination_dir, fetch_all_repos,
                             get_configuration, get_github_token)
from clone_all_repos import parse_arguments as parse_clone_args
from clone_all_repos import (repo_exists_locally, save_results_to_json,
                             update_repository)
# Import our existing modules
from find_all_local_repos import (Colors, get_default_scan_paths, get_git_info,
                                  is_git_repository, print_colored,
                                  scan_for_repositories)


class ZenRepoManager:
    """Unified repository management system"""

    def __init__(self):
        """
        Initialize the ZenRepoManager instance.

        Creates and stores a Colors helper on self.colors for colored terminal output.
        """
        self.colors = Colors()

    def command_scan(self, args) -> int:
        """
        Scan the filesystem for local Git repositories and optionally print details or save results to JSON.

        Parameters:
            args (argparse.Namespace): Parsed command-line arguments. Recognized attributes:
                - path (List[str] | str, optional): Paths to scan; if omitted, default scan paths are used.
                - max_depth (int, optional): Maximum directory depth to search (default 10).
                - exclude (List[str], optional): Glob patterns to exclude from scanning.
                - details (bool, optional): If true, print per-repository detailed information.
                - json (str, optional): File path to write scan results in JSON format.

        Returns:
            int: Exit code — `0` on success, `1` if no valid scan paths were provided.
        """
        print_colored("🔍 Scanning for local repositories...", self.colors.BOLD)

        # Get scan paths
        if hasattr(args, "path") and args.path:
            scan_paths = args.path
        else:
            scan_paths = get_default_scan_paths()

        if not scan_paths:
            print_colored("❌ No valid paths to scan. Please specify paths.", self.colors.RED)
            return 1

        # Perform scan
        repositories = scan_for_repositories(
            scan_paths,
            max_depth=getattr(args, "max_depth", 10),
            exclude_patterns=getattr(args, "exclude", []),
        )

        # Print results
        from find_all_local_repos import (print_repository_details,
                                          print_repository_summary)

        print_repository_summary(repositories)

        if repositories:
            print_repository_details(repositories, show_details=getattr(args, "details", False))

            # Save to JSON if requested
            if hasattr(args, "json") and args.json:
                from find_all_local_repos import save_to_json

                save_to_json(repositories, args.json)

        return 0

    def command_sync(self, args) -> int:
        """
        Synchronize configured GitHub repositories into the local destination.

        Parameters:
            args (argparse.Namespace): Parsed command-line arguments used to derive configuration for the sync operation.

        Returns:
            int: Exit code — `0` on successful completion or when the user declines to proceed, `1` on fatal errors (for example when a GitHub token is unavailable or the destination directory cannot be ensured).
        """
        print_colored("🔄 Syncing repositories...", self.colors.BOLD)

        # This combines local scanning with GitHub operations
        config = get_configuration(args)

        # Get token
        token = get_github_token()
        if not token:
            return 1

        # Ensure destination
        if not ensure_destination_dir(config["destination"], config["dry_run"]):
            return 1

        # Confirm action
        if not confirm_action("Proceed with repository sync?", config["auto_confirm"]):
            return 0

        # Process each user
        all_results = []

        for username in config["usernames"]:
            repos = fetch_all_repos(
                token, username, config["include_private"], config["exclude_forks"]
            )

            for repo in repos:
                repo_name = repo["name"]

                already_local = repo_exists_locally(repo_name, config["destination"])

                if already_local:
                    success, action = update_repository(
                        repo_name, config["destination"], config["dry_run"]
                    )
                else:
                    success, action = clone_repository(
                        repo, config["destination"], config["dry_run"]
                    )

                all_results.append(
                    {
                        "username": username,
                        "repo_name": repo_name,
                        "action": "update" if already_local else "clone",
                        "success": success,
                        "message": action,
                    }
                )

        # Save results if requested
        if config["json_output"]:
            save_results_to_json(config, all_results, config["json_output"])

        return 0

    def command_status(self, args) -> int:
        """
        Scan provided or default filesystem paths for Git repositories, aggregate their statuses, and print a formatted status report.

        Parameters:
            args (argparse.Namespace): Parsed command-line arguments. If `args.path` is present and non-empty, those paths are used for scanning; otherwise default scan paths are used.

        Returns:
            int: Exit code `0` on success.
        """
        print_colored("📊 Checking repository status...", self.colors.BOLD)

        # Get repositories
        if hasattr(args, "path") and args.path:
            scan_paths = args.path
        else:
            scan_paths = get_default_scan_paths()

        repositories = scan_for_repositories(scan_paths)

        # Analyze status
        status_report = self._analyze_repo_status(repositories)
        self._print_status_report(status_report)

        return 0

    def command_audit(self, args) -> int:
        """
        Run a full audit of local repositories and present the results.

        Scans the default repository paths, generates a detailed audit, prints a human-readable audit report, and if the provided args include an `output` path, saves the audit to that file.

        Parameters:
            args (argparse.Namespace): Parsed command arguments. May include an optional `output` attribute (str or pathlib.Path) specifying a file path to write the audit JSON.

        Returns:
            int: Exit code (`0` on success).
        """
        print_colored("🔍 Performing repository audit...", self.colors.BOLD)

        # Get repositories
        scan_paths = get_default_scan_paths()
        repositories = scan_for_repositories(scan_paths)

        # Perform detailed audit
        audit_report = self._perform_audit(repositories)
        self._print_audit_report(audit_report)

        # Save audit if requested
        if hasattr(args, "output") and args.output:
            self._save_audit_report(audit_report, args.output)

        return 0

    def _analyze_repo_status(self, repositories: List[Dict]) -> Dict:
        """
        Produce a summary report of repository health and distribution.

        Parameters:
            repositories (List[Dict]): List of repository info dictionaries. Each dictionary may contain the keys
                'status' (str), 'branch' (str), 'uncommitted_changes' (truthy if present),
                'ahead_behind' (truthy if present), and 'remote_url' (str or falsy).

        Returns:
            Dict: Summary report with the following keys:
                - total_repos (int): Total number of repositories processed.
                - by_status (Dict[str, int]): Counts of repositories grouped by their 'status' value.
                - by_branch (Dict[str, int]): Counts of repositories grouped by their 'branch' value.
                - uncommitted_changes (int): Number of repositories with uncommitted changes.
                - ahead_behind (int): Number of repositories reported as ahead/behind their remote.
                - no_remote (int): Number of repositories missing a remote URL.
                - errors (int): Number of repositories whose status is 'error' or 'invalid'.
        """
        report = {
            "total_repos": len(repositories),
            "by_status": {},
            "by_branch": {},
            "uncommitted_changes": 0,
            "ahead_behind": 0,
            "no_remote": 0,
            "errors": 0,
        }

        for repo in repositories:
            status = repo.get("status", "unknown")
            report["by_status"][status] = report["by_status"].get(status, 0) + 1

            branch = repo.get("branch", "unknown")
            report["by_branch"][branch] = report["by_branch"].get(branch, 0) + 1

            if repo.get("uncommitted_changes"):
                report["uncommitted_changes"] += 1

            if repo.get("ahead_behind"):
                report["ahead_behind"] += 1

            if not repo.get("remote_url"):
                report["no_remote"] += 1

            if status in ["error", "invalid"]:
                report["errors"] += 1

        return report

    def _print_status_report(self, report: Dict) -> None:
        """
        Prints a formatted, colorized repository status report to the console.

        Parameters:
            report (Dict): Aggregated status data with these keys:
                - total_repos (int): Total number of repositories scanned.
                - by_status (Dict[str, int]): Counts of repositories grouped by status (e.g., 'valid', 'invalid').
                - by_branch (Dict[str, int]): Counts of repositories per branch name.
                - uncommitted_changes (int): Number of repositories with uncommitted changes.
                - ahead_behind (int): Number of repositories that are ahead of or behind their remote.
                - no_remote (int): Number of repositories without a configured remote.
                - errors (int): Number of repositories with errors or invalid state.
        """
        print_colored(f"\n{'='*50}", self.colors.BLUE)
        print_colored("📊 REPOSITORY STATUS REPORT", self.colors.BOLD)
        print_colored(f"{'='*50}", self.colors.BLUE)

        print_colored(f"📚 Total repositories: {report['total_repos']}", self.colors.CYAN)

        print_colored(f"\n🔧 Status breakdown:", self.colors.WHITE)
        for status, count in report["by_status"].items():
            color = self.colors.GREEN if status == "valid" else self.colors.RED
            print_colored(f"  {status}: {count}", color)

        print_colored(f"\n🌿 Branch distribution:", self.colors.WHITE)
        for branch, count in sorted(report["by_branch"].items(), key=lambda x: x[1], reverse=True)[
            :10
        ]:
            print_colored(f"  {branch}: {count}", self.colors.CYAN)

        print_colored(f"\n⚠️  Issues detected:", self.colors.YELLOW)
        print_colored(
            f"  📝 Uncommitted changes: {report['uncommitted_changes']}", self.colors.YELLOW
        )
        print_colored(f"  📊 Ahead/behind remote: {report['ahead_behind']}", self.colors.BLUE)
        print_colored(f"  🔗 No remote configured: {report['no_remote']}", self.colors.GRAY)
        print_colored(f"  ❌ Errors: {report['errors']}", self.colors.RED)

    def _perform_audit(self, repositories: List[Dict]) -> Dict:
        """
        Builds a comprehensive audit for the given repositories.

        Parameters:
            repositories (List[Dict]): A list of repository status dictionaries (one per repository) to evaluate.

        Returns:
            Dict: An audit object containing:
                - timestamp: ISO-8601 timestamp when the audit was created.
                - summary: Aggregated status summary for all repositories.
                - issues: Flattened list of detected issues across repositories.
                - recommendations: Flattened list of recommendations across repositories.
                - repositories: Per-repository audit entries with issues, recommendations, and health score.
        """
        audit = {
            "timestamp": datetime.now().isoformat(),
            "summary": {},
            "issues": [],
            "recommendations": [],
            "repositories": [],
        }

        # Analyze each repository
        for repo in repositories:
            repo_audit = self._audit_single_repo(repo)
            audit["repositories"].append(repo_audit)

            # Collect issues
            if repo_audit["issues"]:
                audit["issues"].extend(repo_audit["issues"])

            # Collect recommendations
            if repo_audit["recommendations"]:
                audit["recommendations"].extend(repo_audit["recommendations"])

        # Generate summary
        audit["summary"] = self._analyze_repo_status(repositories)

        return audit

    def _audit_single_repo(self, repo: Dict) -> Dict:
        """
        Evaluate a repository for health issues and generate recommendations and a numeric health score.

        Parameters:
            repo (Dict): Repository metadata with expected keys:
                - name: repository name
                - path: filesystem path
                - status: status string (e.g., "valid", "error")
                - remote_url: remote repository URL or falsy if none
                - uncommitted_changes: truthy if there are uncommitted changes
                - ahead_behind: string describing ahead/behind state (may include "behind")
                - last_commit: string containing an ISO-8601 datetime (used to compute age)

        Returns:
            Dict: Audit summary containing:
                - repo_name (str): repository name
                - path (str): repository path
                - issues (List[str]): detected problems
                - recommendations (List[str]): actionable suggestions
                - health_score (int): overall health between 0 and 100 (higher is better)
        """
        issues = []
        recommendations = []

        # Check for issues
        if repo.get("status") != "valid":
            issues.append(f"Repository status: {repo['status']}")

        if not repo.get("remote_url"):
            issues.append("No remote repository configured")
            recommendations.append("Consider adding a remote origin")

        if repo.get("uncommitted_changes"):
            issues.append("Has uncommitted changes")
            recommendations.append("Consider committing or stashing changes")

        if repo.get("ahead_behind") and "behind" in repo.get("ahead_behind", ""):
            issues.append(f"Behind remote: {repo['ahead_behind']}")
            recommendations.append("Consider pulling latest changes")

        if not repo.get("last_commit"):
            issues.append("No commits found")
        else:
            # Check if last commit is old
            try:
                last_commit_date = datetime.fromisoformat(repo["last_commit"].split()[-1])
                days_since_commit = (datetime.now() - last_commit_date).days
                if days_since_commit > 90:
                    recommendations.append(
                        f"Last commit was {days_since_commit} days ago - consider activity"
                    )
            except:
                pass

        return {
            "repo_name": repo["name"],
            "path": repo["path"],
            "issues": issues,
            "recommendations": recommendations,
            "health_score": max(0, 100 - (len(issues) * 20) - (len(recommendations) * 5)),
        }

    def _print_audit_report(self, audit: Dict) -> None:
        """
        Prints a formatted audit report summarizing repository health, issues, and recommendations.

        Parameters:
            audit (Dict): Audit object with keys:
                - summary (Dict): overall counts (e.g., 'total_repos', 'by_status', 'errors').
                - issues (List[str]): collected critical issue messages.
                - recommendations (List[str]): collected recommendation messages.
                - repositories (List[Dict]): per-repo audit entries; each entry must include a 'health_score' numeric value.
        """
        print_colored(f"\n{'='*60}", self.colors.BLUE)
        print_colored("🔍 REPOSITORY AUDIT REPORT", self.colors.BOLD)
        print_colored(f"{'='*60}", self.colors.BLUE)

        summary = audit["summary"]
        print_colored(f"📚 Total repositories: {summary['total_repos']}", self.colors.CYAN)
        print_colored(
            f"✅ Valid repositories: {summary['by_status'].get('valid', 0)}", self.colors.GREEN
        )
        print_colored(f"❌ Problematic repositories: {summary['errors']}", self.colors.RED)

        print_colored(f"\n🚨 Critical Issues: {len(audit['issues'])}", self.colors.RED)
        for i, issue in enumerate(audit["issues"][:10], 1):  # Show first 10
            print_colored(f"  {i}. {issue}", self.colors.RED)

        if len(audit["issues"]) > 10:
            print_colored(f"  ... and {len(audit['issues']) - 10} more", self.colors.RED)

        print_colored(f"\n💡 Recommendations: {len(audit['recommendations'])}", self.colors.BLUE)
        for i, rec in enumerate(audit["recommendations"][:10], 1):  # Show first 10
            print_colored(f"  {i}. {rec}", self.colors.BLUE)

        if len(audit["recommendations"]) > 10:
            print_colored(f"  ... and {len(audit['recommendations']) - 10} more", self.colors.BLUE)

        # Health score distribution
        health_scores = [r["health_score"] for r in audit["repositories"]]
        if health_scores:
            avg_health = sum(health_scores) / len(health_scores)
            healthy = len([s for s in health_scores if s >= 80])
            needs_attention = len([s for s in health_scores if 50 <= s < 80])
            critical = len([s for s in health_scores if s < 50])

            print_colored(f"\n🏥 Health Overview:", self.colors.WHITE)
            print_colored(f"  📊 Average health score: {avg_health:.1f}", self.colors.CYAN)
            print_colored(f"  🟢 Healthy (80-100): {healthy}", self.colors.GREEN)
            print_colored(f"  🟡 Needs attention (50-79): {needs_attention}", self.colors.YELLOW)
            print_colored(f"  🔴 Critical (<50): {critical}", self.colors.RED)

    def _save_audit_report(self, audit: Dict, output_file: Path) -> None:
        """
        Write the audit dictionary to the given file as pretty-printed UTF-8 JSON and report success or failure.

        Parameters:
            audit (Dict): Audit data structure to serialize to JSON.
            output_file (Path): Path to the file where the JSON will be written; parent directories must exist.

        Notes:
            On success prints a confirmation message. On failure prints an error message with the exception details; exceptions are not propagated.
        """
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(audit, f, indent=2, ensure_ascii=False)
            print_colored(f"💾 Audit report saved to: {output_file}", self.colors.GREEN)
        except Exception as e:
            print_colored(f"❌ Failed to save audit report: {e}", self.colors.RED)


def main():
    """
    Parse command-line arguments and dispatch the selected subcommand to the ZenRepoManager.

    Sets up the CLI with subcommands: scan (discover local repositories), sync (synchronize with remote GitHub repositories), status (check repository status), and audit (generate repository audit). Adds command-specific and global options, creates a ZenRepoManager instance, and invokes the matching command handler. If no command is provided or the command is unknown, prints help or an error and returns a non-zero exit code.

    Returns:
        int: Exit code where `0` indicates success and `1` indicates an error, missing command, or unknown command.
    """
    parser = argparse.ArgumentParser(
        description="zenOS Repository Manager - Unified Git Repository Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan for local repositories")
    scan_parser.add_argument("-p", "--path", action="append", type=Path, help="Paths to scan")
    scan_parser.add_argument("--max-depth", type=int, default=10, help="Maximum scan depth")
    scan_parser.add_argument("--exclude", action="append", default=[], help="Patterns to exclude")
    scan_parser.add_argument("--details", action="store_true", help="Show detailed information")
    scan_parser.add_argument("--json", type=Path, help="Save results to JSON file")

    # Sync command
    sync_parser = subparsers.add_parser("sync", help="Sync repositories with remote sources")
    sync_parser.add_argument("-u", "--username", action="append", help="GitHub usernames")
    sync_parser.add_argument("-d", "--destination", type=Path, help="Destination directory")
    sync_parser.add_argument("--dry-run", action="store_true", help="Preview actions")
    sync_parser.add_argument("--json", type=Path, help="Save results to JSON file")
    sync_parser.add_argument("--yes", action="store_true", help="Skip confirmations")
    sync_parser.add_argument("--include-private", action="store_true", help="Include private repos")
    sync_parser.add_argument("--exclude-forks", action="store_true", help="Exclude forked repos")

    # Status command
    status_parser = subparsers.add_parser("status", help="Check repository status")
    status_parser.add_argument("-p", "--path", action="append", type=Path, help="Paths to check")

    # Audit command
    audit_parser = subparsers.add_parser("audit", help="Perform repository audit")
    audit_parser.add_argument("-o", "--output", type=Path, help="Save audit report to file")

    # Global options
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--quiet", action="store_true", help="Quiet output")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Initialize manager
    manager = ZenRepoManager()

    # Execute command
    command_method = getattr(manager, f"command_{args.command}", None)
    if command_method:
        return command_method(args)
    else:
        print_colored(f"❌ Unknown command: {args.command}", Colors.RED)
        return 1


if __name__ == "__main__":
    sys.exit(main())
