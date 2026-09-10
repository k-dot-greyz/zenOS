"""General-purpose assistant agent."""

import asyncio

from zen.core.agent import Agent, AgentManifest
from zen.providers.openrouter import OpenRouterProvider


class AssistantAgent(Agent):
    """General-purpose AI assistant."""

    def __init__(self):
        manifest = AgentManifest(
            name="assistant",
            description="General-purpose AI assistant",
            version="1.0.0",
            tags=["general", "assistant", "help"],
            prompt_template="""You are a helpful AI assistant. Provide clear, accurate, and helpful responses to the user's query.

Query: {prompt}

Respond with:
- Clear and accurate information
- Practical advice when applicable
- Examples if helpful
- Follow-up questions if needed

Be conversational and engaging while maintaining professionalism.""",
        )
        super().__init__(manifest)

    async def execute_async(self, prompt: str, variables: dict) -> str:
        """Execute the assistant agent asynchronously."""
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
        """Execute the assistant agent (sync wrapper)."""
        return asyncio.run(self.execute_async(prompt, variables))
