#!/usr/bin/env python3
"""
Setup Troubleshooter for zenOS

AI-powered troubleshooting system that diagnoses and fixes setup issues
using the procedures from promptOS intelligent setup wizard.
"""

import json
import os
import platform
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class ValidationResult:
    """Result of a validation check"""

    passed: bool
    message: str
    fix_command: Optional[str] = None
    ai_diagnosis: Optional[str] = None


@dataclass
class Issue:
    """An identified issue"""

    type: str
    description: str
    severity: str
    fix_commands: List[str]
    explanation: str


@dataclass
class Fix:
    """A suggested fix"""

    type: str
    description: str
    commands: List[str]
    explanation: str


class SetupTroubleshooter:
    """AI-powered setup troubleshooter"""

    def __init__(self):
        self.issues = []
        self.fixes = []

    def validate_system(self, env_info) -> Dict:
        """Validate the system and return issues"""
        validations = [
            self._validate_python_environment(),
            self._validate_git_installation(),
            self._validate_shell_configuration(),
            self._validate_directory_structure(env_info.zenos_root),
            self._validate_permissions(env_info.zenos_root),
            self._validate_internet_connectivity(),
        ]

        issues = [v for v in validations if not v.passed]

        return {
            "issues": issues,
            "total_issues": len(issues),
            "validations_passed": len(validations) - len(issues),
            "validations_total": len(validations),
        }

    def _validate_python_environment(self) -> ValidationResult:
        """Validate Python environment"""
        try:
            version = sys.version_info
            if version.major < 3 or (version.major == 3 and version.minor < 7):
                return ValidationResult(
                    passed=False,
                    message=f"Python {version.major}.{version.minor} detected. Python 3.7+ required",
                    fix_command="Install Python 3.7 or higher",
                    ai_diagnosis="Python version too old for zenOS requirements",
                )
            return ValidationResult(
                passed=True, message=f"Python {version.major}.{version.minor} OK"
            )
        except Exception as e:
            return ValidationResult(passed=False, message=f"Python validation failed: {e}")

    def _validate_git_installation(self) -> ValidationResult:
        """Validate git installation"""
        try:
            result = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return ValidationResult(passed=True, message="Git installation OK")
            else:
                return ValidationResult(
                    passed=False,
                    message="Git not installed or not in PATH",
                    fix_command="Install Git",
                    ai_diagnosis="Git required for version control and repository management",
                )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return ValidationResult(
                passed=False,
                message="Git not found in PATH",
                fix_command="Install Git and ensure it's in PATH",
                ai_diagnosis="Git executable not found in system PATH",
            )

    def _validate_shell_configuration(self) -> ValidationResult:
        """Validate shell configuration"""
        if sys.platform == "win32":
            shell = os.environ.get("COMSPEC", "cmd.exe")
            if "powershell" in shell.lower() or "pwsh" in shell.lower() or "cmd" in shell.lower():
                return ValidationResult(
                    passed=True, message=f"Windows shell OK: {os.path.basename(shell)}"
                )
            else:
                return ValidationResult(passed=True, message="Windows shell detected")
        else:
            shell = os.environ.get("SHELL", "unknown")
            if "bash" in shell or "zsh" in shell or "fish" in shell:
                return ValidationResult(passed=True, message=f"Shell {shell} OK")
            else:
                return ValidationResult(
                    passed=False,
                    message=f"Unsupported shell: {shell}",
                    fix_command="Switch to bash, zsh, or fish shell",
                    ai_diagnosis="Unsupported shell may cause compatibility issues",
                )

    def _validate_directory_structure(self, zenos_root: Path) -> ValidationResult:
        """Validate zenOS directory structure"""
        required_dirs = ["zen", "docs", "inbox"]
        missing_dirs = []

        for dir_name in required_dirs:
            if not (zenos_root / dir_name).exists():
                missing_dirs.append(dir_name)

        if missing_dirs:
            return ValidationResult(
                passed=False,
                message=f"Missing directories: {', '.join(missing_dirs)}",
                fix_command="Ensure you're in the correct zenOS directory",
                ai_diagnosis="Required zenOS directory structure is incomplete",
            )
        return ValidationResult(passed=True, message="Directory structure OK")

    def _validate_permissions(self, zenos_root: Path) -> ValidationResult:
        """Validate file permissions"""
        test_file = zenos_root / ".permission_test"
        try:
            test_file.write_text("test")
            test_file.unlink()
            return ValidationResult(passed=True, message="File permissions OK")
        except PermissionError:
            return ValidationResult(
                passed=False,
                message="Insufficient permissions to write to zenOS directory",
                fix_command="Check file permissions or run with appropriate privileges",
                ai_diagnosis="Permission denied - zenOS needs write access to its directory",
            )

    def _validate_internet_connectivity(self) -> ValidationResult:
        """Validate internet connectivity"""
        try:
            import urllib.request

            urllib.request.urlopen("https://github.com", timeout=5)
            return ValidationResult(passed=True, message="Internet connectivity OK")
        except:
            return ValidationResult(
                passed=False,
                message="Internet connectivity issues detected",
                fix_command="Check network connection",
                ai_diagnosis="Internet required for package installation and updates",
            )

    def diagnose_issues(self, issues: List[ValidationResult]) -> Dict:
        """AI-powered diagnosis of issues"""
        diagnosis = {"analysis": "", "fixes": [], "priority": "high" if issues else "low"}

        if not issues:
            diagnosis["analysis"] = "No issues found - system is ready for zenOS setup"
            return diagnosis

        # Analyze issues
        issue_types = [issue.message for issue in issues]
        diagnosis["analysis"] = f"Found {len(issues)} issues: {', '.join(issue_types)}"

        # Generate fixes
        for issue in issues:
            fix = self._generate_fix_for_issue(issue)
            if fix:
                diagnosis["fixes"].append(fix)

        return diagnosis

    def _generate_fix_for_issue(self, issue: ValidationResult) -> Optional[Fix]:
        """Generate a fix for a specific issue"""
        if "Python" in issue.message and "required" in issue.message:
            return Fix(
                type="python_upgrade",
                description="Upgrade Python to 3.7+",
                commands=[
                    "# On macOS with Homebrew:",
                    "brew install python@3.9",
                    "# On Ubuntu/Debian:",
                    "sudo apt update && sudo apt install python3.9",
                    "# On Windows:",
                    "Download from https://python.org/downloads/",
                ],
                explanation="zenOS requires Python 3.7 or higher for modern features",
            )

        elif "Git" in issue.message:
            return Fix(
                type="git_installation",
                description="Install Git",
                commands=[
                    "# On macOS:",
                    "brew install git",
                    "# On Ubuntu/Debian:",
                    "sudo apt update && sudo apt install git",
                    "# On Windows:",
                    "Download from https://git-scm.com/download/win",
                ],
                explanation="Git is required for version control and repository management",
            )

        elif "permissions" in issue.message.lower():
            return Fix(
                type="permission_fix",
                description="Fix file permissions",
                commands=[
                    "# Check current permissions:",
                    "ls -la .",
                    "# Fix ownership:",
                    "sudo chown -R $USER:$USER .",
                    "# Fix permissions:",
                    "chmod -R 755 .",
                ],
                explanation="zenOS needs write access to its directory for configuration and logs",
            )

        elif "internet" in issue.message.lower():
            return Fix(
                type="network_fix",
                description="Check network connectivity",
                commands=[
                    "# Test connectivity:",
                    "ping google.com",
                    "# Check DNS:",
                    "nslookup github.com",
                    "# Check proxy settings:",
                    "echo $HTTP_PROXY $HTTPS_PROXY",
                ],
                explanation="Internet connectivity is required for package installation",
            )

        return None

    def apply_fixes(self, fixes: List[Fix]) -> bool:
        """Apply suggested fixes"""
        success_count = 0

        for fix in fixes:
            print(f"  🔧 Applying fix: {fix.description}")

            try:
                if fix.type == "python_upgrade":
                    # Can't automatically upgrade Python, just provide guidance
                    print(f"    ⚠️  Manual action required: {fix.explanation}")
                    print("    📝 Commands to run:")
                    for cmd in fix.commands:
                        print(f"      {cmd}")
                    success_count += 1

                elif fix.type == "git_installation":
                    # Try to install git if possible
                    if sys.platform == "darwin":
                        try:
                            subprocess.run(["brew", "install", "git"], check=True)
                            print("    ✅ Git installed via Homebrew")
                            success_count += 1
                        except:
                            print("    ⚠️  Homebrew not available, manual installation required")
                    else:
                        print("    ⚠️  Manual installation required")
                        print("    📝 Commands to run:")
                        for cmd in fix.commands:
                            print(f"      {cmd}")

                elif fix.type == "permission_fix":
                    # Try to fix permissions
                    try:
                        if sys.platform != "win32":
                            subprocess.run(["chmod", "-R", "755", "."], check=True)
                            print("    ✅ Permissions fixed")
                            success_count += 1
                        else:
                            print("    ⚠️  Windows permission fix not implemented")
                    except:
                        print("    ❌ Permission fix failed")

                elif fix.type == "network_fix":
                    # Test network connectivity
                    try:
                        import urllib.request

                        urllib.request.urlopen("https://github.com", timeout=5)
                        print("    ✅ Network connectivity restored")
                        success_count += 1
                    except:
                        print("    ❌ Network connectivity still failing")

            except Exception as e:
                print(f"    ❌ Fix failed: {e}")

        return success_count > 0

    def create_helper_tools(self) -> List[Dict]:
        """Create helper tools to prevent future issues"""
        tools = []

        # Create setup validation script
        validation_script = self._create_validation_script()
        if validation_script:
            tools.append(
                {
                    "type": "validation_script",
                    "description": "Setup validation script created",
                    "path": str(validation_script),
                    "usage": f"python {validation_script}",
                }
            )

        # Create troubleshooting guide
        guide = self._create_troubleshooting_guide()
        if guide:
            tools.append(
                {
                    "type": "troubleshooting_guide",
                    "description": "Troubleshooting guide created",
                    "path": str(guide),
                    "usage": "Read for common issues and solutions",
                }
            )

        return tools

    def _create_validation_script(self) -> Optional[Path]:
        """Create a validation script for future use"""
        try:
            script_path = Path("validate_setup.py")

            script_content = '''#!/usr/bin/env python3
"""
zenOS Setup Validation Script
Run this script to validate your zenOS setup
"""

import sys
from pathlib import Path

# Add zenOS to path
sys.path.insert(0, str(Path(__file__).parent))

from zen.setup.troubleshooter import SetupTroubleshooter
from zen.setup.environment_detector import EnvironmentDetector

def main():
    print("🔍 Validating zenOS setup...")
    
    detector = EnvironmentDetector()
    troubleshooter = SetupTroubleshooter()
    
    env_info = detector.detect_environment(Path.cwd())
    validation_results = troubleshooter.validate_system(env_info)
    
    if validation_results['issues']:
        print(f"❌ Found {validation_results['total_issues']} issues")
        for issue in validation_results['issues']:
            print(f"  - {issue.message}")
    else:
        print("✅ All validations passed!")
    
    return validation_results['total_issues'] == 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
'''

            with open(script_path, "w") as f:
                f.write(script_content)

            script_path.chmod(0o755)
            return script_path
        except Exception as e:
            print(f"  ❌ Failed to create validation script: {e}")
            return None

    def _create_troubleshooting_guide(self) -> Optional[Path]:
        """Create a troubleshooting guide"""
        try:
            guide_path = Path("TROUBLESHOOTING.md")

            guide_content = """# zenOS Troubleshooting Guide

## Common Issues and Solutions

### Python Version Issues
**Problem**: Python version too old
**Solution**: Install Python 3.7 or higher
- macOS: `brew install python@3.9`
- Ubuntu/Debian: `sudo apt install python3.9`
- Windows: Download from https://python.org/downloads/

### Git Not Found
**Problem**: Git not installed or not in PATH
**Solution**: Install Git
- macOS: `brew install git`
- Ubuntu/Debian: `sudo apt install git`
- Windows: Download from https://git-scm.com/download/win

### Permission Issues
**Problem**: Insufficient permissions to write to zenOS directory
**Solution**: Fix file permissions
```bash
# Check current permissions
ls -la .

# Fix ownership
sudo chown -R $USER:$USER .

# Fix permissions
chmod -R 755 .
```

### Network Connectivity
**Problem**: Internet connectivity issues
**Solution**: Check network connection
```bash
# Test connectivity
ping google.com

# Check DNS
nslookup github.com

# Check proxy settings
echo $HTTP_PROXY $HTTPS_PROXY
```

### Shell Compatibility
**Problem**: Unsupported shell
**Solution**: Switch to supported shell
- Recommended: bash, zsh, or fish
- Windows: PowerShell or Git Bash

## Getting Help

1. Run the validation script: `python validate_setup.py`
2. Check the setup log: `setup.log`
3. Run zenOS setup again: `python zen/setup/unified_setup.py`
4. Check this guide for specific error messages

## Manual Setup

If automated setup fails, you can manually set up zenOS:

1. Install Python 3.7+
2. Install Git
3. Clone the repository
4. Install dependencies: `pip install -r requirements.txt`
5. Run zenOS: `python zen/cli.py --help`
"""

            with open(guide_path, "w") as f:
                f.write(guide_content)

            return guide_path
        except Exception as e:
            print(f"  ❌ Failed to create troubleshooting guide: {e}")
            return None
