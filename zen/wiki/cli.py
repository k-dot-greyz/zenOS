"""CLI for Visual Wiki — knowledge garden integration."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .export import (
    build_agent_export,
    format_agent_prompt,
    load_resources,
    write_agent_context,
)
from .paths import (
    VISUAL_WIKI_REPO,
    VisualWikiPaths,
    visual_wiki_paths,
)
from .pipe import default_base_url, fetch_handshake, pipe_url

console = Console()


def _require_checkout(paths: VisualWikiPaths) -> None:
    if paths.is_checkout:
        return
    console.print(
        "[red]Visual Wiki is not installed.[/red] Run [cyan]zen wiki setup[/cyan] first."
    )
    sys.exit(1)


def _run_npm(args: list[str], cwd: Path, env: Optional[dict] = None) -> int:
    npm = shutil.which("npm")
    if not npm:
        console.print("[red]npm not found.[/red] Install Node.js to run Visual Wiki.")
        return 1
    merged = {**os.environ, **(env or {})}
    result = subprocess.run([npm, *args], cwd=str(cwd), env=merged)
    return result.returncode


@click.group()
def wiki():
    """🌿 Visual Wiki — curated knowledge garden for AI agents."""
    pass


@wiki.command("setup")
@click.option(
    "--clone",
    is_flag=True,
    help="Clone into ~/.zenOS/visual-wiki instead of using the git submodule",
)
@click.option("--skip-npm", is_flag=True, help="Skip npm install")
def setup(clone: bool, skip_npm: bool):
    """Initialize Visual Wiki (submodule or clone) and install Node dependencies."""
    zenos_root = Path.cwd()
    if (zenos_root / "zen" / "cli.py").is_file():
        wiki_root = zenos_root / "integrations" / "visual-wiki"
    else:
        wiki_root = resolve_visual_wiki_root()

    if clone:
        wiki_root = Path.home() / ".zenOS" / "visual-wiki"
        wiki_root.parent.mkdir(parents=True, exist_ok=True)
        if not (wiki_root / "package.json").is_file():
            console.print(f"Cloning Visual Wiki to {wiki_root}...")
            result = subprocess.run(
                ["git", "clone", "--depth", "1", VISUAL_WIKI_REPO, str(wiki_root)],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                console.print(f"[red]Clone failed:[/red] {result.stderr}")
                sys.exit(1)
        os.environ["ZEN_VISUAL_WIKI_PATH"] = str(wiki_root)
    else:
        wiki_root = zenos_root / "integrations" / "visual-wiki"
        if not (wiki_root / "package.json").is_file():
            console.print("Initializing git submodule...")
            result = subprocess.run(
                [
                    "git",
                    "submodule",
                    "update",
                    "--init",
                    "--recursive",
                    "integrations/visual-wiki",
                ],
                cwd=str(zenos_root),
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                console.print(f"[red]Submodule init failed:[/red] {result.stderr}")
                sys.exit(1)

    paths = visual_wiki_paths(zenos_root)
    if not paths.is_checkout:
        console.print("[red]Visual Wiki checkout not found after setup.[/red]")
        sys.exit(1)

    if skip_npm:
        console.print("[green]✓[/green] Visual Wiki ready (skipped npm install).")
        return

    console.print("Installing npm dependencies...")
    code = _run_npm(["install"], paths.root)
    if code != 0:
        sys.exit(code)
    console.print(f"[green]✓[/green] Visual Wiki ready at {paths.root}")


@wiki.command("path")
def show_path():
    """Print the resolved Visual Wiki root directory."""
    paths = visual_wiki_paths()
    console.print(str(paths.root))


@wiki.command("status")
def status():
    """Show Visual Wiki install and resource summary."""
    paths = visual_wiki_paths()
    resources = load_resources(paths)

    table = Table(title="Visual Wiki")
    table.add_column("Key", style="cyan")
    table.add_column("Value")
    table.add_row("Root", str(paths.root))
    table.add_row("Checkout", "yes" if paths.is_checkout else "no")
    table.add_row("resources.json", "yes" if paths.resources_file.is_file() else "no")
    table.add_row("Resources", str(len(resources)))
    table.add_row("npm", shutil.which("npm") or "not found")
    console.print(table)


@wiki.command("dev")
@click.option("--port", "-p", default=3000, show_default=True, type=int)
def dev(port: int):
    """Start the Visual Wiki Next.js dev server."""
    paths = visual_wiki_paths()
    _require_checkout(paths)
    console.print(
        Panel.fit(
            f"[bold cyan]🌿 Visual Wiki[/bold cyan]\nhttp://localhost:{port}",
            border_style="cyan",
        )
    )
    code = _run_npm(["run", "dev"], paths.root, env={"PORT": str(port)})
    sys.exit(code)


@wiki.command("build")
def build():
    """Run a production build of Visual Wiki."""
    paths = visual_wiki_paths()
    _require_checkout(paths)
    code = _run_npm(["run", "build"], paths.root)
    sys.exit(code)


@wiki.command("export")
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False, writable=True),
    help="Write JSON export to this file (stdout if omitted)",
)
def export_cmd(output: Optional[str]):
    """Export curated resources as agent-ready JSON."""
    resources = load_resources()
    payload = build_agent_export(resources)
    text = json.dumps(payload, indent=2)
    if output:
        Path(output).write_text(text, encoding="utf-8")
        console.print(f"[green]✓[/green] Wrote {output}")
    else:
        console.print(text)


@wiki.command("prompt")
def prompt_cmd():
    """Print the agent-ready text summary of curated resources."""
    resources = load_resources()
    console.print(format_agent_prompt(resources))


@wiki.command("sync")
@click.option(
    "--output-dir",
    "-d",
    type=click.Path(file_okay=False, writable=True),
    help="Directory for visual-wiki.json and visual-wiki-prompt.txt",
)
def sync(output_dir: Optional[str]):
    """Sync exports to ~/.zenOS/context for agent context hydration."""
    out = Path(output_dir) if output_dir else None
    written = write_agent_context(output_dir=out)
    console.print("[green]✓[/green] Agent context updated:")
    for label, path in written.items():
        console.print(f"  {label}: {path}")


@wiki.command("pull")
@click.option(
    "--base-url",
    default=None,
    help="Visual Wiki origin (default: ZEN_VISUAL_WIKI_URL or http://localhost:3000)",
)
def pull(base_url: Optional[str]):
    """Fetch /api/pipe handshake from a running Visual Wiki instance."""
    try:
        data = fetch_handshake(base_url)
    except Exception as exc:
        console.print(
            f"[red]Pull failed:[/red] {exc}\n"
            "Start the app with [cyan]zen wiki dev[/cyan] first."
        )
        sys.exit(1)
    console.print(
        Panel.fit(
            f"status={data.get('status')} total={data.get('total')} "
            f"fingerprint={str(data.get('fingerprint', ''))[:48]}…",
            title="Visual Wiki handshake",
            border_style="cyan",
        )
    )


@wiki.command("pipe")
@click.argument("url")
@click.option(
    "--base-url",
    default=None,
    help="Visual Wiki origin (default: ZEN_VISUAL_WIKI_URL or http://localhost:3000)",
)
@click.option("--type", "resource_type", default=None, help="Pipe type hint (e.g. web)")
def pipe_cmd(url: str, base_url: Optional[str], resource_type: Optional[str]):
    """Ingest a URL into the garden via /api/pipe (dev server must be running)."""
    try:
        result = pipe_url(url, base_url=base_url, resource_type=resource_type)
    except Exception as exc:
        console.print(f"[red]Pipe failed:[/red] {exc}")
        sys.exit(1)
    method = result.get("method", "unknown")
    resource = result.get("resource", {})
    title = resource.get("title", url)
    console.print(f"[green]✓[/green] Ingested via {method}: {title}")
    console.print(
        f"[dim]Then run[/dim] [cyan]zen wiki sync[/cyan] "
        f"[dim]to refresh agent context ({default_base_url()})[/dim]"
    )
