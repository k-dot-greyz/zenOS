"""Context management for zenOS - Project, Git, and Personality awareness.
"""

import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from rich.console import Console

console = Console()


class AgentPersonality(Enum):
    """The philosophical agents that guide zenOS."""

    PROFESSOR = "THE_PROFESSOR"  # Philosophy, Core Narrative
    ARCHITECT = "THE_ARCHITECT"  # System Design, Technical Writing
    ORACLE = "THE_ORACLE"  # Real-time Analysis, Chaotic Insight
    INTERN = "THE_INTERN"  # Marketing Copy, Rapid Prototyping
    SOVEREIGN = "THE_SOVEREIGN"  # The user's own voice


@dataclass
class PersonalityProfile:
    """Profile for an agent personality."""

    name: str
    role: str
    tone: str
    focus: List[str]
    quotes: List[str]


class ContextManager:
    """Manages all context for zenOS:
    - File and project awareness
    - Git integration
    - Personality profiles from genesis docs
    - Cultural touchstones
    """

    # Personality profiles based on genesis docs
    PERSONALITIES = {
        AgentPersonality.PROFESSOR: PersonalityProfile(
            name="THE_PROFESSOR",
            role="Philosophy, Core Narrative",
            tone="Thoughtful, philosophical, systems-thinking",
            focus=["sovereignty", "empire building", "personal OS"],
            quotes=[
                "You are not broken. Your operating system is not buggy.",
                "An empire is not about domination. It is about sovereignty.",
                "The goal is not to conquer the world, but to create a world of your own.",
            ],
        ),
        AgentPersonality.ARCHITECT: PersonalityProfile(
            name="THE_ARCHITECT",
            role="System Design, Technical Writing",
            tone="Precise, structured, implementation-focused",
            focus=["systems", "engines", "scalability"],
            quotes=[
                "A sovereign system is built on three core engines.",
                "Write once, sell forever.",
                "The empire is the real product.",
            ],
        ),
        AgentPersonality.ORACLE: PersonalityProfile(
            name="THE_ORACLE",
            role="Real-time Analysis, Chaotic Insight",
            tone="Unpredictable, insightful, pattern-recognizing",
            focus=["trends", "real-time data", "unexpected connections"],
            quotes=[
                "Scanning real-time data...",
                "The lemonade is an afterthought.",
                "They understood the assignment: sell the system, not the output.",
            ],
        ),
        AgentPersonality.INTERN: PersonalityProfile(
            name="THE_INTERN",
            role="Marketing Copy, Rapid Prototyping",
            tone="Energetic, casual, meme-aware",
            focus=["virality", "quick wins", "MVP mindset"],
            quotes=[
                "Ship it!",
                "Make it viral, make it stick.",
                "The best time to plant a tree was 20 years ago. The second best time is now.",
            ],
        ),
        AgentPersonality.SOVEREIGN: PersonalityProfile(
            name="THE_SOVEREIGN",
            role="The User's Own Voice",
            tone="Direct, authentic, unfiltered",
            focus=["personal goals", "authentic expression", "sovereignty"],
            quotes=[
                "This is my system, my rules.",
                "I build empires, not features.",
                "The pyramid in Rīga isn't just a dream—it's a roadmap.",
            ],
        ),
    }

    # Cultural touchstones from genesis
    CULTURAL_REFERENCES = {
        "lemongrab": {
            "name": "Earl of Lemongrab",
            "concept": "The Tyranny of Unacceptable Conditions",
            "role": "Patron Saint of The 'Why'",
            "quotes": ["UNACCEPTABLE!", "One million years dungeon!"],
        },
        "bateman": {
            "name": "Patrick Bateman",
            "concept": "The Ritual of Surface-Level Control",
            "role": "Case Study for The Persona Engine",
            "quotes": ["I have to return some videotapes.", "Impressive. Very nice."],
        },
        "lisan_al_gaib": {
            "name": "Lisan al Gaib",
            "concept": "The Reluctant Systems-Master",
            "role": "The Archetype of the Operator",
            "quotes": ["The spice must flow.", "I see possible futures."],
        },
    }

    def __init__(self, workspace: Optional[Path] = None):
        """Initialize context manager."""
        self.workspace = workspace or Path.cwd()
        self.current_personality = AgentPersonality.SOVEREIGN
        self.genesis_docs = {}
        self.project_context = {}
        self.git_context = {}

        # Auto-load genesis docs if available
        self._load_genesis_docs()
        self._load_project_context()
        self._load_git_context()

    def _load_genesis_docs(self):
        """Load genesis documents from ai-inbox or project root."""
        search_paths = [
            self.workspace / "ai-inbox",
            self.workspace / "genesis",
            self.workspace / ".zenOS" / "genesis",
            Path.home() / ".zenOS" / "genesis",
            Path.home() / "Desktop" / "ai-inbox",  # Your specific path
        ]

        genesis_files = ["System Manifest.yaml", "Genesis Log.yaml", "zenOS Manuscript Draft.yaml"]

        for search_path in search_paths:
            if search_path.exists():
                for genesis_file in genesis_files:
                    file_path = search_path / genesis_file
                    if file_path.exists():
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                content = f.read()
                                # Try to parse as YAML, fall back to text
                                try:
                                    self.genesis_docs[genesis_file] = yaml.safe_load(content)
                                except:
                                    self.genesis_docs[genesis_file] = content
                            console.print(f"[green]✓[/green] Loaded genesis: {genesis_file}")
                        except Exception as e:
                            console.print(
                                f"[yellow]Warning: Could not load {genesis_file}: {e}[/yellow]"
                            )

    def _load_project_context(self):
        """Load project structure and key files."""
        try:
            # Get project structure
            self.project_context["structure"] = self._get_tree()

            # Load key files
            key_files = ["README.md", "pyproject.toml", "package.json", ".env.example"]
            for file in key_files:
                file_path = self.workspace / file
                if file_path.exists():
                    self.project_context[file] = file_path.read_text()[:1000]

            # Check for zenOS-specific files
            if (self.workspace / "zen").exists():
                self.project_context["is_zenos"] = True
                self.project_context["zenos_version"] = self._get_zenos_version()
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load project context: {e}[/yellow]")

    def _load_git_context(self):
        """Load git information."""
        try:
            # Check if we're in a git repo
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.workspace,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                # Get current branch
                branch_result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    cwd=self.workspace,
                    capture_output=True,
                    text=True,
                )
                self.git_context["branch"] = branch_result.stdout.strip()

                # Get recent commits
                log_result = subprocess.run(
                    ["git", "log", "--oneline", "-5"],
                    cwd=self.workspace,
                    capture_output=True,
                    text=True,
                )
                self.git_context["recent_commits"] = log_result.stdout.strip().split("\n")

                # Get current diff
                diff_result = subprocess.run(
                    ["git", "diff", "--stat"], cwd=self.workspace, capture_output=True, text=True
                )
                self.git_context["diff_stat"] = diff_result.stdout.strip()

                # Get remote URL
                remote_result = subprocess.run(
                    ["git", "remote", "get-url", "origin"],
                    cwd=self.workspace,
                    capture_output=True,
                    text=True,
                )
                self.git_context["remote"] = remote_result.stdout.strip()

        except Exception:
            console.print("[dim]No git context available[/dim]")

    def _get_tree(self, max_depth: int = 3) -> str:
        """Get project tree structure."""
        tree_lines = []

        def walk_dir(path: Path, prefix: str = "", depth: int = 0):
            if depth >= max_depth:
                return

            try:
                items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name))
                for i, item in enumerate(items[:20]):  # Limit items per level
                    if item.name.startswith("."):
                        continue

                    is_last = i == len(items) - 1
                    current_prefix = "└── " if is_last else "├── "
                    next_prefix = "    " if is_last else "│   "

                    tree_lines.append(f"{prefix}{current_prefix}{item.name}")

                    if item.is_dir() and item.name not in ["node_modules", "__pycache__", ".git"]:
                        walk_dir(item, prefix + next_prefix, depth + 1)
            except PermissionError:
                pass

        tree_lines.append(self.workspace.name)
        walk_dir(self.workspace, "", 0)

        return "\n".join(tree_lines[:50])  # Limit total lines

    def _get_zenos_version(self) -> str:
        """Get zenOS version if available."""
        try:
            init_file = self.workspace / "zen" / "__init__.py"
            if init_file.exists():
                content = init_file.read_text()
                for line in content.split("\n"):
                    if "__version__" in line:
                        return line.split("=")[1].strip().strip("\"'")
        except:
            pass
        return "unknown"

    def set_personality(self, personality: AgentPersonality):
        """Switch to a different personality profile."""
        self.current_personality = personality
        profile = self.PERSONALITIES[personality]
        console.print(f"[cyan]🎭 Switched to {profile.name}[/cyan]")
        console.print(f"[dim]{profile.role}[/dim]")
        if profile.quotes:
            import random

            console.print(f"[italic]{random.choice(profile.quotes)}[/italic]")

    def get_personality_prompt(self) -> str:
        """Get the system prompt for current personality."""
        profile = self.PERSONALITIES[self.current_personality]

        prompt = f"""You are {profile.name}, with the role of {profile.role}.
Your tone is {profile.tone}.
You focus on: {', '.join(profile.focus)}.

Key philosophical principles from the genesis documents:
- Sovereignty over features
- Systems over goals  
- The empire (brand, systems) is the real product
- Build a bespoke environment where your native kernel can thrive

"""

        # Add cultural references if appropriate
        if self.current_personality == AgentPersonality.ORACLE:
            prompt += (
                f"\nCultural touchstone: {self.CULTURAL_REFERENCES['lisan_al_gaib']['concept']}"
            )
        elif self.current_personality == AgentPersonality.ARCHITECT:
            prompt += f"\nCultural touchstone: {self.CULTURAL_REFERENCES['bateman']['concept']}"
        elif self.current_personality == AgentPersonality.PROFESSOR:
            prompt += f"\nCultural touchstone: {self.CULTURAL_REFERENCES['lemongrab']['concept']}"

        # Add genesis context if loaded
        if self.genesis_docs:
            prompt += "\n\nYou have access to the foundational genesis documents that define this system's philosophy."

        return prompt

    def get_full_context(self) -> Dict[str, Any]:
        """Get all available context."""
        return {
            "personality": {
                "current": self.current_personality.value,
                "profile": self.PERSONALITIES[self.current_personality].__dict__,
            },
            "genesis": self.genesis_docs,
            "project": self.project_context,
            "git": self.git_context,
            "cultural_references": self.CULTURAL_REFERENCES,
        }

    def format_context_for_prompt(self) -> str:
        """Format all context as a string for inclusion in prompts."""
        parts = []

        # Add personality context
        parts.append(self.get_personality_prompt())

        # Add project context if available
        if self.project_context:
            parts.append("\n--- Project Context ---")
            if "is_zenos" in self.project_context:
                parts.append(
                    f"Working on zenOS v{self.project_context.get('zenos_version', 'unknown')}"
                )
            if "structure" in self.project_context:
                parts.append(f"Project structure:\n{self.project_context['structure'][:500]}...")

        # Add git context if available
        if self.git_context:
            parts.append("\n--- Git Context ---")
            parts.append(f"Branch: {self.git_context.get('branch', 'unknown')}")
            if "recent_commits" in self.git_context:
                parts.append(f"Recent commits: {', '.join(self.git_context['recent_commits'][:3])}")

        # Add genesis wisdom if loaded
        if self.genesis_docs:
            parts.append("\n--- Genesis Wisdom ---")
            parts.append(
                "The system is guided by the genesis documents: System Manifest, Genesis Log, and Manuscript Draft."
            )
            parts.append("Core principle: Build sovereign systems, not features.")

        return "\n".join(parts)
