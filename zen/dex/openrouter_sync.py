"""
OpenRouter API Integration for Dynamic Dex Stats
Pulls real model data and combines with subjective ratings
"""

import asyncio
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
import yaml


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
class ModelBenchStats:
    """Calculated combat stats for model bench"""

    hp: int  # Based on context length
    attack: int  # Based on intelligence/capability
    defense: int  # Based on reliability
    speed: int  # Based on tokens/sec
    special: int  # Based on unique features
    cost: int  # Inverse of pricing (cheaper = higher stat)

    @classmethod
    def calculate(cls, api_stats: ModelAPIStats, subjective: Dict) -> "ModelBenchStats":
        """
        Calculate combat-style benchmark statistics from API metadata and subjective ratings.
        
        Parameters:
        	api_stats (ModelAPIStats): Model metadata, pricing, and context length used for the calculations.
        	subjective (Dict): Subjective ratings and feature data used to derive combat statistics.
        
        Returns:
        	ModelBenchStats: Calculated health, attack, defense, speed, special, and cost statistics.
        """
        # HP based on context (more context = more HP)
        context_ratio = min(api_stats.context_length / 200000, 1.0)  # Max at 200k
        hp = int(50 + (context_ratio * 50))

        # Attack based on subjective intelligence
        attack = subjective.get("intelligence", 70)

        # Defense based on subjective reliability
        defense = subjective.get("reliability", 75)

        # Speed from API or subjective
        speed = subjective.get("speed", 80)

        # Special based on unique abilities count
        special = len(subjective.get("feats", subjective.get("capabilities", []))) * 10

        # Cost stat (inverse - cheaper is better for this stat)
        prompt_cost = api_stats.pricing.get("prompt", 0.001)
        if prompt_cost > 0:
            cost = int(100 - min(prompt_cost * 1000, 95))  # Cheaper = higher stat
        else:
            cost = 100  # Free models get max cost stat

        return cls(hp=hp, attack=attack, defense=defense, speed=speed, special=special, cost=cost)


class OpenRouterSync:
    """Syncs Dex with OpenRouter API data"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"
        self.dex_path = Path("dex")
        self.cache_file = self.dex_path / ".api_cache.json"
        self.cache_duration = timedelta(hours=6)  # Cache for 6 hours

    async def fetch_models(self) -> List[Dict]:
        """
        Retrieve the current model list from the OpenRouter API and cache the result locally.

        If a valid local cache exists, it is returned instead of making a network request. On successful fetch the response is saved to the cache. If the HTTP request fails, the method attempts to return an existing cache (even if expired); if no cache is available, it returns an empty list.

        Returns:
            models (List[Dict]): A list of model metadata dictionaries from OpenRouter, or an empty list if fetching fails and no cache is available.
        """
        # Check cache first
        if self._is_cache_valid():
            return self._load_cache()

        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://github.com/k-dot-greyz/zenOS",
                "X-Title": "zenOS Dex",
            }

            try:
                # Get available models
                response = await client.get(f"{self.base_url}/models", headers=headers)
                response.raise_for_status()
                data = response.json()

                # Cache the response
                self._save_cache(data["data"])
                return data["data"]

            except Exception as e:
                print(f"⚠️ Error fetching from OpenRouter: {e}")
                # Try to use cache even if expired
                if self.cache_file.exists():
                    return self._load_cache()
                return []

    def _is_cache_valid(self) -> bool:
        """Determine whether the cached model data is within its configured validity period.
        
        Returns:
        	bool: `True` if the cache file exists and is current, `False` otherwise.
        """
        if not self.cache_file.exists():
            return False

        cache_time = datetime.fromtimestamp(self.cache_file.stat().st_mtime)
        return datetime.now() - cache_time < self.cache_duration

    def _load_cache(self) -> List[Dict]:
        """
        Load model data from the cache file.
        
        Returns:
            List[Dict]: The cached API model data.
        """
        with open(self.cache_file) as f:
            return json.load(f)

    def _save_cache(self, data: List[Dict]):
        """Save API model data to the local cache file.
        
        Parameters:
        	data (List[Dict]): Model data to serialize to the cache.
        """
        self.dex_path.mkdir(exist_ok=True)
        with open(self.cache_file, "w") as f:
            json.dump(data, f, indent=2)

    def calculate_subjective_stats(self, model_id: str, api_data: Dict) -> Dict:
        """
        Assign subjective ratings from the model family, context length, and naming indicators.
        
        Parameters:
            model_id (str): Model identifier used to determine family and speed ratings.
            api_data (Dict): API metadata containing the model's context length.
        
        Returns:
            Dict: Subjective ratings for intelligence, creativity, speed, memory, and reliability.
        """
        stats = {
            "intelligence": 70,  # Base stat
            "creativity": 70,
            "speed": 70,
            "memory": 70,
            "reliability": 75,
        }

        # Adjust based on model family
        if "gpt-4" in model_id.lower():
            stats["intelligence"] = 92
            stats["creativity"] = 88
        elif "claude-3-opus" in model_id.lower():
            stats["intelligence"] = 95
            stats["creativity"] = 93
        elif "claude-3" in model_id.lower():
            stats["intelligence"] = 85
            stats["creativity"] = 82
        elif "gemini" in model_id.lower():
            stats["intelligence"] = 88
            stats["creativity"] = 85
        elif "mixtral" in model_id.lower():
            stats["intelligence"] = 86
            stats["creativity"] = 83
        elif "llama" in model_id.lower():
            stats["intelligence"] = 85
            stats["creativity"] = 82

        # Adjust memory based on context length
        context = api_data.get("context_length", 4096)
        if context >= 200000:
            stats["memory"] = 95
        elif context >= 100000:
            stats["memory"] = 85
        elif context >= 32000:
            stats["memory"] = 75
        elif context >= 16000:
            stats["memory"] = 65
        else:
            stats["memory"] = 50

        # Speed adjustments
        if "turbo" in model_id.lower() or "haiku" in model_id.lower():
            stats["speed"] = 90
        elif "opus" in model_id.lower():
            stats["speed"] = 70

        return stats

    def determine_tier(self, model_id: str, pricing: Dict) -> str:
        """
        Assign a rarity tier based on the model identifier and prompt pricing.
        
        Parameters:
        	model_id (str): OpenRouter model identifier used to recognize high-end model families.
        	pricing (Dict): Pricing metadata containing the prompt cost.
        
        Returns:
        	str: The model tier: ``"legendary"``, ``"epic"``, ``"rare"``, ``"uncommon"``, or ``"common"``.
        """
        prompt_cost = pricing.get("prompt", 0)

        # Legendary: Top tier, expensive models
        if "opus" in model_id.lower() or (
            "gpt-4" in model_id.lower() and "turbo" not in model_id.lower()
        ):
            return "legendary"

        # Epic: High-end models
        if "gpt-4-turbo" in model_id.lower() or "claude-3-sonnet" in model_id.lower():
            return "epic"

        # Rare: Good mid-tier models
        if prompt_cost > 0.001 and prompt_cost < 0.01:
            return "rare"

        # Uncommon: Decent budget models
        if prompt_cost > 0.0001 and prompt_cost <= 0.001:
            return "uncommon"

        # Common: Free or very cheap
        return "common"

    def determine_feats(self, model_id: str, api_data: Dict) -> List[str]:
        """
        Determine the capabilities associated with a model based on its metadata and identifier.
        
        Parameters:
            model_id (str): Model identifier used to identify model-specific capabilities.
            api_data (Dict): Model metadata containing architecture and context length information.
        
        Returns:
            List[str]: Capability labels inferred from the model's metadata and identifier.
        """
        feats = []

        # Check for vision/multimodal
        if api_data.get("architecture", {}).get("modality") == "multimodal":
            feats.append("Vision Understanding")

        # Check for specific model feats
        if "gpt-4" in model_id.lower():
            feats.extend(["Code Generation", "Complex Reasoning", "Function Calling"])
        elif "claude" in model_id.lower():
            feats.extend(["Deep Analysis", "Nuanced Understanding", "XML Processing"])
        elif "gemini" in model_id.lower():
            feats.extend(["Multimodal Understanding", "Fast Processing"])
        elif "llama" in model_id.lower():
            feats.extend(["Open Source", "Customizable"])
        elif "code" in model_id.lower():
            feats.extend(["Code Completion", "Bug Detection"])

        # Context-based feats
        if api_data.get("context_length", 0) >= 100000:
            feats.append("Massive Context")
        elif api_data.get("context_length", 0) >= 32000:
            feats.append("Large Context")

        return feats

    async def sync_dex(self):
        """
        Synchronize the local Dex with the latest OpenRouter model metadata, statistics, and rankings.
        
        Fetches model data, updates existing entries while preserving selected manual fields, adds newly discovered models, records synchronization statistics, and writes the resulting Dex and bench rankings.
        """
        print("🔄 Syncing Dex with OpenRouter API...")

        # Fetch latest models
        api_models = await self.fetch_models()

        if not api_models:
            print("⚠️ No models fetched from API")
            return

        # Load existing Dex
        dex_file = self.dex_path / "models.yaml"
        if dex_file.exists():
            with open(dex_file) as f:
                dex_data = yaml.safe_load(f)
        else:
            dex_data = {
                "version": "2.0.0",
                "last_updated": datetime.now().isoformat(),
                "models": [],
            }

        # Create lookup for existing models
        existing_models = {m["id"]: m for m in dex_data.get("models", [])}

        # Process API models
        updated_models = []
        new_count = 0
        updated_count = 0

        for api_model in api_models:
            model_id = api_model["id"]

            # Calculate stats
            subjective_stats = self.calculate_subjective_stats(model_id, api_model)
            feats = self.determine_feats(model_id, api_model)

            # Build model entry
            model_entry = {
                "id": model_id,
                "name": api_model.get("name", model_id),
                "provider": model_id.split("/")[0] if "/" in model_id else "unknown",
                "type": (
                    "multimodal"
                    if api_model.get("architecture", {}).get("modality") == "multimodal"
                    else "text"
                ),
                "tier": self.determine_tier(model_id, api_model.get("pricing", {})),
                "stats": subjective_stats,
                "feats": feats,
                "context_window": api_model.get("context_length", 4096),
                "cost_per_1k": {
                    "input": api_model.get("pricing", {}).get("prompt", 0) * 1000,
                    "output": api_model.get("pricing", {}).get("completion", 0) * 1000,
                },
                "api_data": {
                    "top_provider": api_model.get("top_provider"),
                    "per_request_limits": api_model.get("per_request_limits"),
                },
                "last_synced": datetime.now().isoformat(),
            }

            # Calculate combat stats
            bench_stats = ModelBenchStats.calculate(
                ModelAPIStats(
                    id=model_id,
                    name=model_entry["name"],
                    pricing=api_model.get("pricing", {}),
                    context_length=model_entry["context_window"],
                    top_provider=api_model.get("top_provider"),
                    architecture=api_model.get("architecture", {}),
                ),
                {**subjective_stats, "feats": feats},
            )
            model_entry["bench_stats"] = asdict(bench_stats)

            # Check if this is an update or new model
            if model_id in existing_models:
                # Preserve any manual overrides
                existing = existing_models[model_id]
                if "notes" in existing:
                    model_entry["notes"] = existing["notes"]
                if "best_for" in existing:
                    model_entry["best_for"] = existing["best_for"]
                if "discovered_by" in existing:
                    model_entry["discovered_by"] = existing["discovered_by"]
                    model_entry["discovery_date"] = existing.get("discovery_date")
                updated_count += 1
            else:
                model_entry["discovered_by"] = "ai:openrouter-sync"
                model_entry["discovery_date"] = datetime.now().isoformat()
                new_count += 1

            updated_models.append(model_entry)

        # Update Dex data
        dex_data["models"] = updated_models
        dex_data["last_updated"] = datetime.now().isoformat()
        dex_data["total_models"] = len(updated_models)
        dex_data["sync_stats"] = {
            "new_models": new_count,
            "updated_models": updated_count,
            "total_synced": len(api_models),
        }

        # Save updated Dex
        with open(dex_file, "w") as f:
            yaml.dump(dex_data, f, default_flow_style=False, sort_keys=False)

        print(
            f"✅ Dex synced! New: {new_count}, Updated: {updated_count}, Total: {len(updated_models)}"
        )

        # Generate model bench rankings
        await self.generate_bench_rankings(updated_models)

    async def generate_bench_rankings(self, models: List[Dict]):
        """
        Generate and save model bench power rankings.
        
        Parameters:
            models (List[Dict]): Models containing identifiers, names, tiers, and bench statistics.
        """
        print("⚔️ Generating Model Bench Rankings...")

        # Sort by total combat power
        ranked_models = sorted(models, key=lambda m: sum(m["bench_stats"].values()), reverse=True)

        # Create arena file
        arena_data = {
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "power_rankings": [],
            "weight_classes": {
                "heavyweight": [],  # Legendary & Epic
                "middleweight": [],  # Rare
                "lightweight": [],  # Uncommon & Common
            },
        }

        for i, model in enumerate(ranked_models[:20], 1):  # Top 20
            total_power = sum(model["bench_stats"].values())
            entry = {
                "rank": i,
                "id": model["id"],
                "name": model["name"],
                "tier": model["tier"],
                "total_power": total_power,
                "bench_stats": model["bench_stats"],
            }
            arena_data["power_rankings"].append(entry)

            # Assign to weight class
            if model["tier"] in ["legendary", "epic"]:
                arena_data["weight_classes"]["heavyweight"].append(model["id"])
            elif model["tier"] == "rare":
                arena_data["weight_classes"]["middleweight"].append(model["id"])
            else:
                arena_data["weight_classes"]["lightweight"].append(model["id"])

        # Save arena rankings
        arena_file = self.dex_path / "bench_rankings.yaml"
        with open(arena_file, "w") as f:
            yaml.dump(arena_data, f, default_flow_style=False, sort_keys=False)

        print(f"🏆 Arena rankings generated! Top model: {ranked_models[0]['name']}")


# CLI interface
async def main():
    """Run the OpenRouter model synchronization."""
    syncer = OpenRouterSync()
    await syncer.sync_dex()


if __name__ == "__main__":
    asyncio.run(main())
