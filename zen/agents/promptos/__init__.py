"""
PromptOS Integration for zenOS

This module integrates the core PromptOS functionality into zenOS,
including the auto-critique system, specialized agents, and YAML-based templates.
"""

from .prompt_critic import PromptCriticAgent
from .system_troubleshooter import SystemTroubleshooterAgent
from .prompt_security_agent import PromptSecurityAgent

__all__ = [
    'PromptCriticAgent',
    'SystemTroubleshooterAgent', 
    'PromptSecurityAgent'
]
