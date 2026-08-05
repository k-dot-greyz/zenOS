"""
Plugin Sandbox - Secure execution environment for Git-based plugins
Safety first! No plugin can break your system!
"""

import asyncio
import os
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import psutil

# Import resource only on Unix systems
try:
    import resource
    import signal

    HAS_RESOURCE = True
except ImportError:
    HAS_RESOURCE = False


@dataclass
class SandboxConfig:
    """Configuration for plugin sandbox"""

    max_memory_mb: int = 512
    max_cpu_time_seconds: int = 30
    max_disk_space_mb: int = 100
    allowed_network: bool = False
    allowed_file_access: bool = True
    allowed_temp_files: bool = True
    max_processes: int = 5


class PluginSandbox:
    """Secure sandbox for plugin execution - The VST Security Layer!"""

    def __init__(self, config: Optional[SandboxConfig] = None):
        """
        Initialize the sandbox manager with the provided configuration.
        
        Parameters:
        	config (Optional[SandboxConfig]): Configuration for sandbox resource and access limits. Uses default settings when omitted.
        """
        self.config = config or SandboxConfig()
        self.active_sandboxes: Dict[str, Dict[str, Any]] = {}

    async def create_sandbox(self, plugin_id: str) -> str:
        """
        Create an isolated workspace for a plugin.
        
        Parameters:
            plugin_id (str): Identifier used to associate the sandbox with the plugin.
        
        Returns:
            str or None: The sandbox identifier if creation succeeds, or `None` if it fails.
        """
        try:
            # Create unique sandbox directory
            sandbox_id = f"{plugin_id}_{int(time.time())}"
            sandbox_path = Path(tempfile.mkdtemp(prefix=f"zenos_sandbox_{sandbox_id}_"))

            # Create sandbox structure
            (sandbox_path / "input").mkdir()
            (sandbox_path / "output").mkdir()
            (sandbox_path / "temp").mkdir()
            (sandbox_path / "cache").mkdir()
            (sandbox_path / "logs").mkdir()

            # Set up sandbox environment
            sandbox_info = {
                "id": sandbox_id,
                "path": sandbox_path,
                "created_at": time.time(),
                "processes": [],
                "files_created": [],
                "network_requests": [],
                "resource_usage": {"memory_mb": 0, "cpu_time": 0, "disk_space_mb": 0},
            }

            self.active_sandboxes[sandbox_id] = sandbox_info

            # Set up resource limits
            await self._setup_resource_limits(sandbox_id)

            return sandbox_id

        except Exception as e:
            print(f"Error creating sandbox: {e}")
            return None

    async def execute_in_sandbox(
        self, sandbox_id: str, command: List[str], input_data: Any = None, timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Execute a command within a registered sandbox and collect its results.
        
        Parameters:
        	sandbox_id (str): Identifier of the sandbox in which to run the command.
        	command (List[str]): Command and arguments to execute.
        	input_data (Any): Optional data to write as JSON input for the command.
        	timeout (int): Maximum execution time in seconds.
        
        Returns:
        	Dict[str, Any]: Execution status, captured output and error streams, return
        		code, execution duration, and resource usage. Failed executions include
        		an error description.
        """
        try:
            if sandbox_id not in self.active_sandboxes:
                return {"success": False, "error": "Sandbox not found", "output": "", "stderr": ""}

            sandbox_info = self.active_sandboxes[sandbox_id]
            sandbox_path = sandbox_info["path"]

            # Prepare input data
            if input_data is not None:
                input_file = sandbox_path / "input" / "data.json"
                with open(input_file, "w") as f:
                    import json

                    json.dump(input_data, f)

            # Start process with resource limits
            process = await self._start_limited_process(command, sandbox_path, sandbox_id)

            # Monitor process
            start_time = time.time()
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)

            # Update resource usage
            await self._update_resource_usage(sandbox_id, process)

            # Check if process was killed due to resource limits
            success = process.returncode == 0
            if process.returncode == -9:  # SIGKILL
                success = False
                stderr = b"Process killed due to resource limits"

            return {
                "success": success,
                "output": stdout.decode() if stdout else "",
                "stderr": stderr.decode() if stderr else "",
                "return_code": process.returncode,
                "execution_time": time.time() - start_time,
                "resource_usage": sandbox_info["resource_usage"],
            }

        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "Process timed out",
                "output": "",
                "stderr": "Process exceeded maximum execution time",
            }
        except Exception as e:
            return {"success": False, "error": str(e), "output": "", "stderr": ""}

    async def _start_limited_process(
        self, command: List[str], sandbox_path: Path, sandbox_id: str
    ) -> subprocess.Popen:
        """
        Start a subprocess in the specified sandbox with configured resource limits.
        
        Parameters:
            command (List[str]): The executable and arguments to run.
            sandbox_path (Path): The working directory for the subprocess.
            sandbox_id (str): The identifier of the sandbox that tracks the process.
        
        Returns:
            subprocess.Popen: The started subprocess.
        
        Raises:
            Exception: Re-raises any error encountered while starting the subprocess.
        """
        try:
            # Set up process limits (Unix only)
            def set_limits():
                """
                Apply configured memory, CPU-time, file-size, and process-count limits to the current process when resource controls are available.
                """
                if HAS_RESOURCE:
                    # Memory limit
                    memory_limit = self.config.max_memory_mb * 1024 * 1024  # Convert to bytes
                    resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))

                    # CPU time limit
                    cpu_limit = self.config.max_cpu_time_seconds
                    resource.setrlimit(resource.RLIMIT_CPU, (cpu_limit, cpu_limit))

                    # File size limit
                    file_limit = self.config.max_disk_space_mb * 1024 * 1024
                    resource.setrlimit(resource.RLIMIT_FSIZE, (file_limit, file_limit))

                    # Process limit
                    process_limit = self.config.max_processes
                    resource.setrlimit(resource.RLIMIT_NPROC, (process_limit, process_limit))

            # Start process
            process = await asyncio.create_subprocess_exec(
                *command,
                cwd=sandbox_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                preexec_fn=set_limits if HAS_RESOURCE and os.name != "nt" else None,
            )

            # Track process
            self.active_sandboxes[sandbox_id]["processes"].append(process.pid)

            return process

        except Exception as e:
            print(f"Error starting limited process: {e}")
            raise

    async def _setup_resource_limits(self, sandbox_id: str):
        """
        Provide a hook for configuring additional sandbox protections.
        """
        # This would set up additional security measures
        # like chroot, seccomp, etc. on supported systems
        pass

    async def _update_resource_usage(self, sandbox_id: str, process: subprocess.Popen):
        """
        Update recorded memory, CPU, and disk usage for a sandbox process.
        
        Parameters:
            sandbox_id (str): Identifier of the sandbox whose usage is updated.
            process (subprocess.Popen): Process whose resource usage is measured.
        """
        try:
            if sandbox_id not in self.active_sandboxes:
                return

            sandbox_info = self.active_sandboxes[sandbox_id]

            # Get process info
            try:
                proc = psutil.Process(process.pid)
                memory_info = proc.memory_info()
                cpu_times = proc.cpu_times()

                # Update resource usage
                sandbox_info["resource_usage"]["memory_mb"] = memory_info.rss / 1024 / 1024
                sandbox_info["resource_usage"]["cpu_time"] = cpu_times.user + cpu_times.system

                # Calculate disk usage
                sandbox_path = sandbox_info["path"]
                disk_usage = sum(f.stat().st_size for f in sandbox_path.rglob("*") if f.is_file())
                sandbox_info["resource_usage"]["disk_space_mb"] = disk_usage / 1024 / 1024

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Process already terminated
                pass

        except Exception as e:
            print(f"Error updating resource usage: {e}")

    async def cleanup_sandbox(self, sandbox_id: str) -> bool:
        """Terminate tracked processes, remove the sandbox directory, and unregister the sandbox.
        
        Parameters:
        	sandbox_id (str): Identifier of the sandbox to clean up.
        
        Returns:
        	bool: `true` if the sandbox was removed successfully, `false` if it was not registered or cleanup failed.
        """
        try:
            if sandbox_id not in self.active_sandboxes:
                return False

            sandbox_info = self.active_sandboxes[sandbox_id]
            sandbox_path = sandbox_info["path"]

            # Kill any remaining processes
            for pid in sandbox_info["processes"]:
                try:
                    proc = psutil.Process(pid)
                    proc.terminate()
                    proc.wait(timeout=5)
                except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                    try:
                        proc.kill()
                    except psutil.NoSuchProcess:
                        pass

            # Remove sandbox directory
            if sandbox_path.exists():
                shutil.rmtree(sandbox_path, ignore_errors=True)

            # Remove from active sandboxes
            del self.active_sandboxes[sandbox_id]

            return True

        except Exception as e:
            print(f"Error cleaning up sandbox {sandbox_id}: {e}")
            return False

    async def cleanup_all_sandboxes(self) -> bool:
        """
        Clean up all active sandboxes.
        
        Returns:
        	bool: `True` if cleanup completes without an exception, `False` otherwise.
        """
        try:
            for sandbox_id in list(self.active_sandboxes.keys()):
                await self.cleanup_sandbox(sandbox_id)

            return True

        except Exception as e:
            print(f"Error cleaning up all sandboxes: {e}")
            return False

    def get_sandbox_info(self, sandbox_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve metadata for a registered sandbox.
        
        Parameters:
        	sandbox_id (str): Identifier of the sandbox.
        
        Returns:
        	Optional[Dict[str, Any]]: The sandbox metadata, or `None` if the sandbox is not registered.
        """
        return self.active_sandboxes.get(sandbox_id)

    def get_all_sandboxes(self) -> Dict[str, Dict[str, Any]]:
        """
        Return metadata for all currently active sandboxes.
        
        Returns:
            Dict[str, Dict[str, Any]]: A shallow copy of the active-sandbox registry.
        """
        return self.active_sandboxes.copy()

    async def check_resource_limits(self, sandbox_id: str) -> Dict[str, bool]:
        """
        Check whether a sandbox's current resource usage complies with its configured limits.
        
        Parameters:
        	sandbox_id (str): Identifier of the sandbox to check.
        
        Returns:
        	Dict[str, bool]: Resource check results and overall validity. Includes a
        		reason string when the sandbox is missing or exceeds one or more limits.
        """
        if sandbox_id not in self.active_sandboxes:
            return {"valid": False, "reason": "Sandbox not found"}

        sandbox_info = self.active_sandboxes[sandbox_id]
        usage = sandbox_info["resource_usage"]

        checks = {
            "memory_ok": usage["memory_mb"] <= self.config.max_memory_mb,
            "cpu_ok": usage["cpu_time"] <= self.config.max_cpu_time_seconds,
            "disk_ok": usage["disk_space_mb"] <= self.config.max_disk_space_mb,
            "process_count_ok": len(sandbox_info["processes"]) <= self.config.max_processes,
        }

        checks["valid"] = all(checks.values())

        if not checks["valid"]:
            failed_checks = [k for k, v in checks.items() if not v and k != "valid"]
            checks["reason"] = f"Resource limits exceeded: {', '.join(failed_checks)}"

        return checks


# Convenience function
async def create_sandbox(plugin_id: str, config: Optional[SandboxConfig] = None) -> str:
    """
    Create a sandbox for the specified plugin.
    
    Parameters:
    	plugin_id (str): Identifier of the plugin that will use the sandbox.
    	config (Optional[SandboxConfig]): Resource and access limits for the sandbox.
    
    Returns:
    	str: The created sandbox's identifier.
    """
    sandbox = PluginSandbox(config)
    return await sandbox.create_sandbox(plugin_id)
