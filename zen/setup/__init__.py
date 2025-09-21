"""
zenOS Unified Setup System

A bulletproof, environment-agnostic setup system that combines the best
procedures from promptOS and mcp-config to ensure your dev environment
never gets lost again.

Features:
- Cross-platform compatibility (Windows, macOS, Linux, Termux)
- AI-powered troubleshooting and validation
- Git repository setup and maintenance
- MCP server configuration and linking
- Environment detection and adaptation
- Progressive failure recovery
- One-command setup for any environment
"""

from .unified_setup import UnifiedSetupManager
from .environment_detector import EnvironmentDetector
from .git_setup import GitSetupManager
from .mcp_setup import MCPSetupManager
from .troubleshooter import SetupTroubleshooter

__all__ = [
    'UnifiedSetupManager',
    'EnvironmentDetector', 
    'GitSetupManager',
    'MCPSetupManager',
    'SetupTroubleshooter'
]
