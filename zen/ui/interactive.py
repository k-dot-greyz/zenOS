"""Interactive chat mode for zenOS - The zen way to talk to AI.
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from zen.core.context import AgentPersonality, ContextManager
from zen.providers.openrouter import OpenRouterProvider
from zen.ui.display import DisplayManager
from zen.utils.config import Config

console = Console()


# Custom style for prompt_toolkit
style = Style.from_dict(
    {
        "prompt": "#00aa00 bold",
        "input": "#ffffff",
        "command": "#0088ff",
        "meta": "#888888",
    }
)


class ModelCompleter(Completer):
    """Custom completer for model names."""

    def __init__(self):
        self.models = [
            "claude-3-opus",
            "claude-3-sonnet",
            "claude-3-haiku",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
            "mixtral-8x7b",
            "llama-2-70b",
        ]

    def get_completions(self, document, complete_event):
        word = document.get_word_before_cursor()
        for model in self.models:
            if model.startswith(word):
                yield Completion(model, start_position=-len(word))


class InteractiveChat:
    """Interactive chat interface for zenOS.

    Features:
    - Beautiful terminal UI with Rich
    - Conversation history
    - Model switching on the fly
    - File context loading
    - Cost tracking
    - Keyboard shortcuts
    """

    def __init__(self):
        """Initialize the interactive chat."""
        self.config = Config()
        self.provider = None
        self.display = DisplayManager()
        self.context = ContextManager()  # Project and personality awareness
        self.session_id = None
        self.current_model = self.config.config.default_model
        self.conversation_history = []
        self.total_cost = 0.0
        self.context_files = []

        # Setup prompt session
        self.prompt_session = PromptSession(
            history=FileHistory(str(Path.home() / ".zenOS" / "chat_history")),
            auto_suggest=AutoSuggestFromHistory(),
            style=style,
            multiline=False,
            complete_while_typing=True,
        )

        # Setup key bindings
        self.kb = KeyBindings()
        self._setup_keybindings()

        # Commands
        self.commands = {
            "/help": self.show_help,
            "/exit": self.exit_chat,
            "/quit": self.exit_chat,
            "/clear": self.clear_screen,
            "/history": self.show_history,
            "/model": self.switch_model,
            "/models": self.list_models,
            "/context": self.add_context,
            "/cost": self.show_cost,
            "/save": self.save_conversation,
            "/reset": self.reset_conversation,
            "/debug": self.toggle_debug,
            "/personality": self.switch_personality,
            "/personas": self.list_personalities,
            "/project": self.show_project_context,
            "/git": self.show_git_context,
            "/genesis": self.show_genesis_wisdom,
        }

    def _setup_keybindings(self):
        """Setup keyboard shortcuts."""

        @self.kb.add("c-c")
        def _(event):
            """Ctrl+C to cancel current input."""
            event.app.current_buffer.text = ""

        @self.kb.add("c-d")
        def _(event):
            """Ctrl+D to exit."""
            event.app.exit()

        @self.kb.add("c-l")
        def _(event):
            """Ctrl+L to clear screen."""
            console.clear()

    async def start(self):
        """Start the interactive chat session."""
        # Initialize provider
        if not self.config.config.openrouter_api_key:
            console.print("[red]Error: No OpenRouter API key configured![/red]")
            console.print("Set OPENROUTER_API_KEY environment variable or add to .env file")
            return

        self.provider = OpenRouterProvider(self.config.config.openrouter_api_key)

        # Show welcome message
        self.display.show_welcome()

        # Main chat loop
        await self.chat_loop()

    async def chat_loop(self):
        """Main chat interaction loop."""
        while True:
            try:
                # Get user input with fancy prompt
                user_input = await self.get_user_input()

                if not user_input:
                    continue

                # Handle commands
                if user_input.startswith("/"):
                    await self.handle_command(user_input)
                    continue

                # Add to history
                self.conversation_history.append(
                    {"role": "user", "content": user_input, "timestamp": datetime.now()}
                )

                # Get AI response
                await self.get_ai_response(user_input)

            except KeyboardInterrupt:
                continue
            except EOFError:
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                if self.config.config.debug:
                    import traceback

                    console.print(traceback.format_exc())

    async def get_user_input(self) -> str:
        """Get input from user with beautiful prompt."""
        # Create fancy prompt with model info
        model_name = self.current_model.split("/")[-1]
        prompt_text = HTML(
            f"<ansigreen>🧘 zen</ansigreen> "
            f"<ansigray>[{model_name}]</ansigray> "
            f"<ansiwhite>›</ansiwhite> "
        )

        # Get input in async way
        loop = asyncio.get_event_loop()
        future = loop.create_future()

        def get_input():
            try:
                result = self.prompt_session.prompt(
                    prompt_text,
                    key_bindings=self.kb,
                )
                future.set_result(result)
            except (EOFError, KeyboardInterrupt) as e:
                future.set_exception(e)

        # Run in thread to not block async
        await loop.run_in_executor(None, get_input)

        return await future

    async def get_ai_response(self, prompt: str):
        """Get response from AI and display it beautifully."""
        # Show thinking animation
        with console.status("[cyan]Contemplating your request...[/cyan]", spinner="dots"):
            # Add context if any
            full_prompt = self._build_prompt_with_context(prompt)

            # Estimate cost
            estimated_cost = self.provider.estimate_cost(full_prompt, self.current_model)

            # Get response
            response_text = ""

            async with self.provider:
                # Stream the response
                with Live(
                    Panel("", title="🧘 zenOS", border_style="cyan"),
                    console=console,
                    refresh_per_second=10,
                ) as live:
                    async for chunk in self.provider.complete(
                        full_prompt,
                        model=self.current_model,
                        temperature=self.config.config.temperature,
                        max_tokens=self.config.config.max_tokens,
                        stream=True,
                    ):
                        response_text += chunk
                        # Update live display with markdown
                        live.update(
                            Panel(Markdown(response_text), title="🧘 zenOS", border_style="cyan")
                        )

        # Add to history
        self.conversation_history.append(
            {
                "role": "assistant",
                "content": response_text,
                "model": self.current_model,
                "timestamp": datetime.now(),
                "cost": estimated_cost,
            }
        )

        # Update total cost
        self.total_cost += estimated_cost

        # Show cost info if significant
        if estimated_cost > 0.01:
            console.print(f"[dim]Cost: ${estimated_cost:.4f} | Total: ${self.total_cost:.4f}[/dim]")

    def _build_prompt_with_context(self, prompt: str) -> str:
        """Build prompt with conversation history, file context, and personality."""
        parts = []

        # Add personality and project context
        parts.append(self.context.format_context_for_prompt())

        # Add recent conversation history
        if len(self.conversation_history) > 1:
            parts.append("\n--- Recent Conversation ---")
            recent = self.conversation_history[-6:]  # Last 3 exchanges
            for msg in recent:
                if msg["role"] == "user":
                    parts.append(f"User: {msg['content']}")
                elif msg["role"] == "assistant":
                    parts.append(f"Assistant: {msg['content'][:500]}...")  # Truncate long responses

        # Add file context
        if self.context_files:
            parts.append("\n--- Context Files ---")
            for file_path in self.context_files:
                try:
                    content = Path(file_path).read_text()[:1000]  # First 1000 chars
                    parts.append(f"\nFile: {file_path}\n{content}...")
                except:
                    pass

        # Add current prompt
        parts.append(f"\n--- Current Request ---\nUser: {prompt}")

        return "\n\n".join(parts)

    async def handle_command(self, command: str):
        """Handle slash commands."""
        parts = command.split(maxsplit=1)
        cmd = parts[0]
        args = parts[1] if len(parts) > 1 else ""

        if cmd in self.commands:
            await self.commands[cmd](args)
        else:
            console.print(f"[yellow]Unknown command: {cmd}[/yellow]")
            console.print("Type /help for available commands")

    async def show_help(self, args: str = ""):
        """Show help information."""
        help_table = Table(title="🧘 zenOS Chat Commands", show_header=True)
        help_table.add_column("Command", style="cyan")
        help_table.add_column("Description", style="white")

        # Basic commands
        help_table.add_row("/help", "Show this help message")
        help_table.add_row("/exit, /quit", "Exit chat mode")
        help_table.add_row("/clear", "Clear the screen")
        help_table.add_row("/history", "Show conversation history")

        help_table.add_section()  # AI Model section
        help_table.add_row("/model <name>", "Switch to a different AI model")
        help_table.add_row("/models", "List available AI models")

        help_table.add_section()  # Personality section
        help_table.add_row(
            "/personality <name>",
            "Switch personality (professor/architect/oracle/intern/sovereign)",
        )
        help_table.add_row("/personas", "List available personalities")

        help_table.add_section()  # Context section
        help_table.add_row("/context <file>", "Add file to context")
        help_table.add_row("/project", "Show project awareness")
        help_table.add_row("/git", "Show git repository info")
        help_table.add_row("/genesis", "Show genesis wisdom")

        help_table.add_section()  # Session management
        help_table.add_row("/cost", "Show cost breakdown")
        help_table.add_row("/save <file>", "Save conversation to file")
        help_table.add_row("/reset", "Reset conversation history")
        help_table.add_row("/debug", "Toggle debug mode")

        console.print(help_table)

        # Keyboard shortcuts
        console.print("\n[bold]Keyboard Shortcuts:[/bold]")
        console.print("  Ctrl+C - Clear current input")
        console.print("  Ctrl+D - Exit chat")
        console.print("  Ctrl+L - Clear screen")
        console.print("  ↑/↓    - Navigate history")

    async def exit_chat(self, args: str = ""):
        """Exit the chat session."""
        console.print("\n[cyan]Thanks for chatting! Stay zen! 🧘[/cyan]")
        if self.total_cost > 0:
            console.print(f"[dim]Total session cost: ${self.total_cost:.4f}[/dim]")
        sys.exit(0)

    async def clear_screen(self, args: str = ""):
        """Clear the screen."""
        console.clear()
        self.display.show_welcome()

    async def show_history(self, args: str = ""):
        """Show conversation history."""
        if not self.conversation_history:
            console.print("[yellow]No conversation history yet[/yellow]")
            return

        for msg in self.conversation_history[-10:]:  # Last 10 messages
            role_color = "green" if msg["role"] == "user" else "cyan"
            timestamp = msg["timestamp"].strftime("%H:%M:%S")
            console.print(f"[dim]{timestamp}[/dim] [{role_color}]{msg['role']}[/{role_color}]:")

            # Truncate long messages
            content = msg["content"]
            if len(content) > 200:
                content = content[:200] + "..."
            console.print(f"  {content}\n")

    async def switch_model(self, model_name: str):
        """Switch to a different model."""
        if not model_name:
            console.print(f"[cyan]Current model: {self.current_model}[/cyan]")
            return

        # Map short names to full model names
        model_map = {
            "opus": "anthropic/claude-3-opus",
            "sonnet": "anthropic/claude-3-sonnet",
            "haiku": "anthropic/claude-3-haiku",
            "gpt4": "openai/gpt-4-turbo",
            "gpt3": "openai/gpt-3.5-turbo",
            "mixtral": "mixtral-8x7b-instruct",
        }

        full_model = model_map.get(model_name, model_name)

        # Add provider prefix if missing
        if "/" not in full_model:
            if "claude" in full_model:
                full_model = f"anthropic/{full_model}"
            elif "gpt" in full_model:
                full_model = f"openai/{full_model}"

        self.current_model = full_model
        console.print(f"[green]✓[/green] Switched to {full_model}")

        # Show model info
        model_info = self.provider.get_model_info(full_model)
        if model_info:
            console.print(f"[dim]Context: {model_info.context_window:,} tokens")
            console.print(
                f"[dim]Cost: ${model_info.cost_per_1k_input:.4f}/1k in, ${model_info.cost_per_1k_output:.4f}/1k out[/dim]"
            )

    async def list_models(self, args: str = ""):
        """List available models."""
        table = Table(title="🤖 Available Models", show_header=True)
        table.add_column("Model", style="cyan")
        table.add_column("Tier", style="yellow")
        table.add_column("Cost (per 1k)", style="green")
        table.add_column("Context", style="white")

        for model in self.provider.list_models():
            cost = f"${model.cost_per_1k_input:.4f}/${model.cost_per_1k_output:.4f}"
            table.add_row(
                model.name.split("/")[-1], model.tier.value, cost, f"{model.context_window:,}"
            )

        console.print(table)

    async def add_context(self, file_path: str):
        """Add a file to the context."""
        if not file_path:
            if self.context_files:
                console.print("[cyan]Current context files:[/cyan]")
                for f in self.context_files:
                    console.print(f"  - {f}")
            else:
                console.print("[yellow]No context files loaded[/yellow]")
            return

        path = Path(file_path)
        if not path.exists():
            console.print(f"[red]File not found: {file_path}[/red]")
            return

        self.context_files.append(str(path))
        size = path.stat().st_size
        console.print(f"[green]✓[/green] Added {path.name} ({size:,} bytes) to context")

    async def show_cost(self, args: str = ""):
        """Show cost breakdown."""
        console.print(
            Panel.fit(
                f"[bold]Session Cost Breakdown[/bold]\n\n"
                f"Total Cost: [green]${self.total_cost:.4f}[/green]\n"
                f"Messages: {len(self.conversation_history)}\n"
                f"Current Model: {self.current_model}",
                title="💰 Cost Tracking",
                border_style="yellow",
            )
        )

    async def save_conversation(self, file_path: str):
        """Save conversation to a file."""
        if not file_path:
            file_path = f"zenOS_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        path = Path(file_path)

        with open(path, "w") as f:
            f.write("# zenOS Chat Session\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Model: {self.current_model}\n")
            f.write(f"Total Cost: ${self.total_cost:.4f}\n\n")

            for msg in self.conversation_history:
                timestamp = msg["timestamp"].strftime("%H:%M:%S")
                f.write(f"## [{timestamp}] {msg['role'].title()}\n\n")
                f.write(f"{msg['content']}\n\n")

        console.print(f"[green]✓[/green] Conversation saved to {path}")

    async def reset_conversation(self, args: str = ""):
        """Reset conversation history."""
        self.conversation_history.clear()
        self.context_files.clear()
        self.total_cost = 0.0
        console.print("[green]✓[/green] Conversation reset")

    async def toggle_debug(self, args: str = ""):
        """Toggle debug mode."""
        self.config.config.debug = not self.config.config.debug
        status = "enabled" if self.config.config.debug else "disabled"
        console.print(f"[yellow]Debug mode {status}[/yellow]")

    async def switch_personality(self, personality_name: str):
        """Switch to a different personality profile."""
        if not personality_name:
            current = self.context.current_personality.value
            console.print(f"[cyan]Current personality: {current}[/cyan]")
            return

        # Map names to personalities
        personality_map = {
            "professor": AgentPersonality.PROFESSOR,
            "architect": AgentPersonality.ARCHITECT,
            "oracle": AgentPersonality.ORACLE,
            "intern": AgentPersonality.INTERN,
            "sovereign": AgentPersonality.SOVEREIGN,
        }

        personality = personality_map.get(personality_name.lower())
        if personality:
            self.context.set_personality(personality)
        else:
            console.print(f"[red]Unknown personality: {personality_name}[/red]")
            console.print("Available: professor, architect, oracle, intern, sovereign")

    async def list_personalities(self, args: str = ""):
        """List available personality profiles."""
        table = Table(title="🎭 Personality Profiles", show_header=True)
        table.add_column("Name", style="cyan")
        table.add_column("Role", style="yellow")
        table.add_column("Focus", style="green")

        for personality in AgentPersonality:
            profile = self.context.PERSONALITIES[personality]
            table.add_row(personality.value, profile.role, ", ".join(profile.focus[:2]))

        console.print(table)

        # Show current personality
        current = self.context.current_personality.value
        console.print(f"\n[cyan]Current: {current}[/cyan]")

    async def show_project_context(self, args: str = ""):
        """Show project awareness information."""
        context = self.context.project_context

        if not context:
            console.print("[yellow]No project context available[/yellow]")
            return

        console.print(
            Panel.fit(
                f"[bold]Project Context[/bold]\n\n"
                f"Workspace: {self.context.workspace}\n"
                f"Is zenOS: {context.get('is_zenos', False)}\n"
                f"Version: {context.get('zenos_version', 'unknown')}\n\n"
                f"[dim]Structure preview:[/dim]\n{context.get('structure', 'N/A')[:300]}...",
                title="📁 Project Awareness",
                border_style="green",
            )
        )

    async def show_git_context(self, args: str = ""):
        """Show git repository information."""
        context = self.context.git_context

        if not context:
            console.print("[yellow]No git context available[/yellow]")
            return

        commits = "\n".join(context.get("recent_commits", [])[:3])

        console.print(
            Panel.fit(
                f"[bold]Git Context[/bold]\n\n"
                f"Branch: [cyan]{context.get('branch', 'unknown')}[/cyan]\n"
                f"Remote: {context.get('remote', 'N/A')}\n\n"
                f"[dim]Recent commits:[/dim]\n{commits}\n\n"
                f"[dim]Changes:[/dim]\n{context.get('diff_stat', 'No changes')[:200]}",
                title="🔀 Git Awareness",
                border_style="magenta",
            )
        )

    async def show_genesis_wisdom(self, args: str = ""):
        """Show loaded genesis documents and wisdom."""
        if not self.context.genesis_docs:
            console.print("[yellow]No genesis documents found[/yellow]")
            console.print("[dim]Place them in ai-inbox/ or .zenOS/genesis/[/dim]")
            return

        console.print(
            Panel.fit(
                f"[bold]Genesis Documents Loaded[/bold]\n\n"
                f"📜 {', '.join(self.context.genesis_docs.keys())}\n\n"
                f"[cyan]Core Principles:[/cyan]\n"
                f"• Sovereignty over features\n"
                f"• Systems over goals\n"
                f"• The empire is the real product\n"
                f"• Build your native kernel's environment\n\n"
                f"[dim]Cultural Touchstones:[/dim]\n"
                f"• Earl of Lemongrab - The 'Why'\n"
                f"• Patrick Bateman - The Persona Engine\n"
                f"• Lisan al Gaib - The Systems-Master",
                title="🧬 Genesis Wisdom",
                border_style="gold1",
            )
        )
