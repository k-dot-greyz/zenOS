"""
zenOS Plugin System - Git-based VST Architecture
Every GitHub repo is a potential AI tool, every commit is a new feature!
"""

from .discovery import PluginDiscovery
from .executor import PluginExecutor
from .loader import GitPluginLoader
from .registry import PluginRegistry
from .sandbox import PluginSandbox

__all__ = [
    "PluginRegistry",
    "GitPluginLoader",
    "PluginSandbox",
    "PluginDiscovery",
    "PluginExecutor",
]
