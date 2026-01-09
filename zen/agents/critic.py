"""
Critic agent for prompt analysis and improvement.
"""

import asyncio

from zen.core.agent import Agent, AgentManifest
from zen.providers.openrouter import OpenRouterProvider


class CriticAgent(Agent):
    """Agent specialized in analyzing and improving prompts."""

    def __init__(self):
        manifest = AgentManifest(
            name="critic",
            description="Prompt analysis and improvement",
            version="1.0.0",
            tags=["prompt", "analysis", "improvement"],
            prompt_template="""You are a prompt engineering expert. Analyze the given prompt and provide improvements.

Original Prompt: {prompt}

Analyze:
1. Clarity and specificity
2. Context and background
3. Expected output format
4. Potential ambiguities

Provide an improved version with explanations for each change.""",
        )
        super().__init__(manifest)

    async def execute_async(self, prompt: str, variables: dict) -> str:
        """Execute the critic agent asynchronously."""
        rendered_prompt = self.render_prompt(prompt, variables)

        try:
            async with OpenRouterProvider() as provider:
                response = ""
                async for chunk in provider.complete(rendered_prompt, stream=True):
                    response += chunk
                return response
        except Exception as e:
            return f"Error calling AI provider: {e}\n\nRendered prompt:\n{rendered_prompt}"

    def execute(self, prompt: str, variables: dict) -> str:
        """Execute the critic agent (sync wrapper)."""
        return asyncio.run(self.execute_async(prompt, variables))
