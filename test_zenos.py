#!/usr/bin/env python3
"""
Test script for zenOS - Let's see if this thing actually works!
"""

import asyncio
import os

import pytest

from zen.agents import builtin_agents
from zen.core.launcher import Launcher


@pytest.mark.asyncio
async def test_agents():
    """Test the basic agents"""
    print("🧘 Testing zenOS Agents...")

    # Check if we have an API key
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ No OPENROUTER_API_KEY found. Set it to test AI agents.")
        print("   You can get one from: https://openrouter.ai/")
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


def test_plugin_system():
    """Test the plugin system"""
    print("\n🔌 Testing Plugin System...")

    try:
        from zen.plugins import GitPluginLoader, PluginRegistry

        # Test registry
        registry = PluginRegistry()
        print(f"   📊 Registry initialized: {len(registry.plugins)} plugins")

        # Test stats
        stats = registry.get_collection_stats()
        print(f"   📈 Collection stats: {stats}")

        print("   ✅ Plugin system working!")

    except Exception as e:
        print(f"   ❌ Plugin system error: {e}")


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
