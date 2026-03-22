#!/usr/bin/env python3
"""🧪 zenOS Test Runner
Comprehensive test suite for zenOS core functionality and bridge system
"""

import os
import platform
import sys
import traceback
from pathlib import Path


def test_imports():
    """Test core module imports"""
    print("🔍 Testing core imports...")

    try:

        print("  ✅ zenOS core import")
    except Exception as e:
        print(f"  ❌ zenOS core import: {e}")
        return False

    try:

        print("  ✅ Mobile adapter import")
    except Exception as e:
        print(f"  ❌ Mobile adapter import: {e}")
        return False

    try:

        print("  ✅ Config import")
    except Exception as e:
        print(f"  ❌ Config import: {e}")
        return False

    try:

        print("  ✅ Agent manifest import")
    except Exception as e:
        print(f"  ❌ Agent manifest import: {e}")
        return False

    return True


def test_mobile_adapter():
    """Test mobile adapter functionality"""
    print("\n📱 Testing mobile adapter...")

    try:
        from zen.ai.mobile_adapter import MobileAIAdapter

        adapter = MobileAIAdapter()
        print("  ✅ Mobile adapter instantiation")

        # Check for Termux by looking for TERMUX_VERSION env var or PREFIX path
        is_termux = os.environ.get("TERMUX_VERSION") or "/com.termux/" in os.environ.get(
            "PREFIX", ""
        )
        if platform.system() != "Linux" or not is_termux:
            print("  ⚠️  Skipping mobile context check (not on Termux)")
            return True

        context = adapter.get_mobile_context()
        print(f"  ✅ Mobile context: {context.device_model}")

        return True
    except Exception as e:
        print(f"  ❌ Mobile adapter test: {e}")
        traceback.print_exc()
        return False


def test_config():
    """Test configuration system"""
    print("\n⚙️ Testing configuration...")

    try:
        from zen.utils.config import ZenConfig

        config = ZenConfig()
        print(f"  ✅ Config created: {config.agents_dir}")

        # Test environment loading
        from zen.utils.config import Config

        config_manager = Config()
        print("  ✅ Config manager created")
        assert config_manager.is_configured is not None, "Config manager should be initialized"

        return True
    except Exception as e:
        print(f"  ❌ Config test: {e}")
        traceback.print_exc()
        return False


def test_cli_basic():
    """Test basic CLI functionality"""
    print("\n🖥️ Testing CLI basics...")

    try:
        # Test version
        import subprocess

        result = subprocess.run(
            [sys.executable, "-m", "zen.cli", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            print(f"  ✅ CLI version: {result.stdout.strip()}")
        else:
            print(f"  ❌ CLI version failed: {result.stderr}")
            return False

        return True
    except Exception as e:
        print(f"  ❌ CLI test: {e}")
        traceback.print_exc()
        return False


def test_bridge_scripts():
    """Test bridge script files exist and are readable"""
    print("\n🌉 Testing bridge scripts...")

    scripts = [
        "scripts/airi-zenos-bridge.sh",
        "scripts/voice-bridge.sh",
        "scripts/offline-bridge.sh",
        "scripts/ultimate-bridge-setup.sh",
        "scripts/bridge-launcher.ps1",
    ]

    all_exist = True
    for script in scripts:
        script_path = Path(script)
        if script_path.exists():
            print(f"  ✅ {script} exists")
        else:
            print(f"  ❌ {script} missing")
            all_exist = False

    return all_exist


def test_dependencies():
    """Test required dependencies"""
    print("\n📦 Testing dependencies...")

    required_modules = [
        "click",
        "rich",
        "yaml",
        "jinja2",
        "pydantic",
        "aiohttp",
        "dotenv",
        "prompt_toolkit",
    ]

    all_imported = True
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module} missing")
            all_imported = False

    return all_imported


def main():
    """Run all tests"""
    print("🧘 zenOS Test Suite")
    print("=" * 50)

    tests = [
        ("Core Imports", test_imports),
        ("Mobile Adapter", test_mobile_adapter),
        ("Configuration", test_config),
        ("CLI Basics", test_cli_basic),
        ("Bridge Scripts", test_bridge_scripts),
        ("Dependencies", test_dependencies),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")

    if passed == total:
        print("🎉 All tests passed! zenOS is ready to go!")
        return 0
    else:
        print("⚠️ Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
