"""
Web interface for the Text Processor Plugin
"""

from .main import TextProcessorPlugin, create_plugin

# Web plugin is the same as main for now
WebTextProcessorPlugin = TextProcessorPlugin

def create_web_plugin(config):
    """Create a web plugin instance"""
    return create_plugin(config)
