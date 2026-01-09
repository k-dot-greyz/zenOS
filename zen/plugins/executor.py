"""Plugin Executor - Execute Git-based plugins safely
This is the engine that makes your mobile UI actually work!
"""

import importlib.util
import inspect
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .registry import PluginEntry, PluginRegistry
from .sandbox import PluginSandbox


@dataclass
class ExecutionContext:
    """Context for plugin execution"""

    user_id: str
    session_id: str
    device_info: Dict[str, Any]
    mobile_context: Optional[Dict[str, Any]] = None
    zenos_config: Optional[Dict[str, Any]] = None


@dataclass
class ExecutionResult:
    """Result from plugin execution"""

    success: bool
    data: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    performance_metrics: Dict[str, float] = None


class PluginExecutor:
    """Execute plugins safely - The VST Plugin Engine!"""

    def __init__(self, registry: PluginRegistry):
        self.registry = registry
        self.sandbox = PluginSandbox()
        self.active_plugins: Dict[str, Any] = {}

    async def execute_plugin(
        self, plugin_id: str, procedure_id: str, input_data: Any, context: ExecutionContext
    ) -> ExecutionResult:
        """Execute a specific procedure from a plugin"""
        try:
            # Get plugin entry
            entry = self.registry.get_plugin(plugin_id)
            if not entry:
                return ExecutionResult(
                    success=False, data=None, error=f"Plugin {plugin_id} not found"
                )

            # Check if plugin is active
            if not entry.is_active:
                return ExecutionResult(
                    success=False, data=None, error=f"Plugin {plugin_id} is not active"
                )

            # Find the procedure
            procedure = None
            for proc in entry.manifest.procedures:
                if proc["id"] == procedure_id:
                    procedure = proc
                    break

            if not procedure:
                return ExecutionResult(
                    success=False,
                    data=None,
                    error=f"Procedure {procedure_id} not found in plugin {plugin_id}",
                )

            # Load plugin if not already loaded
            if plugin_id not in self.active_plugins:
                plugin_instance = await self._load_plugin_instance(entry)
                if not plugin_instance:
                    return ExecutionResult(
                        success=False, data=None, error=f"Failed to load plugin {plugin_id}"
                    )
                self.active_plugins[plugin_id] = plugin_instance

            # Execute the procedure
            plugin_instance = self.active_plugins[plugin_id]
            result = await self._execute_procedure(plugin_instance, procedure, input_data, context)

            # Update usage statistics
            self.registry.update_usage(plugin_id, result.success)

            return result

        except Exception as e:
            return ExecutionResult(success=False, data=None, error=f"Execution error: {str(e)}")

    async def execute_plugin_chain(
        self, plugin_chain: List[Dict[str, Any]], input_data: Any, context: ExecutionContext
    ) -> ExecutionResult:
        """Execute a chain of plugins (like a VST effect chain)"""
        try:
            current_data = input_data
            results = []

            for i, plugin_config in enumerate(plugin_chain):
                plugin_id = plugin_config["plugin_id"]
                procedure_id = plugin_config["procedure_id"]
                params = plugin_config.get("params", {})

                # Merge current data with parameters
                if isinstance(current_data, dict) and isinstance(params, dict):
                    execution_input = {**current_data, **params}
                else:
                    execution_input = current_data

                # Execute plugin
                result = await self.execute_plugin(
                    plugin_id, procedure_id, execution_input, context
                )

                if not result.success:
                    return ExecutionResult(
                        success=False,
                        data=None,
                        error=f"Chain execution failed at step {i+1}: {result.error}",
                    )

                results.append(result)
                current_data = result.data

            return ExecutionResult(
                success=True,
                data=current_data,
                metadata={
                    "chain_length": len(plugin_chain),
                    "step_results": [r.metadata for r in results],
                },
            )

        except Exception as e:
            return ExecutionResult(
                success=False, data=None, error=f"Chain execution error: {str(e)}"
            )

    async def _load_plugin_instance(self, entry: PluginEntry) -> Optional[Any]:
        """Load a plugin instance dynamically"""
        try:
            # Determine entry point based on context
            entry_point = entry.manifest.entry_points.get("main")
            if not entry_point:
                return None

            # Load the plugin module
            plugin_path = entry.local_path / entry_point
            if not plugin_path.exists():
                return None

            # Import the plugin module
            spec = importlib.util.spec_from_file_location(
                f"plugin_{entry.manifest.id}", plugin_path
            )
            if not spec or not spec.loader:
                return None

            module = importlib.util.module_from_spec(spec)
            sys.modules[f"plugin_{entry.manifest.id}"] = module
            spec.loader.exec_module(module)

            # Find the plugin class
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and hasattr(obj, "process") and hasattr(obj, "initialize"):
                    plugin_class = obj
                    break

            if not plugin_class:
                return None

            # Create plugin instance
            plugin_instance = plugin_class(entry.manifest.dependencies)

            # Initialize plugin
            if hasattr(plugin_instance, "initialize"):
                init_success = await plugin_instance.initialize()
                if not init_success:
                    return None

            return plugin_instance

        except Exception as e:
            print(f"Error loading plugin instance: {e}")
            return None

    async def _execute_procedure(
        self,
        plugin_instance: Any,
        procedure: Dict[str, Any],
        input_data: Any,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """Execute a specific procedure on a plugin instance"""
        try:
            # Create execution context for the plugin
            plugin_context = {
                "user_id": context.user_id,
                "session_id": context.session_id,
                "device_info": context.device_info,
                "mobile_context": context.mobile_context,
                "zenos_config": context.zenos_config,
                "procedure": procedure,
            }

            # Execute the procedure
            if hasattr(plugin_instance, "process"):
                # Use the main process method
                result = await plugin_instance.process(input_data, plugin_context)

                # Handle different result types
                if isinstance(result, dict):
                    if "success" in result:
                        return ExecutionResult(
                            success=result["success"],
                            data=result.get("data"),
                            error=result.get("error"),
                            metadata=result.get("metadata", {}),
                            performance_metrics=result.get("performance_metrics", {}),
                        )
                    else:
                        return ExecutionResult(
                            success=True, data=result, metadata={"method": "process"}
                        )
                else:
                    return ExecutionResult(
                        success=True, data=result, metadata={"method": "process"}
                    )

            elif hasattr(plugin_instance, procedure["id"]):
                # Use a specific procedure method
                method = getattr(plugin_instance, procedure["id"])
                result = await method(input_data, plugin_context)

                return ExecutionResult(
                    success=True, data=result, metadata={"method": procedure["id"]}
                )

            else:
                return ExecutionResult(
                    success=False,
                    data=None,
                    error=f"Procedure {procedure['id']} not found in plugin",
                )

        except Exception as e:
            return ExecutionResult(
                success=False, data=None, error=f"Procedure execution error: {str(e)}"
            )

    async def get_plugin_capabilities(self, plugin_id: str) -> List[str]:
        """Get capabilities of a specific plugin"""
        entry = self.registry.get_plugin(plugin_id)
        if entry:
            return entry.manifest.capabilities
        return []

    async def get_available_procedures(self, plugin_id: str) -> List[Dict[str, Any]]:
        """Get available procedures for a plugin"""
        entry = self.registry.get_plugin(plugin_id)
        if entry:
            return entry.manifest.procedures
        return []

    async def test_plugin(self, plugin_id: str) -> ExecutionResult:
        """Test a plugin with sample data"""
        try:
            entry = self.registry.get_plugin(plugin_id)
            if not entry:
                return ExecutionResult(
                    success=False, data=None, error=f"Plugin {plugin_id} not found"
                )

            # Create test context
            test_context = ExecutionContext(
                user_id="test_user",
                session_id="test_session",
                device_info={"platform": "test", "version": "1.0.0"},
            )

            # Test with sample data
            test_data = {"test": "Hello, zenOS!"}

            # Try to execute the first available procedure
            procedures = entry.manifest.procedures
            if not procedures:
                return ExecutionResult(
                    success=False, data=None, error="No procedures available for testing"
                )

            first_procedure = procedures[0]
            return await self.execute_plugin(
                plugin_id, first_procedure["id"], test_data, test_context
            )

        except Exception as e:
            return ExecutionResult(success=False, data=None, error=f"Plugin test error: {str(e)}")

    async def cleanup_plugin(self, plugin_id: str) -> bool:
        """Cleanup a plugin instance"""
        try:
            if plugin_id in self.active_plugins:
                plugin_instance = self.active_plugins[plugin_id]

                # Call cleanup if available
                if hasattr(plugin_instance, "cleanup"):
                    await plugin_instance.cleanup()

                del self.active_plugins[plugin_id]

            return True

        except Exception as e:
            print(f"Error cleaning up plugin {plugin_id}: {e}")
            return False

    async def cleanup_all_plugins(self) -> bool:
        """Cleanup all active plugins"""
        try:
            for plugin_id in list(self.active_plugins.keys()):
                await self.cleanup_plugin(plugin_id)

            return True

        except Exception as e:
            print(f"Error cleaning up all plugins: {e}")
            return False


# Convenience function
async def execute_plugin(
    plugin_id: str, procedure_id: str, input_data: Any, context: ExecutionContext
) -> ExecutionResult:
    """Execute a plugin procedure"""
    registry = PluginRegistry()
    executor = PluginExecutor(registry)
    return await executor.execute_plugin(plugin_id, procedure_id, input_data, context)
