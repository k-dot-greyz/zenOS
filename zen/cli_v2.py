#!/usr/bin/env python3
"""
zenOS CLI v2 - Enhanced CLI with Dex and Model Bench
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import click
import yaml

# Check if we're in AI mode
AI_MODE = os.environ.get("ZEN_AI_MODE", "false").lower() == "true"


@click.group(invoke_without_command=True)
@click.option("--ai-mode", is_flag=True, help="Enable AI-optimized output")
@click.option("--offline", is_flag=True, help="Use offline models only")
@click.option("--model", help="Specify model to use (see dex/models.yaml)")
@click.option("--eco", is_flag=True, help="Battery-saving mode for mobile")
@click.pass_context
def cli(ctx, ai_mode, offline, model, eco):
    """Configure zenOS operating modes and display the appropriate prompt when no command is selected."""

    # Set global modes
    if ai_mode:
        os.environ["ZEN_AI_MODE"] = "true"
    if offline:
        os.environ["ZEN_OFFLINE"] = "true"
    if eco:
        os.environ["ZEN_ECO_MODE"] = "true"
    if model:
        os.environ["ZEN_MODEL"] = model

    # If no command specified, show interactive menu
    if ctx.invoked_subcommand is None:
        if AI_MODE or ai_mode:
            print("zenOS AI Mode Active. Ready for instructions.")
            print("Available commands: chat, analyze, bench, arena, sync, dex")
        else:
            show_interactive_menu()


def show_interactive_menu():
    """
    Display the interactive menu of available zenOS commands and collaboration options.
    """
    print("""
╔══════════════════════════════════════╗
║         zenOS v2.0 🧘⚔️              ║
║   Where Humans and AIs Collaborate   ║
║        Now with Model Bench!        ║
╚══════════════════════════════════════╝

Quick Commands:
  zen chat              - Start conversation
  zen analyze <file>    - Analyze code
  zen doctor           - Check system health
  zen dex          - Explore models & procedures
  
Model Bench:
  zen bench <m1> <m2>  - Compare two models
  zen sync             - Update model stats from API
  zen arena            - View arena rankings
  
Collaboration:
  zen chat --copilot   - AI assists you
  zen delegate <task>  - AI takes over
  
For help: zen help
    """)


@cli.command()
@click.argument("model1")
@click.argument("model2")
@click.option("--tournament", "-t", multiple=True, help="Add more models for tournament")
def bench(model1, model2, tournament):
    """
    Compare AI models in a single battle or tournament and display the results.
    
    Parameters:
        model1 (str): Name of the first model.
        model2 (str): Name of the second model.
        tournament (tuple[str, ...]): Additional model names to include in tournament mode.
    """
    from zen.dex.bench import ModelBench

    arena = ModelBench()

    if tournament:
        # Tournament mode
        models = [model1, model2] + list(tournament)
        print(f"\n🏆 TOURNAMENT MODE: {len(models)} fighters!\n")
        print("Participants:")
        for m in models:
            print(f"  ⚔️ {m}")
        print()

        result = arena.tournament(models)

        if result.get("champion"):
            print(f"\n🥇 TOURNAMENT CHAMPION: {result['champion']['name']}!")
            print(f"🏆 Defeated {len(models)-1} opponents!")
    else:
        # Single battle
        result = arena.battle(model1, model2)

        if result.get("error"):
            print(f"❌ Error: {result['error']}")
        else:
            winner_emoji = "🥇" if result["winner_name"] != "Draw" else "🤝"
            print(f"\n{winner_emoji} Result: {result['winner_name']}")
            print(f"⏱️ Turns: {result['turns']}")
            print(
                f"💚 Final HP: {model1}: {result['fighter1_hp']} | {model2}: {result['fighter2_hp']}"
            )


@cli.command()
@click.option("--force", "-f", is_flag=True, help="Force sync even if cache is valid")
def sync(force):
    """
    Synchronize model data and rankings with the OpenRouter API.
    
    Parameters:
        force (bool): Whether to clear the existing synchronization cache before syncing.
    """
    from zen.dex.openrouter_sync import OpenRouterSync

    print("🔄 Syncing Dex with OpenRouter API...")
    print("This will fetch latest model stats and pricing...")

    syncer = OpenRouterSync()
    if force:
        print("💪 Force sync enabled - clearing cache...")
        if syncer.cache_file.exists():
            syncer.cache_file.unlink()

    # Run async sync
    asyncio.run(syncer.sync_dex())

    print("\n✨ Sync complete!")
    print("📊 Check dex/models.yaml for updated stats")
    print("🏆 Check dex/bench_rankings.yaml for power rankings")


@cli.command()
def arena():
    """Display the top Model Bench rankings and fighter counts by weight class."""
    arena_file = Path("dex/bench_rankings.yaml")

    if not arena_file.exists():
        print("⚠️ No arena rankings found. Run 'zen sync' first!")
        return

    with open(arena_file) as f:
        data = yaml.safe_load(f)

    print("\n🏆 MODEL BENCH POWER RANKINGS 🏆\n")
    print("Top 10 Fighters by Total Power:")
    print("=" * 50)

    for entry in data["power_rankings"][:10]:
        rank_emoji = {1: "🥇", 2: "🥈", 3: "🥉"}.get(entry["rank"], "🎖️")
        tier_emoji = {
            "legendary": "🔴",
            "epic": "🟡",
            "rare": "🟣",
            "uncommon": "🔵",
            "common": "⚪",
        }.get(entry["tier"], "⚫")

        print(f"{rank_emoji} #{entry['rank']}: {entry['name']} {tier_emoji}")
        print(
            f"   Total Power: {entry['total_power']} | HP: {entry['bench_stats']['hp']} | ATK: {entry['bench_stats']['attack']}"
        )

    print("\n⚔️ Weight Classes:")
    print(f"Heavyweight: {len(data['weight_classes']['heavyweight'])} fighters")
    print(f"Middleweight: {len(data['weight_classes']['middleweight'])} fighters")
    print(f"Lightweight: {len(data['weight_classes']['lightweight'])} fighters")


@cli.command()
@click.argument("category", default="models")
@click.option("--task", help="Find best model for specific task")
@click.option("--tier", help="Filter by tier")
def dex(category, task, tier):
    """
    Explore the model or procedure Dex and display information filtered by category and optional criteria.
    
    Parameters:
        category (str): Dex category to display, such as ``"models"`` or ``"procedures"``.
        task (str): Task category used to show model recommendations.
        tier (str): Model tier used to filter displayed models.
    """

    if category == "models":
        models_file = Path("dex/models.yaml")
        if not models_file.exists():
            print("❌ Models Dex not found. Run 'zen sync' to create it!")
            return

        with open(models_file) as f:
            data = yaml.safe_load(f)

        if task:
            # Find best model for task
            guide = data.get("selection_guide", {}).get("by_task", {})
            if task in guide:
                print(f"\n🎯 Best models for '{task}':\n")
                print("⭐ Recommended:")
                for model in guide[task].get("recommended", []):
                    print(f"   - {model}")
                print("\n💰 Budget options:")
                for model in guide[task].get("budget", []):
                    print(f"   - {model}")
            else:
                print(f"No specific recommendations for '{task}'")
                print("\nAvailable task categories:")
                for t in guide.keys():
                    print(f"  - {t}")

        elif tier:
            # Filter by tier
            print(f"\n🎮 {tier.upper()} Models:\n")
            count = 0
            for model in data.get("models", []):
                if model.get("tier") == tier:
                    count += 1
                    print(f"• {model['name']} ({model['id']})")
                    if "bench_stats" in model:
                        total_power = sum(model["bench_stats"].values())
                        print(
                            f"  Power: {total_power} | Cost: ${model['cost_per_1k']['input']:.4f}/1k"
                        )

            if count == 0:
                print(f"No {tier} models found")

        else:
            # Show summary
            print("\n📊 Dex Statistics:\n")

            if "total_models" in data:
                print(f"Total Models: {data['total_models']}")

            if "sync_stats" in data:
                print(f"Last Sync: {data.get('last_updated', 'Unknown')}")
                print(f"New Models: {data['sync_stats']['new_models']}")
                print(f"Updated: {data['sync_stats']['updated_models']}")

            # Count by rarity
            tier_counts = {}
            for model in data.get("models", []):
                r = model.get("tier", "unknown")
                tier_counts[r] = tier_counts.get(r, 0) + 1

            print("\n🎲 Tier Distribution:")
            for r, emoji in [
                ("legendary", "🔴"),
                ("epic", "🟡"),
                ("rare", "🟣"),
                ("uncommon", "🔵"),
                ("common", "⚪"),
            ]:
                if r in tier_counts:
                    print(f"  {emoji} {r.capitalize()}: {tier_counts[r]}")

            print("\n💡 Tips:")
            print("  • Use 'zen dex models --task <task>' to find best models")
            print("  • Use 'zen dex models --tier legendary' to see top tier")
            print("  • Use 'zen bench <model1> <model2>' to compare models")
            print("  • Use 'zen sync' to update with latest models")

    elif category == "procedures":
        procedures_file = Path("dex/procedures.yaml")
        if not procedures_file.exists():
            print("❌ Procedures Dex not found")
            return

        with open(procedures_file) as f:
            data = yaml.safe_load(f)

        print("\n📜 Discovered Procedures:\n")
        for proc in data.get("procedures", []):
            tier_emoji = {
                "common": "⚪",
                "uncommon": "🔵",
                "rare": "🟣",
                "epic": "🟡",
                "legendary": "🔴",
            }.get(proc["tier"], "⚫")

            print(f"{tier_emoji} {proc['name']} ({proc['id']})")
            print(f"   Type: {proc['type']} | Complexity: {proc['stats']['complexity']}")
            if proc.get("usage_count", 0) > 0:
                print(f"   Used: {proc['usage_count']} times")


@cli.command()
@click.option("--ai-mode", is_flag=True, help="Check AI integration")
def doctor(ai_mode):
    """Check zenOS configuration and data files, then report system readiness.
    
    Parameters:
        ai_mode (bool): Whether AI mode is enabled for this diagnostic run.
    """

    print("\n🏥 zenOS System Diagnostics\n")

    checks = []

    # Check environment
    if Path(".env").exists():
        checks.append(("✅", "Environment file found"))
    else:
        checks.append(("❌", "Environment file missing (copy env.example to .env)"))

    # Check API key
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if api_key and api_key != "your-api-key-here":
        checks.append(("✅", "OpenRouter API key configured"))
    else:
        checks.append(("⚠️", "OpenRouter API key not configured"))

    # Check Dex
    if Path("dex/models.yaml").exists():
        with open("dex/models.yaml") as f:
            data = yaml.safe_load(f)
            model_count = len(data.get("models", []))
        checks.append(("✅", f"Model Dex loaded ({model_count} models)"))
    else:
        checks.append(("⚠️", "Model Dex not found (run 'zen sync')"))

    if Path("dex/procedures.yaml").exists():
        checks.append(("✅", "Procedure Dex available"))
    else:
        checks.append(("⚠️", "Procedure Dex missing"))

    # Check Arena
    if Path("dex/bench_rankings.yaml").exists():
        checks.append(("✅", "Model Bench rankings available"))
    else:
        checks.append(("ℹ️", "No arena rankings (run 'zen sync' to generate)"))

    # AI mode checks
    if ai_mode or AI_MODE:
        checks.append(("✅", "AI mode enabled"))

        if Path("AI_INSTRUCTIONS.md").exists():
            checks.append(("✅", "AI instructions accessible"))
        else:
            checks.append(("❌", "AI instructions missing"))

    # Display results
    all_good = True
    for status, message in checks:
        print(f"{status} {message}")
        if status == "❌":
            all_good = False

    print()
    if all_good:
        print("✨ All systems operational! Ready for battle! ⚔️")
    else:
        print("⚠️ Some issues need attention")

    # Show quick tips
    print("\n💡 Quick Tips:")
    print("  • Run 'zen sync' to update model stats from OpenRouter")
    print("  • Try 'zen bench gpt-4-turbo claude-3-opus' to compare models")
    print("  • Use 'zen dex models --tier legendary' to see top models")


@cli.command()
def help():
    """❓ Show detailed help"""
    print("""
zenOS v2.0 Help System
======================

🎮 Model Bench Commands:
  zen bench <model1> <model2>       - 1v1 model compare
  zen bench <m1> <m2> -t <m3> <m4>  - Tournament mode
  zen sync                          - Update models from OpenRouter API
  zen sync --force                  - Force update (ignore cache)
  zen arena                         - View power rankings

📖 Dex Commands:
  zen dex                       - Show Dex stats
  zen dex models --task <task>  - Find best model for task
  zen dex models --tier <r>   - Filter by tier
  zen dex procedures            - List discovered procedures

🤖 AI Integration:
  zen --ai-mode                     - Enable AI-optimized output
  zen doctor --ai-mode              - Verify AI integration

💬 Basic Commands:
  zen chat                          - Start conversation
  zen analyze <file>                - Analyze code
  zen doctor                        - System health check

🎯 Task Categories:
  - complex_architecture            - System design
  - quick_coding                    - Fast implementation
  - code_review                     - Code analysis
  - bulk_refactoring               - Large-scale changes
  - offline_mobile                 - Mobile/offline use
  - creative_writing               - Content generation

🎲 Model Rarities:
  🔴 Legendary - Top tier (Claude-3-Opus, GPT-4)
  🟡 Epic - High-end (GPT-4-Turbo, Claude-3-Sonnet)
  🟣 Rare - Good mid-tier
  🔵 Uncommon - Budget friendly
  ⚪ Common - Free/cheap options

⚔️ Bench Mechanics:
  - Models fight using their stats (HP, Attack, Defense, Speed)
  - Special abilities based on model features
  - Tier affects power multipliers
  - Tournament mode for multiple fighters

For more: https://github.com/k-dot-greyz/zenOS
    """)


if __name__ == "__main__":
    cli()
