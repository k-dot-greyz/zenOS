"""Plugin Discovery - Find and discover Git-based plugins
The Pokédex for finding new plugins!
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import aiohttp
import yaml


@dataclass
class DiscoveredPlugin:
    """A discovered plugin from GitHub"""

    repository: str
    name: str
    description: str
    author: str
    stars: int
    forks: int
    last_updated: str
    manifest: Optional[Dict[str, Any]] = None
    download_url: Optional[str] = None
    compatibility_score: float = 0.0


class PluginDiscovery:
    """Discover plugins from GitHub - The Plugin Pokédex!"""

    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token
        self.base_url = "https://api.github.com"
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"token {self.github_token}" if self.github_token else "",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "zenOS-PluginDiscovery/1.0",
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def search_plugins(
        self, query: str, category: Optional[str] = None, limit: int = 20
    ) -> List[DiscoveredPlugin]:
        """Search for plugins on GitHub"""
        try:
            if not self.session:
                raise RuntimeError("Discovery not initialized. Use async context manager.")

            # Build search query
            search_query = f"{query} zenos-plugin.yaml"
            if category:
                search_query += f" category:{category}"

            # Search repositories
            search_url = f"{self.base_url}/search/repositories"
            params = {
                "q": search_query,
                "sort": "stars",
                "order": "desc",
                "per_page": min(limit, 100),  # GitHub API limit
            }

            async with self.session.get(search_url, params=params) as response:
                if response.status != 200:
                    print(f"GitHub API error: {response.status}")
                    return []

                data = await response.json()
                repositories = data.get("items", [])

            # Process repositories
            discovered_plugins = []
            for repo in repositories:
                try:
                    plugin = await self._process_repository(repo)
                    if plugin:
                        discovered_plugins.append(plugin)
                except Exception as e:
                    print(f"Error processing repository {repo['full_name']}: {e}")
                    continue

            return discovered_plugins[:limit]

        except Exception as e:
            print(f"Error searching plugins: {e}")
            return []

    async def discover_by_category(self, category: str, limit: int = 20) -> List[DiscoveredPlugin]:
        """Discover plugins by category"""
        return await self.search_plugins("", category, limit)

    async def discover_trending(self, limit: int = 20) -> List[DiscoveredPlugin]:
        """Discover trending plugins"""
        try:
            if not self.session:
                raise RuntimeError("Discovery not initialized. Use async context manager.")

            # Search for recently updated plugins
            search_url = f"{self.base_url}/search/repositories"
            params = {
                "q": "zenos-plugin.yaml",
                "sort": "updated",
                "order": "desc",
                "per_page": min(limit, 100),
            }

            async with self.session.get(search_url, params=params) as response:
                if response.status != 200:
                    return []

                data = await response.json()
                repositories = data.get("items", [])

            # Process repositories
            discovered_plugins = []
            for repo in repositories:
                try:
                    plugin = await self._process_repository(repo)
                    if plugin:
                        discovered_plugins.append(plugin)
                except Exception as e:
                    print(f"Error processing repository {repo['full_name']}: {e}")
                    continue

            return discovered_plugins[:limit]

        except Exception as e:
            print(f"Error discovering trending plugins: {e}")
            return []

    async def discover_featured(self, limit: int = 10) -> List[DiscoveredPlugin]:
        """Discover featured/starred plugins"""
        try:
            if not self.session:
                raise RuntimeError("Discovery not initialized. Use async context manager.")

            # Search for highly starred plugins
            search_url = f"{self.base_url}/search/repositories"
            params = {
                "q": "zenos-plugin.yaml stars:>10",
                "sort": "stars",
                "order": "desc",
                "per_page": min(limit, 100),
            }

            async with self.session.get(search_url, params=params) as response:
                if response.status != 200:
                    return []

                data = await response.json()
                repositories = data.get("items", [])

            # Process repositories
            discovered_plugins = []
            for repo in repositories:
                try:
                    plugin = await self._process_repository(repo)
                    if plugin:
                        discovered_plugins.append(plugin)
                except Exception as e:
                    print(f"Error processing repository {repo['full_name']}: {e}")
                    continue

            return discovered_plugins[:limit]

        except Exception as e:
            print(f"Error discovering featured plugins: {e}")
            return []

    async def _process_repository(self, repo: Dict[str, Any]) -> Optional[DiscoveredPlugin]:
        """Process a GitHub repository to extract plugin information"""
        try:
            # Get plugin manifest
            manifest = await self._get_plugin_manifest(repo["full_name"])
            if not manifest:
                return None

            # Calculate compatibility score
            compatibility_score = self._calculate_compatibility_score(manifest)

            # Create discovered plugin
            plugin = DiscoveredPlugin(
                repository=repo["full_name"],
                name=manifest.get("name", repo["name"]),
                description=manifest.get("description", repo["description"] or ""),
                author=manifest.get("author", repo["owner"]["login"]),
                stars=repo["stargazers_count"],
                forks=repo["forks_count"],
                last_updated=repo["updated_at"],
                manifest=manifest,
                download_url=repo["clone_url"],
                compatibility_score=compatibility_score,
            )

            return plugin

        except Exception as e:
            print(f"Error processing repository {repo['full_name']}: {e}")
            return None

    async def _get_plugin_manifest(self, repo_name: str) -> Optional[Dict[str, Any]]:
        """Get plugin manifest from repository"""
        try:
            if not self.session:
                return None

            # Get manifest file content
            manifest_url = f"{self.base_url}/repos/{repo_name}/contents/zenos-plugin.yaml"

            async with self.session.get(manifest_url) as response:
                if response.status != 200:
                    return None

                data = await response.json()
                if "content" not in data:
                    return None

                # Decode base64 content
                import base64

                content = base64.b64decode(data["content"]).decode("utf-8")

                # Parse YAML
                manifest = yaml.safe_load(content)
                return manifest.get("plugin", manifest)

        except Exception as e:
            print(f"Error getting manifest for {repo_name}: {e}")
            return None

    def _calculate_compatibility_score(self, manifest: Dict[str, Any]) -> float:
        """Calculate compatibility score for a plugin"""
        try:
            score = 0.0

            # Check required fields
            required_fields = ["id", "name", "version", "author", "description", "category"]
            for field in required_fields:
                if field in manifest and manifest[field]:
                    score += 0.1

            # Check capabilities
            if "capabilities" in manifest and manifest["capabilities"]:
                score += min(len(manifest["capabilities"]) * 0.05, 0.3)

            # Check mobile support
            if "mobile" in manifest and manifest["mobile"]:
                score += 0.2

            # Check procedures
            if "procedures" in manifest and manifest["procedures"]:
                score += min(len(manifest["procedures"]) * 0.05, 0.2)

            # Check entry points
            if "entry_points" in manifest and manifest["entry_points"]:
                entry_points = manifest["entry_points"]
                if "main" in entry_points:
                    score += 0.1
                if "mobile" in entry_points:
                    score += 0.1

            return min(score, 1.0)

        except Exception as e:
            print(f"Error calculating compatibility score: {e}")
            return 0.0

    async def get_plugin_categories(self) -> List[str]:
        """Get available plugin categories"""
        try:
            if not self.session:
                return []

            # Search for plugins and extract categories
            search_url = f"{self.base_url}/search/repositories"
            params = {"q": "zenos-plugin.yaml", "sort": "stars", "order": "desc", "per_page": 100}

            async with self.session.get(search_url, params=params) as response:
                if response.status != 200:
                    return []

                data = await response.json()
                repositories = data.get("items", [])

            categories = set()
            for repo in repositories[:20]:  # Limit to avoid rate limits
                try:
                    manifest = await self._get_plugin_manifest(repo["full_name"])
                    if manifest and "category" in manifest:
                        categories.add(manifest["category"])
                except Exception:
                    continue

            return sorted(list(categories))

        except Exception as e:
            print(f"Error getting categories: {e}")
            return []

    async def get_plugin_capabilities(self) -> List[str]:
        """Get available plugin capabilities"""
        try:
            if not self.session:
                return []

            # Search for plugins and extract capabilities
            search_url = f"{self.base_url}/search/repositories"
            params = {"q": "zenos-plugin.yaml", "sort": "stars", "order": "desc", "per_page": 100}

            async with self.session.get(search_url, params=params) as response:
                if response.status != 200:
                    return []

                data = await response.json()
                repositories = data.get("items", [])

            capabilities = set()
            for repo in repositories[:20]:  # Limit to avoid rate limits
                try:
                    manifest = await self._get_plugin_manifest(repo["full_name"])
                    if manifest and "capabilities" in manifest:
                        for cap in manifest["capabilities"]:
                            capabilities.add(cap)
                except Exception:
                    continue

            return sorted(list(capabilities))

        except Exception as e:
            print(f"Error getting capabilities: {e}")
            return []


# Convenience functions
async def search_plugins(
    query: str, category: Optional[str] = None, limit: int = 20, github_token: Optional[str] = None
) -> List[DiscoveredPlugin]:
    """Search for plugins on GitHub"""
    async with PluginDiscovery(github_token) as discovery:
        return await discovery.search_plugins(query, category, limit)


async def discover_trending(
    limit: int = 20, github_token: Optional[str] = None
) -> List[DiscoveredPlugin]:
    """Discover trending plugins"""
    async with PluginDiscovery(github_token) as discovery:
        return await discovery.discover_trending(limit)


async def discover_featured(
    limit: int = 10, github_token: Optional[str] = None
) -> List[DiscoveredPlugin]:
    """Discover featured plugins"""
    async with PluginDiscovery(github_token) as discovery:
        return await discovery.discover_featured(limit)
