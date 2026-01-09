#!/usr/bin/env python3
"""
Safe Command Execution Utility - Following promptOS Best Practices

This utility provides safe, timeout-protected command execution
following the patterns from promptOS git_troubleshooter.py
"""

import subprocess
import sys
import time
from typing import Dict, List, Optional


def run_command(
    cmd: List[str], cwd: Optional[str] = None, timeout: int = 30, capture_output: bool = True
) -> Dict:
    """Safely run a command with timeout and proper error handling"""
    try:
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(
            cmd, cwd=cwd, capture_output=capture_output, text=True, timeout=timeout, check=False
        )

        return {
            "stdout": result.stdout.strip() if capture_output else "",
            "stderr": result.stderr.strip() if capture_output else "",
            "returncode": result.returncode,
            "success": result.returncode == 0,
        }
    except subprocess.TimeoutExpired:
        print(f"❌ Command timed out after {timeout}s")
        return {
            "stdout": "",
            "stderr": f"Command timed out after {timeout}s",
            "returncode": -1,
            "success": False,
        }
    except Exception as e:
        print(f"❌ Command failed: {e}")
        return {"stdout": "", "stderr": str(e), "returncode": -1, "success": False}


def safe_git_add():
    """Safely add all changes"""
    return run_command(["git", "add", "."])


def safe_git_commit(message: str, details: List[str] = None):
    """Safely commit with proper multiline handling"""
    cmd = ["git", "commit", "-m", message]

    if details:
        for detail in details:
            cmd.extend(["-m", detail])

    return run_command(cmd)


def safe_git_push():
    """Safely push to remote"""
    return run_command(["git", "push"])


def safe_git_status():
    """Safely check git status"""
    return run_command(["git", "status", "--porcelain"])


def main():
    """Main function for testing"""
    print("🧠 Safe Command Execution Utility")
    print("Following promptOS best practices")

    # Test git status
    status = safe_git_status()
    if status["success"]:
        print("✅ Git status check successful")
        if status["stdout"]:
            print(f"Changes: {status['stdout']}")
        else:
            print("No changes detected")
    else:
        print(f"❌ Git status failed: {status['stderr']}")


if __name__ == "__main__":
    main()
