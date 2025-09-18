"""
Launcher for zenOS - orchestrates agent execution with AI providers.
"""

import asyncio
from typing import Dict, Any, Optional
from rich.console import Console

from zen.core.agent import AgentRegistry
from zen.providers.openrouter import OpenRouterProvider, ModelTier
from zen.utils.config import Config
from zen.core.security import SecurityFramework
from zen.core.critique import AutoCritique
from zen.utils.mobile_optimizer import get_optimizer, is_mobile

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
        self.security = SecurityFramework()
        self.current_agent = None
        self.provider = None
        self.critique = None
        self.optimizer = None

        # Initialize provider if configured
        if self.config.config.openrouter_api_key:
            self.provider = OpenRouterProvider(self.config.config.openrouter_api_key)
            self.critique = AutoCritique(self.provider, self.debug)

        if is_mobile():
            self.optimizer = get_optimizer()
    
    def load_agent(self, name: str):
        """Load an agent by name."""
        self.current_agent = self.registry.get_agent(name)
        if self.debug:
            console.print(f"[dim]Loaded agent: {name}[/dim]")
    
    async def enhance_prompt_async(self, prompt: str) -> str:
        """
        Enhance a prompt using the critique system.
        
        Args:
            prompt: Original prompt
        
        Returns:
            Enhanced prompt
        """
        if not self.config.config.auto_critique:
            return prompt
        
        if not self.critique:
            console.print("[yellow]Warning: Auto-critique is not available.[/yellow]")
            return prompt

        return await self.critique.enhance_prompt(prompt)

    def enhance_prompt(self, prompt: str) -> str:
        """Synchronous wrapper for enhance_prompt_async."""
        return asyncio.run(self.enhance_prompt_async(prompt))
    
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

        # 1. Security Scan
        security_report = self.security.scan_prompt(prompt)
        if not security_report["safe"]:
            console.print(f"[yellow]Warning: Potential security risk detected: {security_report['risk_level']}[/yellow]")
            for issue in security_report["issues"]:
                console.print(f"[yellow] - {issue['type']}: {issue['pattern']}[/yellow]")

        # 2. Sanitize Prompt
        sanitized_prompt = self.security.sanitize_prompt(prompt)
        if sanitized_prompt != prompt and self.debug:
            console.print("[dim]Prompt was sanitized.[/dim]")

        # If agent is a simple one without AI, just execute it
        if hasattr(self.current_agent, 'execute_func'):
            return await self.current_agent.execute(sanitized_prompt, variables, launcher=self)
        
        # For AI-powered agents, use the provider
        if not self.provider:
            raise ValueError("No AI provider configured. Set OPENROUTER_API_KEY.")
        
        # Render the full prompt with agent template
        rendered_prompt = self.current_agent.render_prompt(sanitized_prompt, variables)
        
        # Check cache if optimizer is available
        if self.optimizer:
            model = variables.get("model", self.config.config.default_model)
            cached_response = self.optimizer.cache.get(rendered_prompt, model)
            if cached_response:
                console.print(cached_response)
                return cached_response

        # Get response from AI
        response = ""
        async with self.provider:
            # Determine model based on agent requirements
            model = variables.get("model", self.config.config.default_model)
            
            # Use optimizer if available
            if self.optimizer:
                model = self.optimizer.battery.get_optimal_model(model)

            async for chunk in self.provider.complete(
                rendered_prompt,
                model=model,
                temperature=self.config.config.temperature,
                max_tokens=self.config.config.max_tokens,
                stream=self.config.config.stream_responses
            ):
                response += chunk
                if self.config.config.stream_responses:
                    console.print(chunk, end="")
        
        # Cache the response if optimizer is available
        if self.optimizer:
            model = variables.get("model", self.config.config.default_model)
            self.optimizer.cache.set(rendered_prompt, model, response)

        # 3. Validate Response
        if not self.security.validate_response(response):
            console.print("[bold red]Warning: AI response may contain sensitive information.[/bold red]")

        return response
    
    def execute(self, prompt: str, variables: Dict[str, Any]) -> Any:
        """Synchronous wrapper for execute_async."""
        return asyncio.run(self.execute_async(prompt, variables))
