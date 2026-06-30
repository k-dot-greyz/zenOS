"""
CLI commands for PKM module.
"""

import asyncio
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .config import PKMConfig
from .extractor import GeminiExtractor
from .processor import ConversationProcessor
from .scheduler import PKMScheduler
from .storage import PKMStorage

console = Console()


@click.group()
def pkm():
    """
    PKM command-line interface group that exposes commands to extract, process, search, export, and manage scheduled jobs for Google Gemini conversation personal knowledge management.

    This Click command group wires the CLI entry point for managing conversations, the knowledge base, configuration, and scheduling operations.
    """
    pass


@pkm.command()
@click.option("--limit", "-l", type=int, help="Maximum number of conversations to extract")
@click.option("--config", "-c", type=click.Path(exists=True), help="Path to configuration file")
def extract(limit: Optional[int], config: Optional[str]):
    """
    Start extraction of conversations from Google Gemini and save them to configured storage.

    Parameters:
        limit (Optional[int]): If provided, override the configured maximum number of conversations to extract for this run.
        config (Optional[str]): Path to a PKM configuration file to load; if omitted, the default configuration is used.
    """
    config_path = Path(config) if config else None
    pkm_config = PKMConfig.load(config_path)

    if limit:
        pkm_config.max_conversations_per_run = limit

    console.print(
        Panel.fit(
            "[bold cyan]🔄 Starting Google Gemini conversation extraction...[/bold cyan]",
            border_style="cyan",
        )
    )

    async def run_extraction():
        """
        Run the conversation extraction process and print a concise summary or errors to the console.

        On success, prints a confirmation plus the number of conversations extracted, total messages, and elapsed time. On failure, prints a failure notice and each reported error.
        """
        async with GeminiExtractor(pkm_config) as extractor:
            result = await extractor.extract_conversations(limit)

            if result.success:
                console.print(f"[green]✅ Extraction completed successfully![/green]")
                console.print(f"📊 Conversations extracted: {result.conversations_extracted}")
                console.print(f"📊 Total messages: {result.total_messages}")
                console.print(f"⏱️ Duration: {result.duration:.2f} seconds")
            else:
                console.print(f"[red]❌ Extraction failed[/red]")
                for error in result.errors:
                    console.print(f"  • {error}")

    asyncio.run(run_extraction())


@pkm.command()
@click.option("--limit", "-l", type=int, default=10, help="Maximum number of conversations to show")
@click.option("--config", "-c", type=click.Path(exists=True), help="Path to configuration file")
def list_conversations(limit: int, config: Optional[str]):
    """
    List recent extracted conversations and print them as a Rich table to the console.

    Displays up to `limit` conversations with columns for ID, title (truncated to 50 characters), message count, last-updated timestamp, and status. If no conversations are found, prints a notice advising to run the extractor.

    Parameters:
        limit (int): Maximum number of conversations to display.
        config (Optional[str]): Path to a PKM config file; when None, the default configuration location is used.
    """
    config_path = Path(config) if config else None
    pkm_config = PKMConfig.load(config_path)
    storage = PKMStorage(pkm_config)

    conversations = storage.list_conversations(limit)

    if not conversations:
        console.print(
            "[yellow]No conversations found. Use 'zen pkm extract' to extract conversations.[/yellow]"
        )
        return

    table = Table(title=f"📚 Recent Conversations ({len(conversations)} shown)", show_header=True)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title", style="white")
    table.add_column("Messages", style="green", justify="right")
    table.add_column("Updated", style="blue")
    table.add_column("Status", style="yellow")

    for conv in conversations:
        table.add_row(
            conv.id[:8] + "...",
            conv.title[:50] + "..." if len(conv.title) > 50 else conv.title,
            str(len(conv.messages)),
            conv.updated_at.strftime("%Y-%m-%d %H:%M"),
            conv.status.value,
        )

    console.print(table)


@pkm.command()
@click.argument("query")
@click.option("--limit", "-l", type=int, default=10, help="Maximum number of results to show")
@click.option("--config", "-c", type=click.Path(exists=True), help="Path to configuration file")
def search(query: str, limit: int, config: Optional[str]):
    """
    Search conversations for a query and display matching conversations in a formatted table.

    Parameters:
        query (str): Search query string used to match conversations.
        limit (int): Maximum number of conversations to retrieve.
        config (Optional[str]): Path to a PKM configuration file; if None, the default configuration is used.
    """
    config_path = Path(config) if config else None
    pkm_config = PKMConfig.load(config_path)
    storage = PKMStorage(pkm_config)

    console.print(f"[cyan]🔍 Searching for: '{query}'[/cyan]")

    conversations = storage.search_conversations(query, limit)

    if not conversations:
        console.print(f"[yellow]No conversations found matching '{query}'[/yellow]")
        return

    table = Table(title=f"🔍 Search Results for '{query}'", show_header=True)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title", style="white")
    table.add_column("Messages", style="green", justify="right")
    table.add_column("Keywords", style="yellow")
    table.add_column("Updated", style="blue")

    for conv in conversations:
        keywords_str = ", ".join(conv.keywords[:3]) if conv.keywords else "None"
        table.add_row(
            conv.id[:8] + "...",
            conv.title[:40] + "..." if len(conv.title) > 40 else conv.title,
            str(len(conv.messages)),
            keywords_str,
            conv.updated_at.strftime("%Y-%m-%d"),
        )

    console.print(table)


@pkm.command()
@click.option("--config", "-c", type=click.Path(exists=True), help="Path to configuration file")
def process(config: Optional[str]):
    """
    Process stored conversations to generate and save knowledge entries.

    Loads the PKM configuration (from `config` if provided), iterates over conversations that have not been processed, processes each conversation to produce knowledge items, saves the updated conversation back to storage, and reports counts of conversations processed and knowledge entries created.

    Parameters:
        config (Optional[str]): Path to a PKM configuration file. If None, the default configuration location is used.
    """
    config_path = Path(config) if config else None
    pkm_config = PKMConfig.load(config_path)
    storage = PKMStorage(pkm_config)
    processor = ConversationProcessor(pkm_config, storage)

    console.print(
        Panel.fit(
            "[bold cyan]🔄 Processing conversations for knowledge extraction...[/bold cyan]",
            border_style="cyan",
        )
    )

    async def run_processing():
        """
        Process all conversations that lack a 'processed_at' metadata entry, persist processed conversations to storage, and print a summary.

        For each unprocessed conversation this function processes it with the ConversationProcessor, saves the processed conversation to storage, counts knowledge entries associated with that conversation, and prints totals for conversations processed and knowledge entries created.
        """
        conversations = storage.list_conversations()
        processed_count = 0
        knowledge_entries = 0

        for conversation in conversations:
            # Check if already processed
            if conversation.metadata.get("processed_at"):
                continue

            # Process the conversation
            processed_conversation = await processor.process_conversation(conversation)
            storage.save_conversation(processed_conversation)
            processed_count += 1

            # Count knowledge entries
            entries = storage.search_knowledge_entries(conversation.id)
            knowledge_entries += len(entries)

        console.print(f"[green]✅ Processing completed![/green]")
        console.print(f"📊 Conversations processed: {processed_count}")
        console.print(f"📊 Knowledge entries created: {knowledge_entries}")

    asyncio.run(run_processing())


@pkm.command()
@click.option(
    "--format", "-f", type=click.Choice(["json", "markdown"]), default="json", help="Export format"
)
@click.option("--limit", "-l", type=int, help="Maximum number of items to export")
@click.option("--config", "-c", type=click.Path(exists=True), help="Path to configuration file")
def export(format: str, limit: Optional[int], config: Optional[str]):
    """
    Export stored conversations and the knowledge base to files in the requested format.

    Exports conversations and knowledge entries using the PKM configuration and storage, prints the resulting export file paths to the console, and reports failures if an exception occurs. Supported formats include "json" and "markdown".

    Parameters:
        format (str): Output format to use for exports (e.g., "json" or "markdown").
        limit (Optional[int]): Maximum number of conversations/knowledge entries to include; if None, export all available items.
        config (Optional[str]): Path to a PKM configuration file; if None, the default configuration is used.
    """
    config_path = Path(config) if config else None
    pkm_config = PKMConfig.load(config_path)
    storage = PKMStorage(pkm_config)

    console.print(f"[cyan]📤 Exporting data in {format} format...[/cyan]")

    try:
        # Export conversations
        conv_export_path = storage.export_conversations(format, limit)

        # Export knowledge base
        kb_export_path = storage.export_knowledge_base(format, limit)

        console.print(f"[green]✅ Export completed![/green]")
        console.print(f"📁 Conversations: {conv_export_path}")
        console.print(f"📁 Knowledge Base: {kb_export_path}")

    except Exception as e:
        console.print(f"[red]❌ Export failed: {e}[/red]")


@pkm.command()
@click.option("--config", "-c", type=click.Path(exists=True), help="Path to configuration file")
def stats(config: Optional[str]):
    """
    Display PKM statistics and storage directory information.

    Loads the PKM configuration (optionally from the provided path), gathers metrics from storage, and prints a summary table with counts and settings plus the conversations, knowledge base, and exports directory paths.

    Parameters:
        config (Optional[str]): Path to a PKM configuration file; when omitted the default configuration is used.
    """
    config_path = Path(config) if config else None
    pkm_config = PKMConfig.load(config_path)
    storage = PKMStorage(pkm_config)

    stats = storage.get_statistics()
    conversations = storage.list_conversations()
    knowledge_entries = storage.list_knowledge_entries()

    total_messages = sum(len(conv.messages) for conv in conversations)
    processed_conversations = sum(1 for conv in conversations if conv.metadata.get("processed_at"))

    table = Table(title="📊 PKM Statistics", show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Total conversations", str(stats["conversations_count"]))
    table.add_row("Knowledge entries", str(stats["knowledge_entries_count"]))
    table.add_row("Total messages", str(total_messages))
    table.add_row("Processed conversations", str(processed_conversations))
    table.add_row("Storage size", f"{stats['total_size_mb']} MB")
    table.add_row("Storage format", pkm_config.storage_format)
    table.add_row("Auto-summarize", "✅" if pkm_config.auto_summarize else "❌")
    table.add_row("Extract keywords", "✅" if pkm_config.extract_keywords else "❌")
    table.add_row("Generate tags", "✅" if pkm_config.generate_tags else "❌")

    console.print(table)

    console.print(f"\n[dim]Storage directories:[/dim]")
    console.print(f"  • Conversations: {stats['conversations_dir']}")
    console.print(f"  • Knowledge Base: {stats['knowledge_base_dir']}")
    console.print(f"  • Exports: {stats['exports_dir']}")


@pkm.group()
def schedule():
    """Manage scheduled PKM jobs"""
    pass


@schedule.command("list")
@click.option("--config", "-c", type=click.Path(exists=True), help="Path to configuration file")
def schedule_list(config: Optional[str]):
    """
    List scheduled PKM jobs.

    Load the PKM configuration from the given path (or the default location) and invoke the scheduler to print the configured scheduled jobs.

    Parameters:
        config (Optional[str]): Path to a PKM configuration file. If omitted, the default configuration location is used.
    """
    config_path = Path(config) if config else None
    pkm_config = PKMConfig.load(config_path)
    scheduler = PKMScheduler(pkm_config)
    scheduler.list_jobs()


@schedule.command("run")
@click.argument("job_name")
@click.option("--config", "-c", type=click.Path(exists=True), help="Path to configuration file")
def schedule_run(job_name: str, config: Optional[str]):
    """
    Run a scheduled PKM job by name immediately.

    Parameters:
        job_name (str): The identifier of the scheduled job to run.
        config (Optional[str]): Path to a PKM configuration file; if omitted, the default config is used.
    """
    config_path = Path(config) if config else None
    pkm_config = PKMConfig.load(config_path)
    scheduler = PKMScheduler(pkm_config)

    success = scheduler.run_job(job_name)
    if success:
        console.print(f"[green]✅ Job '{job_name}' completed successfully[/green]")
    else:
        console.print(f"[red]❌ Job '{job_name}' failed or not found[/red]")


@schedule.command("start")
@click.option("--config", "-c", type=click.Path(exists=True), help="Path to configuration file")
def schedule_start(config: Optional[str]):
    """
    Start the PKM scheduler daemon (demo implementation).

    Parameters:
        config (Optional[str]): Path to a PKM configuration file. If `None`, the default configuration location is used.
    """
    config_path = Path(config) if config else None
    pkm_config = PKMConfig.load(config_path)
    scheduler = PKMScheduler(pkm_config)

    console.print("[cyan]🚀 Starting PKM scheduler daemon...[/cyan]")
    console.print(
        "[yellow]Note: This is a demo implementation. In production, this would run as a background daemon.[/yellow]"
    )

    # In a real implementation, this would start a background daemon
    scheduler.start_scheduler()


@schedule.command("stop")
@click.option("--config", "-c", type=click.Path(exists=True), help="Path to configuration file")
def schedule_stop(config: Optional[str]):
    """
    Stop the PKM scheduler daemon.

    Parameters:
        config (str | None): Path to a PKM configuration file to use; if omitted, the default configuration is loaded.
    """
    config_path = Path(config) if config else None
    pkm_config = PKMConfig.load(config_path)
    scheduler = PKMScheduler(pkm_config)

    scheduler.stop_scheduler()
    console.print("[yellow]⏹️ Scheduler stopped[/yellow]")


@pkm.command()
@click.option("--config", "-c", type=click.Path(exists=True), help="Path to configuration file")
def config_show(config: Optional[str]):
    """
    Display the current PKM configuration in a formatted table to the console.

    Parameters:
        config (Optional[str]): Path to a PKM configuration file. If omitted, the default configuration location is used.
    """
    config_path = Path(config) if config else None
    pkm_config = PKMConfig.load(config_path)

    table = Table(title="⚙️ PKM Configuration", show_header=True)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="white")

    config_dict = pkm_config.to_dict()
    for key, value in config_dict.items():
        if isinstance(value, str) and len(str(value)) > 50:
            value = str(value)[:47] + "..."
        table.add_row(key, str(value))

    console.print(table)


@pkm.command()
@click.option("--config", "-c", type=click.Path(exists=True), help="Path to configuration file")
def setup(config: Optional[str]):
    """
    Initialize PKM directories and persist the configuration.

    Loads the PKM configuration from the given path (or the default if None), ensures the PKM root, conversations, knowledge base, and exports directories exist, saves the configuration (written to pkm_dir/config.yaml), and prints next-step instructions for extracting, processing, and searching conversations.

    Parameters:
        config (Optional[str]): Path to a configuration file to load; if omitted, the default configuration location is used.
    """
    config_path = Path(config) if config else None
    pkm_config = PKMConfig.load(config_path)

    console.print(
        Panel.fit("[bold cyan]🧘 Setting up PKM module...[/bold cyan]", border_style="cyan")
    )

    # Create directories
    for directory in [
        pkm_config.pkm_dir,
        pkm_config.conversations_dir,
        pkm_config.knowledge_base_dir,
        pkm_config.exports_dir,
    ]:
        directory.mkdir(parents=True, exist_ok=True)
        console.print(f"[green]✅[/green] Created directory: {directory}")

    # Save configuration
    pkm_config.save()
    console.print(f"[green]✅[/green] Configuration saved: {pkm_config.pkm_dir / 'config.yaml'}")

    console.print(f"\n[cyan]Next steps:[/cyan]")
    console.print(f"1. Set environment variables:")
    console.print(f"   export GEMINI_SESSION_COOKIE='your_session_cookie'")
    console.print(f"   export GEMINI_CSRF_TOKEN='your_csrf_token'")
    console.print(f"2. Extract conversations: [green]zen pkm extract[/green]")
    console.print(f"3. Process knowledge: [green]zen pkm process[/green]")
    console.print(f"4. Search conversations: [green]zen pkm search 'your query'[/green]")


if __name__ == "__main__":
    pkm()
