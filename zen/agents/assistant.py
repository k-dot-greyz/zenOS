"""
General-purpose assistant agent.
"""

from zen.core.agent import Agent, AgentManifest


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

Be conversational and engaging while maintaining professionalism."""
        )
        super().__init__(manifest)
    
    def execute(self, prompt: str, variables: dict) -> str:
        """Execute the assistant agent."""
        rendered_prompt = self.render_prompt(prompt, variables)
        # For now, just return the rendered prompt
        # In a real implementation, this would call the AI provider
        return f"Assistant Agent Response:\n{rendered_prompt}"
