"""zenOS - The Zen of AI Workflow Orchestration

A powerful, modular AI agent orchestration framework that brings
zen-like simplicity to complex AI workflows.
"""

__version__ = "0.1.0"
__author__ = "Kaspars Greizis"

from zen.core.agent import Agent
from zen.core.critique import AutoCritique
from zen.core.launcher import Launcher

__all__ = ["Agent", "Launcher", "AutoCritique"]
