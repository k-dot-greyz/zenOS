"""Built-in agents for zenOS."""

from ..pkm.agent import PKMAgent
from .assistant import AssistantAgent
from .critic import CriticAgent
from .troubleshooter import TroubleshooterAgent

# Registry of built-in agents
builtin_agents = {
    "troubleshooter": TroubleshooterAgent(),
    "critic": CriticAgent(),
    "assistant": AssistantAgent(),
    "pkm": PKMAgent(),
}
