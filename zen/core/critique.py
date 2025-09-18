"""
Auto-critique system for zenOS.
"""

from typing import Dict, Any, Optional
from zen.providers.openrouter import OpenRouterProvider
from rich.console import Console

console = Console()


class AutoCritique:
    """
    Automatic critique and improvement system for prompts and responses.
    """
    
    def __init__(self, provider: Optional[OpenRouterProvider] = None, debug: bool = False):
        """Initialize the auto-critique system."""
        self.provider = provider
        self.debug = debug
    
    async def enhance_prompt(self, prompt: str) -> str:
        """
        Enhance a prompt using the critique system.
        
        Args:
            prompt: Original prompt
        
        Returns:
            Enhanced prompt
        """
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
    
    async def critique_response(self, response: str, original_prompt: str) -> Dict[str, Any]:
        """
        Critique an AI response for quality and accuracy.
        
        Args:
            response: The response to critique
            original_prompt: The original prompt that generated it
        
        Returns:
            Dictionary with critique and suggestions
        """
        # TODO: Implement response critique
        return {
            "quality_score": 0.8,
            "issues": [],
            "suggestions": []
        }
