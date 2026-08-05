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
    DEFAULT_USER_INSTALL,
    VISUAL_WIKI_REPO,
    VisualWikiPaths,
    dev_master_root,
    dev_master_wiki_candidates,
    locate_visual_wiki,
    visual_wiki_paths,
)
from .pipe import default_base_url, fetch_handshake, pipe_url

console = Console()


def _require_checkout(paths: VisualWikiPaths) -> None:
    if paths.is_checkout:
        return
    console.print(
        "[red]Visual Wiki is not installed.[/red] Run [cyan]zen wiki setup[/cyan] "
        "(clone) or point [cyan]ZEN_VISUAL_WIKI_PATH[/cyan] at a dev-master submodule checkout."
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
    "--into",
    "install_dir",
    type=click.Path(file_okay=False, dir_okay=True),
    help=f"Clone target (default: {DEFAULT_USER_INSTALL})",
)
@click.option(
    "--skip-clone",
    is_flag=True,
    help="Only npm install when a checkout is already resolved",
)
@click.option("--skip-npm", is_flag=True, help="Skip npm install")
def setup(install_dir: Optional[str], skip_clone: bool, skip_npm: bool):
    """
    Clone the standalone visual-wiki repo and install Node dependencies.

    zenOS does not vendor visual-wiki; dev-master tracks it as a submodule at
    dex/09-repos/visual-wiki when that wiring lands. Set ZEN_VISUAL_WIKI_PATH or
    DEV_MASTER_ROOT to use an existing checkout instead of cloning.
    """
    found, source = locate_visual_wiki()
    wiki_root: Optional[Path] = found

    if not wiki_root and not skip_clone:
        wiki_root = Path(install_dir).expanduser() if install_dir else DEFAULT_USER_INSTALL
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
        source = str(wiki_root)
        console.print(
            "[dim]Tip: export ZEN_VISUAL_WIKI_PATH="
            f'"{wiki_root}"[/dim] [dim]to pin this checkout.[/dim]'
        )
    elif wiki_root:
        console.print(f"Using existing checkout ({source}): {wiki_root}")
    else:
        console.print("[red]No checkout found and --skip-clone was set.[/red]")
        sys.exit(1)

    paths = VisualWikiPaths(
        root=wiki_root,
        resources_file=wiki_root / "resources.json",
        package_json=wiki_root / "package.json",
        source=source or "setup",
    )
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
    resources = load_resources(paths) if paths.is_checkout else []

    table = Table(title="Visual Wiki")
    table.add_column("Key", style="cyan")
    table.add_column("Value")
    table.add_row("Root", str(paths.root))
    table.add_row("Source", paths.source)
    table.add_row("Checkout", "yes" if paths.is_checkout else "no")
    table.add_row("resources.json", "yes" if paths.resources_file.is_file() else "no")
    table.add_row("Resources", str(len(resources)))
    table.add_row("npm", shutil.which("npm") or "not found")

    dm = dev_master_root()
    table.add_row("dev-master", str(dm) if dm else "not found")
    for candidate in dev_master_wiki_candidates():
        try:
            label = candidate.relative_to(dm) if dm else candidate
        except ValueError:
            label = candidate
        present = "yes" if (candidate / "package.json").is_file() else "no"
        table.add_row(f"  {label}", present)

    console.print(table)
    if not paths.is_checkout:
        console.print(
            "\n[dim]visual-wiki is a separate repo. Clone with[/dim] "
            "[cyan]zen wiki setup[/cyan][dim], use dev-master's submodule when available, "
            "or set ZEN_VISUAL_WIKI_PATH.[/dim]"
        )


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
    paths = visual_wiki_paths()
    _require_checkout(paths)
    out = Path(output_dir) if output_dir else None
    written = write_agent_context(output_dir=out, paths=paths)
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
