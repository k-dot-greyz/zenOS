"""
Troubleshooter agent for system diagnostics and fixes.
"""

from zen.core.agent import Agent, AgentManifest


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

Be thorough but concise. Focus on actionable solutions."""
        )
        super().__init__(manifest)
    
    def execute(self, prompt: str, variables: dict) -> str:
        """Execute the troubleshooter agent."""
        rendered_prompt = self.render_prompt(prompt, variables)
        # For now, just return the rendered prompt
        # In a real implementation, this would call the AI provider
        return f"Troubleshooter Agent Response:\n{rendered_prompt}"
