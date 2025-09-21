"""
Built-in agents for zenOS.
"""

from .troubleshooter import TroubleshooterAgent
from .critic import CriticAgent
from .assistant import AssistantAgent

# Registry of built-in agents
builtin_agents = {
    "troubleshooter": TroubleshooterAgent(),
    "critic": CriticAgent(),
    "assistant": AssistantAgent(),
}
