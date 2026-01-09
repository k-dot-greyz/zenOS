#!/usr/bin/env python3
"""Get Setup Commands for Current Environment

This script detects your current environment and provides the exact commands
you need to run for a complete development setup.
"""

import os
import platform
from pathlib import Path


def detect_environment():
    """Detect the current environment and return setup commands"""
    # Detect OS
    os_name = platform.system().lower()
    if os_name == "windows":
        return get_windows_commands()
    elif os_name == "linux":
        return get_linux_commands()
    elif os_name == "darwin":
        return get_macos_commands()
    else:
        return get_generic_commands()


def get_windows_commands():
    """Provide a command set for setting up the development environment on Windows.

    Returns:
        commands (dict): Dictionary with the following keys:
            platform (str): Human-readable platform name ("Windows").
            one_liner (str): Single-shell command that clones the zenOS repo and starts setup.
            prerequisites (list[str]): Commands to install required tools (Git, Python, NodeJS) on Windows.
            setup (list[str]): Step-by-step commands to clone the repo and run unattended setup.
            validation (str): Command to validate the installed setup.

    """
    return {
        "platform": "Windows",
        "one_liner": "git clone https://github.com/k-dot-greyz/zenOS.git && cd zenOS && python setup.py",
        "prerequisites": [
            "winget install Git.Git",
            "winget install Python.Python.3.11",
            "winget install OpenJS.NodeJS",
        ],
        "setup": [
            "git clone https://github.com/k-dot-greyz/zenOS.git",
            "cd zenOS",
            "python setup.py --unattended",
        ],
        "validation": "python setup.py --validate-only",
    }


def get_linux_commands():
    """Provide a dictionary of recommended setup and validation commands tailored for Linux development environments.

    Returns:
        dict: A mapping with the following keys:
            - platform (str): The platform name ("Linux").
            - one_liner (str): A single command to clone the zenOS repo and start setup.
            - prerequisites (list[str]): Suggested package installation commands and distro notes.
            - setup (list[str]): Step-by-step commands to clone the repo and run unattended setup.
            - validation (str): A command to validate the installation without making changes.

    """
    return {
        "platform": "Linux",
        "one_liner": "git clone https://github.com/k-dot-greyz/zenOS.git && cd zenOS && python setup.py",
        "prerequisites": [
            "sudo apt update && sudo apt install git python3 python3-pip nodejs",
            "# Or for other distros:",
            "# sudo dnf install git python3 python3-pip nodejs  # Fedora",
            "# sudo pacman -S git python python-pip nodejs     # Arch",
        ],
        "setup": [
            "git clone https://github.com/k-dot-greyz/zenOS.git",
            "cd zenOS",
            "python3 setup.py --unattended",
        ],
        "validation": "python3 setup.py --validate-only",
    }


def get_macos_commands():
    """Provide macOS-specific commands and metadata for setting up the development environment.

    Returns:
        dict: A dictionary with the following keys:
            platform (str): Human-readable platform name ("macOS").
            one_liner (str): Single command to clone the repository and run setup.
            prerequisites (list[str]): Homebrew-based prerequisite install commands and notes.
            setup (list[str]): Ordered shell commands to clone the repo, enter it, and run unattended setup.
            validation (str): Command to validate the installation.

    """
    return {
        "platform": "macOS",
        "one_liner": "git clone https://github.com/k-dot-greyz/zenOS.git && cd zenOS && python setup.py",
        "prerequisites": [
            "brew install git python node",
            "# If you don't have Homebrew:",
            '# /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
        ],
        "setup": [
            "git clone https://github.com/k-dot-greyz/zenOS.git",
            "cd zenOS",
            "python3 setup.py --unattended",
        ],
        "validation": "python3 setup.py --validate-only",
    }


def get_generic_commands():
    """Provide a canonical set of setup commands for unknown or unsupported platforms.

    Returns:
        commands (dict): A mapping with the following keys:
            - platform (str): Human-readable platform name ("Unknown").
            - one_liner (str): Single-shell command to clone the repository and run setup.
            - prerequisites (list[str]): High-level prerequisite instructions or notes.
            - setup (list[str]): Ordered shell commands to clone the repo and run unattended setup.
            - validation (str): Command to validate the installation.

    """
    return {
        "platform": "Unknown",
        "one_liner": "git clone https://github.com/k-dot-greyz/zenOS.git && cd zenOS && python setup.py",
        "prerequisites": [
            "Install Git, Python 3.7+, and Node.js (optional)",
            "See docs/guides/DEV_ENVIRONMENT_SETUP.md for details",
        ],
        "setup": [
            "git clone https://github.com/k-dot-greyz/zenOS.git",
            "cd zenOS",
            "python setup.py --unattended",
        ],
        "validation": "python setup.py --validate-only",
    }


def check_termux():
    """Check if running in Termux"""
    return os.environ.get("TERMUX_VERSION") is not None


def get_termux_commands():
    """Provide Termux (Android) tailored setup commands for cloning and configuring the repository.

    Returns:
        dict: A mapping with the following keys:
            - platform: Platform name ("Termux (Android)").
            - one_liner: Single shell command to install prerequisites, clone the repo, and run setup.
            - prerequisites: List of prerequisite shell commands to run before setup.
            - setup: Ordered list of commands for manual setup steps.
            - validation: Command to validate the completed setup.

    """
    return {
        "platform": "Termux (Android)",
        "one_liner": "pkg update && pkg upgrade && pkg install git python nodejs && git clone https://github.com/k-dot-greyz/zenOS.git && cd zenOS && python setup.py",
        "prerequisites": ["pkg update && pkg upgrade", "pkg install git python nodejs"],
        "setup": [
            "git clone https://github.com/k-dot-greyz/zenOS.git",
            "cd zenOS",
            "python setup.py --unattended",
        ],
        "validation": "python setup.py --validate-only",
    }


def print_commands(commands):
    """Print the setup commands in a nice format"""
    print(f"\n🚀 Setup Commands for {commands['platform']}")
    print("=" * 50)

    print("\n📋 One-Command Setup:")
    print(f"   {commands['one_liner']}")

    print("\n🔧 Prerequisites (if not installed):")
    for cmd in commands["prerequisites"]:
        print(f"   {cmd}")

    print("\n⚙️  Manual Setup Steps:")
    for i, cmd in enumerate(commands["setup"], 1):
        print(f"   {i}. {cmd}")

    print("\n✅ Validation:")
    print(f"   {commands['validation']}")

    print("\n📚 Full Guide: docs/guides/DEV_ENVIRONMENT_SETUP.md")
    print("📋 Cheat Sheet: DEV_SETUP_CHEAT_SHEET.md")


def main():
    """Main function"""
    print("🧘 zenOS Development Environment Setup")
    print("=" * 40)

    # Check if we're in Termux
    if check_termux():
        commands = get_termux_commands()
    else:
        commands = detect_environment()

    print_commands(commands)

    # Check if zenOS is already available
    if Path("setup.py").exists():
        print("\n🎉 zenOS detected in current directory!")
        print("   Run: python setup.py --validate-only")
        print("   Or:  python setup.py --unattended")
    else:
        print("\n💡 Tip: Run the one-command setup above to get started!")


if __name__ == "__main__":
    main()
