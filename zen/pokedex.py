"""zenOS Pokédex System - Discover and catalog models, procedures, and achievements
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class Rarity(Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


@dataclass
class ModelEntry:
    """A model entry in the Pokédex"""

    id: str
    name: str
    provider: str
    type: str
    rarity: Rarity
    stats: Dict[str, int]
    abilities: List[str]
    best_for: List[str]
    context_window: int
    cost_per_1k: Dict[str, float]

    @property
    def overall_score(self) -> float:
        """Calculate overall model score"""
        return sum(self.stats.values()) / len(self.stats)

    def is_suitable_for(self, task: str) -> bool:
        """Check if model is suitable for a task"""
        return task.lower() in [t.lower() for t in self.best_for]


@dataclass
class ProcedureEntry:
    """A procedure entry in the Pokédex"""

    id: str
    name: str
    type: str
    rarity: Rarity
    stats: Dict[str, int]
    requirements: List[str]
    discovered_by: str
    usage_count: int

    @property
    def complexity_rating(self) -> str:
        """Get human-readable complexity rating"""
        complexity = self.stats.get("complexity", 0)
        if complexity < 30:
            return "Simple"
        elif complexity < 60:
            return "Moderate"
        elif complexity < 80:
            return "Complex"
        else:
            return "Expert"


class Pokedex:
    """The zenOS Pokédex - Central catalog for models and procedures"""

    def __init__(self, base_path: Path = Path("pokedex")):
        self.base_path = base_path
        self.models: Dict[str, ModelEntry] = {}
        self.procedures: Dict[str, ProcedureEntry] = {}
        self.achievements: List[Dict] = []
        self.load_data()

    def load_data(self):
        """Load Pokédex data from YAML files"""
        # Load models
        models_file = self.base_path / "models.yaml"
        if models_file.exists():
            with open(models_file) as f:
                data = yaml.safe_load(f)
                for model_data in data.get("models", []):
                    model = ModelEntry(
                        id=model_data["id"],
                        name=model_data["name"],
                        provider=model_data["provider"],
                        type=model_data["type"],
                        rarity=Rarity(model_data["rarity"]),
                        stats=model_data["stats"],
                        abilities=model_data.get("abilities", []),
                        best_for=model_data.get("best_for", []),
                        context_window=model_data.get("context_window", 0),
                        cost_per_1k=model_data.get("cost_per_1k", {}),
                    )
                    self.models[model.id] = model

                self.selection_guide = data.get("selection_guide", {})

        # Load procedures
        procedures_file = self.base_path / "procedures.yaml"
        if procedures_file.exists():
            with open(procedures_file) as f:
                data = yaml.safe_load(f)
                for proc_data in data.get("procedures", []):
                    procedure = ProcedureEntry(
                        id=proc_data["id"],
                        name=proc_data["name"],
                        type=proc_data["type"],
                        rarity=Rarity(proc_data["rarity"]),
                        stats=proc_data["stats"],
                        requirements=proc_data.get("requirements", []),
                        discovered_by=proc_data.get("discovered_by", "unknown"),
                        usage_count=proc_data.get("usage_count", 0),
                    )
                    self.procedures[procedure.id] = procedure

                self.achievements = data.get("achievements", [])
                self.combos = data.get("combos", [])

    def find_model_for_task(self, task: str) -> List[ModelEntry]:
        """Find best models for a specific task"""
        # Check selection guide first
        if "by_task" in self.selection_guide:
            task_guide = self.selection_guide["by_task"].get(task, {})
            recommended_ids = task_guide.get("recommended", [])
            budget_ids = task_guide.get("budget", [])

            recommended = [self.models[id] for id in recommended_ids if id in self.models]
            budget = [self.models[id] for id in budget_ids if id in self.models]

            return recommended + budget

        # Fallback to searching best_for fields
        suitable = []
        for model in self.models.values():
            if model.is_suitable_for(task):
                suitable.append(model)

        # Sort by overall score
        suitable.sort(key=lambda m: m.overall_score, reverse=True)
        return suitable

    def get_models_by_rarity(self, rarity: Rarity) -> List[ModelEntry]:
        """Get all models of a specific rarity"""
        return [m for m in self.models.values() if m.rarity == rarity]

    def get_procedures_by_type(self, proc_type: str) -> List[ProcedureEntry]:
        """Get all procedures of a specific type"""
        return [p for p in self.procedures.values() if p.type == proc_type]

    def get_legendary_items(self) -> Dict[str, List]:
        """Get all legendary models and procedures"""
        return {
            "models": self.get_models_by_rarity(Rarity.LEGENDARY),
            "procedures": [p for p in self.procedures.values() if p.rarity == Rarity.LEGENDARY],
        }

    def calculate_collection_stats(self) -> Dict[str, Any]:
        """Calculate collection statistics"""
        total_models = len(self.models)
        total_procedures = len(self.procedures)

        model_rarities = {}
        for rarity in Rarity:
            count = len(self.get_models_by_rarity(rarity))
            if count > 0:
                model_rarities[rarity.value] = count

        procedure_types = {}
        for proc in self.procedures.values():
            procedure_types[proc.type] = procedure_types.get(proc.type, 0) + 1

        return {
            "total_models": total_models,
            "total_procedures": total_procedures,
            "model_rarities": model_rarities,
            "procedure_types": procedure_types,
            "achievements_available": len(self.achievements),
            "combos_discovered": len(self.combos),
        }

    def log_discovery(self, item_type: str, item_id: str, discovered_by: str):
        """Log a new discovery"""
        # This would update the YAML files with new discoveries
        # For now, just track in memory
        print(f"🎉 New discovery: {item_type} '{item_id}' by {discovered_by}!")

    def check_achievements(self, entity_id: str, action: str) -> List[str]:
        """Check if an action unlocks any achievements"""
        unlocked = []
        # Simple achievement checking logic
        # This would be expanded with actual achievement conditions
        return unlocked


# Singleton instance
_pokedex_instance: Optional[Pokedex] = None


def get_pokedex() -> Pokedex:
    """Get or create the Pokédex singleton"""
    global _pokedex_instance
    if _pokedex_instance is None:
        _pokedex_instance = Pokedex()
    return _pokedex_instance
