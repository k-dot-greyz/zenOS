"""
Launcher for zenOS - orchestrates agent execution with AI providers.
"""

import asyncio
from typing import Dict, Any, Optional
from rich.console import Console

from zen.core.agent import AgentRegistry
from zen.providers.openrouter import OpenRouterProvider, ModelTier
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
        
        # Initialize provider if configured
        if self.config.config.openrouter_api_key:
            self.provider = OpenRouterProvider(self.config.config.openrouter_api_key)
    
    def load_agent(self, name: str):
        """Load an agent by name."""
        self.current_agent = self.registry.get_agent(name)
        if self.debug:
            console.print(f"[dim]Loaded agent: {name}[/dim]")
    
    async def critique_prompt_async(self, prompt: str) -> str:
        """
        Enhance a prompt using the critique system.
        
        Args:
            prompt: Original prompt
        
        Returns:
            Enhanced prompt
        """
        if not self.config.config.auto_critique:
            return prompt
        
        if not self.provider:
            console.print("[yellow]Warning: No AI provider configured for auto-critique[/yellow]")
            return prompt
        
        critique_prompt = f"""
        Please analyze and improve this prompt for clarity, specificity, and effectiveness:
        
        Original prompt: {prompt}
        
        Provide an enhanced version that:
        1. Is more specific and clear
        2. Includes relevant context
        3. Guides toward a better response
        4. Maintains the original intent
        
        Return only the improved prompt, nothing else.
        """
        
        try:
            enhanced = ""
            async with self.provider:
                async for chunk in self.provider.complete(
                    critique_prompt,
                    model="anthropic/claude-3-haiku",  # Use fast model for critique
                    temperature=0.3,
                    max_tokens=500
                ):
                    enhanced += chunk
            
            return enhanced.strip() or prompt
        except Exception as e:
            if self.debug:
                console.print(f"[red]Critique failed: {e}[/red]")
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
        
        # Check if agent has async execution method
        if hasattr(self.current_agent, 'execute_async'):
            return await self.current_agent.execute_async(prompt, variables)
        elif hasattr(self.current_agent, 'execute'):
            return self.current_agent.execute(prompt, variables)
        else:
            raise ValueError(f"Agent {self.current_agent.manifest.name} has no execute method")
    
    def execute(self, prompt: str, variables: Dict[str, Any]) -> Any:
        """Synchronous wrapper for execute_async."""
        return asyncio.run(self.execute_async(prompt, variables))
