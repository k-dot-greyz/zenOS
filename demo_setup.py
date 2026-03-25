#!/usr/bin/env python3
"""
zenOS Setup System Demo

A simple demo showing the unified setup system in action.
This demonstrates the key features without running full tests.
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def demo_environment_detection():
    """Demo the environment detection capabilities"""
    console.print(Panel.fit("🔍 Environment Detection Demo", style="bold blue"))

    try:
        from zen.setup.environment_detector import EnvironmentDetector

        detector = EnvironmentDetector()
        system_info = detector.detect_system_info()

        console.print(f"🖥️  OS: {system_info['os']}")
        console.print(f"🐚 Shell: {system_info['shell']}")
        console.print(f"🐍 Python: {system_info['python_version']}")
        console.print(f"📁 Working Directory: {system_info['working_directory']}")
        console.print(
            f"🌐 Internet: {'✅ Connected' if system_info['internet_available'] else '❌ Offline'}"
        )

        # Run validation
        console.print("\n🔍 Running validation...")
        results = detector.validate_environment(system_info)

        for result in results:
            status = "✅" if result.passed else "❌"
            console.print(f"  {status} {result.message}")

        return True

    except Exception as e:
        console.print(f"❌ Environment detection failed: {e}")
        return False


def demo_git_setup():
    """Demo the Git setup capabilities"""
    console.print(Panel.fit("🔧 Git Setup Demo", style="bold green"))

    try:
        from zen.setup.git_setup import GitSetupManager

        # Create a temporary directory for testing
        temp_dir = tempfile.mkdtemp(prefix="zenos_git_demo_")
        console.print(f"📁 Created test directory: {temp_dir}")

        git_manager = GitSetupManager(temp_dir)

        # Check if it's a git repo
        is_repo = git_manager.is_git_repo()
        console.print(f"🔍 Is Git repo: {'✅ Yes' if is_repo else '❌ No'}")

        if not is_repo:
            console.print("🚀 Initializing Git repository...")
            subprocess.run(["git", "init"], cwd=temp_dir, check=True)
            subprocess.run(["git", "config", "user.name", "Demo User"], cwd=temp_dir, check=True)
            subprocess.run(
                ["git", "config", "user.email", "demo@example.com"], cwd=temp_dir, check=True
            )
            console.print("✅ Git repository initialized")

        # Detect project type
        project_types = git_manager.detect_project_type()
        console.print(f"🔍 Detected project types: {', '.join(project_types)}")

        # Create .gitignore
        console.print("📝 Creating .gitignore...")
        success = git_manager.create_gitignore(project_types)
        if success:
            console.print("✅ .gitignore created successfully")
        else:
            console.print("❌ Failed to create .gitignore")

        # Clean up
        shutil.rmtree(temp_dir)
        console.print("🧹 Cleaned up test directory")

        return True

    except Exception as e:
        console.print(f"❌ Git setup demo failed: {e}")
        return False


def demo_setup_command():
    """Demo the main setup command"""
    console.print(Panel.fit("🚀 Setup Command Demo", style="bold magenta"))

    console.print("Available setup commands:")
    console.print("  python setup.py                    # Full interactive setup")
    console.print("  python setup.py --unattended       # Automated setup")
    console.print("  python setup.py --validate-only    # Just validation")
    console.print("  python setup.py --phase git_setup  # Run specific phase")

    console.print("\nOr via zen CLI:")
    console.print("  zen setup                          # Full setup")
    console.print("  zen setup --unattended             # Automated")
    console.print("  zen setup --validate-only          # Validation only")

    # Show what phases are available
    console.print("\n📋 Available phases:")
    phases = [
        "detection",
        "validation",
        "git_setup",
        "mcp_setup",
        "zenos_setup",
        "integration",
        "verification",
    ]
    for phase in phases:
        console.print(f"  - {phase}")


def main():
    """Run the setup system demo"""
    console.print(
        Panel.fit(
            "🧘 zenOS Setup System Demo\n" "Demonstrating the unified setup system capabilities",
            style="bold cyan",
        )
    )

    demos = [
        ("Environment Detection", demo_environment_detection),
        ("Git Setup", demo_git_setup),
        ("Setup Commands", demo_setup_command),
    ]

    for name, demo_func in demos:
        console.print(f"\n{'='*50}")
        success = demo_func()
        if not success:
            console.print(f"⚠️  {name} demo had issues, but continuing...")

    console.print(f"\n{'='*50}")
    console.print(
        Panel.fit(
            "🎉 Demo Complete!\n\n"
            "The unified setup system is ready to use.\n"
            "Try running: python setup.py --validate-only",
            style="bold green",
        )
    )


if __name__ == "__main__":
    main()
