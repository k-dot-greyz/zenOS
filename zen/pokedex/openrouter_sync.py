"""
OpenRouter API Integration for Dynamic Pokédex Stats
Pulls real model data and combines with subjective ratings
"""

import os
import json
import yaml
import httpx
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

@dataclass
class ModelAPIStats:
    """Real stats from OpenRouter API"""
    id: str
    name: str
    pricing: Dict[str, float]  # per token costs
    context_length: int
    top_provider: Dict[str, Any]
    architecture: Dict[str, Any]
    per_request_limits: Optional[Dict[str, Any]] = None
    
@dataclass
class ModelCombatStats:
    """Calculated combat stats for battle arena"""
    hp: int  # Based on context length
    attack: int  # Based on intelligence/capability
    defense: int  # Based on reliability
    speed: int  # Based on tokens/sec
    special: int  # Based on unique features
    cost: int  # Inverse of pricing (cheaper = higher stat)
    
    @classmethod
    def calculate(cls, api_stats: ModelAPIStats, subjective: Dict) -> 'ModelCombatStats':
        """Calculate combat stats from API and subjective data"""
        # HP based on context (more context = more HP)
        context_ratio = min(api_stats.context_length / 200000, 1.0)  # Max at 200k
        hp = int(50 + (context_ratio * 50))
        
        # Attack based on subjective intelligence
        attack = subjective.get('intelligence', 70)
        
        # Defense based on subjective reliability
        defense = subjective.get('reliability', 75)
        
        # Speed from API or subjective
        speed = subjective.get('speed', 80)
        
        # Special based on unique abilities count
        special = len(subjective.get('abilities', [])) * 10
        
        # Cost stat (inverse - cheaper is better for this stat)
        prompt_cost = api_stats.pricing.get('prompt', 0.001)
        if prompt_cost > 0:
            cost = int(100 - min(prompt_cost * 1000, 95))  # Cheaper = higher stat
        else:
            cost = 100  # Free models get max cost stat
            
        return cls(hp=hp, attack=attack, defense=defense, 
                  speed=speed, special=special, cost=cost)

class OpenRouterSync:
    """Syncs Pokédex with OpenRouter API data"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get('OPENROUTER_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1"
        self.pokedex_path = Path("pokedex")
        self.cache_file = self.pokedex_path / ".api_cache.json"
        self.cache_duration = timedelta(hours=6)  # Cache for 6 hours
        
    async def fetch_models(self) -> List[Dict]:
        """Fetch current model list from OpenRouter"""
        # Check cache first
        if self._is_cache_valid():
            return self._load_cache()
        
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://github.com/kasparsgreizis/zenOS",
                "X-Title": "zenOS Pokédex"
            }
            
            try:
                # Get available models
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()
                
                # Cache the response
                self._save_cache(data['data'])
                return data['data']
                
            except Exception as e:
                print(f"⚠️ Error fetching from OpenRouter: {e}")
                # Try to use cache even if expired
                if self.cache_file.exists():
                    return self._load_cache()
                return []
    
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid"""
        if not self.cache_file.exists():
            return False
        
        cache_time = datetime.fromtimestamp(self.cache_file.stat().st_mtime)
        return datetime.now() - cache_time < self.cache_duration
    
    def _load_cache(self) -> List[Dict]:
        """Load cached API data"""
        with open(self.cache_file) as f:
            return json.load(f)
    
    def _save_cache(self, data: List[Dict]):
        """Save API data to cache"""
        self.pokedex_path.mkdir(exist_ok=True)
        with open(self.cache_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def calculate_subjective_stats(self, model_id: str, api_data: Dict) -> Dict:
        """Calculate subjective stats based on model characteristics"""
        stats = {
            'intelligence': 70,  # Base stat
            'creativity': 70,
            'speed': 70,
            'memory': 70,
            'reliability': 75
        }
        
        # Adjust based on model family
        if 'gpt-4' in model_id.lower():
            stats['intelligence'] = 92
            stats['creativity'] = 88
        elif 'claude-3-opus' in model_id.lower():
            stats['intelligence'] = 95
            stats['creativity'] = 93
        elif 'claude-3' in model_id.lower():
            stats['intelligence'] = 85
            stats['creativity'] = 82
        elif 'gemini' in model_id.lower():
            stats['intelligence'] = 88
            stats['creativity'] = 85
        elif 'mixtral' in model_id.lower():
            stats['intelligence'] = 86
            stats['creativity'] = 83
        elif 'llama' in model_id.lower():
            stats['intelligence'] = 85
            stats['creativity'] = 82
        
        # Adjust memory based on context length
        context = api_data.get('context_length', 4096)
        if context >= 200000:
            stats['memory'] = 95
        elif context >= 100000:
            stats['memory'] = 85
        elif context >= 32000:
            stats['memory'] = 75
        elif context >= 16000:
            stats['memory'] = 65
        else:
            stats['memory'] = 50
            
        # Speed adjustments
        if 'turbo' in model_id.lower() or 'haiku' in model_id.lower():
            stats['speed'] = 90
        elif 'opus' in model_id.lower():
            stats['speed'] = 70
            
        return stats
    
    def determine_rarity(self, model_id: str, pricing: Dict) -> str:
        """Determine model rarity based on capabilities and cost"""
        prompt_cost = pricing.get('prompt', 0)
        
        # Legendary: Top tier, expensive models
        if 'opus' in model_id.lower() or ('gpt-4' in model_id.lower() and 'turbo' not in model_id.lower()):
            return 'legendary'
        
        # Epic: High-end models
        if 'gpt-4-turbo' in model_id.lower() or 'claude-3-sonnet' in model_id.lower():
            return 'epic'
        
        # Rare: Good mid-tier models
        if prompt_cost > 0.001 and prompt_cost < 0.01:
            return 'rare'
        
        # Uncommon: Decent budget models
        if prompt_cost > 0.0001 and prompt_cost <= 0.001:
            return 'uncommon'
        
        # Common: Free or very cheap
        return 'common'
    
    def determine_abilities(self, model_id: str, api_data: Dict) -> List[str]:
        """Determine model abilities based on characteristics"""
        abilities = []
        
        # Check for vision/multimodal
        if api_data.get('architecture', {}).get('modality') == 'multimodal':
            abilities.append("Vision Understanding")
        
        # Check for specific model abilities
        if 'gpt-4' in model_id.lower():
            abilities.extend(["Code Generation", "Complex Reasoning", "Function Calling"])
        elif 'claude' in model_id.lower():
            abilities.extend(["Deep Analysis", "Nuanced Understanding", "XML Processing"])
        elif 'gemini' in model_id.lower():
            abilities.extend(["Multimodal Understanding", "Fast Processing"])
        elif 'llama' in model_id.lower():
            abilities.extend(["Open Source", "Customizable"])
        elif 'code' in model_id.lower():
            abilities.extend(["Code Completion", "Bug Detection"])
            
        # Context-based abilities
        if api_data.get('context_length', 0) >= 100000:
            abilities.append("Massive Context")
        elif api_data.get('context_length', 0) >= 32000:
            abilities.append("Large Context")
            
        return abilities
    
    async def sync_pokedex(self):
        """Sync Pokédex with latest API data"""
        print("🔄 Syncing Pokédex with OpenRouter API...")
        
        # Fetch latest models
        api_models = await self.fetch_models()
        
        if not api_models:
            print("⚠️ No models fetched from API")
            return
        
        # Load existing Pokédex
        pokedex_file = self.pokedex_path / "models.yaml"
        if pokedex_file.exists():
            with open(pokedex_file) as f:
                pokedex_data = yaml.safe_load(f)
        else:
            pokedex_data = {
                'version': '2.0.0',
                'last_updated': datetime.now().isoformat(),
                'models': []
            }
        
        # Create lookup for existing models
        existing_models = {m['id']: m for m in pokedex_data.get('models', [])}
        
        # Process API models
        updated_models = []
        new_count = 0
        updated_count = 0
        
        for api_model in api_models:
            model_id = api_model['id']
            
            # Calculate stats
            subjective_stats = self.calculate_subjective_stats(model_id, api_model)
            
            # Build model entry
            model_entry = {
                'id': model_id,
                'name': api_model.get('name', model_id),
                'provider': model_id.split('/')[0] if '/' in model_id else 'unknown',
                'type': 'multimodal' if api_model.get('architecture', {}).get('modality') == 'multimodal' else 'text',
                'rarity': self.determine_rarity(model_id, api_model.get('pricing', {})),
                'stats': subjective_stats,
                'abilities': self.determine_abilities(model_id, api_model),
                'context_window': api_model.get('context_length', 4096),
                'cost_per_1k': {
                    'input': api_model.get('pricing', {}).get('prompt', 0) * 1000,
                    'output': api_model.get('pricing', {}).get('completion', 0) * 1000
                },
                'api_data': {
                    'top_provider': api_model.get('top_provider'),
                    'per_request_limits': api_model.get('per_request_limits')
                },
                'last_synced': datetime.now().isoformat()
            }
            
            # Calculate combat stats
            combat_stats = ModelCombatStats.calculate(
                ModelAPIStats(
                    id=model_id,
                    name=model_entry['name'],
                    pricing=api_model.get('pricing', {}),
                    context_length=model_entry['context_window'],
                    top_provider=api_model.get('top_provider'),
                    architecture=api_model.get('architecture', {})
                ),
                subjective_stats
            )
            model_entry['combat_stats'] = asdict(combat_stats)
            
            # Check if this is an update or new model
            if model_id in existing_models:
                # Preserve any manual overrides
                existing = existing_models[model_id]
                if 'notes' in existing:
                    model_entry['notes'] = existing['notes']
                if 'best_for' in existing:
                    model_entry['best_for'] = existing['best_for']
                if 'discovered_by' in existing:
                    model_entry['discovered_by'] = existing['discovered_by']
                    model_entry['discovery_date'] = existing.get('discovery_date')
                updated_count += 1
            else:
                model_entry['discovered_by'] = 'ai:openrouter-sync'
                model_entry['discovery_date'] = datetime.now().isoformat()
                new_count += 1
            
            updated_models.append(model_entry)
        
        # Update Pokédex data
        pokedex_data['models'] = updated_models
        pokedex_data['last_updated'] = datetime.now().isoformat()
        pokedex_data['total_models'] = len(updated_models)
        pokedex_data['sync_stats'] = {
            'new_models': new_count,
            'updated_models': updated_count,
            'total_synced': len(api_models)
        }
        
        # Save updated Pokédex
        with open(pokedex_file, 'w') as f:
            yaml.dump(pokedex_data, f, default_flow_style=False, sort_keys=False)
        
        print(f"✅ Pokédex synced! New: {new_count}, Updated: {updated_count}, Total: {len(updated_models)}")
        
        # Generate battle arena rankings
        await self.generate_arena_rankings(updated_models)
    
    async def generate_arena_rankings(self, models: List[Dict]):
        """Generate battle arena power rankings"""
        print("⚔️ Generating Battle Arena Rankings...")
        
        # Sort by total combat power
        ranked_models = sorted(models, 
                              key=lambda m: sum(m['combat_stats'].values()), 
                              reverse=True)
        
        # Create arena file
        arena_data = {
            'version': '1.0.0',
            'last_updated': datetime.now().isoformat(),
            'power_rankings': [],
            'weight_classes': {
                'heavyweight': [],  # Legendary & Epic
                'middleweight': [],  # Rare
                'lightweight': [],   # Uncommon & Common
            }
        }
        
        for i, model in enumerate(ranked_models[:20], 1):  # Top 20
            total_power = sum(model['combat_stats'].values())
            entry = {
                'rank': i,
                'id': model['id'],
                'name': model['name'],
                'rarity': model['rarity'],
                'total_power': total_power,
                'combat_stats': model['combat_stats']
            }
            arena_data['power_rankings'].append(entry)
            
            # Assign to weight class
            if model['rarity'] in ['legendary', 'epic']:
                arena_data['weight_classes']['heavyweight'].append(model['id'])
            elif model['rarity'] == 'rare':
                arena_data['weight_classes']['middleweight'].append(model['id'])
            else:
                arena_data['weight_classes']['lightweight'].append(model['id'])
        
        # Save arena rankings
        arena_file = self.pokedex_path / "arena_rankings.yaml"
        with open(arena_file, 'w') as f:
            yaml.dump(arena_data, f, default_flow_style=False, sort_keys=False)
        
        print(f"🏆 Arena rankings generated! Top model: {ranked_models[0]['name']}")

# CLI interface
async def main():
    """Run the sync from command line"""
    syncer = OpenRouterSync()
    await syncer.sync_pokedex()

if __name__ == "__main__":
    asyncio.run(main())
