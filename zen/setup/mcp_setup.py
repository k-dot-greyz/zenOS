#!/usr/bin/env python3
"""MCP Setup Manager for zenOS

Handles MCP (Model Context Protocol) server installation, configuration,
and linking based on the procedures from mcp-config.
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Optional


class MCPSetupManager:
    """Manages MCP server setup and configuration"""

    def __init__(self, zenos_root: Path):
        self.zenos_root = zenos_root
        self.mcp_config_dir = self.zenos_root / "mcp-config"
        self.central_config = self.mcp_config_dir / "configs" / "mcp.json"

        # Required MCP servers
        self.required_servers = [
            "@cyanheads/git-mcp-server",
            "@modelcontextprotocol/server-filesystem",
            "@jpisnice/shadcn-ui-mcp-server",
            "@steipete/peekaboo-mcp",
        ]

    def install_servers(self) -> bool:
        """Install required MCP servers"""
        try:
            print("  📦 Installing MCP servers...")

            for server in self.required_servers:
                print(f"    Installing {server}...")

                # Check if already installed
                if self._is_server_installed(server):
                    print(f"    ✅ {server} already installed")
                    continue

                # Install server
                result = subprocess.run(
                    ["npm", "install", "-g", server], capture_output=True, text=True, check=False
                )

                if result.returncode == 0:
                    print(f"    ✅ {server} installed successfully")
                else:
                    print(f"    ❌ Failed to install {server}: {result.stderr}")
                    return False

            print("  ✅ All MCP servers installed")
            return True
        except Exception as e:
            print(f"  ❌ MCP server installation failed: {e}")
            return False

    def _is_server_installed(self, server: str) -> bool:
        """Check if a server is already installed"""
        try:
            result = subprocess.run(
                ["npm", "list", "-g", server], capture_output=True, text=True, check=False
            )
            return result.returncode == 0
        except:
            return False

    def link_configurations(self) -> bool:
        """Link MCP configurations to various tools"""
        try:
            print("  🔗 Linking MCP configurations...")

            # Check if central config exists
            if not self.central_config.exists():
                print("  ⚠️  Central MCP config not found, creating basic one...")
                if not self._create_basic_config():
                    return False

            # Link to Cursor
            if not self._link_cursor_config():
                print("  ⚠️  Cursor config linking failed, continuing...")

            # Link to Warp
            if not self._link_warp_config():
                print("  ⚠️  Warp config linking failed, continuing...")

            # Link to Claude Desktop
            if not self._link_claude_config():
                print("  ⚠️  Claude Desktop config linking failed, continuing...")

            print("  ✅ MCP configurations linked")
            return True
        except Exception as e:
            print(f"  ❌ MCP configuration linking failed: {e}")
            return False

    def _create_basic_config(self) -> bool:
        """Create basic MCP configuration"""
        try:
            # Create config directory
            config_dir = self.central_config.parent
            config_dir.mkdir(parents=True, exist_ok=True)

            # Create basic config
            config = {
                "mcpServers": {
                    "git": {"command": "git-mcp-server", "args": []},
                    "filesystem": {
                        "command": "mcp-server-filesystem",
                        "args": [str(self.zenos_root)],
                    },
                    "shadcn": {"command": "shadcn-ui-mcp-server", "args": []},
                    "peekaboo": {"command": "peekaboo-mcp", "args": []},
                }
            }

            with open(self.central_config, "w") as f:
                json.dump(config, f, indent=2)

            print("  ✅ Basic MCP config created")
            return True
        except Exception as e:
            print(f"  ❌ Failed to create basic config: {e}")
            return False

    def _link_cursor_config(self) -> bool:
        """Link MCP config to Cursor"""
        try:
            cursor_config = Path.home() / ".cursor" / "mcp.json"
            cursor_config.parent.mkdir(parents=True, exist_ok=True)

            # Backup existing config if it exists and isn't a symlink
            if cursor_config.exists() and not cursor_config.is_symlink():
                backup_path = cursor_config.with_suffix(f".backup.{int(time.time())}")
                cursor_config.rename(backup_path)
                print(f"  📋 Backed up existing Cursor config to {backup_path}")

            # Create symlink
            if cursor_config.is_symlink():
                cursor_config.unlink()

            cursor_config.symlink_to(self.central_config)
            print("  ✅ Cursor config linked")
            return True
        except Exception as e:
            print(f"  ❌ Cursor config linking failed: {e}")
            return False

    def _link_warp_config(self) -> bool:
        """Link MCP config to Warp"""
        try:
            # Add environment variable to shell profile
            shell_profile = self._get_shell_profile()
            if not shell_profile:
                print("  ⚠️  Could not determine shell profile for Warp")
                return False

            env_line = f'export MCP_CONFIG="{self.central_config}"'

            # Check if already exists
            if shell_profile.exists():
                with open(shell_profile, "r") as f:
                    content = f.read()
                if "MCP_CONFIG" in content:
                    print("  ✅ Warp config already linked")
                    return True

            # Add to profile
            with open(shell_profile, "a") as f:
                f.write(f"\n# MCP Configuration\n{env_line}\n")

            print("  ✅ Warp config linked")
            print(f"  📝 Restart shell or run: source {shell_profile}")
            return True
        except Exception as e:
            print(f"  ❌ Warp config linking failed: {e}")
            return False

    def _link_claude_config(self) -> bool:
        """Link MCP config to Claude Desktop"""
        try:
            claude_config = (
                Path.home()
                / "Library"
                / "Application Support"
                / "Claude"
                / "claude_desktop_config.json"
            )

            if not claude_config.exists():
                print("  ⚠️  Claude Desktop config not found, skipping...")
                return True

            print("  ℹ️  Claude Desktop requires manual configuration")
            print(f"  📝 Consider copying servers from {self.central_config} to {claude_config}")
            return True
        except Exception as e:
            print(f"  ❌ Claude config linking failed: {e}")
            return False

    def _get_shell_profile(self) -> Optional[Path]:
        """Get the appropriate shell profile file"""
        shell = os.environ.get("SHELL", "")

        if "zsh" in shell:
            return Path.home() / ".zshrc"
        elif "bash" in shell:
            return Path.home() / ".bashrc"
        else:
            return Path.home() / ".profile"

    def run_health_checks(self) -> bool:
        """Run MCP health checks"""
        try:
            print("  🏥 Running MCP health checks...")

            all_healthy = True

            # Check if servers are available
            for server in self.required_servers:
                server_name = server.split("/")[-1]
                if self._is_server_installed(server):
                    print(f"    ✅ {server_name} is available")
                else:
                    print(f"    ❌ {server_name} is not available")
                    all_healthy = False

            # Check if config file exists
            if self.central_config.exists():
                print("    ✅ Central config exists")
            else:
                print("    ❌ Central config missing")
                all_healthy = False

            # Check if config is valid JSON
            try:
                with open(self.central_config, "r") as f:
                    json.load(f)
                print("    ✅ Config is valid JSON")
            except json.JSONDecodeError:
                print("    ❌ Config is not valid JSON")
                all_healthy = False

            if all_healthy:
                print("  ✅ All MCP health checks passed")
            else:
                print("  ⚠️  Some MCP health checks failed")

            return all_healthy
        except Exception as e:
            print(f"  ❌ MCP health checks failed: {e}")
            return False

    def update_documentation(self) -> bool:
        """Update MCP documentation"""
        try:
            docs_dir = self.mcp_config_dir / "docs"
            docs_dir.mkdir(parents=True, exist_ok=True)

            versions_file = docs_dir / "versions.md"

            with open(versions_file, "w") as f:
                f.write("# MCP Server Versions\n\n")
                f.write(f"*Last updated: {self._get_current_time()}*\n\n")
                f.write("## Installed MCP Servers\n\n")

                for server in self.required_servers:
                    version = self._get_server_version(server)
                    f.write(f"- **{server.split('/')[-1]}**: {server}@{version}\n")

                f.write("\n## Binary Paths\n\n")
                f.write(f"- `git-mcp-server`: {self._get_binary_path('git-mcp-server')}\n")
                f.write(
                    f"- `mcp-server-filesystem`: {self._get_binary_path('mcp-server-filesystem')}\n"
                )

            print("  ✅ MCP documentation updated")
            return True
        except Exception as e:
            print(f"  ❌ MCP documentation update failed: {e}")
            return False

    def _get_current_time(self) -> str:
        """Get current time string"""
        import time

        return time.strftime("%Y-%m-%d %H:%M:%S")

    def _get_server_version(self, server: str) -> str:
        """Get version of installed server"""
        try:
            result = subprocess.run(
                ["npm", "list", "-g", server], capture_output=True, text=True, check=False
            )

            if result.returncode == 0:
                # Extract version from output
                lines = result.stdout.split("\n")
                for line in lines:
                    if server in line:
                        parts = line.split("@")
                        if len(parts) > 1:
                            return parts[-1].strip()

            return "not installed"
        except:
            return "unknown"

    def _get_binary_path(self, binary_name: str) -> str:
        """Get path to binary"""
        try:
            result = subprocess.run(
                ["which", binary_name], capture_output=True, text=True, check=False
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return "not found"
        except:
            return "not found"

    def create_helper_scripts(self) -> bool:
        """Create helper scripts for MCP management"""
        try:
            scripts_dir = self.mcp_config_dir / "scripts"
            scripts_dir.mkdir(parents=True, exist_ok=True)

            # Create bootstrap script
            bootstrap_script = scripts_dir / "bootstrap-mcp.sh"
            with open(bootstrap_script, "w") as f:
                f.write(self._get_bootstrap_script_content())
            bootstrap_script.chmod(0o755)

            # Create link script
            link_script = scripts_dir / "link-config.sh"
            with open(link_script, "w") as f:
                f.write(self._get_link_script_content())
            link_script.chmod(0o755)

            # Create audit script
            audit_script = scripts_dir / "mcp-audit.sh"
            with open(audit_script, "w") as f:
                f.write(self._get_audit_script_content())
            audit_script.chmod(0o755)

            print("  ✅ MCP helper scripts created")
            return True
        except Exception as e:
            print(f"  ❌ MCP helper scripts creation failed: {e}")
            return False

    def _get_bootstrap_script_content(self) -> str:
        """Get bootstrap script content"""
        return """#!/bin/bash
# MCP Bootstrap Script for zenOS
# Automated setup of MCP servers and configuration

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MCP_CONFIG_DIR="$(dirname "$SCRIPT_DIR")"

echo "🚀 MCP Bootstrap Script for zenOS"
echo "=================================="

# Check prerequisites
if ! command -v node >/dev/null 2>&1; then
    echo "❌ Node.js not found. Please install Node.js first."
    exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
    echo "❌ npm not found. Please install npm first."
    exit 1
fi

# Install MCP servers
echo "📦 Installing MCP servers..."
npm install -g @cyanheads/git-mcp-server
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @jpisnice/shadcn-ui-mcp-server
npm install -g @steipete/peekaboo-mcp

echo "✅ MCP servers installed successfully"
echo "🎉 MCP bootstrap complete!"
"""

    def _get_link_script_content(self) -> str:
        """Get link script content"""
        return """#!/bin/bash
# MCP Configuration Linker for zenOS
# Creates symlinks to the central MCP configuration

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MCP_CONFIG_DIR="$(dirname "$SCRIPT_DIR")"
CENTRAL_CONFIG="$MCP_CONFIG_DIR/configs/mcp.json"

echo "🔗 Linking MCP configurations..."

# Link to Cursor
CURSOR_CONFIG="$HOME/.cursor/mcp.json"
mkdir -p "$(dirname "$CURSOR_CONFIG")"
if [ -f "$CURSOR_CONFIG" ] && [ ! -L "$CURSOR_CONFIG" ]; then
    mv "$CURSOR_CONFIG" "$CURSOR_CONFIG.backup.$(date +%Y%m%d-%H%M%S)"
fi
ln -sf "$CENTRAL_CONFIG" "$CURSOR_CONFIG"
echo "✅ Cursor config linked"

# Link to Warp
SHELL_PROFILE="$HOME/.zshrc"
if [ -n "${BASH_VERSION:-}" ]; then
    SHELL_PROFILE="$HOME/.bashrc"
fi

if ! grep -q "MCP_CONFIG" "$SHELL_PROFILE" 2>/dev/null; then
    echo "" >> "$SHELL_PROFILE"
    echo "# MCP Configuration" >> "$SHELL_PROFILE"
    echo "export MCP_CONFIG=\"$CENTRAL_CONFIG\"" >> "$SHELL_PROFILE"
    echo "✅ Warp config linked"
else
    echo "✅ Warp config already linked"
fi

echo "🎉 MCP configuration linking complete!"
"""

    def _get_audit_script_content(self) -> str:
        """Get audit script content"""
        return r"""#!/bin/bash
# MCP Configuration Audit Script for zenOS
# Captures current system state for MCP servers and configuration

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCS_DIR="$(dirname "$SCRIPT_DIR")/docs"
AUDIT_FILE="$DOCS_DIR/audit-$(date +%Y%m%d-%H%M%S).md"

mkdir -p "$DOCS_DIR"

echo "🔍 Running MCP Configuration Audit..."

cat > "$AUDIT_FILE" << EOF
# MCP Configuration Audit - $(date)

## System Information

### Node.js Environment
\`\`\`bash
Node Version: $(node -v 2>/dev/null || echo 'Not found')
NPM Version: $(npm -v 2>/dev/null || echo 'Not found')
Current Node: $(which node 2>/dev/null || echo 'Not found')
\`\`\`

### Global NPM Packages
\`\`\`bash
$(npm list -g --depth=0 2>/dev/null | grep -E "(mcp|shadcn|git)" || echo "No MCP-related packages found")
\`\`\`

### MCP Configuration Files
\`\`\`bash
$(find ~ -name "mcp.json" -maxdepth 4 2>/dev/null | while read -r file; do
    echo "Found: $file"
    echo "  Size: $(stat -f%z "$file" 2>/dev/null || echo 'Unknown') bytes"
    echo "  Modified: $(stat -f%Sm "$file" 2>/dev/null || echo 'Unknown')"
done)
\`\`\`

### MCP Server Binaries
\`\`\`bash
$(for cmd in git-mcp-server mcp-server-filesystem shadcn-ui-mcp-server; do
    if which "$cmd" >/dev/null 2>&1; then
        echo "✅ $cmd: $(which "$cmd")"
    else
        echo "❌ $cmd: Not found in PATH"
    fi
done)
\`\`\`

---
*Audit completed at $(date)*
EOF

echo "✅ Audit completed. Report saved to: $AUDIT_FILE"
"""
