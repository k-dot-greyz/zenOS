#!/usr/bin/env python3
"""
Safe Command Execution Utility - Following promptOS Best Practices

This utility provides safe, timeout-protected command execution
following the patterns from promptOS git_troubleshooter.py and git_aliases.sh
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union


class SafeCommandExecutor:
    """Safe command execution following promptOS best practices"""

    def __init__(self, default_timeout: int = 30):
        """
        Initialize the command executor with a default execution timeout and ensure Git has a configured editor.
        
        Parameters:
        	default_timeout (int): Maximum execution time in seconds for commands that do not specify a timeout.
        """
        self.default_timeout = default_timeout
        self._ensure_git_safety()

    def _ensure_git_safety(self):
        """
        Ensure Git has a configured editor to prevent interactive commands from hanging.
        """
        try:
            # Check if git editor is set
            result = self.run_command(["git", "config", "--global", "core.editor"], timeout=5)
            if not result["success"] or not result["stdout"]:
                # Set a safe editor to prevent hanging
                self.run_command(["git", "config", "--global", "core.editor", "nano"], timeout=5)
                print("✅ Set Git editor to nano to prevent hanging")
        except Exception:
            pass  # Continue even if git config fails

    def run_command(
        self,
        cmd: Union[List[str], str],
        cwd: Optional[Union[str, Path]] = None,
        timeout: Optional[int] = None,
        capture_output: bool = True,
        check: bool = False,
    ) -> Dict:
        """
        Execute a command with a timeout and return its execution result.
        
        Parameters:
            cmd (Union[List[str], str]): Command and arguments, provided as a list or whitespace-separated string.
            cwd (Optional[Union[str, Path]]): Working directory for the command.
            timeout (Optional[int]): Maximum execution time in seconds; uses the default timeout when omitted.
            capture_output (bool): Whether to capture standard output and error.
            check (bool): Whether command failures should be treated as subprocess errors.
        
        Returns:
            Dict: Result containing trimmed ``stdout`` and ``stderr``, ``returncode``, and ``success``. Timeout and execution errors use return code ``-1`` and set ``success`` to ``False``.
        """

        if isinstance(cmd, str):
            cmd = cmd.split()

        timeout = timeout or self.default_timeout

        try:
            print(f"🔧 Running: {' '.join(cmd)}")
            result = subprocess.run(
                cmd, cwd=cwd, capture_output=capture_output, text=True, timeout=timeout, check=check
            )

            success = result.returncode == 0
            if success:
                print(f"✅ Command succeeded")
            else:
                print(f"❌ Command failed with exit code {result.returncode}")

            return {
                "stdout": result.stdout.strip() if capture_output else "",
                "stderr": result.stderr.strip() if capture_output else "",
                "returncode": result.returncode,
                "success": success,
            }

        except subprocess.TimeoutExpired:
            print(f"⏰ Command timed out after {timeout}s")
            return {
                "stdout": "",
                "stderr": f"Command timed out after {timeout}s",
                "returncode": -1,
                "success": False,
            }
        except Exception as e:
            print(f"💥 Command failed: {e}")
            return {"stdout": "", "stderr": str(e), "returncode": -1, "success": False}

    def safe_git_add(self, files: str = ".") -> Dict:
        """Stage the specified files for the next Git commit.
        
        Parameters:
            files (str): Files or paths to stage. Defaults to the current directory.
        
        Returns:
            Dict: The command execution result."""
        return self.run_command(["git", "add", files], timeout=10)

    def safe_git_commit(self, message: str, details: Optional[List[str]] = None) -> Dict:
        """Create a Git commit with a primary message and optional additional message paragraphs.
        
        Parameters:
            message (str): The primary commit message.
            details (Optional[List[str]]): Additional commit message paragraphs.
        
        Returns:
            Dict: The command execution result."""
        cmd = ["git", "commit", "-m", message]

        if details:
            for detail in details:
                cmd.extend(["-m", detail])

        return self.run_command(cmd, timeout=15)

    def safe_git_push(self, remote: str = "origin", branch: str = "main") -> Dict:
        """
        Push the specified branch to a Git remote with a bounded execution time.
        
        Parameters:
        	remote (str): Name of the Git remote.
        	branch (str): Name of the branch to push.
        
        Returns:
        	Dict: Command execution results, including output, return code, and success status.
        """
        return self.run_command(["git", "push", remote, branch], timeout=30)

    def safe_git_status(self) -> Dict:
        """Safely check git status"""
        return self.run_command(["git", "status", "--porcelain"], timeout=5)

    def safe_git_pull(self, remote: str = "origin", branch: str = "main") -> Dict:
        """
        Pull changes from a remote Git branch.
        
        Parameters:
        	remote (str): Name of the Git remote.
        	branch (str): Name of the branch to pull.
        
        Returns:
        	Dict: The command execution result.
        """
        return self.run_command(["git", "pull", remote, branch], timeout=30)

    def safe_git_checkout(self, branch: str) -> Dict:
        """
        Safely switch to a Git branch.
        
        Parameters:
        	branch (str): Name of the branch to check out.
        
        Returns:
        	Dict: Command execution result.
        """
        return self.run_command(["git", "checkout", branch], timeout=10)

    def safe_git_branch(self, branch: str) -> Dict:
        """Create and switch to a new Git branch.
        
        Parameters:
        	branch (str): Name of the branch to create.
        
        Returns:
        	Dict: Command execution results."""
        return self.run_command(["git", "checkout", "-b", branch], timeout=10)

    def safe_git_merge(self, branch: str) -> Dict:
        """
        Safely merge a branch into the current Git branch.
        
        Parameters:
        	branch (str): Name of the branch to merge.
        
        Returns:
        	Dict: Result containing the command output, return code, and success status.
        """
        return self.run_command(["git", "merge", branch], timeout=30)

    def safe_git_log(self, count: int = 10) -> Dict:
        """
        Retrieve a bounded list of recent Git commits.
        
        Parameters:
        	count (int): Maximum number of commits to include.
        
        Returns:
        	Dict: Command execution results containing the commit log or failure details.
        """
        return self.run_command(["git", "log", "--oneline", f"-{count}"], timeout=10)

    def safe_git_diff(self) -> Dict:
        """
        Retrieve the differences between the working tree and the index.
        
        Returns:
            Dict: Command execution results, including the diff output, status, and return code.
        """
        return self.run_command(["git", "diff"], timeout=10)

    def safe_git_diff_staged(self) -> Dict:
        """Retrieve the staged changes in the current Git repository.
        
        Returns:
            Dict: The command result containing the staged diff and execution status.
        """
        return self.run_command(["git", "diff", "--staged"], timeout=10)

    def safe_git_remote(self) -> Dict:
        """
        List the configured Git remotes and their URLs.
        
        Returns:
            Dict: The command execution result containing the remotes or failure details.
        """
        return self.run_command(["git", "remote", "-v"], timeout=5)

    def safe_git_branches(self) -> Dict:
        """List local and remote Git branches.
        
        Returns:
        	Dict: The command result containing branch information, output, return code, and success status.
        """
        return self.run_command(["git", "branch", "-a"], timeout=5)

    def safe_python_script(self, script_path: str, args: Optional[List[str]] = None) -> Dict:
        """
        Run a Python script with an optional list of command-line arguments.
        
        Parameters:
        	script_path (str): Path to the Python script to execute.
        	args (Optional[List[str]]): Additional command-line arguments for the script.
        
        Returns:
        	Dict: Command execution results, including output, return code, and success status.
        """
        cmd = [sys.executable, script_path]
        if args:
            cmd.extend(args)
        return self.run_command(cmd, timeout=60)

    def safe_pip_install(self, package: str) -> Dict:
        """Safely install a Python package.
        
        Parameters:
            package (str): The package name or installation specification.
        
        Returns:
            Dict: The command execution result.
        """
        return self.run_command([sys.executable, "-m", "pip", "install", package], timeout=120)

    def safe_pip_install_requirements(self, requirements_file: str = "requirements.txt") -> Dict:
        """Safely install the packages listed in a requirements file.
        
        Parameters:
        	requirements_file (str): Path to the requirements file.
        
        Returns:
        	Dict: The command execution result.
        """
        return self.run_command(
            [sys.executable, "-m", "pip", "install", "-r", requirements_file], timeout=180
        )

    def safe_npm_install(self, package: Optional[str] = None) -> Dict:
        """
        Install an npm package or the project's dependencies.
        
        Parameters:
            package (Optional[str]): Name of the package to install. If omitted, installs all project dependencies.
        
        Returns:
            Dict: Command execution results, including output, return code, and success status.
        """
        if package:
            cmd = ["npm", "install", package]
        else:
            cmd = ["npm", "install"]
        return self.run_command(cmd, timeout=120)

    def safe_npm_run(self, script: str) -> Dict:
        """Execute an npm script and return its execution result.
        
        Parameters:
            script (str): Name of the npm script to run.
        
        Returns:
            Dict: Command execution results, including output, return code, and success status.
        """
        return self.run_command(["npm", "run", script], timeout=60)


# Convenience functions for quick access
def run_safe_command(cmd: Union[List[str], str], **kwargs) -> Dict:
    """
    Execute a command with timeout protection and return its execution details.
    
    Parameters:
        cmd (Union[List[str], str]): Command and arguments to execute.
        **kwargs: Optional execution settings passed to the command executor.
    
    Returns:
        Dict: Execution results, including output, error text, return code, and success status.
    """
    executor = SafeCommandExecutor()
    return executor.run_command(cmd, **kwargs)


def safe_git_workflow(
    message: str,
    details: Optional[List[str]] = None,
    push: bool = True,
    remote: str = "origin",
    branch: str = "main",
) -> Dict:
    """
    Complete a Git add, commit, and optional push workflow.
    
    Parameters:
        message (str): Primary commit message.
        details (Optional[List[str]]): Additional commit message lines.
        push (bool): Whether to push the commit after it is created.
        remote (str): Git remote to push to.
        branch (str): Branch to push to.
    
    Returns:
        Dict: The successful results for each completed stage, or the first failed operation result.
    """
    executor = SafeCommandExecutor()

    # Add all changes
    add_result = executor.safe_git_add()
    if not add_result["success"]:
        return add_result

    # Commit changes
    commit_result = executor.safe_git_commit(message, details)
    if not commit_result["success"]:
        return commit_result

    # Push if requested
    if push:
        push_result = executor.safe_git_push(remote, branch)
        if not push_result["success"]:
            return push_result

    return {
        "success": True,
        "message": "Git workflow completed successfully",
        "add": add_result,
        "commit": commit_result,
        "push": push_result if push else None,
    }


if __name__ == "__main__":
    # Test the safe command executor
    executor = SafeCommandExecutor()

    print("🧠 Safe Command Executor Test")
    print("=" * 40)

    # Test git status
    status = executor.safe_git_status()
    if status["success"]:
        print("✅ Git status check successful")
        if status["stdout"]:
            print(f"Changes: {status['stdout']}")
        else:
            print("No changes detected")
    else:
        print(f"❌ Git status failed: {status['stderr']}")

    # Test git log
    log = executor.safe_git_log(5)
    if log["success"]:
        print("✅ Git log check successful")
        print("Recent commits:")
        for line in log["stdout"].split("\n")[:3]:
            if line.strip():
                print(f"  {line}")
    else:
        print(f"❌ Git log failed: {log['stderr']}")
