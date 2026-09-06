#!/usr/bin/env python3
"""
Quick setup script for PKM module authentication.
"""

import os
import sys
from pathlib import Path


def main():
    """
    Guide the user through PKM Gemini authentication setup by printing step-by-step instructions and validating the environment.

    Prints guidance on obtaining Gemini cookies/tokens and how to configure them (environment variables or a .env file), then checks that the "zen/pkm" directory exists and that the GEMINI_SESSION_COOKIE and GEMINI_CSRF_TOKEN environment variables are present.

    Returns:
        True if the "zen/pkm" directory exists and both GEMINI_SESSION_COOKIE and GEMINI_CSRF_TOKEN are set, False otherwise.
    """
    print("PKM Module Authentication Setup")
    print("=" * 40)

    print("\n1. First, you need to get your Google Gemini cookies and tokens.")
    print("   See the detailed guide: zen/pkm/GEMINI_AUTH_GUIDE.md")

    print("\n2. Once you have them, you can set them in several ways:")

    print("\n   Option A - Environment Variables (Recommended):")
    print("   Windows PowerShell:")
    print('   $env:GEMINI_SESSION_COOKIE="your_session_cookie_here"')
    print('   $env:GEMINI_CSRF_TOKEN="your_csrf_token_here"')

    print("\n   Linux/macOS:")
    print('   export GEMINI_SESSION_COOKIE="your_session_cookie_here"')
    print('   export GEMINI_CSRF_TOKEN="your_csrf_token_here"')

    print("\n   Option B - .env file:")
    print("   Create a .env file in the zenOS directory with:")
    print("   GEMINI_SESSION_COOKIE=your_session_cookie_here")
    print("   GEMINI_CSRF_TOKEN=your_csrf_token_here")

    print("\n3. Test your setup:")
    print("   python test_pkm_simple.py")
    print("   zen pkm extract --limit 1")
    print("   zen pkm list-conversations")

    print("\n4. If you need help:")
    print("   - Check zen/pkm/GEMINI_AUTH_GUIDE.md for detailed instructions")
    print("   - Run with --debug flag for more information")
    print("   - Make sure you're signed into Gemini in your browser")

    # Check if we're in the right directory
    if not Path("zen/pkm").exists():
        print("\n⚠️  Warning: PKM module not found. Make sure you're in the zenOS directory.")
        return False

    # Check if environment variables are set
    session_cookie = os.getenv("GEMINI_SESSION_COOKIE")
    csrf_token = os.getenv("GEMINI_CSRF_TOKEN")

    if session_cookie and csrf_token:
        print("\n✅ Environment variables are set!")
        print(f"   Session Cookie: {session_cookie[:20]}...")
        print(f"   CSRF Token: {csrf_token[:20]}...")
        return True
    else:
        print("\n❌ Environment variables not set yet.")
        print("   Please set GEMINI_SESSION_COOKIE and GEMINI_CSRF_TOKEN")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
