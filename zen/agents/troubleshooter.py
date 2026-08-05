"""
Troubleshooter agent for system diagnostics and fixes.
"""

import asyncio

from zen.core.agent import Agent, AgentManifest
from zen.providers.openrouter import OpenRouterProvider


class TroubleshooterAgent(Agent):
    """Agent specialized in troubleshooting and system diagnostics."""

    def __init__(self):
        """
        Initialize the troubleshooter agent with its diagnostic and automated-fix configuration.
        """
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
        """
        Execute the troubleshooter agent with the rendered prompt.
        
        Parameters:
        	prompt (str): Prompt template to render.
        	variables (dict): Values used to render the prompt.
        
        Returns:
        	str: Generated response, or an error message containing the exception and rendered prompt.
        """
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
        """
        Execute the troubleshooter agent synchronously.
        
        Parameters:
        	prompt (str): The prompt to render and execute.
        	variables (dict): Values used to render the prompt.
        
        Returns:
        	str: The troubleshooter agent's response.
        """
        return asyncio.run(self.execute_async(prompt, variables))
