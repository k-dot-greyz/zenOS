"""
Template catalog package exposing registry-aware utilities.
"""

from .catalog import TemplateCatalog
from .validator import TemplateValidator

__all__ = ["TemplateCatalog", "TemplateValidator"]
