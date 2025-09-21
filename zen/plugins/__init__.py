"""
zenOS Plugin System - Git-based VST Architecture
Every GitHub repo is a potential AI tool, every commit is a new feature!
"""

from .registry import PluginRegistry
from .loader import GitPluginLoader
from .sandbox import PluginSandbox
from .discovery import PluginDiscovery
from .executor import PluginExecutor

__all__ = [
    'PluginRegistry',
    'GitPluginLoader', 
    'PluginSandbox',
    'PluginDiscovery',
    'PluginExecutor'
]
