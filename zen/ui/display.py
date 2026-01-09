"""Display manager for zenOS - Beautiful terminal UI components."""

import random
from typing import Any, Dict, List

from rich import box
from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.layout import Layout
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

console = Console()


class DisplayManager:
    """Manages beautiful terminal displays for zenOS."""

    # Zen quotes for inspiration
    ZEN_QUOTES = [
        "The mind is everything. What you think you become.",
        "In the beginner's mind there are many possibilities.",
        "When you realize nothing is lacking, the whole world belongs to you.",
        "The only way to make sense out of change is to plunge into it.",
        "Simplicity is the ultimate sophistication.",
        "The journey of a thousand miles begins with a single step.",
        "Be water, my friend.",
        "The obstacle is the path.",
    ]

    # ASCII art logo
    LOGO = """
    ███████╗███████╗███╗   ██╗ ██████╗ ███████╗
    ╚══███╔╝██╔════╝████╗  ██║██╔═══██╗██╔════╝
      ███╔╝ █████╗  ██╔██╗ ██║██║   ██║███████╗
     ███╔╝  ██╔══╝  ██║╚██╗██║██║   ██║╚════██║
    ███████╗███████╗██║ ╚████║╚██████╔╝███████║
    ╚══════╝╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝
    """

    def __init__(self):
        """Initialize the display manager."""
        self.console = console

    def show_welcome(self):
        """Show beautiful welcome screen."""
        # Create layout
        layout = Layout()

        # Logo panel
        logo_panel = Panel(
            Align.center(Text(self.LOGO, style="cyan bold"), vertical="middle"),
            box=box.DOUBLE,
            border_style="cyan",
            padding=(1, 2),
        )

        # Random zen quote
        quote = random.choice(self.ZEN_QUOTES)
        quote_panel = Panel(
            Align.center(Text(f'"{quote}"', style="italic dim"), vertical="middle"),
            box=box.ROUNDED,
            border_style="dim",
            padding=(0, 2),
        )

        # Info panel
        info_text = Text.from_markup(
            "[bold cyan]Welcome to zenOS Chat Mode[/bold cyan]\n\n"
            "[white]Your AI assistant in the terminal[/white]\n"
            "[dim]Type [bold]/help[/bold] for commands • [bold]Ctrl+D[/bold] to exit[/dim]"
        )

        info_panel = Panel(
            Align.center(info_text, vertical="middle"),
            box=box.ROUNDED,
            border_style="green",
            padding=(1, 2),
        )

        # Combine and display
        self.console.print(logo_panel)
        self.console.print(quote_panel)
        self.console.print(info_panel)
        self.console.print()

    def show_thinking(self, message: str = "Contemplating your request..."):
        """Show a thinking animation."""
        with Progress(
            SpinnerColumn(spinner_name="dots"),
            TextColumn("[cyan]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task(message, total=None)
            return progress, task

    def show_response(self, response: str, title: str = "🧘 zenOS", format: str = "markdown"):
        """Display a response with beautiful formatting."""
        if format == "markdown":
            content = Markdown(response)
        elif format == "code":
            # Try to detect language
            content = Syntax(response, "python", theme="monokai", line_numbers=True)
        else:
            content = Text(response)

        panel = Panel(content, title=title, border_style="cyan", box=box.ROUNDED, padding=(1, 2))

        self.console.print(panel)

    def show_error(self, error: str, title: str = "❌ Error"):
        """Display an error message."""
        panel = Panel(
            Text(error, style="red"), title=title, border_style="red", box=box.HEAVY, padding=(1, 2)
        )

        self.console.print(panel)

    def show_success(self, message: str, title: str = "✅ Success"):
        """Display a success message."""
        panel = Panel(
            Text(message, style="green"),
            title=title,
            border_style="green",
            box=box.ROUNDED,
            padding=(1, 2),
        )

        self.console.print(panel)

    def show_info(self, message: str, title: str = "ℹ️ Info"):
        """Display an info message."""
        panel = Panel(
            Text(message, style="yellow"),
            title=title,
            border_style="yellow",
            box=box.ROUNDED,
            padding=(1, 2),
        )

        self.console.print(panel)

    def show_cost_breakdown(self, costs: List[Dict[str, Any]]):
        """Show a beautiful cost breakdown table."""
        table = Table(
            title="💰 Session Cost Breakdown",
            show_header=True,
            header_style="bold cyan",
            box=box.ROUNDED,
        )

        table.add_column("Time", style="dim")
        table.add_column("Model", style="cyan")
        table.add_column("Tokens", justify="right")
        table.add_column("Cost", justify="right", style="green")

        total_cost = 0.0
        for cost in costs:
            table.add_row(
                cost["timestamp"].strftime("%H:%M:%S"),
                cost["model"].split("/")[-1],
                f"{cost.get('tokens', 0):,}",
                f"${cost['cost']:.4f}",
            )
            total_cost += cost["cost"]

        table.add_section()
        table.add_row("", "[bold]Total[/bold]", "", f"[bold green]${total_cost:.4f}[/bold green]")

        self.console.print(table)

    def show_model_comparison(self):
        """Show a comparison of available models."""
        table = Table(
            title="🤖 Model Comparison",
            show_header=True,
            header_style="bold cyan",
            box=box.DOUBLE_EDGE,
        )

        table.add_column("Model", style="cyan")
        table.add_column("Speed", justify="center")
        table.add_column("Quality", justify="center")
        table.add_column("Cost", justify="center")
        table.add_column("Best For", style="dim")

        models = [
            ("Claude 3 Opus", "⭐⭐", "⭐⭐⭐⭐⭐", "💰💰💰", "Complex reasoning, debugging"),
            ("Claude 3 Sonnet", "⭐⭐⭐", "⭐⭐⭐⭐", "💰💰", "Balanced tasks, coding"),
            ("Claude 3 Haiku", "⭐⭐⭐⭐⭐", "⭐⭐⭐", "💰", "Quick queries, simple tasks"),
            ("GPT-4 Turbo", "⭐⭐⭐", "⭐⭐⭐⭐", "💰💰", "Code generation, creativity"),
            ("GPT-3.5 Turbo", "⭐⭐⭐⭐", "⭐⭐", "💰", "Fast responses, basic tasks"),
        ]

        for model, speed, quality, cost, best_for in models:
            table.add_row(model, speed, quality, cost, best_for)

        self.console.print(table)

    def show_stats(self, stats: Dict[str, Any]):
        """Show session statistics."""
        # Create stats panels
        panels = []

        # Messages panel
        msg_text = Text()
        msg_text.append(f"{stats.get('total_messages', 0)}\n", style="bold cyan")
        msg_text.append("Messages", style="dim")
        panels.append(Panel(Align.center(msg_text), box=box.ROUNDED))

        # Tokens panel
        token_text = Text()
        token_text.append(f"{stats.get('total_tokens', 0):,}\n", style="bold green")
        token_text.append("Tokens", style="dim")
        panels.append(Panel(Align.center(token_text), box=box.ROUNDED))

        # Cost panel
        cost_text = Text()
        cost_text.append(f"${stats.get('total_cost', 0):.4f}\n", style="bold yellow")
        cost_text.append("Total Cost", style="dim")
        panels.append(Panel(Align.center(cost_text), box=box.ROUNDED))

        # Time panel
        time_text = Text()
        duration = stats.get("duration", 0)
        time_text.append(f"{duration // 60}m {duration % 60}s\n", style="bold magenta")
        time_text.append("Duration", style="dim")
        panels.append(Panel(Align.center(time_text), box=box.ROUNDED))

        # Display in columns
        self.console.print(Columns(panels, equal=True, expand=True))

    def create_progress_bar(self, total: int, description: str = "Processing"):
        """Create a progress bar for long operations."""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console,
        )
