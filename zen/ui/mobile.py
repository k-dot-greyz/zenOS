"""
Mobile-optimized UI for zenOS - Because you run Arch on your phone, you madlad.
"""

import os
import sys
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich import box

# Detect if we're in mobile/compact mode
IS_MOBILE = (
    os.environ.get("COMPACT_MODE") == "1" or
    os.environ.get("TERMUX_VERSION") or
    int(os.environ.get("COLUMNS", 80)) < 60
)

# Mobile-optimized console
console = Console(
    width=min(50, int(os.environ.get("COLUMNS", 50))) if IS_MOBILE else None,
    legacy_windows=False,
    force_terminal=True
)


class MobileUI:
    """
    Ultra-compact UI for mobile terminals.
    
    Optimized for:
    - Narrow screens (< 60 chars)
    - Touch typing
    - Quick commands
    - Minimal scrolling
    """
    
    # Compact ASCII logo
    LOGO_MINI = """
    ███████╗███████╗███╗   ██╗
    ╚══███╔╝██╔════╝████╗  ██║
      ███╔╝ █████╗  ██╔██╗ ██║
     ███╔╝  ██╔══╝  ██║╚██╗██║
    ███████╗███████╗██║ ╚████║
    ╚══════╝╚══════╝╚═╝  ╚═══╝
    """
    
    LOGO_TINY = "🧘 zenOS"
    
    def __init__(self):
        """Initialize mobile UI."""
        self.console = console
        self.width = self.console.width or 50
        self.is_portrait = self.width < 60
        self.is_landscape = self.width >= 80
    
    def show_welcome(self):
        """Show compact welcome screen."""
        if self.is_portrait:
            # Ultra compact for portrait
            self.console.print(
                Panel(
                    Align.center(Text(self.LOGO_TINY, style="cyan bold")),
                    box=box.ROUNDED,
                    border_style="cyan"
                )
            )
            self.console.print("[dim]Type /h for help[/dim]")
        else:
            # Slightly bigger for landscape
            self.console.print(
                Panel(
                    Align.center(Text(self.LOGO_MINI, style="cyan")),
                    box=box.DOUBLE,
                    border_style="cyan"
                )
            )
            self.console.print("[cyan]Chat Mode[/cyan] | [dim]/help[/dim]")
    
    def show_response(self, text: str, title: Optional[str] = None):
        """Show response in compact format."""
        # Truncate title for mobile
        if title and len(title) > 20:
            title = title[:17] + "..."
        
        # Word wrap for narrow screens
        if self.is_portrait:
            # Super compact panel
            panel = Panel(
                Text(text, overflow="fold"),
                title=title or "🧘",
                border_style="cyan",
                box=box.MINIMAL,
                padding=(0, 1)
            )
        else:
            # Normal panel for landscape
            panel = Panel(
                Text(text, overflow="fold"),
                title=title or "🧘 zenOS",
                border_style="cyan",
                box=box.ROUNDED,
                padding=(0, 1)
            )
        
        self.console.print(panel)
    
    def show_cost(self, cost: float, total: float):
        """Show cost in compact format."""
        if cost > 0.001:  # Only show if significant
            self.console.print(
                f"[dim]${cost:.3f} | Σ${total:.3f}[/dim]",
                justify="right"
            )
    
    def show_error(self, error: str):
        """Show error in compact format."""
        self.console.print(f"[red]❌ {error[:40]}...[/red]" if len(error) > 40 else f"[red]❌ {error}[/red]")
    
    def show_help_mini(self):
        """Ultra-compact help for mobile."""
        help_text = """
[cyan]Commands:[/cyan]
/m haiku   - Fast mode
/m opus    - Power mode
/c <file>  - Add context
/s         - Save chat
/q         - Quit

[dim]Swipe up for history[/dim]
        """
        self.console.print(Panel(
            help_text.strip(),
            title="Help",
            box=box.MINIMAL
        ))
    
    def format_prompt(self, model: str) -> str:
        """Format prompt for mobile."""
        if self.is_portrait:
            # Ultra short
            model_short = {
                "claude-3-haiku": "H",
                "claude-3-sonnet": "S", 
                "claude-3-opus": "O",
                "gpt-4-turbo": "G4",
                "gpt-3.5-turbo": "G3",
            }.get(model.split("/")[-1], "?")
            return f"[{model_short}]> "
        else:
            # Slightly longer
            model_name = model.split("/")[-1].split("-")[0]
            return f"🧘[{model_name}]› "
    
    def show_message(self, role: str, content: str, timestamp: Optional[datetime] = None):
        """Show a message in mobile format."""
        if self.is_portrait:
            # Super compact
            role_char = "U" if role == "user" else "A"
            time_str = timestamp.strftime("%H:%M") if timestamp else ""
            
            # Truncate long messages
            if len(content) > 100:
                content = content[:97] + "..."
            
            self.console.print(f"[dim]{time_str}[/dim] [{role_char}] {content}")
        else:
            # Normal format
            role_color = "green" if role == "user" else "cyan"
            self.console.print(f"[{role_color}]{role}:[/{role_color}] {content[:200]}...")


class MobileChat:
    """
    Simplified chat interface for mobile.
    """
    
    def __init__(self):
        """Initialize mobile chat."""
        self.ui = MobileUI()
        self.shortcuts = {
            "/h": "/help",
            "/q": "/exit",
            "/m": "/model",
            "/c": "/context",
            "/s": "/save",
            "/r": "/reset",
            "/?": "/cost",
        }
        
        # Import the real chat for backend
        from zen.ui.interactive import InteractiveChat
        self.backend = InteractiveChat()
    
    async def start(self):
        """Start mobile chat session."""
        # Show compact welcome
        self.ui.show_welcome()
        
        # Delegate to backend with mobile UI overrides
        await self.backend.start()
    
    def expand_shortcut(self, command: str) -> str:
        """Expand mobile shortcuts."""
        parts = command.split(maxsplit=1)
        cmd = parts[0]
        args = parts[1] if len(parts) > 1 else ""
        
        # Expand shortcut
        full_cmd = self.shortcuts.get(cmd, cmd)
        
        # Handle model shortcuts
        if full_cmd == "/model" and args:
            model_map = {
                "h": "haiku",
                "s": "sonnet",
                "o": "opus",
                "g": "gpt-3.5-turbo",
                "g4": "gpt-4-turbo",
            }
            args = model_map.get(args, args)
        
        return f"{full_cmd} {args}".strip() if args else full_cmd
    
    def format_for_mobile(self, text: str) -> str:
        """Format text for mobile display."""
        # Break long lines
        max_width = self.ui.width - 4  # Account for padding
        lines = []
        
        for line in text.split("\n"):
            if len(line) <= max_width:
                lines.append(line)
            else:
                # Word wrap
                words = line.split()
                current = []
                current_len = 0
                
                for word in words:
                    if current_len + len(word) + 1 <= max_width:
                        current.append(word)
                        current_len += len(word) + 1
                    else:
                        if current:
                            lines.append(" ".join(current))
                        current = [word]
                        current_len = len(word)
                
                if current:
                    lines.append(" ".join(current))
        
        return "\n".join(lines)


# Voice integration for Termux
class VoiceInterface:
    """
    Voice input/output for mobile.
    """
    
    @staticmethod
    def is_available() -> bool:
        """Check if voice is available."""
        return os.path.exists("/data/data/com.termux/files/usr/bin/termux-speech-to-text")
    
    @staticmethod
    def listen() -> Optional[str]:
        """Get voice input."""
        if not VoiceInterface.is_available():
            return None
        
        import subprocess
        try:
            result = subprocess.run(
                ["termux-speech-to-text"],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout.strip()
        except:
            return None
    
    @staticmethod 
    def speak(text: str):
        """Speak text."""
        if not VoiceInterface.is_available():
            return
        
        import subprocess
        try:
            subprocess.run(
                ["termux-tts-speak", text],
                timeout=30
            )
        except:
            pass


# Auto-detect and setup
def get_ui():
    """Get appropriate UI for environment."""
    if IS_MOBILE:
        return MobileUI()
    else:
        from zen.ui.display import DisplayManager
        return DisplayManager()


def get_chat():
    """Get appropriate chat interface."""
    if IS_MOBILE:
        return MobileChat()
    else:
        from zen.ui.interactive import InteractiveChat
        return InteractiveChat()
