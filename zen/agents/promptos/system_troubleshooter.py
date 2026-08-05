#!/usr/bin/env python3
"""
System Troubleshooter Agent - Development Environment Diagnostics

This agent diagnoses, troubleshoots, and automatically resolves common
local development setup issues including git, shell configuration,
permissions, and tool installation problems.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from zen.core.agent import Agent, AgentManifest
from zen.providers.openrouter import OpenRouterProvider
from zen.utils.safe_commands import SafeCommandExecutor


class SystemTroubleshooterAgent(Agent):
    """System Troubleshooter Agent - Development environment diagnostics"""

    def __init__(self, config: Optional[Dict] = None):
        # Create agent manifest
        """Initialize the system troubleshooter agent with optional configuration."""
        manifest = AgentManifest(
            name="system_troubleshooter",
            description="Diagnoses and fixes development environment issues",
            version="1.0.0",
            author="PromptOS",
            tags=["troubleshooting", "system", "diagnostics"],
        )
        super().__init__(manifest)

        self.specialty = "local development environment diagnostics and automated fixing"
        self.primary_function = "To diagnose, troubleshoot, and automatically resolve common local development setup issues"
        self.voice = (
            "Methodical, diagnostic-focused, and solution-oriented with step-by-step guidance"
        )

        # Initialize components
        self.provider = OpenRouterProvider()
        self.safe_executor = SafeCommandExecutor()

        # Available tools
        self.tools = {
            "system_diagnostic": self._run_system_diagnostic,
            "git_troubleshoot": self._run_git_troubleshoot,
            "shell_config_fix": self._run_shell_config_fix,
            "permission_fixer": self._run_permission_fixer,
            "dependency_checker": self._run_dependency_checker,
            "environment_validator": self._run_environment_validator,
        }

    def execute(self, prompt: str, variables: Dict[str, Any]) -> Any:
        """Run system troubleshooting for the provided prompt and variables.
        
        Parameters:
            prompt (str): The troubleshooting request.
            variables (Dict[str, Any]): Contextual values used during troubleshooting.
        
        Returns:
            Any: The troubleshooting report.
        """
        return self.diagnose_and_fix(prompt, variables)

    def diagnose_and_fix(self, query: str, context: Optional[Dict] = None) -> str:
        """
        Diagnose the local system and produce a troubleshooting report with recommended and safely applied fixes.
        
        Parameters:
            query (str): Description of the system issue to investigate.
            context (Optional[Dict]): Additional troubleshooting context.
        
        Returns:
            str: Markdown-formatted troubleshooting report.
        """

        # Step 1: Run system diagnostics
        diagnostic_result = self._run_system_diagnostic(query)

        # Step 2: Analyze the results
        analysis = self._analyze_diagnostic_results(diagnostic_result, query)

        # Step 3: Generate fixes
        fixes = self._generate_fixes(analysis, query)

        # Step 4: Apply fixes if safe
        applied_fixes = self._apply_safe_fixes(fixes)

        # Step 5: Generate report
        report = self._generate_troubleshooting_report(
            diagnostic_result, analysis, fixes, applied_fixes
        )

        return report

    def _run_system_diagnostic(self, query: str) -> Dict:
        """
        Collect diagnostic information about the operating system, environment, Git status, shell, permissions, and dependencies.
        
        Parameters:
        	query (str): Diagnostic request context.
        
        Returns:
        	Dict: A mapping containing the collected system diagnostic information.
        """
        diagnostic_info = {
            "os": os.name,
            "platform": sys.platform,
            "python_version": sys.version,
            "current_directory": os.getcwd(),
            "environment_variables": dict(os.environ),
            "git_status": self._check_git_status(),
            "shell_info": self._check_shell_info(),
            "permissions": self._check_permissions(),
            "dependencies": self._check_dependencies(),
        }
        return diagnostic_info

    def _check_git_status(self) -> Dict:
        """
        Check Git availability, configuration, and repository status.
        
        Returns:
            Dict: Git availability, version, configured username and email, and whether
                the current directory is inside a repository. Returns an error message
                and ``available`` set to ``False`` if inspection fails.
        """
        try:
            # Check if git is available
            git_version = self.safe_executor.run_command(["git", "--version"], timeout=5)

            # Check git config
            user_name = self.safe_executor.run_command(
                ["git", "config", "--global", "user.name"], timeout=5
            )
            user_email = self.safe_executor.run_command(
                ["git", "config", "--global", "user.email"], timeout=5
            )

            # Check if in git repo
            is_repo = self.safe_executor.run_command(["git", "rev-parse", "--git-dir"], timeout=5)

            return {
                "available": git_version["success"],
                "version": git_version["stdout"] if git_version["success"] else None,
                "user_name": user_name["stdout"] if user_name["success"] else None,
                "user_email": user_email["stdout"] if user_email["success"] else None,
                "in_repo": is_repo["success"],
            }
        except Exception as e:
            return {"error": str(e), "available": False}

    def _check_shell_info(self) -> Dict:
        """Collect the active shell, executable search path, and home directory from the environment.
        
        Returns:
            Dict: Shell configuration values keyed by ``shell``, ``path``, and ``home``.
        """
        shell = os.environ.get("SHELL", os.environ.get("COMSPEC", "unknown"))
        return {
            "shell": shell,
            "path": os.environ.get("PATH", ""),
            "home": os.environ.get("HOME", os.environ.get("USERPROFILE", "")),
        }

    def _check_permissions(self) -> Dict:
        """
        Check read, write, and execute access for the current directory.
        
        Returns:
        	dict: Access status for the current directory, or an error message if inspection fails.
        """
        try:
            current_dir = Path.cwd()
            return {
                "readable": os.access(current_dir, os.R_OK),
                "writable": os.access(current_dir, os.W_OK),
                "executable": os.access(current_dir, os.X_OK),
            }
        except Exception as e:
            return {"error": str(e)}

    def _check_dependencies(self) -> Dict:
        """
        Check the availability of common Python and Node.js dependencies.
        
        Returns:
            Dict[str, bool]: A mapping of dependency names to availability status.
        """
        dependencies = {}

        # Check Python packages
        try:
            import requests

            dependencies["requests"] = True
        except ImportError:
            dependencies["requests"] = False

        try:
            import click

            dependencies["click"] = True
        except ImportError:
            dependencies["click"] = False

        # Check Node.js
        node_check = self.safe_executor.run_command(["node", "--version"], timeout=5)
        dependencies["nodejs"] = node_check["success"]

        # Check npm
        npm_check = self.safe_executor.run_command(["npm", "--version"], timeout=5)
        dependencies["npm"] = npm_check["success"]

        return dependencies

    def _analyze_diagnostic_results(self, diagnostic_result: Dict, query: str) -> Dict:
        """
        Analyze diagnostic results and identify system issues with recommended remediation steps.
        
        Parameters:
            diagnostic_result (Dict): Diagnostic data collected from the system.
            query (str): User query associated with the diagnostic request.
        
        Returns:
            Dict: A report containing identified issues, recommendations, and an overall severity.
        """
        issues = []
        recommendations = []

        # Check git issues
        git_status = diagnostic_result.get("git_status", {})
        if not git_status.get("available"):
            issues.append("Git is not installed or not in PATH")
            recommendations.append("Install Git and ensure it's in your PATH")
        elif not git_status.get("user_name") or not git_status.get("user_email"):
            issues.append("Git user configuration is missing")
            recommendations.append("Run: git config --global user.name 'Your Name'")
            recommendations.append("Run: git config --global user.email 'your.email@example.com'")

        # Check permissions
        permissions = diagnostic_result.get("permissions", {})
        if not permissions.get("writable"):
            issues.append("Current directory is not writable")
            recommendations.append("Check directory permissions or change to a writable directory")

        # Check dependencies
        dependencies = diagnostic_result.get("dependencies", {})
        missing_deps = [dep for dep, available in dependencies.items() if not available]
        if missing_deps:
            issues.append(f"Missing dependencies: {', '.join(missing_deps)}")
            recommendations.append(
                f"Install missing dependencies: pip install {' '.join(missing_deps)}"
            )

        return {
            "issues": issues,
            "recommendations": recommendations,
            "severity": "high" if issues else "low",
        }

    def _generate_fixes(self, analysis: Dict, query: str) -> List[Dict]:
        """
        Generate proposed fixes for the issues identified in a diagnostic analysis.
        
        Parameters:
            analysis (Dict): Diagnostic analysis containing an "issues" list.
            query (str): Original troubleshooting query.
        
        Returns:
            List[Dict]: Fix records containing issue details, commands, and safety status.
        """
        fixes = []

        for i, issue in enumerate(analysis.get("issues", [])):
            fix = {
                "id": f"fix_{i+1}",
                "issue": issue,
                "description": f"Fix: {issue}",
                "commands": [],
                "safe": True,
            }

            if "Git user configuration" in issue:
                fix["commands"] = [
                    "git config --global user.name 'Your Name'",
                    "git config --global user.email 'your.email@example.com'",
                ]
            elif "Missing dependencies" in issue:
                missing_deps = [dep for dep in issue.split(": ")[1].split(", ")]
                fix["commands"] = [f"pip install {' '.join(missing_deps)}"]
            elif "not writable" in issue:
                fix["commands"] = ["chmod +w ."]
                fix["safe"] = False  # Potentially destructive

            fixes.append(fix)

        return fixes

    def _apply_safe_fixes(self, fixes: List[Dict]) -> List[Dict]:
        """
        Apply fixes marked as safe and record the outcome of each command.
        
        Parameters:
            fixes (List[Dict]): Fix definitions containing an identifier, safety flag, and commands.
        
        Returns:
            List[Dict]: Results for each executed command, including its fix identifier, command, success status, and any error message.
        """
        applied = []

        for fix in fixes:
            if not fix.get("safe", False):
                continue

            for command in fix.get("commands", []):
                try:
                    result = self.safe_executor.run_command(command.split(), timeout=30)
                    if result["success"]:
                        applied.append({"fix_id": fix["id"], "command": command, "success": True})
                    else:
                        applied.append(
                            {
                                "fix_id": fix["id"],
                                "command": command,
                                "success": False,
                                "error": result["stderr"],
                            }
                        )
                except Exception as e:
                    applied.append(
                        {"fix_id": fix["id"], "command": command, "success": False, "error": str(e)}
                    )

        return applied

    def _generate_troubleshooting_report(
        self, diagnostic_result: Dict, analysis: Dict, fixes: List[Dict], applied_fixes: List[Dict]
    ) -> str:
        """
        Builds a Markdown report summarizing diagnostic findings, recommended fixes, applied fixes, and system information.
        
        Parameters:
            diagnostic_result (Dict): Collected system information.
            analysis (Dict): Identified issues and their analysis.
            fixes (List[Dict]): Recommended fixes and their commands.
            applied_fixes (List[Dict]): Fixes that were attempted and their outcomes.
        
        Returns:
            str: A formatted troubleshooting report.
        """

        report = f"""
# System Troubleshooting Report

## Issues Found
{len(analysis.get('issues', []))} issues identified

"""

        for issue in analysis.get("issues", []):
            report += f"- ❌ {issue}\n"

        if analysis.get("issues"):
            report += f"\n## Recommended Fixes\n"
            for fix in fixes:
                report += f"\n### {fix['description']}\n"
                for command in fix.get("commands", []):
                    report += f"```bash\n{command}\n```\n"

        if applied_fixes:
            report += f"\n## Applied Fixes\n"
            for fix in applied_fixes:
                status = "✅" if fix["success"] else "❌"
                report += f"{status} {fix['command']}\n"
                if not fix["success"] and "error" in fix:
                    report += f"   Error: {fix['error']}\n"

        report += f"\n## System Information\n"
        report += f"- OS: {diagnostic_result.get('platform', 'Unknown')}\n"
        report += f"- Python: {diagnostic_result.get('python_version', 'Unknown')}\n"
        report += f"- Current Directory: {diagnostic_result.get('current_directory', 'Unknown')}\n"

        return report

    # Tool methods
    def _run_git_troubleshoot(self, query: str) -> str:
        """Return information about the current Git installation and repository status."""
        return self._check_git_status()

    def _run_shell_config_fix(self, query: str) -> str:
        """Report that shell configuration fixes are not implemented."""
        return "Shell configuration fix not implemented yet"

    def _run_permission_fixer(self, query: str) -> str:
        """Report that permission issue remediation is not implemented."""
        return "Permission fixer not implemented yet"

    def _run_dependency_checker(self, query: str) -> str:
        """Reports the availability of supported project dependencies.
        
        Parameters:
        	query (str): The troubleshooting query associated with the dependency check.
        
        Returns:
        	str: A string representation of dependency availability results.
        """
        return str(self._check_dependencies())

    def _run_environment_validator(self, query: str) -> str:
        """Report that environment validation is not implemented."""
        return "Environment validation not implemented yet"
