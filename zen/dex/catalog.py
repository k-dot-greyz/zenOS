"""
zenOS Dex System - Discover and catalog models, procedures, and achievements
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class Tier(Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


@dataclass
class ModelEntry:
    """A model entry in the Dex"""

    id: str
    name: str
    provider: str
    type: str
    tier: Tier
    stats: Dict[str, int]
    feats: List[str]
    best_for: List[str]
    context_window: int
    cost_per_1k: Dict[str, float]

    @property
    def overall_score(self) -> float:
        """
        Calculate the model's overall score from its statistics.
        
        Returns:
            float: The average of the model's statistic values.
        """
        return sum(self.stats.values()) / len(self.stats)

    def is_suitable_for(self, task: str) -> bool:
        """
        Determine whether the model is suitable for a task.
        
        Parameters:
        	task (str): The task to match against the model's supported tasks.
        
        Returns:
        	bool: `true` if the task matches a supported task, `false` otherwise.
        """
        return task.lower() in [t.lower() for t in self.best_for]


@dataclass
class ProcedureEntry:
    """A procedure entry in the Dex"""

    id: str
    name: str
    type: str
    tier: Tier
    stats: Dict[str, int]
    requirements: List[str]
    discovered_by: str
    usage_count: int

    @property
    def complexity_rating(self) -> str:
        """Classify the procedure's complexity using its complexity statistic.
        
        Returns:
        	str: "Simple", "Moderate", "Complex", or "Expert".
        """
        complexity = self.stats.get("complexity", 0)
        if complexity < 30:
            return "Simple"
        elif complexity < 60:
            return "Moderate"
        elif complexity < 80:
            return "Complex"
        else:
            return "Expert"


class DexCatalog:
    """The zenOS Dex - Central catalog for models and procedures"""

    def __init__(self, base_path: Path = Path("dex")):
        """Initialize the catalog with a data directory and load its catalog entries.
        
        Parameters:
        	base_path (Path): Directory containing the catalog data files.
        """
        self.base_path = base_path
        self.models: Dict[str, ModelEntry] = {}
        self.procedures: Dict[str, ProcedureEntry] = {}
        self.achievements: List[Dict] = []
        self.load_data()

    def load_data(self):
        """
        Load models, procedures, selection guides, achievements, and combos from YAML files in the catalog directory.
        """
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
                        tier=Tier(model_data["tier"]),
                        stats=model_data["stats"],
                        feats=model_data.get("feats", model_data.get("capabilities", [])),
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
                        tier=Tier(proc_data["tier"]),
                        stats=proc_data["stats"],
                        requirements=proc_data.get("requirements", []),
                        discovered_by=proc_data.get("discovered_by", "unknown"),
                        usage_count=proc_data.get("usage_count", 0),
                    )
                    self.procedures[procedure.id] = procedure

                self.achievements = data.get("achievements", [])
                self.combos = data.get("combos", [])

    def find_model_for_task(self, task: str) -> List[ModelEntry]:
        """
        Find models suited to a specific task.
        
        Parameters:
        	task (str): The task to match against the catalog's task recommendations or model suitability metadata.
        
        Returns:
        	List[ModelEntry]: Recommended and budget models from the selection guide, or matching models sorted by descending overall score.
        """
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

    def get_models_by_tier(self, rarity: Tier) -> List[ModelEntry]:
        """
        Get all models assigned to a specific tier.
        
        Parameters:
            rarity (Tier): Tier to match.
        
        Returns:
            List[ModelEntry]: Models assigned to the specified tier.
        """
        return [m for m in self.models.values() if m.tier == rarity]

    def get_procedures_by_type(self, proc_type: str) -> List[ProcedureEntry]:
        """Get all procedures of a specific type"""
        return [p for p in self.procedures.values() if p.type == proc_type]

    def get_legendary_items(self) -> Dict[str, List]:
        """Collect all models and procedures with legendary tier.
        
        Returns:
            Dict[str, List]: A dictionary containing legendary models under ``"models"`` and legendary procedures under ``"procedures"``.
        """
        return {
            "models": self.get_models_by_tier(Tier.LEGENDARY),
            "procedures": [p for p in self.procedures.values() if p.tier == Tier.LEGENDARY],
        }

    def calculate_collection_stats(self) -> Dict[str, Any]:
        """
        Summarize the contents of the catalog.
        
        Returns:
            Dict[str, Any]: Counts of models, procedures, models by tier, procedures by type,
            available achievements, and discovered combos.
        """
        total_models = len(self.models)
        total_procedures = len(self.procedures)

        model_tiers = {}
        for rarity in Tier:
            count = len(self.get_models_by_tier(rarity))
            if count > 0:
                model_tiers[rarity.value] = count

        procedure_types = {}
        for proc in self.procedures.values():
            procedure_types[proc.type] = procedure_types.get(proc.type, 0) + 1

        return {
            "total_models": total_models,
            "total_procedures": total_procedures,
            "model_tiers": model_tiers,
            "procedure_types": procedure_types,
            "achievements_available": len(self.achievements),
            "combos_discovered": len(self.combos),
        }

    def log_discovery(self, item_type: str, item_id: str, discovered_by: str):
        """Display a message announcing a newly discovered catalog item.
        
        Parameters:
            item_type (str): The type of discovered item.
            item_id (str): The discovered item's identifier.
            discovered_by (str): The source or user credited with the discovery.
        """
        # This would update the YAML files with new discoveries
        # For now, just track in memory
        print(f"🎉 New discovery: {item_type} '{item_id}' by {discovered_by}!")

    def check_achievements(self, entity_id: str, action: str) -> List[str]:
        """
        Check whether an entity action unlocks any achievements.
        
        Parameters:
            entity_id (str): Identifier of the entity performing the action.
            action (str): Action to evaluate.
        
        Returns:
            List[str]: Achievement identifiers unlocked by the action; currently always empty.
        """
        unlocked = []
        # Simple achievement checking logic
        # This would be expanded with actual achievement conditions
        return unlocked


# Singleton instance
_dex_catalog_instance: Optional[DexCatalog] = None


def get_dex_catalog() -> DexCatalog:
    """
    Get the shared Dex catalog instance, creating it when necessary.
    
    Returns:
        DexCatalog: The shared catalog instance.
    """
    global _dex_catalog_instance
    if _dex_catalog_instance is None:
        _dex_catalog_instance = DexCatalog()
    return _dex_catalog_instance
