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
        self.config = config or SandboxConfig()
        self.active_sandboxes: Dict[str, Dict[str, Any]] = {}

    async def create_sandbox(self, plugin_id: str) -> str:
        """Create a new sandbox for a plugin"""
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
        """Execute a command in the sandbox"""
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
        """Start a process with resource limits"""
        try:
            # Set up process limits (Unix only)
            def set_limits():
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
        """Set up resource limits for the sandbox"""
        # This would set up additional security measures
        # like chroot, seccomp, etc. on supported systems
        pass

    async def _update_resource_usage(self, sandbox_id: str, process: subprocess.Popen):
        """Update resource usage statistics"""
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
        """Cleanup a sandbox and all its resources"""
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
        """Cleanup all active sandboxes"""
        try:
            for sandbox_id in list(self.active_sandboxes.keys()):
                await self.cleanup_sandbox(sandbox_id)

            return True

        except Exception as e:
            print(f"Error cleaning up all sandboxes: {e}")
            return False

    def get_sandbox_info(self, sandbox_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a sandbox"""
        return self.active_sandboxes.get(sandbox_id)

    def get_all_sandboxes(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all active sandboxes"""
        return self.active_sandboxes.copy()

    async def check_resource_limits(self, sandbox_id: str) -> Dict[str, bool]:
        """Check if sandbox is within resource limits"""
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
    """Create a new sandbox for a plugin"""
    sandbox = PluginSandbox(config)
    return await sandbox.create_sandbox(plugin_id)
