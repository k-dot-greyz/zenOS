"""Plugin catalog and execution use cases."""

from __future__ import annotations

from typing import Any, Dict, Optional

from zen.plugins.executor import ExecutionContext, ExecutionResult, PluginExecutor
from zen.plugins.registry import PluginEntry, PluginRegistry
from zen.services.errors import NotFoundError, ServiceError


class PluginService:
    """List, inspect, and execute Git-based zenOS plugins."""

    def __init__(
        self,
        registry: Optional[PluginRegistry] = None,
        executor: Optional[PluginExecutor] = None,
    ) -> None:
        self._registry = registry
        self._executor = executor

    def _get_registry(self) -> PluginRegistry:
        if self._registry is None:
            self._registry = PluginRegistry()
        return self._registry

    def _get_executor(self) -> PluginExecutor:
        if self._executor is None:
            self._executor = PluginExecutor(self._get_registry())
        return self._executor

    def plugin_fields(self, entry: PluginEntry) -> Dict[str, Any]:
        """Serialize a plugin registry entry to card fields."""
        manifest = entry.manifest
        return {
            "name": manifest.name,
            "version": manifest.version,
            "author": manifest.author,
            "description": manifest.description,
            "category": manifest.category,
            "capabilities": list(manifest.capabilities),
            "is_active": entry.is_active,
            "usage_count": entry.usage_count,
        }

    def list_plugins(self) -> list:
        """Return installed plugin entries."""
        return list(self._get_registry().plugins.values())

    def get_plugin(self, plugin_id: str) -> PluginEntry:
        """Return one plugin or raise NotFoundError."""
        entry = self._get_registry().get_plugin(plugin_id)
        if entry is None:
            raise NotFoundError(f"Plugin not found: {plugin_id}", details={"id": plugin_id})
        return entry

    async def execute(
        self,
        plugin_id: str,
        procedure_id: str,
        input_data: Any,
        context: Optional[ExecutionContext] = None,
    ) -> ExecutionResult:
        """Execute a plugin procedure."""
        self.get_plugin(plugin_id)
        ctx = context or ExecutionContext(user_id="api", session_id="local", device_info={})
        result = await self._get_executor().execute_plugin(plugin_id, procedure_id, input_data, ctx)
        if not result.success:
            error = result.error or "Plugin execution failed"
            lowered = error.lower()
            if "not found" in lowered:
                raise NotFoundError(error, details={"id": plugin_id, "procedure_id": procedure_id})
            raise ServiceError(error, details={"id": plugin_id, "procedure_id": procedure_id})
        return result
