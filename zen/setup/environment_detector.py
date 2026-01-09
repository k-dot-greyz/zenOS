#!/usr/bin/env python3
"""Environment Detector for zenOS Setup

Detects and analyzes the current environment to provide optimal setup procedures.
Handles Windows, macOS, Linux, and Termux environments with specific optimizations.
"""

import os
import platform
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


@dataclass
class EnvironmentInfo:
    """Information about the current environment"""

    platform: str
    shell: str
    python_version: str
    git_available: bool
    node_available: bool
    is_termux: bool
    is_windows: bool
    is_macos: bool
    is_linux: bool
    zenos_root: Path
    user_home: Path
    setup_log: Path


class EnvironmentDetector:
    """Detects and analyzes the current environment"""

    def __init__(self):
        self.platform_info = platform.platform()
        self.system = platform.system().lower()

    def detect_environment(self, zenos_root: Path) -> EnvironmentInfo:
        """Detect and analyze the current environment"""
        # Detect platform
        platform_name = self._detect_platform()

        # Detect shell
        shell = self._detect_shell()

        # Detect Python version
        python_version = (
            f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        )

        # Check for Git
        git_available = self._check_git_available()

        # Check for Node.js
        node_available = self._check_node_available()

        # Detect Termux
        is_termux = self._detect_termux()

        # Platform flags
        is_windows = self.system == "windows"
        is_macos = self.system == "darwin"
        is_linux = self.system == "linux"

        # Paths
        user_home = Path.home()
        setup_log = zenos_root / "setup.log"

        return EnvironmentInfo(
            platform=platform_name,
            shell=shell,
            python_version=python_version,
            git_available=git_available,
            node_available=node_available,
            is_termux=is_termux,
            is_windows=is_windows,
            is_macos=is_macos,
            is_linux=is_linux,
            zenos_root=zenos_root,
            user_home=user_home,
            setup_log=setup_log,
        )

    def _detect_platform(self) -> str:
        """Detect the specific platform"""
        if self.system == "windows":
            return "windows"
        elif self.system == "darwin":
            return "macos"
        elif self.system == "linux":
            # Check for Termux
            if self._detect_termux():
                return "termux"
            else:
                return "linux"
        else:
            return "unknown"

    def _detect_shell(self) -> str:
        """Detect the current shell"""
        # Check environment variables
        shell = os.environ.get("SHELL", "")
        if shell:
            return Path(shell).name

        # Check COMSPEC on Windows
        if self.system == "windows":
            comspec = os.environ.get("COMSPEC", "")
            if "powershell" in comspec.lower():
                return "powershell"
            elif "cmd" in comspec.lower():
                return "cmd"
            else:
                return "powershell"  # Default to PowerShell

        # Try to detect from process
        try:
            import psutil

            current_process = psutil.Process()
            parent = current_process.parent()
            if parent:
                return Path(parent.exe()).name
        except:
            pass

        # Fallback
        return "bash"

    def _check_git_available(self) -> bool:
        """Check if Git is available"""
        try:
            result = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _check_node_available(self) -> bool:
        """Check if Node.js is available"""
        try:
            result = subprocess.run(
                ["node", "--version"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _detect_termux(self) -> bool:
        """Detect if running in Termux"""
        # Check for Termux-specific environment variables
        termux_vars = ["TERMUX_VERSION", "PREFIX"]
        if any(os.environ.get(var) for var in termux_vars):
            return True

        # Check for Termux-specific paths
        termux_paths = ["/data/data/com.termux/files/usr/bin"]
        if any(Path(path).exists() for path in termux_paths):
            return True

        # Check if we're in a Termux-like environment
        if self.system == "linux":
            # Check for Android-specific indicators
            android_indicators = ["/system/bin", "/system/lib", "/data/data"]
            if any(Path(path).exists() for path in android_indicators):
                return True

        return False

    def get_platform_specific_commands(self, env_info: EnvironmentInfo) -> Dict[str, List[str]]:
        """Get platform-specific commands for setup"""
        commands = {
            "install_python_deps": [],
            "install_node_deps": [],
            "setup_shell_aliases": [],
            "setup_git_config": [],
            "setup_mcp_servers": [],
        }

        if env_info.is_termux:
            commands["install_python_deps"] = [
                "pkg update",
                "pkg install python",
                "pip install --user -r requirements.txt",
            ]
            commands["install_node_deps"] = [
                "pkg install nodejs",
                "npm install -g @modelcontextprotocol/server-filesystem",
            ]
            commands["setup_shell_aliases"] = [
                "echo \"alias zen='python3 zen/cli.py'\" >> ~/.bashrc",
                "source ~/.bashrc",
            ]

        elif env_info.is_windows:
            commands["install_python_deps"] = ["python -m pip install -r requirements.txt"]
            commands["install_node_deps"] = [
                "npm install -g @modelcontextprotocol/server-filesystem"
            ]
            commands["setup_shell_aliases"] = ["Import-Module ./zenos.psm1"]

        elif env_info.is_macos:
            commands["install_python_deps"] = ["python3 -m pip install -r requirements.txt"]
            commands["install_node_deps"] = [
                "npm install -g @modelcontextprotocol/server-filesystem"
            ]
            commands["setup_shell_aliases"] = [
                "echo \"alias zen='python3 zen/cli.py'\" >> ~/.zshrc",
                "source ~/.zshrc",
            ]

        else:  # Linux
            commands["install_python_deps"] = [
                "sudo apt update",
                "sudo apt install python3-pip",
                "python3 -m pip install -r requirements.txt",
            ]
            commands["install_node_deps"] = [
                "curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -",
                "sudo apt-get install -y nodejs",
                "npm install -g @modelcontextprotocol/server-filesystem",
            ]
            commands["setup_shell_aliases"] = [
                "echo \"alias zen='python3 zen/cli.py'\" >> ~/.bashrc",
                "source ~/.bashrc",
            ]

        return commands

    def get_environment_warnings(self, env_info: EnvironmentInfo) -> List[str]:
        """Get environment-specific warnings and recommendations"""
        warnings = []

        if env_info.is_termux:
            warnings.extend(
                [
                    "Termux detected - using user installation for Python packages",
                    "Some features may be limited on mobile devices",
                    "Consider using a desktop environment for full functionality",
                ]
            )

        if not env_info.git_available:
            warnings.append("Git not available - git integration will be disabled")

        if not env_info.node_available:
            warnings.append("Node.js not available - MCP integration will be disabled")

        if env_info.python_version < "3.7":
            warnings.append(f"Python {env_info.python_version} detected - Python 3.7+ recommended")

        if env_info.is_windows and "powershell" not in env_info.shell.lower():
            warnings.append("PowerShell recommended on Windows for best compatibility")

        return warnings

    def get_optimization_suggestions(self, env_info: EnvironmentInfo) -> List[str]:
        """Get environment-specific optimization suggestions"""
        suggestions = []

        if env_info.is_termux:
            suggestions.extend(
                [
                    "Enable battery optimization for zenOS",
                    "Use Termux:API for enhanced mobile features",
                    "Consider using a physical keyboard for better productivity",
                ]
            )

        if env_info.is_windows:
            suggestions.extend(
                [
                    "Enable Windows Subsystem for Linux (WSL) for better Unix compatibility",
                    "Use Windows Terminal for better terminal experience",
                    "Consider using Git Bash for Unix-like commands",
                ]
            )

        if env_info.is_macos:
            suggestions.extend(
                [
                    "Install Homebrew for better package management",
                    "Use iTerm2 for enhanced terminal experience",
                    "Enable Touch ID for secure authentication",
                ]
            )

        if env_info.is_linux:
            suggestions.extend(
                [
                    "Install zsh and oh-my-zsh for better shell experience",
                    "Use tmux or screen for session management",
                    "Consider using a tiling window manager for efficiency",
                ]
            )

        return suggestions
