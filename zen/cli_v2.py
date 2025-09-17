#!/usr/bin/env python3
"""
zenOS CLI v2 - Enhanced CLI with Pokédex and Battle Arena
"""

import os
import sys
import json
import yaml
import click
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any

# Check if we're in AI mode
AI_MODE = os.environ.get('ZEN_AI_MODE', 'false').lower() == 'true'

@click.group(invoke_without_command=True)
@click.option('--ai-mode', is_flag=True, help='Enable AI-optimized output')
@click.option('--offline', is_flag=True, help='Use offline models only')
@click.option('--model', help='Specify model to use (see pokedex/models.yaml)')
@click.option('--eco', is_flag=True, help='Battery-saving mode for mobile')
@click.pass_context
def cli(ctx, ai_mode, offline, model, eco):
    """zenOS - Where Humans and AIs Collaborate"""
    
    # Set global modes
    if ai_mode:
        os.environ['ZEN_AI_MODE'] = 'true'
    if offline:
        os.environ['ZEN_OFFLINE'] = 'true'
    if eco:
        os.environ['ZEN_ECO_MODE'] = 'true'
    if model:
        os.environ['ZEN_MODEL'] = model
    
    # If no command specified, show interactive menu
    if ctx.invoked_subcommand is None:
        if AI_MODE or ai_mode:
            print("zenOS AI Mode Active. Ready for instructions.")
            print("Available commands: chat, analyze, battle, sync, pokedex")
        else:
            show_interactive_menu()

def show_interactive_menu():
    """Show the interactive menu for humans"""
    print("""
╔══════════════════════════════════════╗
║         zenOS v2.0 🧘⚔️              ║
║   Where Humans and AIs Collaborate   ║
║        Now with Battle Arena!        ║
╚══════════════════════════════════════╝

Quick Commands:
  zen chat              - Start conversation
  zen analyze <file>    - Analyze code
  zen doctor           - Check system health
  zen pokedex          - Explore models & procedures
  
Battle Arena:
  zen battle <m1> <m2>  - Battle two models
  zen sync             - Update model stats from API
  zen arena            - View arena rankings
  
Collaboration:
  zen chat --copilot   - AI assists you
  zen delegate <task>  - AI takes over
  
For help: zen help
    """)

@cli.command()
@click.argument('model1')
@click.argument('model2')
@click.option('--tournament', '-t', multiple=True, help='Add more models for tournament')
def battle(model1, model2, tournament):
    """⚔️ Battle AI models in the arena!"""
    from zen.pokedex.battle_arena import BattleArena
    
    arena = BattleArena()
    
    if tournament:
        # Tournament mode
        models = [model1, model2] + list(tournament)
        print(f"\n🏆 TOURNAMENT MODE: {len(models)} fighters!\n")
        print("Participants:")
        for m in models:
            print(f"  ⚔️ {m}")
        print()
        
        result = arena.tournament(models)
        
        if result.get('champion'):
            print(f"\n🥇 TOURNAMENT CHAMPION: {result['champion']['name']}!")
            print(f"🏆 Defeated {len(models)-1} opponents!")
    else:
        # Single battle
        result = arena.battle(model1, model2)
        
        if result.get('error'):
            print(f"❌ Error: {result['error']}")
        else:
            winner_emoji = "🥇" if result['winner_name'] != "Draw" else "🤝"
            print(f"\n{winner_emoji} Result: {result['winner_name']}")
            print(f"⏱️ Turns: {result['turns']}")
            print(f"💚 Final HP: {model1}: {result['fighter1_hp']} | {model2}: {result['fighter2_hp']}")

@cli.command()
@click.option('--force', '-f', is_flag=True, help='Force sync even if cache is valid')
def sync(force):
    """🔄 Sync Pokédex with OpenRouter API"""
    from zen.pokedex.openrouter_sync import OpenRouterSync
    
    print("🔄 Syncing Pokédex with OpenRouter API...")
    print("This will fetch latest model stats and pricing...")
    
    syncer = OpenRouterSync()
    if force:
        print("💪 Force sync enabled - clearing cache...")
        if syncer.cache_file.exists():
            syncer.cache_file.unlink()
    
    # Run async sync
    asyncio.run(syncer.sync_pokedex())
    
    print("\n✨ Sync complete!")
    print("📊 Check pokedex/models.yaml for updated stats")
    print("🏆 Check pokedex/arena_rankings.yaml for power rankings")

@cli.command()
def arena():
    """🏆 View Battle Arena rankings"""
    arena_file = Path("pokedex/arena_rankings.yaml")
    
    if not arena_file.exists():
        print("⚠️ No arena rankings found. Run 'zen sync' first!")
        return
    
    with open(arena_file) as f:
        data = yaml.safe_load(f)
    
    print("\n🏆 BATTLE ARENA POWER RANKINGS 🏆\n")
    print("Top 10 Fighters by Total Power:")
    print("=" * 50)
    
    for entry in data['power_rankings'][:10]:
        rank_emoji = {1: "🥇", 2: "🥈", 3: "🥉"}.get(entry['rank'], "🎖️")
        rarity_emoji = {
            'legendary': '🔴',
            'epic': '🟡',
            'rare': '🟣',
            'uncommon': '🔵',
            'common': '⚪'
        }.get(entry['rarity'], '⚫')
        
        print(f"{rank_emoji} #{entry['rank']}: {entry['name']} {rarity_emoji}")
        print(f"   Total Power: {entry['total_power']} | HP: {entry['combat_stats']['hp']} | ATK: {entry['combat_stats']['attack']}")
    
    print("\n⚔️ Weight Classes:")
    print(f"Heavyweight: {len(data['weight_classes']['heavyweight'])} fighters")
    print(f"Middleweight: {len(data['weight_classes']['middleweight'])} fighters")
    print(f"Lightweight: {len(data['weight_classes']['lightweight'])} fighters")

@cli.command()
@click.argument('category', default='models')
@click.option('--task', help='Find best model for specific task')
@click.option('--rarity', help='Filter by rarity')
def pokedex(category, task, rarity):
    """📖 Explore the Model & Procedure Pokédex"""
    
    if category == 'models':
        models_file = Path('pokedex/models.yaml')
        if not models_file.exists():
            print("❌ Models Pokédex not found. Run 'zen sync' to create it!")
            return
        
        with open(models_file) as f:
            data = yaml.safe_load(f)
        
        if task:
            # Find best model for task
            guide = data.get('selection_guide', {}).get('by_task', {})
            if task in guide:
                print(f"\n🎯 Best models for '{task}':\n")
                print("⭐ Recommended:")
                for model in guide[task].get('recommended', []):
                    print(f"   - {model}")
                print("\n💰 Budget options:")
                for model in guide[task].get('budget', []):
                    print(f"   - {model}")
            else:
                print(f"No specific recommendations for '{task}'")
                print("\nAvailable task categories:")
                for t in guide.keys():
                    print(f"  - {t}")
        
        elif rarity:
            # Filter by rarity
            print(f"\n🎮 {rarity.upper()} Models:\n")
            count = 0
            for model in data.get('models', []):
                if model.get('rarity') == rarity:
                    count += 1
                    print(f"• {model['name']} ({model['id']})")
                    if 'combat_stats' in model:
                        total_power = sum(model['combat_stats'].values())
                        print(f"  Power: {total_power} | Cost: ${model['cost_per_1k']['input']:.4f}/1k")
            
            if count == 0:
                print(f"No {rarity} models found")
        
        else:
            # Show summary
            print("\n📊 Pokédex Statistics:\n")
            
            if 'total_models' in data:
                print(f"Total Models: {data['total_models']}")
            
            if 'sync_stats' in data:
                print(f"Last Sync: {data.get('last_updated', 'Unknown')}")
                print(f"New Models: {data['sync_stats']['new_models']}")
                print(f"Updated: {data['sync_stats']['updated_models']}")
            
            # Count by rarity
            rarity_counts = {}
            for model in data.get('models', []):
                r = model.get('rarity', 'unknown')
                rarity_counts[r] = rarity_counts.get(r, 0) + 1
            
            print("\n🎲 Rarity Distribution:")
            for r, emoji in [('legendary', '🔴'), ('epic', '🟡'), ('rare', '🟣'), 
                            ('uncommon', '🔵'), ('common', '⚪')]:
                if r in rarity_counts:
                    print(f"  {emoji} {r.capitalize()}: {rarity_counts[r]}")
            
            print("\n💡 Tips:")
            print("  • Use 'zen pokedex models --task <task>' to find best models")
            print("  • Use 'zen pokedex models --rarity legendary' to see top tier")
            print("  • Use 'zen battle <model1> <model2>' to test in combat")
            print("  • Use 'zen sync' to update with latest models")
    
    elif category == 'procedures':
        procedures_file = Path('pokedex/procedures.yaml')
        if not procedures_file.exists():
            print("❌ Procedures Pokédex not found")
            return
        
        with open(procedures_file) as f:
            data = yaml.safe_load(f)
        
        print("\n📜 Discovered Procedures:\n")
        for proc in data.get('procedures', []):
            rarity_emoji = {
                'common': '⚪',
                'uncommon': '🔵',
                'rare': '🟣',
                'epic': '🟡',
                'legendary': '🔴'
            }.get(proc['rarity'], '⚫')
            
            print(f"{rarity_emoji} {proc['name']} ({proc['id']})")
            print(f"   Type: {proc['type']} | Complexity: {proc['stats']['complexity']}")
            if proc.get('usage_count', 0) > 0:
                print(f"   Used: {proc['usage_count']} times")

@cli.command()
@click.option('--ai-mode', is_flag=True, help='Check AI integration')
def doctor(ai_mode):
    """🏥 Check zenOS system health"""
    
    print("\n🏥 zenOS System Diagnostics\n")
    
    checks = []
    
    # Check environment
    if Path('.env').exists():
        checks.append(("✅", "Environment file found"))
    else:
        checks.append(("❌", "Environment file missing (copy env.example to .env)"))
    
    # Check API key
    api_key = os.environ.get('OPENROUTER_API_KEY', '')
    if api_key and api_key != 'your-api-key-here':
        checks.append(("✅", "OpenRouter API key configured"))
    else:
        checks.append(("⚠️", "OpenRouter API key not configured"))
    
    # Check Pokédex
    if Path('pokedex/models.yaml').exists():
        with open('pokedex/models.yaml') as f:
            data = yaml.safe_load(f)
            model_count = len(data.get('models', []))
        checks.append(("✅", f"Model Pokédex loaded ({model_count} models)"))
    else:
        checks.append(("⚠️", "Model Pokédex not found (run 'zen sync')"))
    
    if Path('pokedex/procedures.yaml').exists():
        checks.append(("✅", "Procedure Pokédex available"))
    else:
        checks.append(("⚠️", "Procedure Pokédex missing"))
    
    # Check Arena
    if Path('pokedex/arena_rankings.yaml').exists():
        checks.append(("✅", "Battle Arena rankings available"))
    else:
        checks.append(("ℹ️", "No arena rankings (run 'zen sync' to generate)"))
    
    # AI mode checks
    if ai_mode or AI_MODE:
        checks.append(("✅", "AI mode enabled"))
        
        if Path('AI_INSTRUCTIONS.md').exists():
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
    print("  • Try 'zen battle gpt-4-turbo claude-3-opus' for an epic fight")
    print("  • Use 'zen pokedex models --rarity legendary' to see top models")

@cli.command()
def help():
    """❓ Show detailed help"""
    print("""
zenOS v2.0 Help System
======================

🎮 Battle Arena Commands:
  zen battle <model1> <model2>      - 1v1 model battle
  zen battle <m1> <m2> -t <m3> <m4> - Tournament mode
  zen sync                          - Update models from OpenRouter API
  zen sync --force                  - Force update (ignore cache)
  zen arena                         - View power rankings

📖 Pokédex Commands:
  zen pokedex                       - Show Pokédex stats
  zen pokedex models --task <task>  - Find best model for task
  zen pokedex models --rarity <r>   - Filter by rarity
  zen pokedex procedures            - List discovered procedures

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

⚔️ Battle Mechanics:
  - Models fight using their stats (HP, Attack, Defense, Speed)
  - Special abilities based on model features
  - Rarity affects power multipliers
  - Tournament mode for multiple fighters

For more: https://github.com/kasparsgreizis/zenOS
    """)

if __name__ == '__main__':
    cli()
