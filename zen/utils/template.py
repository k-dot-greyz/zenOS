"""
Template engine for zenOS using Jinja2.
"""

from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader, Template, select_autoescape


class TemplateEngine:
    """
    Jinja2-based template engine for rendering prompts and content.
    """

    def __init__(self, template_dir: Optional[Path] = None):
        """
        Initialize the template engine with an optional template directory.
        
        Parameters:
            template_dir (Optional[Path]): Directory containing template files. Uses the project's default templates directory when omitted.
        """
        if template_dir is None:
            template_dir = Path(__file__).parent.parent / "templates"

        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)) if template_dir.exists() else None,
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Add custom filters
        self.env.filters["markdown"] = self._markdown_filter
        self.env.filters["code"] = self._code_filter

    def render(self, template_str: str, variables: Dict[str, Any]) -> str:
        """
        Render a template string with variables.

        Args:
            template_str: The template string
            variables: Variables to inject

        Returns:
            Rendered string
        """
        template = Template(template_str)
        return template.render(**variables)

    def render_file(self, template_name: str, variables: Dict[str, Any]) -> str:
        """
        Render a configured template file with the supplied variables.
        
        Args:
            template_name: Name of the template file.
            variables: Values available to the template.
        
        Returns:
            The rendered template content.
        
        Raises:
            ValueError: If no template directory is configured.
        """
        if not self.env.loader:
            raise ValueError("No template directory configured")

        template = self.env.get_template(template_name)
        return template.render(**variables)

    def _markdown_filter(self, text: str) -> str:
        """Wrap text in a fenced Markdown code block labeled `markdown`."""
        # Simple markdown formatting
        return f"```markdown\n{text}\n```"

    def _code_filter(self, text: str, language: str = "python") -> str:
        """
        Format text as a fenced code block.
        
        Parameters:
            text (str): The code content to format.
            language (str): The language label for the code block.
        
        Returns:
            str: The formatted fenced code block.
        """
        return f"```{language}\n{text}\n```"
