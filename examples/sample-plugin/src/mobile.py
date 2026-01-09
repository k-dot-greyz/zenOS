"""
Mobile-optimized version of the Text Processor Plugin
"""

from .main import TextProcessorPlugin, create_plugin

# Mobile plugin is the same as main for now
MobileTextProcessorPlugin = TextProcessorPlugin


def create_mobile_plugin(config):
    """Create a mobile plugin instance"""
    return create_plugin(config)
