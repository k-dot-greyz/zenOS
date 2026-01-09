#!/usr/bin/env python3
"""zenOS AI Post Template Selector
Loads YAML templates and provides interactive selection with clipboard support
"""

import platform
import subprocess
import sys

import yaml


def load_templates(yaml_path="../ai_post_templates.yaml"):
    """Load templates from YAML file"""
    try:
        with open(yaml_path, "r") as f:
            return yaml.safe_load(f)["ai_post_templates"]
    except FileNotFoundError:
        print(f"❌ Template file '{yaml_path}' not found!")
        print("Make sure the YAML file is in the parent directory.")
        sys.exit(1)
    except KeyError:
        print("❌ Invalid YAML structure. Expected 'ai_post_templates' key.")
        sys.exit(1)


def copy_to_clipboard_cross_platform(text):
    """Copy text to clipboard using system-appropriate method"""
    system = platform.system().lower()

    try:
        if system == "darwin":  # macOS
            subprocess.run(["pbcopy"], input=text, text=True, check=True)
        elif system == "linux":
            # Try xclip first, then xsel
            try:
                subprocess.run(
                    ["xclip", "-selection", "clipboard"], input=text, text=True, check=True
                )
            except FileNotFoundError:
                subprocess.run(
                    ["xsel", "--clipboard", "--input"], input=text, text=True, check=True
                )
        elif system == "windows":
            subprocess.run(["clip"], input=text, text=True, check=True)
        else:
            print(f"⚠️  Unknown system: {system}")
            return False

        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"⚠️  Clipboard operation failed: {e}")
        return False


def present_choices(templates):
    """Display template choices and get user selection"""
    print("\n🎭 zenOS AI Post Template Selector")
    print("=" * 50)

    keys = list(templates.keys())
    for i, key in enumerate(keys):
        template = templates[key]
        print(f"{i+1}. {template['title']}")
        print(f"   📝 {template['vibe']}")
        print()

    while True:
        try:
            choice = input("Select template (1-3) or 'q' to quit: ").strip()
            if choice.lower() == "q":
                print("👋 Goodbye!")
                sys.exit(0)

            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(keys):
                return keys[choice_idx]
            else:
                print(f"❌ Please enter a number between 1 and {len(keys)}")
        except ValueError:
            print("❌ Please enter a valid number or 'q' to quit")


def preview_template(template_data):
    """Show template preview before copying"""
    print("\n" + "=" * 60)
    print(f"🎯 {template_data['title']} ({template_data['vibe']})")
    print("=" * 60)
    print(template_data["template"])
    print("=" * 60)


def main():
    """Main execution flow"""
    print("🚀 Loading zenOS AI Post Templates...")

    # Load templates
    templates = load_templates()

    while True:
        # Present choices
        selected_key = present_choices(templates)
        selected_template = templates[selected_key]

        # Preview template
        preview_template(selected_template)

        # Ask for confirmation
        confirm = input("\n📋 Copy to clipboard? (y/n/q): ").strip().lower()

        if confirm == "q":
            print("👋 Goodbye!")
            break
        elif confirm == "y":
            success = copy_to_clipboard_cross_platform(selected_template["template"])
            if success:
                print("✅ Template copied to clipboard!")
                print("🎉 Ready to paste and post!")
            else:
                print("📝 Manual copy required:")
                print("\nTemplate text:")
                print("-" * 40)
                print(selected_template["template"])
                print("-" * 40)

            another = input("\n🔄 Select another template? (y/n): ").strip().lower()
            if another != "y":
                break
        else:
            print("↩️  Returning to template selection...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
        sys.exit(0)
