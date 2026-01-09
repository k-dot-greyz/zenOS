#!/usr/bin/env python3
"""Test script for zenOS - Let's see if this thing actually works!
"""

import asyncio
import os

from zen.agents import builtin_agents
from zen.core.launcher import Launcher


async def test_agents():
    """Test the basic agents"""
    print("🧘 Testing zenOS Agents...")

    # Check if we have an API key
    if not os.getenv("OPENROUTER_API_KEY"):
        print("⚠️  No OPENROUTER_API_KEY found. Skipping agent tests.")
        # If running in pytest, skip properly
        if "pytest" in sys.modules:
            import pytest
            pytest.skip("OPENROUTER_API_KEY not set")
        return

    launcher = Launcher(debug=True)

    # Test each agent
    for agent_name, agent in builtin_agents.items():
        print(f"\n🔧 Testing {agent_name} agent...")

        try:
            launcher.load_agent(agent_name)

            # Test with a simple prompt
            test_prompt = "Hello, can you help me with a simple question?"

            print(f"   Prompt: {test_prompt}")
            print("   Response:")

            response = await launcher.execute_async(test_prompt, {})
            print(f"   {response[:100]}...")
            print("   ✅ Success!")

        except Exception as e:
            print(f"   ❌ Error: {e}")
            if "pytest" in sys.modules:
                import pytest
                pytest.fail(f"Agent {agent_name} failed: {e}")


def test_plugin_system():
    """Test the plugin system"""
    print("\n🔌 Testing Plugin System...")

    try:
        from zen.plugins import PluginRegistry

        # Test registry
        registry = PluginRegistry()
        print(f"   📊 Registry initialized: {len(registry.plugins)} plugins")

        # Test stats
        stats = registry.get_collection_stats()
        print(f"   📈 Collection stats: {stats}")

        print("   ✅ Plugin system working!")

    except Exception as e:
        print(f"   ❌ Plugin system error: {e}")
        if "pytest" in sys.modules:
            import pytest
            pytest.fail(f"Plugin system failed: {e}")
        if "pytest" in sys.modules:
            import pytest
            pytest.fail(f"Plugin system failed: {e}")
        if "pytest" in sys.modules:
            import pytest
            pytest.fail(f"Plugin system failed: {e}")
        if "pytest" in sys.modules:
            import pytest
            pytest.fail(f"Plugin system failed: {e}")


async def main():
    """Main test function"""
    print("🚀 zenOS Test Suite")
    print("=" * 50)

    # Test plugin system (doesn't need API key)
    test_plugin_system()

    # Test agents (needs API key)
    await test_agents()

    print("\n🎉 Test complete!")


if __name__ == "__main__":
    asyncio.run(main())
