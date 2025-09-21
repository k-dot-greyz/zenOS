"""
Critic agent for prompt analysis and improvement.
"""

from zen.core.agent import Agent, AgentManifest


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

Provide an improved version with explanations for each change."""
        )
        super().__init__(manifest)
    
    def execute(self, prompt: str, variables: dict) -> str:
        """Execute the critic agent."""
        rendered_prompt = self.render_prompt(prompt, variables)
        # For now, just return the rendered prompt
        # In a real implementation, this would call the AI provider
        return f"Critic Agent Response:\n{rendered_prompt}"
