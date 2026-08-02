#!/usr/bin/env python3
"""
Quick Test for zenOS Setup System

A minimal test to verify the setup system is working.
"""

import subprocess
import sys
from pathlib import Path


def test_imports():
    """Test that all setup modules can be imported"""
    print("🧪 Testing imports...")

    try:
        from zen.setup.unified_setup import UnifiedSetupManager

        print("✅ UnifiedSetupManager imported")

        from zen.setup.environment_detector import EnvironmentDetector

        print("✅ EnvironmentDetector imported")

        from zen.setup.git_setup import GitSetupManager

        print("✅ GitSetupManager imported")

        from zen.setup.mcp_setup import MCPSetupManager

        print("✅ MCPSetupManager imported")

        from zen.setup.troubleshooter import SetupTroubleshooter

        print("✅ SetupTroubleshooter imported")

        return True

    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_environment_detection():
    """Test environment detection"""
    print("\n🔍 Testing environment detection...")

    try:
        from zen.setup.environment_detector import EnvironmentDetector

        detector = EnvironmentDetector()
        env_info = detector.detect_environment(Path.cwd())

        print(f"✅ OS: {env_info.platform}")
        print(f"✅ Python: {env_info.python_version}")
        print(f"✅ Shell: {env_info.shell}")

        return True

    except Exception as e:
        print(f"❌ Environment detection failed: {e}")
        return False


def test_setup_command():
    """Test the setup command"""
    print("\n🚀 Testing setup command...")

    try:
        # Test validation only
        result = subprocess.run(
            [sys.executable, "setup.py", "--validate-only"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            print("✅ Setup command validation passed")
            return True
        else:
            print(f"❌ Setup command failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Setup command test failed: {e}")
        return False


def main():
    """Run quick tests"""
    print("🧘 zenOS Setup System - Quick Test")
    print("=" * 40)

    tests = [
        ("Imports", test_imports),
        ("Environment Detection", test_environment_detection),
        ("Setup Command", test_setup_command),
    ]

    passed = 0
    total = len(tests)

    for name, test_func in tests:
        print(f"\n--- {name} ---")
        if test_func():
            passed += 1
        else:
            print(f"❌ {name} failed")

    print(f"\n📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Setup system is working.")
    else:
        print("⚠️  Some tests failed. Check the output above.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
