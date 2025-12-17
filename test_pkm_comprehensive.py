#!/usr/bin/env python3
"""
Comprehensive test suite for PKM module.
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, '.')

def test_imports():
    """Test that all PKM modules can be imported."""
    print("🧪 Testing PKM module imports...")
    
    try:
        import zen.pkm
        print("✅ Main PKM module imported")
        
        from zen.pkm.config import PKMConfig
        print("✅ PKMConfig imported")
        
        from zen.pkm.models import Conversation, Message, MessageRole, KnowledgeEntry
        print("✅ Data models imported")
        
        from zen.pkm.storage import PKMStorage
        print("✅ PKMStorage imported")
        
        from zen.pkm.extractor import GeminiExtractor
        print("✅ GeminiExtractor imported")
        
        from zen.pkm.processor import ConversationProcessor
        print("✅ ConversationProcessor imported")
        
        from zen.pkm.scheduler import PKMScheduler
        print("✅ PKMScheduler imported")
        
        from zen.pkm.agent import PKMAgent
        print("✅ PKMAgent imported")
        
        from zen.pkm.cli import pkm
        print("✅ PKM CLI imported")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_config():
    """Test PKM configuration."""
    print("\n🧪 Testing PKM configuration...")
    
    try:
        from zen.pkm.config import PKMConfig
        
        # Test default config
        config = PKMConfig()
        print(f"✅ Default config created: {config.pkm_dir}")
        
        # Test config serialization
        config_dict = config.to_dict()
        print(f"✅ Config serialized: {len(config_dict)} keys")
        
        # Test config save/load
        test_config_path = Path("test_pkm_config.yaml")
        config.save(test_config_path)
        print("✅ Config saved to file")
        
        loaded_config = PKMConfig.load(test_config_path)
        print("✅ Config loaded from file")
        
        # Cleanup
        test_config_path.unlink()
        print("✅ Test config file cleaned up")
        
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False


def test_models():
    """Test data models."""
    print("\n🧪 Testing data models...")
    
    try:
        from zen.pkm.models import Conversation, Message, MessageRole, KnowledgeEntry, ConversationStatus
        
        # Test Message creation
        message = Message(
            role=MessageRole.USER,
            content="Hello, this is a test message",
            timestamp=datetime.now()
        )
        print("✅ Message created")
        
        # Test Conversation creation
        conversation = Conversation(
            id="test-conv-001",
            title="Test Conversation",
            messages=[message],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status=ConversationStatus.COMPLETED
        )
        print("✅ Conversation created")
        
        # Test serialization
        conv_dict = conversation.to_dict()
        print(f"✅ Conversation serialized: {len(conv_dict)} keys")
        
        # Test deserialization
        conv_restored = Conversation.from_dict(conv_dict)
        print("✅ Conversation deserialized")
        
        # Test KnowledgeEntry
        knowledge = KnowledgeEntry(
            id="kb-001",
            title="Test Knowledge",
            content="This is test knowledge content",
            source_conversation_id="test-conv-001",
            source_message_index=0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        print("✅ KnowledgeEntry created")
        
        return True
    except Exception as e:
        print(f"❌ Models test failed: {e}")
        return False


def test_storage():
    """Test storage functionality."""
    print("\n🧪 Testing storage functionality...")
    
    try:
        from zen.pkm.storage import PKMStorage
        from zen.pkm.config import PKMConfig
        from zen.pkm.models import Conversation, Message, MessageRole, ConversationStatus
        
        # Create test config with temp directory
        config = PKMConfig()
        config.pkm_dir = Path("test_pkm_storage")
        
        # Initialize storage
        storage = PKMStorage(config)
        print("✅ PKMStorage initialized")
        
        # Create test conversation
        test_message = Message(
            role=MessageRole.USER,
            content="Test message for storage",
            timestamp=datetime.now()
        )
        
        test_conversation = Conversation(
            id="storage-test-001",
            title="Storage Test Conversation",
            messages=[test_message],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status=ConversationStatus.COMPLETED
        )
        
        # Test save conversation
        storage.save_conversation(test_conversation)
        print("✅ Conversation saved")
        
        # Test load conversation
        loaded_conv = storage.load_conversation("storage-test-001")
        print("✅ Conversation loaded")
        
        # Test list conversations
        conversations = storage.list_conversations()
        print(f"✅ Listed {len(conversations)} conversations")
        
        # Test search
        search_results = storage.search_conversations("test")
        print(f"✅ Search returned {len(search_results)} results")
        
        # Test statistics
        stats = storage.get_statistics()
        print(f"✅ Statistics: {stats}")
        
        # Cleanup
        import shutil
        shutil.rmtree("test_pkm_storage", ignore_errors=True)
        print("✅ Test storage cleaned up")
        
        return True
    except Exception as e:
        print(f"❌ Storage test failed: {e}")
        return False


def test_processor():
    """Test conversation processor."""
    print("\n🧪 Testing conversation processor...")
    
    try:
        from zen.pkm.processor import ConversationProcessor
        from zen.pkm.config import PKMConfig
        from zen.pkm.models import Conversation, Message, MessageRole, ConversationStatus
        
        # Create test config
        config = PKMConfig()
        config.auto_summarize = True
        config.extract_keywords = True
        config.generate_tags = True
        config.pkm_dir = Path("test_pkm_processor")
        
        # Initialize storage and processor
        storage = PKMStorage(config)
        processor = ConversationProcessor(config, storage)
        print("✅ ConversationProcessor initialized")
        
        # Create test conversation
        messages = [
            Message(role=MessageRole.USER, content="What is Python programming?"),
            Message(role=MessageRole.ASSISTANT, content="Python is a high-level programming language known for its simplicity and readability."),
            Message(role=MessageRole.USER, content="Can you give me an example?"),
            Message(role=MessageRole.ASSISTANT, content="Sure! Here's a simple Python example:\n\nprint('Hello, World!')")
        ]
        
        conversation = Conversation(
            id="processor-test-001",
            title="Python Programming Discussion",
            messages=messages,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status=ConversationStatus.COMPLETED
        )
        
        # Test processing
        processed_conv = processor.process_conversation(conversation)
        print("✅ Conversation processed")
        
        # Check if processing added metadata
        if processed_conv.summary:
            print(f"✅ Summary generated: {len(processed_conv.summary)} chars")
        
        if processed_conv.keywords:
            print(f"✅ Keywords extracted: {processed_conv.keywords}")
        
        if processed_conv.tags:
            print(f"✅ Tags generated: {processed_conv.tags}")
        
        return True
    except Exception as e:
        print(f"❌ Processor test failed: {e}")
        return False


def test_scheduler():
    """Test scheduler functionality."""
    print("\n🧪 Testing scheduler functionality...")
    
    try:
        from zen.pkm.scheduler import PKMScheduler
        from zen.pkm.config import PKMConfig
        
        # Create test config
        config = PKMConfig()
        config.cron_enabled = True
        
        # Initialize scheduler
        scheduler = PKMScheduler(config)
        print("✅ PKMScheduler initialized")
        
        # Test job registration
        def test_job():
            print("Test job executed")
        
        scheduler.register_job("test_job", test_job, "*/1 * * * *")  # Every minute
        print("✅ Test job registered")
        
        # Test job listing
        jobs = scheduler.list_jobs()
        print(f"✅ Listed {len(jobs)} jobs")
        
        # Test job removal
        scheduler.remove_job("test_job")
        print("✅ Test job removed")
        
        return True
    except Exception as e:
        print(f"❌ Scheduler test failed: {e}")
        return False


def test_agent():
    """Test PKM agent."""
    print("\n🧪 Testing PKM agent...")
    
    try:
        from zen.pkm.agent import PKMAgent
        
        # Initialize agent
        agent = PKMAgent()
        print("✅ PKMAgent initialized")
        
        # Test agent manifest
        manifest = agent.manifest
        print(f"✅ Agent manifest: {manifest.name} - {manifest.description}")
        
        # Test agent execution (without actual extraction)
        test_prompt = "Show me my conversation statistics"
        result = agent.execute(test_prompt, {})
        print("✅ Agent executed successfully")
        
        return True
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        return False


def test_cli():
    """Test CLI functionality."""
    print("\n🧪 Testing CLI functionality...")
    
    try:
        from zen.pkm.cli import pkm
        import click.testing
        
        # Test CLI group creation
        runner = click.testing.CliRunner()
        result = runner.invoke(pkm, ['--help'])
        
        if result.exit_code == 0:
            print("✅ PKM CLI help command works")
        else:
            print(f"❌ PKM CLI help failed: {result.output}")
            return False
        
        # Test individual commands
        commands = ['extract', 'process', 'search', 'list', 'stats', 'export', 'schedule']
        
        for cmd in commands:
            result = runner.invoke(pkm, [cmd, '--help'])
            if result.exit_code == 0:
                print(f"✅ PKM CLI {cmd} command available")
            else:
                print(f"❌ PKM CLI {cmd} command failed")
                return False
        
        return True
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False


async def test_async_functionality():
    """Test async functionality."""
    print("\n🧪 Testing async functionality...")
    
    try:
        from zen.pkm.extractor import GeminiExtractor
        from zen.pkm.config import PKMConfig
        
        # Create test config
        config = PKMConfig()
        
        # Test async context manager
        async with GeminiExtractor(config) as extractor:
            print("✅ GeminiExtractor async context manager works")
        
        return True
    except Exception as e:
        print(f"❌ Async test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("PKM Module Comprehensive Test Suite")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Data Models", test_models),
        ("Storage", test_storage),
        ("Processor", test_processor),
        ("Scheduler", test_scheduler),
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
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    # Test async functionality
    try:
        if asyncio.run(test_async_functionality()):
            passed += 1
        else:
            print("❌ Async functionality test failed")
    except Exception as e:
        print(f"❌ Async functionality test crashed: {e}")
    
    total += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! PKM module is ready to use.")
        return True
    else:
        print("Some tests failed. Check the output above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
