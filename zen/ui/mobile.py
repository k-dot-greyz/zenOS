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
    Enhanced mobile chat interface with Termux integration.
    """
    
    def __init__(self):
        """Initialize mobile chat."""
        self.ui = MobileUI()
        self.termux = TermuxInterface()
        self.shortcuts = {
            "/h": "/help",
            "/q": "/exit",
            "/m": "/model",
            "/c": "/context",
            "/s": "/save",
            "/r": "/reset",
            "/?": "/cost",
            "/v": "/voice",     # Voice input
            "/cb": "/clipboard", # Clipboard input
            "/sh": "/share",    # Share output
            "/n": "/notify",    # Enable notifications
        }
        
        # Battery-aware mode
        self.eco_mode = False
        self._check_battery()
        
        # Import the real chat for backend
        from zen.ui.interactive import InteractiveChat
        self.backend = InteractiveChat()
    
    def _check_battery(self):
        """Check battery and enable eco mode if low."""
        if self.termux.is_termux():
            battery = self.termux.battery_status()
            if battery and battery.get('percentage', 100) < 20:
                self.eco_mode = True
                self.ui.console.print("[yellow]⚠️ Low battery - eco mode enabled[/yellow]")
    
    async def start(self):
        """Start enhanced mobile chat session."""
        # Acquire wake lock for long sessions
        if self.termux.is_termux():
            self.termux.wake_lock_acquire()
        
        # Show compact welcome
        self.ui.show_welcome()
        
        # Check for Termux API
        if self.termux.is_termux() and self.termux.is_api_available():
            self.ui.console.print("[green]✅ Termux API detected - voice & clipboard enabled![/green]")
        
        # Delegate to backend with mobile UI overrides
        try:
            await self.backend.start()
        finally:
            # Release wake lock when done
            if self.termux.is_termux():
                self.termux.wake_lock_release()
    
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
    
    async def handle_voice_input(self) -> Optional[str]:
        """Get voice input from user."""
        if not self.termux.is_api_available():
            self.ui.show_error("Termux API not available")
            return None
        
        self.ui.console.print("[cyan]🎤 Listening...[/cyan]")
        text = self.termux.voice_input()
        
        if text:
            self.ui.console.print(f"[green]You said: {text}[/green]")
            # Haptic feedback
            self.termux.vibrate(100)
        else:
            self.ui.show_error("No voice input received")
        
        return text
    
    async def handle_clipboard_input(self) -> Optional[str]:
        """Get clipboard content as input."""
        text = self.termux.clipboard_get()
        
        if text:
            preview = text[:50] + "..." if len(text) > 50 else text
            self.ui.console.print(f"[green]📋 Clipboard: {preview}[/green]")
        else:
            self.ui.show_error("Clipboard is empty")
        
        return text
    
    def share_output(self, text: str):
        """Share output via Android share sheet."""
        if self.termux.is_termux():
            self.termux.share(text, title="zenOS Output")
            self.ui.console.print("[green]📤 Shared![/green]")
        else:
            self.ui.show_error("Share not available")
    
    def notify_complete(self, query: str, response: str):
        """Send notification when query completes."""
        if self.termux.is_api_available():
            preview = response[:100] + "..." if len(response) > 100 else response
            self.termux.notify(
                title="🧘 zenOS Complete",
                content=preview,
                actions=["Share", "Copy"]
            )
            # Vibrate to notify
            self.termux.vibrate(200)


# Enhanced Termux integration
class TermuxInterface:
    """
    Complete Termux API integration for mobile.
    """
    
    @staticmethod
    def is_termux() -> bool:
        """Check if running in Termux."""
        return (
            os.environ.get("TERMUX_VERSION") is not None or
            os.path.exists("/data/data/com.termux")
        )
    
    @staticmethod
    def is_api_available() -> bool:
        """Check if Termux:API is installed."""
        return os.path.exists("/data/data/com.termux/files/usr/bin/termux-speech-to-text")
    
    @staticmethod
    def voice_input() -> Optional[str]:
        """Get voice input via Termux API."""
        if not TermuxInterface.is_api_available():
            return None
        
        import subprocess
        try:
            result = subprocess.run(
                ["termux-speech-to-text"],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except:
            return None
    
    @staticmethod
    def speak(text: str, language: str = "en-US", pitch: float = 1.0, rate: float = 1.0):
        """Speak text via Termux TTS."""
        if not TermuxInterface.is_api_available():
            return
        
        import subprocess
        try:
            cmd = ["termux-tts-speak"]
            cmd.extend(["-l", language])
            cmd.extend(["-p", str(pitch)])
            cmd.extend(["-r", str(rate)])
            cmd.append(text)
            subprocess.run(cmd, timeout=30)
        except:
            pass
    
    @staticmethod
    def clipboard_get() -> Optional[str]:
        """Get clipboard content."""
        if not TermuxInterface.is_termux():
            return None
        
        import subprocess
        try:
            result = subprocess.run(
                ["termux-clipboard-get"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except:
            return None
    
    @staticmethod
    def clipboard_set(text: str):
        """Set clipboard content."""
        if not TermuxInterface.is_termux():
            return
        
        import subprocess
        try:
            subprocess.run(
                ["termux-clipboard-set"],
                input=text,
                text=True,
                timeout=5
            )
        except:
            pass
    
    @staticmethod
    def notify(title: str, content: str, actions: Optional[List[str]] = None):
        """Send notification."""
        if not TermuxInterface.is_api_available():
            return
        
        import subprocess
        try:
            cmd = ["termux-notification"]
            cmd.extend(["--title", title])
            cmd.extend(["--content", content])
            
            if actions:
                for action in actions:
                    cmd.extend(["--action", action])
            
            subprocess.run(cmd, timeout=5)
        except:
            pass
    
    @staticmethod
    def vibrate(duration_ms: int = 200):
        """Vibrate the device."""
        if not TermuxInterface.is_api_available():
            return
        
        import subprocess
        try:
            subprocess.run(
                ["termux-vibrate", "-d", str(duration_ms)],
                timeout=2
            )
        except:
            pass
    
    @staticmethod
    def battery_status() -> Optional[Dict[str, Any]]:
        """Get battery status."""
        if not TermuxInterface.is_api_available():
            return None
        
        import subprocess
        import json
        try:
            result = subprocess.run(
                ["termux-battery-status"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
        except:
            pass
        return None
    
    @staticmethod
    def share(text: str, title: Optional[str] = None):
        """Share text via Android share sheet."""
        if not TermuxInterface.is_termux():
            return
        
        import subprocess
        try:
            cmd = ["termux-share"]
            if title:
                cmd.extend(["--title", title])
            cmd.extend(["--text", text])
            subprocess.run(cmd, timeout=5)
        except:
            pass
    
    @staticmethod
    def wake_lock_acquire():
        """Acquire wake lock to keep CPU running."""
        if not TermuxInterface.is_termux():
            return
        
        import subprocess
        try:
            subprocess.run(["termux-wake-lock"], timeout=2)
        except:
            pass
    
    @staticmethod
    def wake_lock_release():
        """Release wake lock."""
        if not TermuxInterface.is_termux():
            return
        
        import subprocess
        try:
            subprocess.run(["termux-wake-unlock"], timeout=2)
        except:
            pass

# Legacy alias for backwards compatibility
VoiceInterface = TermuxInterface


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
