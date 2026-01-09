"""
zenOS Plugin CLI - Command-line interface for Git-based VST plugins
This is where your mobile UI connects to the actual plugin system!
"""

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.table import Table

from .plugins import (GitPluginLoader, PluginDiscovery, PluginExecutor,
                      PluginRegistry)
from .plugins.discovery import DiscoveredPlugin
from .plugins.executor import ExecutionContext

console = Console()


@click.group()
def plugins():
    """🔌 zenOS Plugin System - Git-based VST plugins for AI workflows"""
    pass


@plugins.command()
@click.argument("source")
@click.option("--version", default="main", help="Git branch or tag to use")
@click.option("--force", is_flag=True, help="Force reinstall if plugin exists")
@click.option("--local", is_flag=True, help="Install from local directory")
def install(source: str, version: str, force: bool, local: bool):
    """Install a plugin from a Git repository or local directory"""

    async def _install():
        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console
        ) as progress:
            task = progress.add_task("Installing plugin...", total=None)

            try:
                registry = PluginRegistry()
                loader = GitPluginLoader(registry)

                if local:
                    # Install from local directory
                    local_path = Path(source)
                    if not local_path.exists():
                        console.print(f"❌ Local path does not exist: {source}")
                        return

                    entry = await loader.load_plugin_from_local(local_path)
                else:
                    # Install from Git repository
                    # Check if plugin already exists
                    plugin_id = source.split("/")[-1].replace(".git", "")
                    if not force and registry.get_plugin(plugin_id):
                        if not Confirm.ask("Plugin already exists. Reinstall?"):
                            console.print("❌ Installation cancelled")
                            return

                    # Load plugin
                    entry = await loader.load_plugin_from_git(source, version)

                if entry:
                    progress.update(task, description="✅ Plugin installed successfully!")
                    console.print(f"🎉 Installed: {entry.manifest.name} ({entry.manifest.id})")
                    console.print(f"📝 Description: {entry.manifest.description}")
                    console.print(f"🔧 Capabilities: {', '.join(entry.manifest.capabilities)}")
                else:
                    progress.update(task, description="❌ Installation failed")
                    console.print("❌ Failed to install plugin")

            except Exception as e:
                progress.update(task, description="❌ Installation failed")
                console.print(f"❌ Error: {e}")

    asyncio.run(_install())


@plugins.command()
def list():
    """List all installed plugins"""
    registry = PluginRegistry()
    plugins = registry.plugins

    if not plugins:
        console.print("📭 No plugins installed")
        return

    table = Table(title="🔌 Installed Plugins")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Version", style="yellow")
    table.add_column("Category", style="blue")
    table.add_column("Status", style="red")
    table.add_column("Usage", style="magenta")

    for entry in plugins.values():
        status = "🟢 Active" if entry.is_active else "🔴 Inactive"
        table.add_row(
            entry.manifest.id,
            entry.manifest.name,
            entry.manifest.version,
            entry.manifest.category,
            status,
            str(entry.usage_count),
        )

    console.print(table)


@plugins.command()
@click.argument("plugin_id")
def info(plugin_id: str):
    """Show detailed information about a plugin"""
    registry = PluginRegistry()
    entry = registry.get_plugin(plugin_id)

    if not entry:
        console.print(f"❌ Plugin '{plugin_id}' not found")
        return

    # Create info panel
    info_text = f"""
[bold green]{entry.manifest.name}[/bold green] ({entry.manifest.id})
[bold]Version:[/bold] {entry.manifest.version}
[bold]Author:[/bold] {entry.manifest.author}
[bold]Description:[/bold] {entry.manifest.description}
[bold]Category:[/bold] {entry.manifest.category}
[bold]Capabilities:[/bold] {', '.join(entry.manifest.capabilities)}
[bold]Status:[/bold] {'🟢 Active' if entry.is_active else '🔴 Inactive'}
[bold]Usage Count:[/bold] {entry.usage_count}
[bold]Rarity:[/bold] {entry.rarity}
[bold]Overall Score:[/bold] {entry.overall_score:.1f}
[bold]Git URL:[/bold] {entry.git_url}
[bold]Local Path:[/bold] {entry.local_path}
[bold]Installed:[/bold] {entry.installed_at.strftime('%Y-%m-%d %H:%M:%S')}
[bold]Last Updated:[/bold] {entry.last_updated.strftime('%Y-%m-%d %H:%M:%S')}
"""

    console.print(Panel(info_text, title="🔌 Plugin Information", border_style="blue"))

    # Show procedures
    if entry.manifest.procedures:
        console.print("\n[bold]Available Procedures:[/bold]")
        for proc in entry.manifest.procedures:
            console.print(f"  • {proc['id']}: {proc['name']}")


@plugins.command()
@click.argument("plugin_id")
def remove(plugin_id: str):
    """Remove a plugin"""
    registry = PluginRegistry()
    entry = registry.get_plugin(plugin_id)

    if not entry:
        console.print(f"❌ Plugin '{plugin_id}' not found")
        return

    if Confirm.ask(f"Remove plugin '{entry.manifest.name}'?"):
        if registry.unregister_plugin(plugin_id):
            console.print(f"✅ Removed plugin: {entry.manifest.name}")
        else:
            console.print("❌ Failed to remove plugin")
    else:
        console.print("❌ Removal cancelled")


@plugins.command()
@click.argument("plugin_id")
def test(plugin_id: str):
    """Test a plugin with sample data"""

    async def _test():
        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console
        ) as progress:
            task = progress.add_task("Testing plugin...", total=None)

            try:
                registry = PluginRegistry()
                executor = PluginExecutor(registry)

                result = await executor.test_plugin(plugin_id)

                if result.success:
                    progress.update(task, description="✅ Plugin test successful!")
                    console.print(f"✅ Plugin test passed!")
                    console.print(f"📊 Data: {result.data}")
                    if result.metadata:
                        console.print(f"📈 Metadata: {result.metadata}")
                else:
                    progress.update(task, description="❌ Plugin test failed")
                    console.print(f"❌ Plugin test failed: {result.error}")

            except Exception as e:
                progress.update(task, description="❌ Plugin test failed")
                console.print(f"❌ Error: {e}")

    asyncio.run(_test())


@plugins.command()
@click.argument("plugin_id")
@click.argument("procedure_id")
@click.argument("input_data")
@click.option("--user-id", default="cli_user", help="User ID for execution context")
@click.option("--session-id", default="cli_session", help="Session ID for execution context")
def execute(plugin_id: str, procedure_id: str, input_data: str, user_id: str, session_id: str):
    """Execute a specific procedure from a plugin"""

    async def _execute():
        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console
        ) as progress:
            task = progress.add_task("Executing procedure...", total=None)

            try:
                registry = PluginRegistry()
                executor = PluginExecutor(registry)

                # Parse input data
                try:
                    parsed_input = json.loads(input_data)
                except json.JSONDecodeError:
                    parsed_input = input_data

                # Create execution context
                context = ExecutionContext(
                    user_id=user_id,
                    session_id=session_id,
                    device_info={"platform": "cli", "version": "1.0.0"},
                )

                result = await executor.execute_plugin(
                    plugin_id, procedure_id, parsed_input, context
                )

                if result.success:
                    progress.update(task, description="✅ Procedure executed successfully!")
                    console.print(f"✅ Procedure executed successfully!")
                    console.print(f"📊 Result: {result.data}")
                    if result.metadata:
                        console.print(f"📈 Metadata: {result.metadata}")
                else:
                    progress.update(task, description="❌ Procedure execution failed")
                    console.print(f"❌ Procedure execution failed: {result.error}")

            except Exception as e:
                progress.update(task, description="❌ Procedure execution failed")
                console.print(f"❌ Error: {e}")

    asyncio.run(_execute())


@plugins.command()
@click.argument("query")
@click.option("--category", help="Filter by category")
@click.option("--limit", default=10, help="Maximum number of results")
def search(query: str, category: Optional[str], limit: int):
    """Search for plugins on GitHub"""

    async def _search():
        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console
        ) as progress:
            task = progress.add_task("Searching plugins...", total=None)

            try:
                async with PluginDiscovery() as discovery:
                    plugins = await discovery.search_plugins(query, category, limit)

                if plugins:
                    progress.update(task, description="✅ Search completed!")

                    table = Table(title=f"🔍 Search Results for '{query}'")
                    table.add_column("Repository", style="cyan")
                    table.add_column("Name", style="green")
                    table.add_column("Description", style="yellow")
                    table.add_column("Stars", style="blue")
                    table.add_column("Compatibility", style="magenta")

                    for plugin in plugins:
                        table.add_row(
                            plugin.repository,
                            plugin.name,
                            (
                                plugin.description[:50] + "..."
                                if len(plugin.description) > 50
                                else plugin.description
                            ),
                            str(plugin.stars),
                            f"{plugin.compatibility_score:.1f}",
                        )

                    console.print(table)
                else:
                    progress.update(task, description="❌ No plugins found")
                    console.print("❌ No plugins found")

            except Exception as e:
                progress.update(task, description="❌ Search failed")
                console.print(f"❌ Error: {e}")

    asyncio.run(_search())


@plugins.command()
@click.option("--limit", default=10, help="Maximum number of results")
def trending(limit: int):
    """Discover trending plugins"""

    async def _trending():
        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console
        ) as progress:
            task = progress.add_task("Discovering trending plugins...", total=None)

            try:
                async with PluginDiscovery() as discovery:
                    plugins = await discovery.discover_trending(limit)

                if plugins:
                    progress.update(task, description="✅ Trending plugins found!")

                    table = Table(title="🔥 Trending Plugins")
                    table.add_column("Repository", style="cyan")
                    table.add_column("Name", style="green")
                    table.add_column("Description", style="yellow")
                    table.add_column("Stars", style="blue")
                    table.add_column("Updated", style="magenta")

                    for plugin in plugins:
                        table.add_row(
                            plugin.repository,
                            plugin.name,
                            (
                                plugin.description[:50] + "..."
                                if len(plugin.description) > 50
                                else plugin.description
                            ),
                            str(plugin.stars),
                            plugin.last_updated[:10],
                        )

                    console.print(table)
                else:
                    progress.update(task, description="❌ No trending plugins found")
                    console.print("❌ No trending plugins found")

            except Exception as e:
                progress.update(task, description="❌ Discovery failed")
                console.print(f"❌ Error: {e}")

    asyncio.run(_trending())


@plugins.command()
def stats():
    """Show plugin collection statistics"""
    registry = PluginRegistry()
    stats = registry.get_collection_stats()

    console.print(
        Panel(
            f"""
[bold]Total Plugins:[/bold] {stats['total_plugins']}
[bold]Active Plugins:[/bold] {stats['active_plugins']}
[bold]Total Usage:[/bold] {stats['total_usage']}

[bold]Categories:[/bold]
{chr(10).join(f"  • {cat}: {count}" for cat, count in stats['categories'].items())}

[bold]Capabilities:[/bold]
{chr(10).join(f"  • {cap}: {count}" for cap, count in stats['capabilities'].items())}

[bold]Rarities:[/bold]
{chr(10).join(f"  • {rarity}: {count}" for rarity, count in stats['rarities'].items())}
""",
            title="📊 Plugin Collection Statistics",
            border_style="green",
        )
    )


if __name__ == "__main__":
    plugins()
