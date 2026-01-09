"""CLI interface for the Text Processor Plugin
"""

import json
import sys

from .main import create_plugin


def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python cli.py <procedure> <input_data>")
        print("Available procedures: text.process, text.summarize, text.sentiment")
        sys.exit(1)

    procedure = sys.argv[1]
    input_data = sys.argv[2] if len(sys.argv) > 2 else "Hello, world!"

    # Create plugin instance
    config = {"language": "en", "max_length": 1000, "enable_sentiment": True}

    plugin = create_plugin(config)

    # Execute procedure
    import asyncio

    async def run():
        await plugin.initialize()
        result = await plugin.process(input_data, {"procedure": {"id": procedure}})
        print(json.dumps(result, indent=2))
        await plugin.cleanup()

    asyncio.run(run())


if __name__ == "__main__":
    main()
