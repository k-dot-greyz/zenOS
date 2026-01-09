"""Troubleshooter agent for system diagnostics and fixes."""

import asyncio

from zen.core.agent import Agent, AgentManifest
from zen.providers.openrouter import OpenRouterProvider


class TroubleshooterAgent(Agent):
    """Agent specialized in troubleshooting and system diagnostics."""

    def __init__(self):
        manifest = AgentManifest(
            name="troubleshooter",
            description="System diagnostics and automated fixes",
            version="1.0.0",
            tags=["system", "diagnostics", "troubleshooting"],
            prompt_template="""You are a system troubleshooting expert. Analyze the user's problem and provide step-by-step solutions.

Problem: {prompt}

Provide:
1. Root cause analysis
2. Step-by-step solution
3. Prevention tips
4. Alternative approaches if needed

Be thorough but concise. Focus on actionable solutions.""",
        )
        super().__init__(manifest)

    async def execute_async(self, prompt: str, variables: dict) -> str:
        """Execute the troubleshooter agent asynchronously."""
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
        """Execute the troubleshooter agent (sync wrapper)."""
        return asyncio.run(self.execute_async(prompt, variables))
