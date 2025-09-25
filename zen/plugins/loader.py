"""
Git Plugin Loader - Clone and load GitHub repositories as VST plugins
This is where the magic happens - turning Git repos into live plugins!
"""

import asyncio
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse
import yaml
import aiohttp
from .registry import PluginRegistry, PluginManifest, PluginEntry
from .sandbox import PluginSandbox

class GitPluginLoader:
    """Load plugins from GitHub repositories - The VST Plugin Loader!"""
    
    def __init__(self, registry: PluginRegistry):
        self.registry = registry
        self.temp_dir = Path(tempfile.gettempdir()) / "zenos_plugins"
        self.temp_dir.mkdir(exist_ok=True)
    
    async def load_plugin_from_git(self, git_url: str, version: str = "main") -> Optional[PluginEntry]:
        """Load a plugin from a GitHub repository"""
        try:
            # Parse Git URL
            repo_info = self._parse_git_url(git_url)
            if not repo_info:
                print(f"Invalid Git URL: {git_url}")
                return None
            
            # Clone repository
            local_path = await self._clone_repository(git_url, version)
            if not local_path:
                return None
            
            # Load plugin manifest
            manifest = await self._load_manifest(local_path)
            if not manifest:
                print(f"No zenos-plugin.yaml found in {git_url}")
                shutil.rmtree(local_path, ignore_errors=True)
                return None
            
            # Validate plugin
            if not await self._validate_plugin(manifest, local_path):
                print(f"Plugin validation failed for {manifest.id}")
                shutil.rmtree(local_path, ignore_errors=True)
                return None
            
            # Register plugin
            success = self.registry.register_plugin(manifest, git_url, local_path)
            if success:
                print(f"🎉 Successfully loaded plugin: {manifest.name} ({manifest.id})")
                return self.registry.get_plugin(manifest.id)
            else:
                print(f"Failed to register plugin: {manifest.id}")
                shutil.rmtree(local_path, ignore_errors=True)
                return None
                
        except Exception as e:
            print(f"Error loading plugin from {git_url}: {e}")
            return None
    
    async def update_plugin(self, plugin_id: str) -> bool:
        """Update a plugin to the latest version"""
        entry = self.registry.get_plugin(plugin_id)
        if not entry:
            return False
        
        try:
            # Pull latest changes
            result = await self._git_pull(entry.local_path)
            if result.returncode != 0:
                print(f"Failed to update {plugin_id}: {result.stderr}")
                return False
            
            # Reload manifest
            manifest = await self._load_manifest(entry.local_path)
            if not manifest:
                print(f"Failed to reload manifest for {plugin_id}")
                return False
            
            # Update registry entry
            entry.manifest = manifest
            entry.last_updated = datetime.now()
            self.registry.save_registry()
            
            print(f"✅ Updated plugin: {manifest.name}")
            return True
            
        except Exception as e:
            print(f"Error updating plugin {plugin_id}: {e}")
            return False
    
    async def install_dependencies(self, plugin_path: Path) -> bool:
        """Install plugin dependencies"""
        try:
            # Check for requirements.txt
            requirements_file = plugin_path / "requirements.txt"
            if requirements_file.exists():
                print(f"Installing dependencies from {requirements_file}")
                result = await asyncio.create_subprocess_exec(
                    "pip", "install", "-r", str(requirements_file),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await result.communicate()
                
                if result.returncode != 0:
                    print(f"Dependency installation failed: {stderr.decode()}")
                    print("Continuing anyway...")
                    # Don't fail the plugin installation for dependency issues
                    return True
            
            # Check for package.json (Node.js dependencies)
            package_json = plugin_path / "package.json"
            if package_json.exists():
                print(f"Installing Node.js dependencies from {package_json}")
                result = await asyncio.create_subprocess_exec(
                    "npm", "install",
                    cwd=plugin_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await result.communicate()
                
                if result.returncode != 0:
                    print(f"Node.js dependency installation failed: {stderr.decode()}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"Error installing dependencies: {e}")
            return False
    
    def _parse_git_url(self, git_url: str) -> Optional[Dict[str, str]]:
        """Parse Git URL to extract repository information"""
        try:
            # Handle different Git URL formats
            if git_url.startswith("https://github.com/"):
                # https://github.com/username/repo
                parts = git_url.replace("https://github.com/", "").split("/")
                if len(parts) >= 2:
                    return {
                        "owner": parts[0],
                        "repo": parts[1].replace(".git", ""),
                        "platform": "github"
                    }
            elif git_url.startswith("git@github.com:"):
                # git@github.com:username/repo.git
                parts = git_url.replace("git@github.com:", "").replace(".git", "").split("/")
                if len(parts) >= 2:
                    return {
                        "owner": parts[0],
                        "repo": parts[1],
                        "platform": "github"
                    }
            elif git_url.startswith("github.com/"):
                # github.com/username/repo
                parts = git_url.replace("github.com/", "").split("/")
                if len(parts) >= 2:
                    return {
                        "owner": parts[0],
                        "repo": parts[1].replace(".git", ""),
                        "platform": "github"
                    }
            
            return None
            
        except Exception as e:
            print(f"Error parsing Git URL {git_url}: {e}")
            return None
    
    async def _clone_repository(self, git_url: str, version: str = "main") -> Optional[Path]:
        """Clone a Git repository to a temporary directory"""
        try:
            # Create unique directory name
            repo_name = urlparse(git_url).path.split("/")[-1].replace(".git", "")
            local_path = self.temp_dir / f"{repo_name}_{asyncio.get_event_loop().time()}"
            
            # Clone repository
            print(f"Cloning {git_url} to {local_path}")
            result = await asyncio.create_subprocess_exec(
                "git", "clone", "--depth", "1", "--branch", version, git_url, str(local_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                print(f"Git clone failed: {stderr.decode()}")
                return None
            
            return local_path
            
        except Exception as e:
            print(f"Error cloning repository {git_url}: {e}")
            return None
    
    async def _load_manifest(self, plugin_path: Path) -> Optional[PluginManifest]:
        """Load plugin manifest from zenos-plugin.yaml"""
        try:
            manifest_file = plugin_path / "zenos-plugin.yaml"
            if not manifest_file.exists():
                return None
            
            with open(manifest_file) as f:
                data = yaml.safe_load(f)
            
            return PluginManifest.from_dict(data)
            
        except Exception as e:
            print(f"Error loading manifest: {e}")
            return None
    
    async def _validate_plugin(self, manifest: PluginManifest, plugin_path: Path) -> bool:
        """Validate plugin structure and requirements"""
        try:
            # Check required entry points exist
            for entry_point, file_path in manifest.entry_points.items():
                full_path = plugin_path / file_path
                if not full_path.exists():
                    print(f"Missing entry point: {file_path}")
                    return False
            
            # Check mobile entry point if mobile capabilities are specified
            if manifest.mobile and "mobile" in manifest.entry_points:
                mobile_path = plugin_path / manifest.entry_points["mobile"]
                if not mobile_path.exists():
                    print(f"Missing mobile entry point: {manifest.entry_points['mobile']}")
                    return False
            
            # Install dependencies (non-blocking)
            await self.install_dependencies(plugin_path)
            
            return True
            
        except Exception as e:
            print(f"Error validating plugin: {e}")
            return False
    
    async def _git_pull(self, plugin_path: Path) -> subprocess.CompletedProcess:
        """Pull latest changes from Git repository"""
        return await asyncio.create_subprocess_exec(
            "git", "pull", "origin", "main",
            cwd=plugin_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
    
    async def discover_plugins(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Discover plugins from GitHub using search API"""
        try:
            # This would use GitHub API to search for repositories with zenos-plugin.yaml
            # For now, return empty list - this would be implemented with GitHub API
            return []
            
        except Exception as e:
            print(f"Error discovering plugins: {e}")
            return []
    
    async def load_plugin_from_local(self, local_path: Path) -> Optional[PluginEntry]:
        """Load a plugin from a local directory"""
        try:
            # Load manifest
            manifest = await self._load_manifest(local_path)
            if not manifest:
                return None
            
            # Validate plugin
            if not await self._validate_plugin(manifest, local_path):
                return None
            
            # Register plugin
            success = self.registry.register_plugin(manifest, f"local:{local_path}", local_path)
            if success:
                return self.registry.get_plugin(manifest.id)
            
            return None
            
        except Exception as e:
            print(f"Error loading local plugin: {e}")
            return None

# Convenience function
async def load_plugin_from_git(git_url: str, version: str = "main") -> Optional[PluginEntry]:
    """Load a plugin from Git URL"""
    registry = PluginRegistry()
    loader = GitPluginLoader(registry)
    return await loader.load_plugin_from_git(git_url, version)
