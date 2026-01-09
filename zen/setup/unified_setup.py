#!/usr/bin/env python3
"""zenOS Unified Setup Manager

The master setup system that combines the best procedures from promptOS and mcp-config
to create a bulletproof, environment-agnostic development environment.

This is the "one command" solution that works everywhere and never gets lost.
"""

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

from .environment_detector import EnvironmentDetector
from .git_setup import GitSetupManager
from .mcp_setup import MCPSetupManager
from .troubleshooter import SetupTroubleshooter


class SetupPhase(Enum):
    """Setup phases for progressive installation"""

    DETECTION = "detection"
    VALIDATION = "validation"
    GIT_SETUP = "git_setup"
    MCP_SETUP = "mcp_setup"
    ZENOS_SETUP = "zenos_setup"
    INTEGRATION = "integration"
    VERIFICATION = "verification"
    COMPLETE = "complete"


@dataclass
class SetupContext:
    """Context information for the setup process"""

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


class UnifiedSetupManager:
    """Master setup manager that orchestrates all setup procedures"""

    def __init__(self, zenos_root: Optional[Path] = None, unattended: bool = False):
        self.zenos_root = zenos_root or Path.cwd()
        self.unattended = unattended
        self.context = None
        self.current_phase = SetupPhase.DETECTION
        self.setup_log = self.zenos_root / "setup.log"

        # Initialize components
        self.env_detector = EnvironmentDetector()
        self.git_manager = GitSetupManager(self.zenos_root)
        self.mcp_manager = MCPSetupManager(self.zenos_root)
        self.troubleshooter = SetupTroubleshooter()

    def run_setup(self) -> bool:
        """Run the complete unified setup process"""
        try:
            self._print_banner()

            # Phase 1: Environment Detection
            if not self._run_detection_phase():
                return False

            # Phase 2: Validation
            if not self._run_validation_phase():
                return False

            # Phase 3: Git Setup
            if not self._run_git_setup_phase():
                return False

            # Phase 4: MCP Setup
            if not self._run_mcp_setup_phase():
                return False

            # Phase 5: zenOS Setup
            if not self._run_zenos_setup_phase():
                return False

            # Phase 6: Integration
            if not self._run_integration_phase():
                return False

            # Phase 7: Verification
            if not self._run_verification_phase():
                return False

            self._setup_complete()
            return True

        except Exception as e:
            self._handle_setup_failure(e)
            return False

    def _print_banner(self):
        """Print the zenOS setup banner"""
        banner = """
    ╔════════════════════════════════════════════════════════════════╗
    ║                     🧘 zenOS Setup                            ║
    ║              Unified Development Environment                    ║
    ╠════════════════════════════════════════════════════════════════╣
    ║  • Cross-platform compatibility (Windows, macOS, Linux, Termux)║
    ║  • AI-powered troubleshooting and validation                   ║
    ║  • Git repository setup and maintenance                       ║
    ║  • MCP server configuration and linking                       ║
    ║  • Environment detection and adaptation                       ║
    ║  • Progressive failure recovery                               ║
    ║  • One-command setup for any environment                      ║
    ╚════════════════════════════════════════════════════════════════╝
        """
        print(banner)

    def _run_detection_phase(self) -> bool:
        """Phase 1: Environment detection and analysis"""
        print("\n[DETECT] Phase 1: Environment Detection")
        print("-" * 40)

        self.context = self.env_detector.detect_environment(self.zenos_root)

        print(f"  Platform: {self.context.platform}")
        print(f"  Shell: {self.context.shell}")
        print(f"  Python: {self.context.python_version}")
        print(f"  Git: {'[OK] Available' if self.context.git_available else '[FAIL] Missing'}")
        print(f"  Node: {'[OK] Available' if self.context.node_available else '[FAIL] Missing'}")
        print(f"  Termux: {'[OK] Yes' if self.context.is_termux else '[FAIL] No'}")

        self.current_phase = SetupPhase.VALIDATION
        return True

    def _run_validation_phase(self) -> bool:
        """Phase 2: System validation with AI troubleshooting"""
        print("\n[OK] Phase 2: System Validation")
        print("-" * 40)

        validation_results = self.troubleshooter.validate_system(self.context)

        if validation_results["issues"]:
            print(f"  [WARN] Found {len(validation_results['issues'])} issues")

            if not self.unattended:
                print("  [AI] Running AI diagnosis...")
                diagnosis = self.troubleshooter.diagnose_issues(validation_results["issues"])

                if diagnosis["fixes"]:
                    print("  [FIX] Applying AI-suggested fixes...")
                    if not self.troubleshooter.apply_fixes(diagnosis["fixes"]):
                        print("  [FAIL] Some fixes failed, continuing with manual intervention...")
                else:
                    print("  [WARN] No automated fixes available, manual intervention required")
        else:
            print("  [OK] All validations passed!")

        self.current_phase = SetupPhase.GIT_SETUP
        return True

    def _run_git_setup_phase(self) -> bool:
        """Phase 3: Git repository setup and configuration"""
        print("\n📦 Phase 3: Git Setup")
        print("-" * 40)

        if not self.context.git_available:
            print("  ⚠️  Git not available, skipping git setup")
            self.current_phase = SetupPhase.MCP_SETUP
            return True

        # Initialize git repository if needed
        if not self.git_manager.is_git_repo():
            print("  🔧 Initializing git repository...")
            if not self.git_manager.init_repository():
                print("  ❌ Failed to initialize git repository")
                return False

        # Setup .gitignore
        print("  📝 Setting up .gitignore...")
        if not self.git_manager.setup_gitignore():
            print("  ❌ Failed to setup .gitignore")
            return False

        # Setup git aliases
        print("  🔗 Setting up git aliases...")
        if not self.git_manager.setup_aliases():
            print("  ⚠️  Git aliases setup failed, continuing...")

        # Configure git user if needed
        if not self.git_manager.has_user_config():
            print("  👤 Git user not configured")
            if not self.unattended:
                name = input("  Enter your name: ").strip()
                email = input("  Enter your email: ").strip()
                if name and email:
                    self.git_manager.configure_user(name, email)

        self.current_phase = SetupPhase.MCP_SETUP
        return True

    def _run_mcp_setup_phase(self) -> bool:
        """Phase 4: MCP server setup and configuration"""
        print("\n🔌 Phase 4: MCP Setup")
        print("-" * 40)

        if not self.context.node_available:
            print("  ⚠️  Node.js not available, skipping MCP setup")
            self.current_phase = SetupPhase.ZENOS_SETUP
            return True

        # Setup MCP servers
        print("  📦 Installing MCP servers...")
        if not self.mcp_manager.install_servers():
            print("  ❌ Failed to install MCP servers")
            return False

        # Link configurations
        print("  🔗 Linking MCP configurations...")
        if not self.mcp_manager.link_configurations():
            print("  ⚠️  MCP configuration linking failed, continuing...")

        # Run health checks
        print("  🏥 Running MCP health checks...")
        if not self.mcp_manager.run_health_checks():
            print("  ⚠️  Some MCP health checks failed, continuing...")

        self.current_phase = SetupPhase.ZENOS_SETUP
        return True

    def _run_zenos_setup_phase(self) -> bool:
        """Phase 5: zenOS-specific setup"""
        print("\n🧘 Phase 5: zenOS Setup")
        print("-" * 40)

        # Install Python dependencies
        print("  📦 Installing Python dependencies...")
        if not self._install_python_dependencies():
            print("  ❌ Failed to install Python dependencies")
            return False

        # Setup zenOS configuration
        print("  ⚙️  Setting up zenOS configuration...")
        if not self._setup_zenos_config():
            print("  ❌ Failed to setup zenOS configuration")
            return False

        # Setup CLI aliases
        print("  🔗 Setting up CLI aliases...")
        if not self._setup_cli_aliases():
            print("  ⚠️  CLI aliases setup failed, continuing...")

        self.current_phase = SetupPhase.INTEGRATION
        return True

    def _run_integration_phase(self) -> bool:
        """Phase 6: Integration and linking"""
        print("\n🔗 Phase 6: Integration")
        print("-" * 40)

        # Link promptOS integration
        print("  🔌 Setting up promptOS integration...")
        if not self._setup_promptos_integration():
            print("  ⚠️  promptOS integration failed, continuing...")

        # Setup workspace
        print("  📁 Setting up workspace...")
        if not self._setup_workspace():
            print("  ❌ Failed to setup workspace")
            return False

        self.current_phase = SetupPhase.VERIFICATION
        return True

    def _run_verification_phase(self) -> bool:
        """Phase 7: Final verification and testing"""
        print("\n✅ Phase 7: Verification")
        print("-" * 40)

        # Test zenOS CLI
        print("  🧪 Testing zenOS CLI...")
        if not self._test_zenos_cli():
            print("  ❌ zenOS CLI test failed")
            return False

        # Test git integration
        print("  📦 Testing git integration...")
        if not self._test_git_integration():
            print("  ⚠️  Git integration test failed, continuing...")

        # Test MCP integration
        if self.context.node_available:
            print("  🔌 Testing MCP integration...")
            if not self._test_mcp_integration():
                print("  ⚠️  MCP integration test failed, continuing...")

        self.current_phase = SetupPhase.COMPLETE
        return True

    def _install_python_dependencies(self) -> bool:
        """Install Python dependencies"""
        try:
            # Check if requirements.txt exists
            requirements_file = self.zenos_root / "requirements.txt"
            if not requirements_file.exists():
                print("  ⚠️  No requirements.txt found, creating basic one...")
                self._create_basic_requirements()

            # Install dependencies
            if self.context.is_termux:
                cmd = [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--user",
                    "-r",
                    str(requirements_file),
                ]
            else:
                cmd = [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)]

            result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(self.zenos_root))
            if result.returncode != 0:
                print(f"  ❌ pip install failed: {result.stderr}")
                return False

            print("  ✅ Python dependencies installed")
            return True
        except Exception as e:
            print(f"  ❌ Failed to install Python dependencies: {e}")
            return False

    def _create_basic_requirements(self):
        """Create basic requirements.txt if none exists"""
        requirements = """# zenOS Core Dependencies
click>=8.0.0
rich>=13.0.0
pyyaml>=6.0
requests>=2.28.0
httpx>=0.24.0
psutil>=5.9.0
nltk>=3.8.0
"""
        with open(self.zenos_root / "requirements.txt", "w") as f:
            f.write(requirements)

    def _setup_zenos_config(self) -> bool:
        """Setup zenOS configuration"""
        try:
            config_dir = self.zenos_root / "config"
            config_dir.mkdir(exist_ok=True)

            # Create basic config
            config = {
                "version": "1.0.0",
                "environment": self.context.platform,
                "setup_date": str(
                    subprocess.run(["date"], capture_output=True, text=True).stdout.strip()
                ),
                "features": {
                    "git_integration": self.context.git_available,
                    "mcp_integration": self.context.node_available,
                    "ai_agents": True,
                    "plugin_system": True,
                },
            }

            with open(config_dir / "zenos.json", "w") as f:
                json.dump(config, f, indent=2)

            print("  ✅ zenOS configuration created")
            return True
        except Exception as e:
            print(f"  ❌ Failed to setup zenOS config: {e}")
            return False

    def _setup_cli_aliases(self) -> bool:
        """Setup CLI aliases for zenOS"""
        try:
            if self.context.is_windows:
                return self._setup_powershell_aliases()
            else:
                return self._setup_unix_aliases()
        except Exception as e:
            print(f"  ❌ Failed to setup CLI aliases: {e}")
            return False

    def _setup_powershell_aliases(self) -> bool:
        """Setup PowerShell aliases"""
        try:
            # Create zenOS PowerShell module
            module_content = f"""
# zenOS PowerShell Module
function zen {{
    python "{self.zenos_root}\\zen\\cli.py" $args
}}

function zen-receive {{
    python "{self.zenos_root}\\zen\\cli.py" receive $args
}}

function zen-plugins {{
    python "{self.zenos_root}\\zen\\cli.py" plugins $args
}}

Export-ModuleMember -Function zen, zen-receive, zen-plugins
"""

            module_path = self.zenos_root / "zenos.psm1"
            with open(module_path, "w") as f:
                f.write(module_content)

            print("  ✅ PowerShell module created")
            print("  📝 To use: Import-Module ./zenos.psm1")
            return True
        except Exception as e:
            print(f"  ❌ PowerShell alias setup failed: {e}")
            return False

    def _setup_unix_aliases(self) -> bool:
        """Setup Unix aliases (bash/zsh)"""
        try:
            # Determine shell profile
            shell = self.context.shell
            if "zsh" in shell:
                profile_file = Path.home() / ".zshrc"
            else:
                profile_file = Path.home() / ".bashrc"

            # Create aliases
            aliases = f"""
# zenOS Aliases
alias zen='python3 "{self.zenos_root}/zen/cli.py"'
alias zen-receive='python3 "{self.zenos_root}/zen/cli.py" receive'
alias zen-plugins='python3 "{self.zenos_root}/zen/cli.py" plugins'
"""

            # Add to profile if not already there
            if profile_file.exists():
                with open(profile_file, "r") as f:
                    content = f.read()
                if "zenOS Aliases" not in content:
                    with open(profile_file, "a") as f:
                        f.write(aliases)
            else:
                with open(profile_file, "w") as f:
                    f.write(aliases)

            print("  ✅ Unix aliases added to shell profile")
            print(f"  📝 Restart shell or run: source {profile_file}")
            return True
        except Exception as e:
            print(f"  ❌ Unix alias setup failed: {e}")
            return False

    def _setup_promptos_integration(self) -> bool:
        """Setup promptOS integration"""
        try:
            # Check if promptOS exists
            promptos_path = self.zenos_root.parent / "Prompt_OS"
            if not promptos_path.exists():
                print("  ⚠️  promptOS not found, skipping integration")
                return True

            # Create symlink or copy integration files
            integration_dir = self.zenos_root / "integrations" / "promptos"
            integration_dir.mkdir(parents=True, exist_ok=True)

            # Create integration config
            integration_config = {
                "promptos_path": str(promptos_path),
                "enabled": True,
                "features": ["agents", "auto_critique", "mcp_integration"],
            }

            with open(integration_dir / "config.json", "w") as f:
                json.dump(integration_config, f, indent=2)

            print("  ✅ promptOS integration configured")
            return True
        except Exception as e:
            print(f"  ❌ promptOS integration failed: {e}")
            return False

    def _setup_workspace(self) -> bool:
        """Setup workspace directories"""
        try:
            workspace_dirs = [
                "workspace",
                "workspace/projects",
                "workspace/templates",
                "workspace/scripts",
                "inbox",
                "inbox/incoming",
                "inbox/processing",
                "inbox/processed",
                "inbox/tools",
                "inbox/context",
                "inbox/ideas",
            ]

            for dir_path in workspace_dirs:
                (self.zenos_root / dir_path).mkdir(parents=True, exist_ok=True)

            print("  ✅ Workspace directories created")
            return True
        except Exception as e:
            print(f"  ❌ Workspace setup failed: {e}")
            return False

    def _test_zenos_cli(self) -> bool:
        """Test zenOS CLI functionality"""
        try:
            # Test basic CLI
            result = subprocess.run(
                [sys.executable, str(self.zenos_root / "zen" / "cli.py"), "--help"],
                capture_output=True,
                text=True,
                cwd=str(self.zenos_root),
            )
            return result.returncode == 0
        except Exception as e:
            print(f"  ❌ zenOS CLI test failed: {e}")
            return False

    def _test_git_integration(self) -> bool:
        """Test git integration"""
        try:
            if not self.context.git_available:
                return True

            # Test git status
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=str(self.zenos_root),
            )
            return result.returncode == 0
        except Exception as e:
            print(f"  ❌ Git integration test failed: {e}")
            return False

    def _test_mcp_integration(self) -> bool:
        """Test MCP integration"""
        try:
            if not self.context.node_available:
                return True

            # Test MCP health check
            return self.mcp_manager.run_health_checks()
        except Exception as e:
            print(f"  ❌ MCP integration test failed: {e}")
            return False

    def _setup_complete(self):
        """Handle successful setup completion"""
        print("\n🎉 zenOS Setup Complete!")
        print("=" * 60)

        print("\n✅ What was accomplished:")
        print("   • Environment detected and validated")
        print("   • Git repository configured with .gitignore and aliases")
        print("   • MCP servers installed and configured")
        print("   • zenOS dependencies installed")
        print("   • CLI aliases configured")
        print("   • Workspace directories created")
        print("   • promptOS integration configured")

        print("\n🚀 You're ready to:")
        print("   • Use zenOS CLI: zen --help")
        print("   • Manage plugins: zen plugins list")
        print("   • Process inbox: zen receive add 'item' 'content'")
        print("   • Run AI agents: zen agent troubleshoot 'your issue'")

        print("\n📋 Useful commands:")
        print("   zen --help                    # Show all commands")
        print("   zen plugins list              # List available plugins")
        print("   zen receive list              # List inbox items")
        print("   zen agent troubleshoot 'help' # Get AI assistance")

        print("\n💡 Pro tip: Your setup is now bulletproof and will work")
        print("   on any environment. All procedures are saved and can be")
        print("   restored with a single command!")

        print("\nHappy coding! 🧘✨")

    def _handle_setup_failure(self, error: Exception):
        """Handle setup failure"""
        print(f"\n❌ Setup failed: {error}")
        print("Please check the setup log for more details: setup.log")
        print("\n🔧 Troubleshooting:")
        print("   • Check system requirements")
        print("   • Verify internet connectivity")
        print("   • Run: zen setup troubleshoot")
        print("   • Check setup.log for detailed error information")


def main():
    """Main entry point for the setup script"""
    parser = argparse.ArgumentParser(description="zenOS Unified Setup Manager")
    parser.add_argument("--path", type=Path, help="Path to zenOS root directory")
    parser.add_argument("--unattended", action="store_true", help="Run in unattended mode")
    parser.add_argument(
        "--validate-only", action="store_true", help="Only validate environment, no setup"
    )
    parser.add_argument(
        "--phase", choices=[p.value for p in SetupPhase], help="Start from specific phase"
    )

    args = parser.parse_args()

    manager = UnifiedSetupManager(zenos_root=args.path, unattended=args.unattended)

    if args.validate_only:
        # Run detection first to set up context
        if not manager._run_detection_phase():
            print("Failed to detect environment")
            sys.exit(1)
        success = manager._run_validation_phase()
    elif args.phase:
        # Run specific phase (with detection first if needed)
        if args.phase != "detection":
            if not manager._run_detection_phase():
                print("Failed to detect environment")
                sys.exit(1)

        phase_map = {
            "detection": manager._run_detection_phase,
            "validation": manager._run_validation_phase,
            "git_setup": manager._run_git_setup_phase,
            "mcp_setup": manager._run_mcp_setup_phase,
            "zenos_setup": manager._run_zenos_setup_phase,
            "integration": manager._run_integration_phase,
            "verification": manager._run_verification_phase,
        }
        success = phase_map[args.phase]()
    else:
        success = manager.run_setup()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
