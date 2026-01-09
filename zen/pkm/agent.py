"""PKM Agent for zenOS - provides conversation extraction and knowledge management."""

import asyncio
from typing import Any, Dict

from rich.console import Console
from rich.table import Table

from zen.core.agent import Agent, AgentManifest
from zen.providers.openrouter import OpenRouterProvider

from .config import PKMConfig
from .extractor import GeminiExtractor
from .processor import ConversationProcessor
from .scheduler import PKMScheduler
from .storage import PKMStorage

console = Console()


class PKMAgent(Agent):
    """Personal Knowledge Management agent for zenOS."""

    def __init__(self):
        """Initialize the PKM agent and its core components.

        Creates an AgentManifest describing the agent and its prompt template, passes it to the base Agent initializer, loads PKM configuration, and constructs the storage, conversation processor, and scheduler instances used by the agent.
        """
        manifest = AgentManifest(
            name="pkm",
            description="Personal Knowledge Management - Extract and manage Google Gemini conversations",
            version="1.0.0",
            tags=["pkm", "knowledge", "conversations", "extraction", "management"],
            prompt_template="""You are a Personal Knowledge Management (PKM) assistant specialized in extracting, processing, and managing conversations from Google Gemini.

Your capabilities include:
- Extracting conversations from Google Gemini web interface
- Processing conversations to extract insights and knowledge
- Managing a personal knowledge base
- Scheduling automated extraction jobs
- Searching and organizing conversation data

Current request: {prompt}

Provide helpful guidance on PKM operations, conversation extraction, and knowledge management.""",
        )
        super().__init__(manifest)

        # Initialize PKM components
        self.config = PKMConfig.load()
        self.storage = PKMStorage(self.config)
        self.processor = ConversationProcessor(self.config, self.storage)
        self.scheduler = PKMScheduler(self.config)

    async def execute_async(self, prompt: str, variables: dict) -> str:
        """Dispatches a PKM prompt to the appropriate handler and returns the handler's response.

        Parameters
        ----------
            prompt (str): The user's PKM prompt or command string.
            variables (dict): Runtime variables or context passed to handlers.

        Returns
        -------
            str: The textual response produced by the selected handler. If an unhandled exception occurs, returns an error message beginning with "Error executing PKM command:".

        """
        try:
            # Parse the command from the prompt
            command = self._parse_command(prompt)

            if command["action"] == "extract":
                return await self._handle_extract(command, variables)
            elif command["action"] == "list":
                return await self._handle_list(command, variables)
            elif command["action"] == "search":
                return await self._handle_search(command, variables)
            elif command["action"] == "process":
                return await self._handle_process(command, variables)
            elif command["action"] == "schedule":
                return await self._handle_schedule(command, variables)
            elif command["action"] == "export":
                return await self._handle_export(command, variables)
            elif command["action"] == "stats":
                return await self._handle_stats(command, variables)
            elif command["action"] == "help":
                return await self._handle_help(command, variables)
            else:
                return await self._handle_general_query(prompt, variables)

        except Exception as e:
            return f"Error executing PKM command: {e}"

    def execute(self, prompt: str, variables: dict) -> str:
        """Execute a prompt using the PKM agent and return the agent's response.

        Parameters
        ----------
            prompt (str): The user prompt or command to execute.
            variables (dict): Optional runtime variables supplied to the execution context.

        Returns
        -------
            str: The agent's response text.

        """
        return asyncio.run(self.execute_async(prompt, variables))

    def _parse_command(self, prompt: str) -> Dict[str, Any]:
        """Determine an action and its arguments from a user PKM prompt.

        Returns:
            result (Dict[str, Any]): Mapping with keys:
                - "action": one of "extract", "list", "search", "process", "schedule", "export", "stats", "help", or "query".
                - "args": the remaining prompt text after the recognized command (for "query", the original prompt is returned).

        """
        prompt_lower = prompt.lower().strip()

        if prompt_lower.startswith("extract"):
            return {"action": "extract", "args": prompt[7:].strip()}
        elif prompt_lower.startswith("list"):
            return {"action": "list", "args": prompt[4:].strip()}
        elif prompt_lower.startswith("search"):
            return {"action": "search", "args": prompt[6:].strip()}
        elif prompt_lower.startswith("process"):
            return {"action": "process", "args": prompt[7:].strip()}
        elif prompt_lower.startswith("schedule"):
            return {"action": "schedule", "args": prompt[8:].strip()}
        elif prompt_lower.startswith("export"):
            return {"action": "export", "args": prompt[6:].strip()}
        elif prompt_lower.startswith("stats"):
            return {"action": "stats", "args": prompt[5:].strip()}
        elif prompt_lower.startswith("help"):
            return {"action": "help", "args": prompt[4:].strip()}
        else:
            return {"action": "query", "args": prompt}

    async def _handle_extract(self, command: Dict[str, Any], variables: Dict[str, Any]) -> str:
        """Extract conversations into local storage and return a human-readable extraction report.

        Reads an optional numeric limit from command["args"] to cap the number of conversations to extract, then runs the extraction using GeminiExtractor. On success returns a formatted summary with counts (extracted, processed, total messages), duration, storage location, and next-step guidance. On an extraction failure returns a formatted list of errors and warnings. On unexpected exceptions returns a concise error message containing the exception.

        Parameters
        ----------
            command (Dict[str, Any]): Parsed command dictionary; expected to contain an optional "args" entry representing a numeric limit for extraction.
            variables (Dict[str, Any]): Additional runtime variables (may be unused by this handler).

        Returns
        -------
            str: A human-readable report describing the extraction outcome (success summary, failure details, or error message).

        """
        args = command["args"]
        max_conversations = None

        # Parse arguments
        if args:
            try:
                max_conversations = int(args)
            except ValueError:
                pass

        console.print("[cyan]🔄 Starting conversation extraction...[/cyan]")

        try:
            async with GeminiExtractor(self.config) as extractor:
                result = await extractor.extract_conversations(max_conversations)

                if result.success:
                    return f"""✅ **Extraction Completed Successfully**

**Results:**
- Conversations extracted: {result.conversations_extracted}
- Conversations processed: {result.conversations_processed}
- Total messages: {result.total_messages}
- Duration: {result.duration:.2f} seconds

**Storage Location:** {self.config.conversations_dir}

**Next Steps:**
- Use `zen pkm process` to extract knowledge from conversations
- Use `zen pkm list` to view extracted conversations
- Use `zen pkm search <query>` to search through conversations"""
                else:
                    return f"""❌ **Extraction Failed**

**Errors:**
{chr(10).join(f"- {error}" for error in result.errors)}

**Warnings:**
{chr(10).join(f"- {warning}" for warning in result.warnings)}

**Troubleshooting:**
- Ensure you have valid Google Gemini session cookies
- Check your internet connection
- Verify the Gemini web interface is accessible"""

        except Exception as e:
            return f"❌ **Extraction Error:** {e}"

    async def _handle_list(self, command: Dict[str, Any], variables: Dict[str, Any]) -> str:
        """List recent conversations and present a summary.

        Parameters
        ----------
            command (Dict[str, Any]): Parsed command with an "args" entry optionally containing a numeric limit for results.
            variables (Dict[str, Any]): Execution variables and context (unused by this handler but passed through by the agent).

        Returns
        -------
            str: A user-facing summary message. The handler also prints a formatted table of recent conversations to the console and returns a short summary with next-step guidance.

        """
        args = command["args"]
        limit = 10

        # Parse limit from args
        if args:
            try:
                limit = int(args)
            except ValueError:
                pass

        conversations = self.storage.list_conversations(limit)

        if not conversations:
            return "📭 **No conversations found**\n\nUse `zen pkm extract` to extract conversations from Google Gemini."

        # Create table
        table = Table(
            title=f"📚 Recent Conversations (showing {len(conversations)})", show_header=True
        )
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

        return f"📊 **Found {len(conversations)} conversations**\n\nUse `zen pkm search <query>` to search through conversations or `zen pkm stats` for detailed statistics."

    async def _handle_search(self, command: Dict[str, Any], variables: Dict[str, Any]) -> str:
        """Search stored conversations for the provided query and display results in a formatted table.

        Parameters
        ----------
                command (Dict[str, Any]): Command dictionary; expects the search text in `command["args"]`.
                variables (Dict[str, Any]): Runtime variables or context (not required for search).

        Returns
        -------
                result (str): A user-facing summary message indicating the search outcome (error when missing query, no matches, or a summary of found conversations).

        """
        query = command["args"]

        if not query:
            return "❌ **Search query required**\n\nUsage: `zen pkm search <query>`"

        console.print(f"[cyan]🔍 Searching for: '{query}'[/cyan]")

        conversations = self.storage.search_conversations(query, limit=10)

        if not conversations:
            return f"🔍 **No conversations found matching '{query}'**\n\nTry different keywords or use `zen pkm list` to see all conversations."

        # Create table
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

        return f"📊 **Found {len(conversations)} conversations matching '{query}'**\n\nUse `zen pkm list` to see all conversations or refine your search query."

    async def _handle_process(self, command: Dict[str, Any], variables: Dict[str, Any]) -> str:
        """Process unprocessed conversations to extract knowledge, save updated conversations, and count created knowledge entries.

        The returned string is a user-facing, formatted summary that includes the number of conversations processed, the number of knowledge entries created, the knowledge base storage location, and brief next-step guidance.

        Returns:
            summary (str): Formatted summary of processing results and next steps.

        """
        console.print("[cyan]🔄 Processing conversations for knowledge extraction...[/cyan]")

        conversations = self.storage.list_conversations()
        processed_count = 0
        knowledge_entries = 0

        for conversation in conversations:
            # Check if already processed
            if conversation.metadata.get("processed_at"):
                continue

            # Process the conversation
            processed_conversation = await self.processor.process_conversation(conversation)

            # Save the processed conversation and check for failure
            if not self.storage.save_conversation(processed_conversation):
                raise RuntimeError(
                    f"Failed to persist processed conversation {conversation.id} ('{conversation.title}'). "
                    f"Storage may be unavailable or disk may be full."
                )

            processed_count += 1

            # Count knowledge entries from metadata (added during processing)
            knowledge_entries += processed_conversation.metadata.get("knowledge_entries_count", 0)

        return f"""✅ **Processing Completed**

**Results:**
- Conversations processed: {processed_count}
- Knowledge entries created: {knowledge_entries}
- Storage location: {self.config.knowledge_base_dir}

**Next Steps:**
- Use `zen pkm search <query>` to search through knowledge entries
- Use `zen pkm export` to export your knowledge base
- Use `zen pkm stats` to view detailed statistics"""

    async def _handle_schedule(self, command: Dict[str, Any], variables: Dict[str, Any]) -> str:
        """Dispatch and execute PKM scheduler commands extracted from the parsed user command.

        Supports the following subcommands in command["args"]:
        - "list": list scheduled jobs via the scheduler.
        - "start": start the scheduler (demo implementation; does not spawn a background daemon here).
        - "stop": stop the scheduler.
        - "run <job_name>": run a specific scheduled job immediately.
        - any other value: return a brief help text describing available scheduler commands and default jobs.

        Returns:
            str: A user-facing status message describing the outcome or help text for the requested scheduler action.

        """
        args = command["args"].lower().strip()

        if args == "list":
            self.scheduler.list_jobs()
            return "📅 **Scheduled Jobs Listed**\n\nUse `zen pkm schedule start` to start the scheduler daemon."

        elif args == "start":
            console.print("[cyan]🚀 Starting PKM scheduler...[/cyan]")
            # Note: In a real implementation, this would start a background daemon
            return "✅ **Scheduler Started**\n\nNote: This is a demo implementation. In production, the scheduler would run as a background daemon."

        elif args == "stop":
            self.scheduler.stop_scheduler()
            return "⏹️ **Scheduler Stopped**"

        elif args.startswith("run "):
            job_name = args[4:].strip()
            success = self.scheduler.run_job(job_name)
            if success:
                return f"✅ **Job '{job_name}' completed successfully**"
            else:
                return f"❌ **Job '{job_name}' failed or not found**"

        else:
            return """📅 **PKM Scheduler Commands**

**Available Commands:**
- `zen pkm schedule list` - List all scheduled jobs
- `zen pkm schedule start` - Start the scheduler daemon
- `zen pkm schedule stop` - Stop the scheduler daemon
- `zen pkm schedule run <job_name>` - Run a specific job immediately

**Default Jobs:**
- `extract_conversations` - Extract conversations from Google Gemini
- `process_knowledge` - Process conversations and extract knowledge
- `cleanup_old_data` - Clean up old data files"""

    async def _handle_export(self, command: Dict[str, Any], variables: Dict[str, Any]) -> str:
        """Export conversations and the knowledge base to a chosen format and return a human-readable status message.

        Parameters
        ----------
            command (Dict[str, Any]): Parsed command object; expected to contain an "args" string indicating the export format ("json", "markdown", or "md"). If empty or missing, defaults to "json".
            variables (Dict[str, Any]): Additional runtime variables (not required for export).

        Returns
        -------
            str: A formatted message describing the result. On success, includes paths to the exported conversations and knowledge base and the export directory. If the format is unsupported, returns an error message indicating valid formats. If an exception occurs during export, returns a failure message containing the exception text.

        """
        args = command["args"].lower().strip()
        format_type = "json"

        if args:
            if args in ["json", "markdown", "md"]:
                format_type = args
            else:
                return f"❌ **Invalid export format: {args}**\n\nSupported formats: json, markdown"

        console.print(f"[cyan]📤 Exporting data in {format_type} format...[/cyan]")

        try:
            # Export conversations
            conv_export_path = self.storage.export_conversations(format_type)

            # Export knowledge base
            kb_export_path = self.storage.export_knowledge_base(format_type)

            return f"""✅ **Export Completed**

**Exported Files:**
- Conversations: {conv_export_path}
- Knowledge Base: {kb_export_path}

**Export Location:** {self.config.exports_dir}

**Next Steps:**
- Use these files to backup your PKM data
- Import them into other knowledge management systems
- Share specific conversations or insights with others"""

        except Exception as e:
            return f"❌ **Export Failed:** {e}"

    async def _handle_stats(self, command: Dict[str, Any], variables: Dict[str, Any]) -> str:
        """Render PKM storage and content statistics as a formatted markdown string.

        Returns:
            A string containing a human-readable Markdown summary of storage metrics (conversation and knowledge entry counts, total size, processed conversation count), content metrics (total and average message counts), relevant directory paths (conversations, knowledge base, exports), and current configuration flags (auto-summarize, extract keywords, generate tags, storage format).

        """
        stats = self.storage.get_statistics()

        # Get additional stats
        conversations = self.storage.list_conversations()
        knowledge_entries = self.storage.list_knowledge_entries()

        total_messages = sum(len(conv.messages) for conv in conversations)
        processed_conversations = sum(
            1 for conv in conversations if conv.metadata.get("processed_at")
        )

        return f"""📊 **PKM Statistics**

**Storage:**
- Total conversations: {stats['conversations_count']}
- Knowledge entries: {stats['knowledge_entries_count']}
- Total size: {stats['total_size_mb']} MB
- Processed conversations: {processed_conversations}

**Content:**
- Total messages: {total_messages}
- Average messages per conversation: {total_messages / max(len(conversations), 1):.1f}

**Directories:**
- Conversations: {stats['conversations_dir']}
- Knowledge Base: {stats['knowledge_base_dir']}
- Exports: {stats['exports_dir']}

**Configuration:**
- Auto-summarize: {'✅' if self.config.auto_summarize else '❌'}
- Extract keywords: {'✅' if self.config.extract_keywords else '❌'}
- Generate tags: {'✅' if self.config.generate_tags else '❌'}
- Storage format: {self.config.storage_format}"""

    async def _handle_help(self, command: Dict[str, Any], variables: Dict[str, Any]) -> str:
        """Return the help text describing available PKM agent commands, scheduling controls, configuration, examples, workflow, and a demo disclaimer.

        Returns:
            help_text (str): A Markdown-formatted help message that lists core commands (extract, list, search, process, export, stats), scheduling commands, configuration notes (environment variables and config path), usage examples, a recommended workflow, and a note that the implementation is a demo.

        """
        return """🧘 **PKM Agent Help**

**Personal Knowledge Management for Google Gemini Conversations**

**Core Commands:**
- `zen pkm extract [limit]` - Extract conversations from Google Gemini
- `zen pkm list [limit]` - List all conversations
- `zen pkm search <query>` - Search through conversations
- `zen pkm process` - Process conversations and extract knowledge
- `zen pkm export [format]` - Export data (json/markdown)
- `zen pkm stats` - Show storage and processing statistics

**Scheduling Commands:**
- `zen pkm schedule list` - List scheduled jobs
- `zen pkm schedule start` - Start scheduler daemon
- `zen pkm schedule stop` - Stop scheduler daemon
- `zen pkm schedule run <job>` - Run specific job

**Configuration:**
- Set `GEMINI_SESSION_COOKIE` environment variable for authentication
- Set `GEMINI_CSRF_TOKEN` environment variable for CSRF protection
- Configuration stored in `~/.zenOS/pkm/config.yaml`

**Examples:**
- `zen pkm extract 10` - Extract up to 10 conversations
- `zen pkm search "python programming"` - Search for Python-related conversations
- `zen pkm export markdown` - Export all data as Markdown files
- `zen pkm schedule run extract_conversations` - Run extraction job immediately

**Workflow:**
1. Configure authentication (session cookies)
2. Extract conversations: `zen pkm extract`
3. Process for knowledge: `zen pkm process`
4. Search and explore: `zen pkm search <query>`
5. Export data: `zen pkm export`

**Note:** This is a demo implementation. Real Google Gemini extraction requires proper authentication and API access."""

    async def _handle_general_query(self, prompt: str, variables: Dict[str, Any]) -> str:
        """Generate expert, practical Personal Knowledge Management (PKM) guidance in response to a free-form user query.

        Parameters
        ----------
            prompt (str): The user's PKM-related question or request.
            variables (Dict[str, Any]): Optional runtime variables or context that may influence response generation.

        Returns
        -------
            str: A consolidated response containing actionable advice on PKM topics (extraction, organization, search, automation). On failure, an error message recommending `zen pkm help`.

        """
        # Use AI to provide helpful responses about PKM
        try:
            async with OpenRouterProvider() as provider:
                enhanced_prompt = f"""You are a Personal Knowledge Management (PKM) expert. The user is asking about PKM, conversation extraction, or knowledge management.

User query: {prompt}

Provide helpful, specific advice about:
- PKM best practices
- Conversation extraction techniques
- Knowledge organization strategies
- Search and discovery methods
- Automation and scheduling

Keep responses practical and actionable."""

                response = ""
                async for chunk in provider.complete(enhanced_prompt, stream=True):
                    response += chunk

                return response

        except Exception as e:
            return f"❌ **Error processing query:** {e}\n\nTry using specific PKM commands like `zen pkm help` for available operations."
