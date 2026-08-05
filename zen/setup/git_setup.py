#!/usr/bin/env python3
"""
Git Setup Manager for zenOS

Handles all git-related setup procedures including repository initialization,
.gitignore creation, git aliases, and user configuration.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from zen.utils.safe_commands import SafeCommandExecutor


class GitSetupManager:
    """Manages git repository setup and configuration"""

    def __init__(self, zenos_root: Path):
        """Initialize a Git setup manager for the specified zenOS root directory.
        
        Parameters:
        	zenos_root (Path): The root directory of the zenOS installation.
        """
        self.zenos_root = zenos_root
        self.gitignore_path = self.zenos_root / ".gitignore"
        self.safe_executor = SafeCommandExecutor()

    def is_git_repo(self) -> bool:
        """Check if the current directory is a Git repository"""
        result = self.safe_executor.run_command(
            ["git", "rev-parse", "--git-dir"], cwd=self.zenos_root, timeout=5
        )
        return result["success"]

    def init_repository(self) -> bool:
        """
        Initialize a Git repository in the zenOS root directory.
        
        Returns:
            bool: True if initialization succeeds, False otherwise.
        """
        result = self.safe_executor.run_command(["git", "init"], cwd=self.zenos_root, timeout=10)
        if result["success"]:
            print(f"  ✅ Git repository initialized")
        else:
            print(f"  ❌ Failed to initialize git repository: {result['stderr']}")
        return result["success"]

    def setup_gitignore(self) -> bool:
        """
        Create a comprehensive `.gitignore` file based on the detected project types.
        
        Returns:
        	bool: `True` if the file is created successfully, `False` if an error occurs.
        """
        try:
            # Detect project types
            project_types = self._detect_project_types()

            # Generate .gitignore content
            content = self._generate_gitignore_content(project_types)

            # Write .gitignore
            with open(self.gitignore_path, "w") as f:
                f.write(content)

            print(f"  ✅ .gitignore created for: {', '.join(project_types)}")
            return True
        except Exception as e:
            print(f"  ❌ Failed to create .gitignore: {e}")
            return False

    def _detect_project_types(self) -> List[str]:
        """
        Identify project categories from files in the zenOS root directory and the current operating system.
        
        Returns:
            List[str]: Detected project categories, including platform, IDE, and logging categories.
        """
        project_types = []

        # Check for Python
        if any(self.zenos_root.glob("*.py")) or (self.zenos_root / "requirements.txt").exists():
            project_types.append("python")

        # Check for Node.js
        if (self.zenos_root / "package.json").exists() or (self.zenos_root / "yarn.lock").exists():
            project_types.append("node")

        # Check for build files
        if any(self.zenos_root.glob("Makefile")) or any(self.zenos_root.glob("CMakeLists.txt")):
            project_types.append("build")

        # Always add OS-specific patterns
        if sys.platform == "darwin":
            project_types.append("macos")
        elif sys.platform == "win32":
            project_types.append("windows")
        elif sys.platform.startswith("linux"):
            project_types.append("linux")

        # Always add IDE and logs patterns
        project_types.extend(["ide", "logs"])

        return project_types

    def _generate_gitignore_content(self, project_types: List[str]) -> str:
        """
        Generate `.gitignore` content for the detected project types.
        
        Parameters:
        	project_types (List[str]): Project type names whose ignore patterns should be included.
        
        Returns:
        	str: Combined project-specific and zenOS-specific ignore patterns.
        """
        templates = self._get_gitignore_templates()

        content = "# zenOS .gitignore\n"
        content += f"# Project types detected: {', '.join(project_types)}\n\n"

        for project_type in project_types:
            if project_type in templates:
                content += f"# {project_type.upper()}\n"
                content += templates[project_type] + "\n"

        # Add zenOS-specific patterns
        content += "\n# zenOS Specific\n"
        content += "setup.log\n"
        content += "*.log\n"
        content += "temp/\n"
        content += "workspace/temp/\n"
        content += "inbox/temp/\n"
        content += ".zenos_setup_complete\n"

        return content

    def _get_gitignore_templates(self) -> Dict[str, str]:
        """
        Provide ignore-pattern templates for supported project types and development environments.
        
        Returns:
            Dict[str, str]: A mapping from template names to their `.gitignore` contents.
        """
        return {
            "python": """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/
.venv/
.env/

# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

# pipenv
Pipfile.lock

# PEP 582
__pypackages__/

# Celery
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/
""",
            "node": """# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
lerna-debug.log*
.pnpm-debug.log*

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/
*.lcov

# nyc test coverage
.nyc_output

# Grunt intermediate storage
.grunt

# Bower dependency directory
bower_components

# node-waf configuration
.lock-wscript

# Compiled binary addons
build/Release

# Dependency directories
jspm_packages/

# TypeScript cache
*.tsbuildinfo

# Optional npm cache directory
.npm

# Optional eslint cache
.eslintcache

# Optional stylelint cache
.stylelintcache

# Microbundle cache
.rpt2_cache/
.rts2_cache_cjs/
.rts2_cache_es/
.rts2_cache_umd/

# Optional REPL history
.node_repl_history

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity

# dotenv environment variable files
.env
.env.development.local
.env.test.local
.env.production.local
.env.local

# parcel-bundler cache
.cache
.parcel-cache

# Next.js build output
.next
out

# Nuxt.js build / generate output
.nuxt
dist

# Gatsby files
.cache/
public

# Storybook build outputs
.out
.storybook-out
.storybook-static

# Temporary folders
tmp/
temp/
""",
            "macos": """# macOS system files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Icon must end with two \r
Icon

# Thumbnails
._*

# Files that might appear in the root of a volume
.DocumentRevisions-V100
.fseventsd
.Spotlight-V100
.TemporaryItems
.Trashes
.VolumeIcon.icns
.com.apple.timemachine.donotpresent

# Directories potentially created on remote AFP share
.AppleShare
Network Trash Folder
Temporary Items
.apdisk
""",
            "windows": """# Windows
Thumbs.db
Thumbs.db:encryptable
ehthumbs.db
ehthumbs_vista.db

# Dump file
*.stackdump

# Folder config file
[Dd]esktop.ini

# Recycle Bin used on file shares
$RECYCLE.BIN/

# Windows Installer files
*.cab
*.msi
*.msix
*.msm
*.msp

# Windows shortcuts
*.lnk
""",
            "linux": """# Linux
*~

# temporary files which can be created if a process still has a handle open of a deleted file
.fuse_hidden*

# KDE directory preferences
.directory

# Linux trash folder which might appear on any partition or disk
.Trash-*

# .nfs files are created when an open file is removed but is still being accessed
.nfs*
""",
            "ide": """# IDEs and editors
.vscode/
.idea/
*.swp
*.swo
*~
.project
.classpath
.settings/
*.sublime-project
*.sublime-workspace

# Vim
[._]*.s[a-v][a-z]
[._]*.sw[a-p]
[._]s[a-rt-v][a-z]
[._]ss[a-gi-z]
[._]sw[a-p]

# Emacs
*~
#*#
/.emacs.desktop
/.emacs.desktop.lock
*.elc
auto-save-list
tramp
.#*

# Sublime Text
*.sublime-project
*.sublime-workspace

# VSCode
.vscode/*
!.vscode/settings.json
!.vscode/tasks.json
!.vscode/launch.json
!.vscode/extensions.json
!.vscode/*.code-snippets

# Local History for Visual Studio Code
.history/

# Built Visual Studio Code Extensions
*.vsix
""",
            "logs": """# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
lerna-debug.log*
.pnpm-debug.log*

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/
*.lcov

# nyc test coverage
.nyc_output

# Grunt intermediate storage
.grunt

# Bower dependency directory
bower_components

# node-waf configuration
.lock-wscript

# Compiled binary addons
build/Release

# Dependency directories
jspm_packages/

# TypeScript cache
*.tsbuildinfo

# Optional npm cache directory
.npm

# Optional eslint cache
.eslintcache

# Optional stylelint cache
.stylelintcache

# Microbundle cache
.rts2_cache/
.rts2_cache_cjs/
.rts2_cache_es/
.rts2_cache_umd/

# Optional REPL history
.node_repl_history

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity

# dotenv environment variable files
.env
.env.development.local
.env.test.local
.env.production.local
.env.local

# parcel-bundler cache
.cache
.parcel-cache

# Next.js build output
.next
out

# Nuxt.js build / generate output
.nuxt
dist

# Gatsby files
.cache/
public

# Storybook build outputs
.out
.storybook-out
.storybook-static

# Temporary folders
tmp/
temp/
""",
            "build": """# Build outputs
dist/
build/
out/
target/
*.o
*.so
*.dll
*.dylib
*.exe
*.app
*.ipa
*.apk

# Package files
*.tar.gz
*.zip
*.rar
*.7z

# Compiled source
*.com
*.class
*.dll
*.exe
*.o
*.so

# Packages
*.7z
*.dmg
*.gz
*.iso
*.jar
*.rar
*.tar
*.zip

# Archives
*.7z
*.dmg
*.gz
*.iso
*.jar
*.rar
*.tar
*.zip

# Database
*.db
*.sqlite
*.sqlite3
""",
        }

    def setup_aliases(self) -> bool:
        """
        Configure global Git aliases for common repository workflows.
        
        Returns:
        	bool: `True` if all aliases are configured successfully, `False` if a Git command fails.
        """
        try:
            aliases = {
                "st": "status",
                "co": "checkout",
                "br": "branch",
                "ci": "commit",
                "unstage": "reset HEAD --",
                "last": "log -1 HEAD",
                "visual": "!gitk",
                "lg": "log --oneline --decorate --graph --all",
                "amend": "commit --amend --no-edit",
                "undo": "reset HEAD~1",
                "wip": 'commit -am "WIP"',
                "unwip": "reset HEAD~1",
                "wipe": '!git add -A && git commit -qm "WIPE SAVEPOINT" && git reset HEAD~1 --hard',
                "save": '!git add -A && git commit -m "SAVEPOINT"',
                "restore": "!git reset HEAD~1 --hard",
            }

            for alias, command in aliases.items():
                subprocess.run(["git", "config", "--global", f"alias.{alias}", command], check=True)

            print("  ✅ Git aliases configured")
            return True
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Failed to setup git aliases: {e}")
            return False

    def has_user_config(self) -> bool:
        """Determine whether Git has both a global user name and email configured.
        
        Returns:
        	bool: `True` if both values are nonempty, `False` otherwise.
        """
        try:
            name_result = subprocess.run(
                ["git", "config", "--global", "user.name"],
                capture_output=True,
                text=True,
                check=True,
            )
            email_result = subprocess.run(
                ["git", "config", "--global", "user.email"],
                capture_output=True,
                text=True,
                check=True,
            )
            return bool(name_result.stdout.strip() and email_result.stdout.strip())
        except subprocess.CalledProcessError:
            return False

    def configure_user(self, name: str, email: str) -> bool:
        """
        Configure the global Git user identity.
        
        Parameters:
            name (str): Name to associate with Git commits.
            email (str): Email address to associate with Git commits.
        
        Returns:
            bool: `True` if both identity values are configured successfully, `False` otherwise.
        """
        try:
            subprocess.run(["git", "config", "--global", "user.name", name], check=True)
            subprocess.run(["git", "config", "--global", "user.email", email], check=True)
            print(f"  ✅ Git user configured: {name} <{email}>")
            return True
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Failed to configure git user: {e}")
            return False

    def remove_tracked_unwanted_files(self) -> List[str]:
        """
        Remove tracked files matching common generated, temporary, environment, and IDE-specific patterns.
        
        Returns:
            List[str]: Paths removed from Git tracking.
        """
        removed_files = []

        # Common patterns to remove
        patterns = [
            ".DS_Store",
            "**/.DS_Store",
            "**/__pycache__",
            "**/*.pyc",
            "**/*.pyo",
            "**/*.pyd",
            "**/.Python",
            "**/build",
            "**/dist",
            "**/*.egg-info",
            "**/.pytest_cache",
            "**/.coverage",
            "**/.mypy_cache",
            "**/.tox",
            "**/.venv",
            "**/venv",
            "**/env",
            "**/.env",
            "**/.vscode",
            "**/.idea",
            "**/*.log",
            "**/logs",
            "**/tmp",
            "**/temp",
            "**/.cache",
        ]

        for pattern in patterns:
            try:
                result = subprocess.run(
                    ["git", "rm", "--cached", "-r", "--ignore-unmatch", pattern],
                    cwd=self.zenos_root,
                    capture_output=True,
                    text=True,
                    check=False,
                )

                if result.returncode == 0 and result.stdout.strip():
                    removed_files.extend(result.stdout.strip().split("\n"))
            except Exception as e:
                print(f"  ⚠️  Warning: Could not process pattern '{pattern}': {e}")

        return removed_files

    def commit_changes(
        self, message: str = "chore: add .gitignore and cleanup tracked files"
    ) -> bool:
        """
        Stage the repository's .gitignore file and commit the changes.
        
        Parameters:
            message (str): Commit message to use.
        
        Returns:
            bool: True if staging and committing succeed, False if either Git command fails.
        """
        try:
            # Add .gitignore
            subprocess.run(["git", "add", ".gitignore"], cwd=self.zenos_root, check=True)

            # Commit changes
            subprocess.run(["git", "commit", "-m", message], cwd=self.zenos_root, check=True)

            print("  ✅ Changes committed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Failed to commit changes: {e}")
            return False

    def verify_setup(self) -> bool:
        """
        Verify that the Git repository setup is functioning correctly.
        
        Returns:
        	bool: `True` if Git status succeeds and any existing `.DS_Store` file is ignored, `False` otherwise.
        """
        try:
            # Check git status
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.zenos_root,
                capture_output=True,
                text=True,
                check=True,
            )

            # Check if .DS_Store files are being ignored
            test_file = self.zenos_root / ".DS_Store"
            if test_file.exists():
                result = subprocess.run(
                    ["git", "check-ignore", ".DS_Store"],
                    cwd=self.zenos_root,
                    capture_output=True,
                    text=True,
                    check=False,
                )

                if result.returncode == 0:
                    print("  ✅ .gitignore is working correctly")
                    return True
                else:
                    print("  ⚠️  Warning: .DS_Store files might not be ignored")
                    return False

            print("  ✅ Git setup verified")
            return True

        except Exception as e:
            print(f"  ❌ Failed to verify git setup: {e}")
            return False
