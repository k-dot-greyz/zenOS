"""
Launcher for zenOS - orchestrates agent execution with AI providers.
"""

import asyncio
from typing import Any, Dict, Optional

from rich.console import Console

from zen.agents.promptos.prompt_critic import PromptCriticAgent
from zen.core.agent import AgentRegistry
from zen.providers.openrouter import ModelTier, OpenRouterProvider
from zen.utils.config import Config

console = Console()


class Launcher:
    """
    Main launcher for executing agents with AI capabilities.
    """

    def __init__(self, debug: bool = False):
        """Initialize the launcher."""
        self.debug = debug
        self.config = Config()
        self.registry = AgentRegistry()
        self.current_agent = None
        self.provider = None
        self.prompt_critic = None

        # Initialize provider if configured
        if self.config.config.openrouter_api_key:
            self.provider = OpenRouterProvider(self.config.config.openrouter_api_key)
            # Initialize PromptOS critique system
            self.prompt_critic = PromptCriticAgent()

    def load_agent(self, name: str):
        """Load an agent by name."""
        self.current_agent = self.registry.get_agent(name)
        if self.debug:
            console.print(f"[dim]Loaded agent: {name}[/dim]")

    async def critique_prompt_async(self, prompt: str) -> str:
        """
        Improve a prompt when automatic critique is enabled.
        
        Parameters:
            prompt (str): The original prompt to evaluate.
        
        Returns:
            str: The improved prompt, or the original prompt when critique is disabled, unavailable, or fails.
        """
        if not self.config.config.auto_critique:
            return prompt

        if not self.prompt_critic:
            console.print("[yellow]Warning: PromptOS critique system not available[/yellow]")
            return prompt

        try:
            # Use PromptOS critique system
            improved_prompt = self.prompt_critic.get_improved_prompt(prompt)
            if self.debug:
                console.print("[dim]Prompt enhanced using PromptOS critique system[/dim]")
            return improved_prompt
        except Exception as e:
            console.print(f"[yellow]Warning: Critique failed: {e}[/yellow]")
            return prompt

    def critique_prompt(self, prompt: str) -> str:
        """
        Improve a prompt using the configured critique system.
        
        Parameters:
            prompt (str): The prompt to critique.
        
        Returns:
            str: The improved prompt, or the original prompt when critique is unavailable or fails.
        """
        return asyncio.run(self.critique_prompt_async(prompt))

    async def execute_async(self, prompt: str, variables: Dict[str, Any]) -> Any:
        """
        Execute the currently loaded agent with the provided prompt and variables.
        
        Parameters:
            prompt (str): The prompt to send to the agent.
            variables (Dict[str, Any]): Additional values supplied to the agent.
        
        Returns:
            Any: The agent's response.
        
        Raises:
            ValueError: If no agent is loaded or the loaded agent has no execution method.
        """
        if not self.current_agent:
            raise ValueError("No agent loaded")

        # Check if agent has async execution method
        if hasattr(self.current_agent, "execute_async"):
            return await self.current_agent.execute_async(prompt, variables)
        elif hasattr(self.current_agent, "execute"):
            return self.current_agent.execute(prompt, variables)
        else:
            raise ValueError(f"Agent {self.current_agent.manifest.name} has no execute method")

    def execute(self, prompt: str, variables: Dict[str, Any]) -> Any:
        """Synchronous wrapper for execute_async."""
        return asyncio.run(self.execute_async(prompt, variables))
