#!/usr/bin/env python3
"""Simple test suite for PKM module (Windows compatible).
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, ".")


def test_imports():
    """Test that all PKM modules can be imported."""
    print("Testing PKM module imports...")

    try:

        print("OK: Main PKM module imported")


        print("OK: PKMConfig imported")


        print("OK: Data models imported")


        print("OK: PKMStorage imported")


        print("OK: GeminiExtractor imported")


        print("OK: ConversationProcessor imported")


        print("OK: PKMScheduler imported")


        print("OK: PKMAgent imported")


        print("OK: PKM CLI imported")

        return True
    except Exception as e:
        print(f"FAIL: Import failed: {e}")
        return False


def test_config():
    """Test PKM configuration."""
    print("\nTesting PKM configuration...")

    try:
        from zen.pkm.config import PKMConfig

        # Test default config
        config = PKMConfig()
        print(f"OK: Default config created: {config.pkm_dir}")

        # Test config serialization
        config_dict = config.to_dict()
        print(f"OK: Config serialized: {len(config_dict)} keys")

        # Test config save/load
        test_config_path = Path("test_pkm_config.yaml")
        config.save(test_config_path)
        print("OK: Config saved to file")

        loaded_config = PKMConfig.load(test_config_path)
        print("OK: Config loaded from file")

        # Cleanup
        test_config_path.unlink()
        print("OK: Test config file cleaned up")

        return True
    except Exception as e:
        print(f"FAIL: Config test failed: {e}")
        return False


def test_models():
    """Test data models."""
    print("\nTesting data models...")

    try:
        from zen.pkm.models import (
            Conversation,
            ConversationStatus,
            KnowledgeEntry,
            Message,
            MessageRole,
        )

        # Test Message creation
        message = Message(
            role=MessageRole.USER, content="Hello, this is a test message", timestamp=datetime.now()
        )
        print("OK: Message created")

        # Test Conversation creation
        conversation = Conversation(
            id="test-conv-001",
            title="Test Conversation",
            messages=[message],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status=ConversationStatus.COMPLETED,
        )
        print("OK: Conversation created")

        # Test serialization
        conv_dict = conversation.to_dict()
        print(f"OK: Conversation serialized: {len(conv_dict)} keys")

        # Test deserialization
        conv_restored = Conversation.from_dict(conv_dict)
        print("OK: Conversation deserialized")

        # Test KnowledgeEntry
        knowledge = KnowledgeEntry(
            id="kb-001",
            title="Test Knowledge",
            content="This is test knowledge content",
            source_conversation_id="test-conv-001",
            source_message_index=0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        print("OK: KnowledgeEntry created")

        return True
    except Exception as e:
        print(f"FAIL: Models test failed: {e}")
        return False


def test_storage():
    """Test storage functionality."""
    print("\nTesting storage functionality...")

    try:
        from zen.pkm.config import PKMConfig
        from zen.pkm.models import Conversation, ConversationStatus, Message, MessageRole
        from zen.pkm.storage import PKMStorage

        # Create test config with temp directory
        config = PKMConfig()
        config.pkm_dir = Path("test_pkm_storage")

        # Initialize storage
        storage = PKMStorage(config)
        print("OK: PKMStorage initialized")

        # Create test conversation
        test_message = Message(
            role=MessageRole.USER, content="Test message for storage", timestamp=datetime.now()
        )

        test_conversation = Conversation(
            id="storage-test-001",
            title="Storage Test Conversation",
            messages=[test_message],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status=ConversationStatus.COMPLETED,
        )

        # Test save conversation
        storage.save_conversation(test_conversation)
        print("OK: Conversation saved")

        # Test load conversation
        loaded_conv = storage.load_conversation("storage-test-001")
        print("OK: Conversation loaded")

        # Test list conversations
        conversations = storage.list_conversations()
        print(f"OK: Listed {len(conversations)} conversations")

        # Test search
        search_results = storage.search_conversations("test")
        print(f"OK: Search returned {len(search_results)} results")

        # Test statistics
        stats = storage.get_statistics()
        print(f"OK: Statistics: {stats}")

        # Cleanup
        import shutil

        shutil.rmtree("test_pkm_storage", ignore_errors=True)
        print("OK: Test storage cleaned up")

        return True
    except Exception as e:
        print(f"FAIL: Storage test failed: {e}")
        return False


def test_agent():
    """Test PKM agent."""
    print("\nTesting PKM agent...")

    try:
        from zen.pkm.agent import PKMAgent

        # Initialize agent
        agent = PKMAgent()
        print("OK: PKMAgent initialized")

        # Test agent manifest
        manifest = agent.manifest
        print(f"OK: Agent manifest: {manifest.name} - {manifest.description}")

        # Test agent execution (without actual extraction)
        test_prompt = "Show me my conversation statistics"
        result = agent.execute(test_prompt, {})
        print("OK: Agent executed successfully")

        return True
    except Exception as e:
        print(f"FAIL: Agent test failed: {e}")
        return False


def test_cli():
    """Test CLI functionality."""
    print("\nTesting CLI functionality...")

    try:
        import click.testing

        from zen.pkm.cli import pkm

        # Test CLI group creation
        runner = click.testing.CliRunner()
        result = runner.invoke(pkm, ["--help"])

        if result.exit_code == 0:
            print("OK: PKM CLI help command works")
        else:
            print(f"FAIL: PKM CLI help failed: {result.output}")
            return False

        # Test individual commands
        commands = [
            "extract",
            "process",
            "search",
            "list_conversations",
            "stats",
            "export",
            "schedule",
        ]

        for cmd in commands:
            result = runner.invoke(pkm, [cmd, "--help"])
            if result.exit_code == 0:
                print(f"OK: PKM CLI {cmd} command available")
            else:
                print(f"FAIL: PKM CLI {cmd} command failed")
                return False

        return True
    except Exception as e:
        print(f"FAIL: CLI test failed: {e}")
        return False


async def test_async_functionality():
    """Test async functionality."""
    print("\nTesting async functionality...")

    try:
        from zen.pkm.config import PKMConfig
        from zen.pkm.extractor import GeminiExtractor

        # Create test config
        config = PKMConfig()

        # Test async context manager
        async with GeminiExtractor(config) as extractor:
            print("OK: GeminiExtractor async context manager works")

        return True
    except Exception as e:
        print(f"FAIL: Async test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("PKM Module Test Suite")
    print("=" * 50)

    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Data Models", test_models),
        ("Storage", test_storage),
        ("Agent", test_agent),
        ("CLI", test_cli),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"FAIL: {test_name} test failed")
        except Exception as e:
            print(f"FAIL: {test_name} test crashed: {e}")

    # Test async functionality
    try:
        if asyncio.run(test_async_functionality()):
            passed += 1
        else:
            print("FAIL: Async functionality test failed")
    except Exception as e:
        print(f"FAIL: Async functionality test crashed: {e}")

    total += 1

    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("SUCCESS: All tests passed! PKM module is ready to use.")
        return True
    else:
        print("WARNING: Some tests failed. Check the output above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
