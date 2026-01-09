#!/usr/bin/env python3
"""Safe Command Execution Utility - Following promptOS Best Practices

This utility provides safe, timeout-protected command execution
following the patterns from promptOS git_troubleshooter.py and git_aliases.sh
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union


class SafeCommandExecutor:
    """Safe command execution following promptOS best practices"""

    def __init__(self, default_timeout: int = 30):
        self.default_timeout = default_timeout
        self._ensure_git_safety()

    def _ensure_git_safety(self):
        """Ensure Git is configured safely to prevent hanging"""
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
        """Safely run a command with timeout and proper error handling"""
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
                print("✅ Command succeeded")
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
        """Safely add files to git"""
        return self.run_command(["git", "add", files], timeout=10)

    def safe_git_commit(self, message: str, details: Optional[List[str]] = None) -> Dict:
        """Safely commit with proper multiline handling (following promptOS gcommit pattern)"""
        cmd = ["git", "commit", "-m", message]

        if details:
            for detail in details:
                cmd.extend(["-m", detail])

        return self.run_command(cmd, timeout=15)

    def safe_git_push(self, remote: str = "origin", branch: str = "main") -> Dict:
        """Safely push to remote"""
        return self.run_command(["git", "push", remote, branch], timeout=30)

    def safe_git_status(self) -> Dict:
        """Safely check git status"""
        return self.run_command(["git", "status", "--porcelain"], timeout=5)

    def safe_git_pull(self, remote: str = "origin", branch: str = "main") -> Dict:
        """Safely pull from remote"""
        return self.run_command(["git", "pull", remote, branch], timeout=30)

    def safe_git_checkout(self, branch: str) -> Dict:
        """Safely checkout branch"""
        return self.run_command(["git", "checkout", branch], timeout=10)

    def safe_git_branch(self, branch: str) -> Dict:
        """Safely create and checkout new branch"""
        return self.run_command(["git", "checkout", "-b", branch], timeout=10)

    def safe_git_merge(self, branch: str) -> Dict:
        """Safely merge branch"""
        return self.run_command(["git", "merge", branch], timeout=30)

    def safe_git_log(self, count: int = 10) -> Dict:
        """Safely get git log"""
        return self.run_command(["git", "log", "--oneline", f"-{count}"], timeout=10)

    def safe_git_diff(self) -> Dict:
        """Safely get git diff"""
        return self.run_command(["git", "diff"], timeout=10)

    def safe_git_diff_staged(self) -> Dict:
        """Safely get staged git diff"""
        return self.run_command(["git", "diff", "--staged"], timeout=10)

    def safe_git_remote(self) -> Dict:
        """Safely get git remotes"""
        return self.run_command(["git", "remote", "-v"], timeout=5)

    def safe_git_branches(self) -> Dict:
        """Safely get git branches"""
        return self.run_command(["git", "branch", "-a"], timeout=5)

    def safe_python_script(self, script_path: str, args: Optional[List[str]] = None) -> Dict:
        """Safely run Python script"""
        cmd = [sys.executable, script_path]
        if args:
            cmd.extend(args)
        return self.run_command(cmd, timeout=60)

    def safe_pip_install(self, package: str) -> Dict:
        """Safely install Python package"""
        return self.run_command([sys.executable, "-m", "pip", "install", package], timeout=120)

    def safe_pip_install_requirements(self, requirements_file: str = "requirements.txt") -> Dict:
        """Safely install from requirements file"""
        return self.run_command(
            [sys.executable, "-m", "pip", "install", "-r", requirements_file], timeout=180
        )

    def safe_npm_install(self, package: Optional[str] = None) -> Dict:
        """Safely install npm package or all dependencies"""
        if package:
            cmd = ["npm", "install", package]
        else:
            cmd = ["npm", "install"]
        return self.run_command(cmd, timeout=120)

    def safe_npm_run(self, script: str) -> Dict:
        """Safely run npm script"""
        return self.run_command(["npm", "run", script], timeout=60)


# Convenience functions for quick access
def run_safe_command(cmd: Union[List[str], str], **kwargs) -> Dict:
    """Quick access to safe command execution"""
    executor = SafeCommandExecutor()
    return executor.run_command(cmd, **kwargs)


def safe_git_workflow(
    message: str,
    details: Optional[List[str]] = None,
    push: bool = True,
    remote: str = "origin",
    branch: str = "main",
) -> Dict:
    """Complete safe git workflow: add, commit, optionally push"""
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
