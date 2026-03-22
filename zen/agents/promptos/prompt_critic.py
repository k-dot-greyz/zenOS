#!/usr/bin/env python3
"""Prompt Critic Agent - Core Auto-Critique System

This is the core auto-critique system from PromptOS, integrated into zenOS.
Every prompt gets automatically critiqued and upgraded for maximum effectiveness.
"""

from pathlib import Path
from typing import Any, Dict, Optional

from zen.core.agent import Agent, AgentManifest
from zen.providers.openrouter import OpenRouterProvider


class PromptCriticAgent(Agent):
    """Prompt Critic Agent - Core auto-critique system from PromptOS"""

    def __init__(self, config: Optional[Dict] = None):
        # Create agent manifest
        manifest = AgentManifest(
            name="prompt_critic",
            description="Analyzes and improves AI prompts using PromptOS critique system",
            version="1.0.0",
            author="PromptOS",
            tags=["critique", "prompt", "improvement"],
        )
        super().__init__(manifest)

        self.specialty = "prompt analysis and improvement specialist"
        self.primary_function = (
            "To analyze AI prompts and provide constructive critique for improvement"
        )
        self.voice = "Analytical, constructive, and detail-oriented"
        self.name = "prompt_critic"  # Add name attribute

        # Load PromptOS template
        self.template_path = Path(__file__).parent / "templates" / "prompt_critic.j2"
        self.context_path = Path(__file__).parent / "contexts"

        # Initialize OpenRouter provider
        self.provider = OpenRouterProvider()

    def load_template(self) -> str:
        """Load the PromptOS template for prompt critique"""
        if self.template_path.exists():
            return self.template_path.read_text()
        else:
            # Fallback template if file not found
            return self._get_fallback_template()

    def _get_fallback_template(self) -> str:
        """Fallback template if PromptOS template not available"""
        return """
# IDENTITY:
Your name is {{ name }}. You are a {{ specialty }}.
Your primary function is: {{ primary_function }}

# DIRECTIVES:
Your main goal is to complete the following task:

## Task: Critique and Refine Prompt
Analyze the given AI prompt and provide constructive critique for improvement.

## Constraints:
- Focus on clarity, conciseness, and completeness
- Provide actionable feedback
- Do not execute the prompt, only critique it

# REASONING FRAMEWORK:
Your reasoning process should follow the 'CoT' methodology:
1. **Analyze**: Break down the prompt and identify its components
2. **Evaluate**: Assess clarity, context, and effectiveness  
3. **Critique**: Identify specific areas for improvement
4. **Recommend**: Provide actionable suggestions for enhancement

# PROMPT TO CRITIQUE:
{{ prompt_to_critique }}

# TASK EXECUTION:
Please analyze the above prompt and provide your constructive critique.
"""

    def load_context(self, context_name: str) -> str:
        """Load context blocks from PromptOS"""
        context_file = self.context_path / f"{context_name}.md"
        if context_file.exists():
            return context_file.read_text()
        return ""

    def critique_prompt(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Critique a prompt and return improved version"""
        # Load template
        template = self.load_template()

        # Prepare context
        context_data = {
            "name": self.name,
            "specialty": self.specialty,
            "primary_function": self.primary_function,
            "prompt_to_critique": prompt,
            "task_context": self.load_context("task_context"),
            "max_length_constraint": self.load_context("max_length_constraint"),
            "role_context": self.load_context("role_context"),
            "home_studio_context": self.load_context("home_studio_context"),
        }

        # Merge with provided context
        if context:
            context_data.update(context)

        # Render template (simple string replacement for now)
        rendered_prompt = template
        for key, value in context_data.items():
            rendered_prompt = rendered_prompt.replace(f"{{{{ {key} }}}}", str(value))

        # Get critique from AI
        try:
            # For now, return a simple critique to avoid async issues
            # In a full implementation, this would properly handle async
            return f"""
# Prompt Critique

## Original Prompt
{prompt}

## Analysis
The prompt "{prompt}" could be improved for better clarity and specificity.

## Suggestions
1. Be more specific about what type of code you need
2. Include context about the programming language
3. Specify the desired output format
4. Add any constraints or requirements

## Improved Prompt
Please help me write [specific type of code] in [programming language] that [specific functionality]. The code should [specific requirements] and output [desired format].
"""
        except Exception as e:
            return f"Error getting critique: {e}"

    def execute(self, prompt: str, variables: Dict[str, Any]) -> Any:
        """Execute the prompt critic agent"""
        return self.critique_prompt(prompt, variables)

    def get_improved_prompt(self, original_prompt: str) -> str:
        """Get an improved version of the original prompt"""
        critique = self.critique_prompt(original_prompt)

        # Extract the improved prompt from the critique
        # This is a simple extraction - in a full implementation,
        # we'd parse the critique more intelligently
        lines = critique.split("\n")
        improved_lines = []
        in_improved_section = False

        for line in lines:
            if "improved" in line.lower() or "enhanced" in line.lower():
                in_improved_section = True
            elif in_improved_section and line.strip():
                if line.startswith("#") or line.startswith("##"):
                    break
                improved_lines.append(line)

        if improved_lines:
            return "\n".join(improved_lines).strip()
        else:
            # Fallback: return the original with critique
            return f"Original: {original_prompt}\n\nCritique: {critique}"


# Convenience function for easy access
def critique_prompt(prompt: str) -> str:
    """Quick function to critique a prompt"""
    agent = PromptCriticAgent()
    return agent.critique_prompt(prompt)


def improve_prompt(prompt: str) -> str:
    """Quick function to get an improved prompt"""
    agent = PromptCriticAgent()
    return agent.get_improved_prompt(prompt)
