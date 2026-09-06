"""
Configuration management for zenOS.
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv


@dataclass
class ZenConfig:
    """zenOS configuration."""

    # Paths
    root_dir: Path = field(default_factory=Path.cwd)
    config_dir: Path = field(default_factory=lambda: Path.home() / ".zenOS")
    agents_dir: Path = field(default_factory=lambda: Path.cwd() / "agents")
    modules_dir: Path = field(default_factory=lambda: Path.cwd() / "modules")
    workspace_dir: Path = field(default_factory=lambda: Path.cwd() / "workspace")

    # API Configuration
    openrouter_api_key: Optional[str] = None
    default_model: str = "anthropic/claude-3-sonnet"

    # Database
    db_url: Optional[str] = None
    redis_url: Optional[str] = None

    # Behavior
    auto_critique: bool = True
    stream_responses: bool = True
    save_history: bool = True
    debug: bool = False

    # Limits
    max_tokens: int = 2000
    max_cost_per_request: float = 1.0
    temperature: float = 0.7


class Config:
    """
    Configuration manager for zenOS.

    Loads configuration from:
    1. Environment variables
    2. .env file
    3. ~/.zenOS/config.yaml
    4. ./zenOS.yaml
    """

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize configuration."""
        self.config = ZenConfig()

        # Load environment variables
        load_dotenv()

        # Load from various sources
        self._load_from_env()
        self._load_from_home()
        self._load_from_local()

        if config_path:
            self._load_from_file(config_path)

        # Ensure directories exist
        self._ensure_directories()

    def _load_from_env(self):
        """Load configuration from environment variables."""
        # API keys
        self.config.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

        # Database URLs
        self.config.db_url = os.getenv(
            "ZEN_DB_URL", "postgresql://zen:zenpass@localhost:5432/zenos"
        )
        self.config.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

        # Behavior
        self.config.auto_critique = os.getenv("ZEN_AUTO_CRITIQUE", "true").lower() == "true"
        self.config.stream_responses = os.getenv("ZEN_STREAM", "true").lower() == "true"
        self.config.debug = os.getenv("ZEN_DEBUG", "false").lower() == "true"

        # Model settings
        self.config.default_model = os.getenv("ZEN_DEFAULT_MODEL", self.config.default_model)
        self.config.max_tokens = int(os.getenv("ZEN_MAX_TOKENS", "2000"))
        self.config.temperature = float(os.getenv("ZEN_TEMPERATURE", "0.7"))

    def _load_from_home(self):
        """Load configuration from ~/.zenOS/config.yaml."""
        config_file = Path.home() / ".zenOS" / "config.yaml"
        if config_file.exists():
            self._load_from_file(config_file)

    def _load_from_local(self):
        """Load configuration from ./zenOS.yaml."""
        local_config = Path.cwd() / "zenOS.yaml"
        if local_config.exists():
            self._load_from_file(local_config)

    def _load_from_file(self, path: Path):
        """Load configuration from a YAML file."""
        try:
            with open(path, "r") as f:
                data = yaml.safe_load(f)

                if data:
                    # Update config with loaded data
                    for key, value in data.items():
                        if hasattr(self.config, key):
                            setattr(self.config, key, value)
        except Exception as e:
            print(f"Warning: Failed to load config from {path}: {e}")

    def _ensure_directories(self):
        """Ensure required directories exist."""
        dirs = [
            self.config.config_dir,
            self.config.agents_dir,
            self.config.modules_dir,
            self.config.workspace_dir,
        ]

        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Create module subdirectories
        for subdir in ["roles", "tasks", "contexts", "constraints"]:
            (self.config.modules_dir / subdir).mkdir(exist_ok=True)

    def save(self, path: Optional[Path] = None):
        """Save configuration to file."""
        if path is None:
            path = self.config.config_dir / "config.yaml"

        path.parent.mkdir(parents=True, exist_ok=True)

        # Convert config to dict
        config_dict = {
            "default_model": self.config.default_model,
            "auto_critique": self.config.auto_critique,
            "stream_responses": self.config.stream_responses,
            "save_history": self.config.save_history,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "max_cost_per_request": self.config.max_cost_per_request,
        }

        with open(path, "w") as f:
            yaml.dump(config_dict, f, default_flow_style=False)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return getattr(self.config, key, default)

    def set(self, key: str, value: Any):
        """Set a configuration value."""
        if hasattr(self.config, key):
            setattr(self.config, key, value)

    @property
    def agents_dir(self) -> Path:
        """Get the agents directory path."""
        return self.config.agents_dir

    @property
    def modules_dir(self) -> Path:
        """Get the modules directory path."""
        return self.config.modules_dir

    @property
    def workspace_dir(self) -> Path:
        """Get the workspace directory path."""
        return self.config.workspace_dir

    @property
    def config_dir(self) -> Path:
        """Get the config directory path."""
        return self.config.config_dir

    @property
    def is_configured(self) -> bool:
        """Check if zenOS is properly configured."""
        return bool(self.config.openrouter_api_key)
