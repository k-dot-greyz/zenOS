#!/usr/bin/env python3
"""
zenOS CLI - The main command-line interface for zenOS.

Usage:
    zen <agent> "your prompt"
    zen --list
    zen --create <agent>
"""

import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.syntax import Syntax

from zen.core.launcher import Launcher
from zen.core.agent import AgentRegistry
from zen.utils.config import Config
from zen import __version__

console = Console()


@click.command()
@click.argument("agent", required=False)
@click.argument("prompt", required=False)
@click.option("--list", "list_agents", is_flag=True, help="List all available agents")
@click.option("--create", help="Create a new agent from template")
@click.option("--vars", help="Variables as JSON string or key=value pairs")
@click.option("--no-critique", is_flag=True, help="Disable auto-critique")
@click.option("--upgrade-only", is_flag=True, help="Only upgrade the prompt, don't execute")
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.option("--version", is_flag=True, help="Show version")
@click.option("--chat", is_flag=True, help="Start interactive chat mode")
def main(
    agent: Optional[str],
    prompt: Optional[str],
    list_agents: bool,
    create: Optional[str],
    vars: Optional[str],
    no_critique: bool,
    upgrade_only: bool,
    debug: bool,
    version: bool,
    chat: bool,
) -> None:
    """
    🧘 zenOS - The Zen of AI Workflow Orchestration
    
    Run AI agents with zen-like simplicity.
    
    Examples:
        zen chat                      # Start interactive chat mode
        zen troubleshoot "fix my git issue"
        zen critic "review this prompt"
        zen --list
        zen --create my-agent
    """
    
    if version:
        console.print(f"[cyan]zenOS version {__version__}[/cyan]")
        return
    
    if chat or (agent and agent == "chat"):
        # Start interactive chat mode
        import asyncio
        from zen.ui.interactive import InteractiveChat
        
        chat_session = InteractiveChat()
        asyncio.run(chat_session.start())
        return
    
    if list_agents:
        show_agents()
        return
    
    if create:
        create_agent(create)
        return
    
    if not agent:
        console.print("[red]Error:[/red] Please specify an agent or use --chat for interactive mode")
        console.print("\n[dim]Usage: zen chat  OR  zen <agent> \"your prompt\"[/dim]")
        sys.exit(1)
    
    if not prompt and not upgrade_only:
        console.print("[red]Error:[/red] Please provide a prompt")
        console.print("\n[dim]Usage: zen <agent> \"your prompt\"[/dim]")
        sys.exit(1)
    
    # Parse variables
    variables = parse_variables(vars) if vars else {}
    
    # Run the agent
    run_agent(
        agent=agent,
        prompt=prompt or "",
        variables=variables,
        no_critique=no_critique,
        upgrade_only=upgrade_only,
        debug=debug,
    )


def show_agents() -> None:
    """Display all available agents in a beautiful table."""
    registry = AgentRegistry()
    agents = registry.list_agents()
    
    if not agents:
        console.print("[yellow]No agents found.[/yellow]")
        console.print("\nCreate your first agent with: [cyan]zen --create my-agent[/cyan]")
        return
    
    table = Table(title="🤖 Available Agents", show_header=True, header_style="bold cyan")
    table.add_column("Agent", style="green", no_wrap=True)
    table.add_column("Description", style="white")
    table.add_column("Type", style="yellow")
    
    for agent_info in agents:
        table.add_row(
            agent_info["name"],
            agent_info.get("description", "No description"),
            agent_info.get("type", "custom"),
        )
    
    console.print(table)
    console.print("\n[dim]Run an agent: zen <agent> \"your prompt\"[/dim]")


def create_agent(name: str) -> None:
    """Create a new agent from template."""
    console.print(f"[cyan]Creating new agent: {name}[/cyan]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Setting up agent template...", total=None)
        
        registry = AgentRegistry()
        try:
            agent_path = registry.create_agent(name)
            progress.update(task, completed=True)
            
            console.print(f"[green]✓[/green] Agent created at: {agent_path}")
            console.print(f"\nEdit your agent configuration and run:")
            console.print(f"[cyan]zen {name} \"your prompt\"[/cyan]")
            
        except Exception as e:
            progress.update(task, completed=True)
            console.print(f"[red]✗[/red] Failed to create agent: {e}")
            sys.exit(1)


def parse_variables(vars_str: str) -> Dict[str, Any]:
    """Parse variables from string input."""
    # Try JSON first
    try:
        return json.loads(vars_str)
    except json.JSONDecodeError:
        pass
    
    # Try key=value pairs
    variables = {}
    for pair in vars_str.split(","):
        if "=" in pair:
            key, value = pair.split("=", 1)
            variables[key.strip()] = value.strip()
    
    return variables


def run_agent(
    agent: str,
    prompt: str,
    variables: Dict[str, Any],
    no_critique: bool,
    upgrade_only: bool,
    debug: bool,
) -> None:
    """Run an agent with the given prompt."""
    console.print(Panel.fit(
        f"[bold cyan]🧘 Running Agent:[/bold cyan] {agent}",
        border_style="cyan",
    ))
    
    launcher = Launcher(debug=debug)
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Load agent
            task = progress.add_task("Loading agent...", total=None)
            launcher.load_agent(agent)
            progress.update(task, completed=True)
            
            # Auto-critique unless disabled
            if not no_critique:
                task = progress.add_task("Enhancing prompt with auto-critique...", total=None)
                prompt = launcher.critique_prompt(prompt)
                progress.update(task, completed=True)
                
                if upgrade_only:
                    console.print("\n[green]✓[/green] Prompt upgraded successfully!")
                    console.print(Panel(prompt, title="Enhanced Prompt", border_style="green"))
                    return
            
            # Execute agent
            task = progress.add_task("Executing agent...", total=None)
            result = launcher.execute(prompt, variables)
            progress.update(task, completed=True)
        
        # Display result
        console.print("\n[green]✓[/green] Agent completed successfully!")
        
        if isinstance(result, str):
            console.print(Panel(result, title="Result", border_style="green"))
        else:
            # Pretty print JSON/dict results
            syntax = Syntax(
                json.dumps(result, indent=2),
                "json",
                theme="monokai",
                line_numbers=False,
            )
            console.print(Panel(syntax, title="Result", border_style="green"))
            
    except Exception as e:
        console.print(f"\n[red]✗[/red] Agent failed: {e}")
        if debug:
            import traceback
            console.print("[dim]" + traceback.format_exc() + "[/dim]")
        sys.exit(1)


if __name__ == "__main__":
    main()
