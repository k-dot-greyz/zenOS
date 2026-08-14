"""
Launcher for zenOS - orchestrates agent execution with AI providers.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Optional

from zen.core.agent import AgentRegistry
from zen.providers.openrouter import OpenRouterProvider
from zen.utils.config import Config

logger = logging.getLogger(__name__)


class Launcher:
    """
    Main launcher for executing agents with AI capabilities.
    """

    def __init__(
        self,
        debug: bool = False,
        registry: Optional[AgentRegistry] = None,
        config: Optional[Config] = None,
    ):
        """Initialize the launcher."""
        self.debug = debug
        self.config = config or Config()
        self.registry = registry or AgentRegistry()
        self.current_agent = None
        self.provider = None
        self.prompt_critic = None

        if self.config.config.openrouter_api_key:
            try:
                self.provider = OpenRouterProvider(self.config.config.openrouter_api_key)
                from zen.agents.promptos.prompt_critic import PromptCriticAgent

                self.prompt_critic = PromptCriticAgent()
            except Exception as exc:
                logger.warning("AI provider init failed: %s", exc)

    def load_agent(self, name: str):
        """Load an agent by name."""
        self.current_agent = self.registry.get_agent(name)
        logger.debug("Loaded agent: %s", name)

    async def critique_prompt_async(self, prompt: str) -> str:
        """
        Enhance a prompt using the PromptOS critique system.

        Args:
            prompt: Original prompt

        Returns:
            Enhanced prompt
        """
        if not self.config.config.auto_critique:
            return prompt

        if not self.prompt_critic:
            logger.warning("PromptOS critique system not available")
            return prompt

        try:
            improved_prompt = self.prompt_critic.get_improved_prompt(prompt)
            logger.debug("Prompt enhanced using PromptOS critique system")
            return improved_prompt
        except Exception as exc:
            logger.warning("Critique failed: %s", exc)
            return prompt

    def critique_prompt(self, prompt: str) -> str:
        """Synchronous wrapper for critique_prompt_async."""
        return asyncio.run(self.critique_prompt_async(prompt))

    async def execute_async(self, prompt: str, variables: Dict[str, Any]) -> Any:
        """
        Execute an agent with AI capabilities.

        Args:
            prompt: User prompt
            variables: Additional variables

        Returns:
            Agent response
        """
        if not self.current_agent:
            raise ValueError("No agent loaded")

        if hasattr(self.current_agent, "execute_async"):
            return await self.current_agent.execute_async(prompt, variables)
        if hasattr(self.current_agent, "execute"):
            return self.current_agent.execute(prompt, variables)
        raise ValueError(f"Agent {self.current_agent.manifest.name} has no execute method")

    def execute(self, prompt: str, variables: Dict[str, Any]) -> Any:
        """Synchronous wrapper for execute_async."""
        return asyncio.run(self.execute_async(prompt, variables))
