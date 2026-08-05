"""
Web interface for the Text Processor Plugin
"""

from .main import TextProcessorPlugin, create_plugin

# Web plugin is the same as main for now
WebTextProcessorPlugin = TextProcessorPlugin


def create_web_plugin(config):
    """Create a web text processor plugin from the given configuration.
    
    Parameters:
    	config: Configuration used to create the plugin.
    
    Returns:
    	The created web text processor plugin.
    """
    return create_plugin(config)
