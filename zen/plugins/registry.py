"""Plugin Registry - Central catalog for all Git-based plugins
Like a Pokédex for GitHub repositories!
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


@dataclass
class PluginManifest:
    """Plugin manifest from zenos-plugin.yaml"""

    id: str
    name: str
    version: str
    author: str
    description: str
    category: str
    capabilities: List[str]
    entry_points: Dict[str, str]
    dependencies: Dict[str, Any]
    mobile: Dict[str, Any]
    permissions: List[str]
    procedures: List[Dict[str, Any]]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginManifest":
        """Create manifest from dictionary"""
        # Handle both direct manifest data and wrapped in 'plugin' key
        manifest_data = data.get("plugin", data)

        return cls(
            id=manifest_data["id"],
            name=manifest_data["name"],
            version=manifest_data["version"],
            author=manifest_data["author"],
            description=manifest_data["description"],
            category=manifest_data["category"],
            capabilities=manifest_data["capabilities"],
            entry_points=manifest_data["entry_points"],
            dependencies=manifest_data["dependencies"],
            mobile=manifest_data.get("mobile", {}),
            permissions=manifest_data.get("permissions", []),
            procedures=manifest_data.get("procedures", []),
        )


@dataclass
class PluginEntry:
    """A plugin entry in the registry"""

    manifest: PluginManifest
    git_url: str
    local_path: Path
    installed_at: datetime
    last_updated: datetime
    usage_count: int
    is_active: bool
    performance_metrics: Dict[str, float]

    @property
    def rarity(self) -> str:
        """Calculate plugin rarity based on usage and capabilities"""
        if self.usage_count > 1000 and len(self.manifest.capabilities) > 5:
            return "legendary"
        elif self.usage_count > 500 and len(self.manifest.capabilities) > 3:
            return "epic"
        elif self.usage_count > 100:
            return "rare"
        elif self.usage_count > 10:
            return "uncommon"
        else:
            return "common"

    @property
    def overall_score(self) -> float:
        """Calculate overall plugin score"""
        capability_score = len(self.manifest.capabilities) * 10
        usage_score = min(self.usage_count, 1000) / 10
        performance_score = self.performance_metrics.get("success_rate", 0) * 100
        return (capability_score + usage_score + performance_score) / 3


class PluginRegistry:
    """Central registry for all Git-based plugins - The Pokédex of Plugins!"""

    def __init__(self, registry_path: Path = Path("~/.zenos/plugins").expanduser()):
        self.registry_path = registry_path
        self.registry_path.mkdir(parents=True, exist_ok=True)
        self.plugins: Dict[str, PluginEntry] = {}
        self.categories: Dict[str, Set[str]] = {}
        self.capabilities: Dict[str, Set[str]] = {}
        self.load_registry()

    def load_registry(self):
        """Load plugin registry from disk"""
        registry_file = self.registry_path / "registry.json"
        if registry_file.exists():
            try:
                with open(registry_file) as f:
                    data = json.load(f)
                    for plugin_id, plugin_data in data.get("plugins", {}).items():
                        manifest = PluginManifest.from_dict(plugin_data["manifest"])
                        entry = PluginEntry(
                            manifest=manifest,
                            git_url=plugin_data["git_url"],
                            local_path=Path(plugin_data["local_path"]),
                            installed_at=datetime.fromisoformat(plugin_data["installed_at"]),
                            last_updated=datetime.fromisoformat(plugin_data["last_updated"]),
                            usage_count=plugin_data["usage_count"],
                            is_active=plugin_data["is_active"],
                            performance_metrics=plugin_data["performance_metrics"],
                        )
                        self.plugins[plugin_id] = entry
                        self._update_indexes(entry)
            except Exception as e:
                print(f"Error loading registry: {e}")

    def save_registry(self):
        """Save plugin registry to disk"""
        registry_file = self.registry_path / "registry.json"
        data = {
            "plugins": {
                plugin_id: {
                    "manifest": asdict(entry.manifest),
                    "git_url": entry.git_url,
                    "local_path": str(entry.local_path),
                    "installed_at": entry.installed_at.isoformat(),
                    "last_updated": entry.last_updated.isoformat(),
                    "usage_count": entry.usage_count,
                    "is_active": entry.is_active,
                    "performance_metrics": entry.performance_metrics,
                }
                for plugin_id, entry in self.plugins.items()
            }
        }

        with open(registry_file, "w") as f:
            json.dump(data, f, indent=2)

    def register_plugin(self, manifest: PluginManifest, git_url: str, local_path: Path) -> bool:
        """Register a new plugin"""
        try:
            entry = PluginEntry(
                manifest=manifest,
                git_url=git_url,
                local_path=local_path,
                installed_at=datetime.now(),
                last_updated=datetime.now(),
                usage_count=0,
                is_active=True,
                performance_metrics={},
            )

            self.plugins[manifest.id] = entry
            self._update_indexes(entry)
            self.save_registry()
            return True
        except Exception as e:
            print(f"Error registering plugin: {e}")
            return False

    def unregister_plugin(self, plugin_id: str) -> bool:
        """Unregister a plugin"""
        if plugin_id in self.plugins:
            entry = self.plugins[plugin_id]
            self._remove_from_indexes(entry)
            del self.plugins[plugin_id]
            self.save_registry()
            return True
        return False

    def get_plugin(self, plugin_id: str) -> Optional[PluginEntry]:
        """Get a plugin by ID"""
        return self.plugins.get(plugin_id)

    def get_plugins_by_category(self, category: str) -> List[PluginEntry]:
        """Get all plugins in a category"""
        plugin_ids = self.categories.get(category, set())
        return [self.plugins[pid] for pid in plugin_ids if pid in self.plugins]

    def get_plugins_by_capability(self, capability: str) -> List[PluginEntry]:
        """Get all plugins with a specific capability"""
        plugin_ids = self.capabilities.get(capability, set())
        return [self.plugins[pid] for pid in plugin_ids if pid in self.plugins]

    def search_plugins(self, query: str) -> List[PluginEntry]:
        """Search plugins by name, description, or capabilities"""
        query_lower = query.lower()
        results = []

        for entry in self.plugins.values():
            if (
                query_lower in entry.manifest.name.lower()
                or query_lower in entry.manifest.description.lower()
                or any(query_lower in cap.lower() for cap in entry.manifest.capabilities)
            ):
                results.append(entry)

        # Sort by overall score
        results.sort(key=lambda p: p.overall_score, reverse=True)
        return results

    def get_legendary_plugins(self) -> List[PluginEntry]:
        """Get all legendary plugins"""
        return [p for p in self.plugins.values() if p.rarity == "legendary"]

    def get_most_used_plugins(self, limit: int = 10) -> List[PluginEntry]:
        """Get most used plugins"""
        sorted_plugins = sorted(self.plugins.values(), key=lambda p: p.usage_count, reverse=True)
        return sorted_plugins[:limit]

    def get_recommended_plugins(self, task: str) -> List[PluginEntry]:
        """Get recommended plugins for a specific task"""
        # Simple recommendation based on capabilities
        task_lower = task.lower()
        recommended = []

        for entry in self.plugins.values():
            if entry.is_active:
                # Check if any capability matches the task
                if any(task_lower in cap.lower() for cap in entry.manifest.capabilities):
                    recommended.append(entry)

        # Sort by overall score
        recommended.sort(key=lambda p: p.overall_score, reverse=True)
        return recommended

    def update_usage(self, plugin_id: str, success: bool = True):
        """Update plugin usage statistics"""
        if plugin_id in self.plugins:
            entry = self.plugins[plugin_id]
            entry.usage_count += 1

            # Update performance metrics
            if "success_rate" not in entry.performance_metrics:
                entry.performance_metrics["success_rate"] = 0.0

            # Simple moving average for success rate
            current_rate = entry.performance_metrics["success_rate"]
            new_rate = (current_rate * 0.9) + (1.0 if success else 0.0) * 0.1
            entry.performance_metrics["success_rate"] = new_rate

            self.save_registry()

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        total_plugins = len(self.plugins)
        active_plugins = len([p for p in self.plugins.values() if p.is_active])

        categories = {}
        for category, plugin_ids in self.categories.items():
            categories[category] = len(plugin_ids)

        capabilities = {}
        for capability, plugin_ids in self.capabilities.items():
            capabilities[capability] = len(plugin_ids)

        rarities = {}
        for entry in self.plugins.values():
            rarity = entry.rarity
            rarities[rarity] = rarities.get(rarity, 0) + 1

        return {
            "total_plugins": total_plugins,
            "active_plugins": active_plugins,
            "categories": categories,
            "capabilities": capabilities,
            "rarities": rarities,
            "total_usage": sum(p.usage_count for p in self.plugins.values()),
        }

    def _update_indexes(self, entry: PluginEntry):
        """Update category and capability indexes"""
        # Update category index
        category = entry.manifest.category
        if category not in self.categories:
            self.categories[category] = set()
        self.categories[category].add(entry.manifest.id)

        # Update capability index
        for capability in entry.manifest.capabilities:
            if capability not in self.capabilities:
                self.capabilities[capability] = set()
            self.capabilities[capability].add(entry.manifest.id)

    def _remove_from_indexes(self, entry: PluginEntry):
        """Remove plugin from indexes"""
        # Remove from category index
        category = entry.manifest.category
        if category in self.categories:
            self.categories[category].discard(entry.manifest.id)
            if not self.categories[category]:
                del self.categories[category]

        # Remove from capability index
        for capability in entry.manifest.capabilities:
            if capability in self.capabilities:
                self.capabilities[capability].discard(entry.manifest.id)
                if not self.capabilities[capability]:
                    del self.capabilities[capability]


# Singleton instance
_registry_instance: Optional[PluginRegistry] = None


def get_registry() -> PluginRegistry:
    """Get or create the plugin registry singleton"""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = PluginRegistry()
    return _registry_instance
