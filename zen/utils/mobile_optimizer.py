"""
Mobile Performance Optimizer for zenOS
Optimize for battery life, data usage, and mobile processors
"""

import hashlib
import json
import os
import time
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class MobileConfig:
    """Mobile-optimized configuration."""

    # Model settings
    default_model: str = "claude-3-haiku-20240307"  # Fastest model
    max_tokens: int = 500  # Shorter responses on mobile
    temperature: float = 0.7

    # Cache settings
    enable_cache: bool = True
    cache_dir: str = "~/.zen-cache"
    cache_ttl_hours: int = 72  # 3 days
    max_cache_size_mb: int = 100

    # Performance settings
    enable_compression: bool = True
    batch_requests: bool = True
    request_timeout: int = 30

    # Battery settings
    eco_mode_threshold: int = 20  # Battery percentage
    eco_model: str = "claude-3-haiku-20240307"
    sleep_between_requests: float = 0.5  # Seconds

    # Data settings
    compress_responses: bool = True
    strip_markdown: bool = False
    max_context_tokens: int = 2000

    # UI settings
    compact_mode: bool = True
    show_costs: bool = False  # Hide costs on mobile
    auto_scroll: bool = True
    vibrate_on_complete: bool = True


class ResponseCache:
    """
    Smart response caching for offline/fast access.
    """

    def __init__(self, config: MobileConfig):
        """Initialize the response cache using the configured directory and remove expired entries."""
        self.config = config
        self.cache_dir = Path(os.path.expanduser(config.cache_dir))
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Cache index for fast lookup
        self.index_file = self.cache_dir / "index.json"
        self.index = self._load_index()

        # Clean old entries on startup
        self._cleanup_old_entries()

    def _load_index(self) -> Dict[str, Any]:
        """
        Load the cache index from disk.
        
        Returns:
            Dict[str, Any]: The stored cache index, or an empty dictionary when the index is unavailable or unreadable.
        """
        if self.index_file.exists():
            try:
                with open(self.index_file, "r") as f:
                    return json.load(f)
            except:
                pass
        return {}

    def _save_index(self):
        """Save cache index."""
        with open(self.index_file, "w") as f:
            json.dump(self.index, f, indent=2)

    def _cleanup_old_entries(self):
        """Remove expired cache entries."""
        current_time = time.time()
        ttl_seconds = self.config.cache_ttl_hours * 3600

        expired = []
        for key, meta in self.index.items():
            if current_time - meta["timestamp"] > ttl_seconds:
                expired.append(key)

        for key in expired:
            self._remove_entry(key)

        if expired:
            self._save_index()

    def _remove_entry(self, key: str):
        """Remove a cache entry."""
        if key in self.index:
            cache_file = self.cache_dir / f"{key}.json"
            if cache_file.exists():
                cache_file.unlink()
            del self.index[key]

    def _get_cache_key(self, prompt: str, model: str, **kwargs) -> str:
        """Generate a deterministic cache key from a prompt, model, and request settings.
        
        Parameters:
        	prompt (str): The request prompt.
        	model (str): The model used for the request.
        	**kwargs: Additional request settings included in the key.
        
        Returns:
        	str: The hexadecimal MD5 digest identifying the request configuration.
        """
        # Create deterministic key from inputs
        key_data = {"prompt": prompt, "model": model, **kwargs}
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, prompt: str, model: str, **kwargs) -> Optional[str]:
        """Retrieve a cached response for the specified prompt, model, and options.
        
        Parameters:
            prompt (str): The request text used to identify the cached response.
            model (str): The model associated with the request.
            **kwargs: Additional request options used to identify the cached response.
        
        Returns:
            Optional[str]: The cached response, or `None` if no readable cached response is available.
        """
        if not self.config.enable_cache:
            return None

        key = self._get_cache_key(prompt, model, **kwargs)

        if key in self.index:
            cache_file = self.cache_dir / f"{key}.json"
            if cache_file.exists():
                try:
                    with open(cache_file, "r") as f:
                        data = json.load(f)
                        # Update access time
                        self.index[key]["last_accessed"] = time.time()
                        self.index[key]["hit_count"] = self.index[key].get("hit_count", 0) + 1
                        return data["response"]
                except:
                    pass

        return None

    def set(self, prompt: str, model: str, response: str, **kwargs):
        """Store a response and its request metadata in the response cache when caching is enabled.
        
        Parameters:
            prompt (str): The request prompt.
            model (str): The model used to generate the response.
            response (str): The generated response.
            **kwargs: Additional request parameters used to identify the cached response.
        """
        if not self.config.enable_cache:
            return

        key = self._get_cache_key(prompt, model, **kwargs)
        cache_file = self.cache_dir / f"{key}.json"

        # Store response
        data = {
            "prompt": prompt,
            "model": model,
            "response": response,
            "timestamp": time.time(),
            "kwargs": kwargs,
        }

        with open(cache_file, "w") as f:
            json.dump(data, f, indent=2)

        # Update index
        self.index[key] = {
            "timestamp": data["timestamp"],
            "last_accessed": data["timestamp"],
            "model": model,
            "prompt_preview": prompt[:50],
            "hit_count": 0,
            "size_bytes": cache_file.stat().st_size,
        }

        self._save_index()
        self._check_cache_size()

    def _check_cache_size(self):
        """Ensure cache doesn't exceed size limit."""
        total_size = sum(meta.get("size_bytes", 0) for meta in self.index.values())
        max_size = self.config.max_cache_size_mb * 1024 * 1024

        if total_size > max_size:
            # Remove least recently accessed entries
            sorted_entries = sorted(self.index.items(), key=lambda x: x[1].get("last_accessed", 0))

            while total_size > max_size and sorted_entries:
                key, meta = sorted_entries.pop(0)
                total_size -= meta.get("size_bytes", 0)
                self._remove_entry(key)

            self._save_index()

    def get_stats(self) -> Dict[str, Any]:
        """
        Return statistics for the cached responses.
        
        Returns:
            Dict[str, Any]: Cache entry count, total size in megabytes, total hit count,
                and average hits per entry.
        """
        total_size = sum(meta.get("size_bytes", 0) for meta in self.index.values())
        total_hits = sum(meta.get("hit_count", 0) for meta in self.index.values())

        return {
            "entries": len(self.index),
            "size_mb": round(total_size / 1024 / 1024, 2),
            "total_hits": total_hits,
            "hit_rate": round(total_hits / max(len(self.index), 1), 2),
        }


class BatteryManager:
    """
    Battery-aware performance management.
    """

    def __init__(self, config: MobileConfig):
        """Initialize battery manager."""
        self.config = config
        self.eco_mode = False
        self._last_check = 0

    def check_battery(self) -> Optional[int]:
        """
        Determine the current battery charge percentage.
        
        Returns:
            Optional[int]: The battery percentage, or `None` if it cannot be determined.
        """
        # Check if we're on Termux
        if os.environ.get("TERMUX_VERSION"):
            try:
                import subprocess

                result = subprocess.run(
                    ["termux-battery-status"], capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    return data.get("percentage", 100)
            except:
                pass

        # Fallback: check if on Linux with battery
        battery_path = Path("/sys/class/power_supply/BAT0/capacity")
        if battery_path.exists():
            try:
                with open(battery_path, "r") as f:
                    return int(f.read().strip())
            except:
                pass

        return None

    def should_use_eco_mode(self) -> bool:
        """
        Determine whether power-saving mode should be enabled based on the current battery level.
        
        Returns:
        	bool: `True` if eco mode is enabled, `False` otherwise.
        """
        # Rate limit checks (every 60 seconds)
        current_time = time.time()
        if current_time - self._last_check < 60:
            return self.eco_mode

        self._last_check = current_time
        battery = self.check_battery()

        if battery is not None:
            self.eco_mode = battery < self.config.eco_mode_threshold

        return self.eco_mode

    def get_optimal_model(self, requested_model: str) -> str:
        """
        Select the model appropriate for the current battery conditions.
        
        Parameters:
        	requested_model (str): Model to use when eco mode is inactive.
        
        Returns:
        	str: The configured eco model when eco mode is active; otherwise, the requested model.
        """
        if self.should_use_eco_mode():
            return self.config.eco_model
        return requested_model

    def get_sleep_duration(self) -> float:
        """
        Determine the delay between requests based on the current power-saving mode.
        
        Returns:
        	float: The configured delay, doubled when eco mode is active.
        """
        if self.should_use_eco_mode():
            return self.config.sleep_between_requests * 2  # Double sleep in eco mode
        return self.config.sleep_between_requests


class DataOptimizer:
    """
    Optimize data usage for mobile networks.
    """

    @staticmethod
    def compress_text(text: str) -> str:
        """Compress text for transmission."""
        import base64
        import zlib

        compressed = zlib.compress(text.encode("utf-8"), level=9)
        return base64.b64encode(compressed).decode("ascii")

    @staticmethod
    def decompress_text(compressed: str) -> str:
        """
        Decompress Base64-encoded, zlib-compressed text.
        
        Parameters:
            compressed (str): The encoded compressed text.
        
        Returns:
            str: The decompressed UTF-8 text.
        """
        import base64
        import zlib

        data = base64.b64decode(compressed.encode("ascii"))
        return zlib.decompress(data).decode("utf-8")

    @staticmethod
    def strip_markdown(text: str) -> str:
        """
        Remove common Markdown formatting and excess blank lines from text.
        
        Parameters:
            text (str): Text containing Markdown formatting.
        
        Returns:
            str: Text with formatting removed and surrounding whitespace trimmed.
        """
        import re

        # Remove code blocks
        text = re.sub(r"```[^`]*```", "[code removed]", text, flags=re.DOTALL)
        text = re.sub(r"`[^`]+`", "[inline code]", text)

        # Remove formatting
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)  # Bold
        text = re.sub(r"\*([^*]+)\*", r"\1", text)  # Italic
        text = re.sub(r"#+\s+", "", text)  # Headers
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)  # Links

        # Remove excessive whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    @staticmethod
    def truncate_context(messages: List[Dict], max_tokens: int) -> List[Dict]:
        """
        Limit conversation messages to fit within an estimated token budget.
        
        Parameters:
            messages (List[Dict]): Conversation messages ordered from oldest to newest.
            max_tokens (int): Maximum estimated token count to retain.
        
        Returns:
            List[Dict]: The newest messages that fit within the token budget.
        """

        # Simple token estimation (4 chars ≈ 1 token)
        def estimate_tokens(text: str) -> int:
            """Estimate the number of tokens in text using four characters per token."""
            return len(text) // 4

        total_tokens = 0
        truncated = []

        # Keep most recent messages
        for msg in reversed(messages):
            msg_tokens = estimate_tokens(msg.get("content", ""))
            if total_tokens + msg_tokens > max_tokens:
                break
            truncated.insert(0, msg)
            total_tokens += msg_tokens

        return truncated


class MobileOptimizer:
    """
    Main optimizer coordinating all mobile optimizations.
    """

    def __init__(self, config: Optional[MobileConfig] = None):
        """Initialize mobile optimizer."""
        self.config = config or MobileConfig()
        self.cache = ResponseCache(self.config)
        self.battery = BatteryManager(self.config)
        self.data = DataOptimizer()

        # Apply environment overrides
        self._apply_env_overrides()

    def _apply_env_overrides(self):
        """
        Apply supported environment variable overrides to the mobile configuration.
        
        Environment variables:
            COMPACT_MODE (str): Enables compact mode when set to ``"1"``.
            ZEN_MAX_TOKENS (str): Sets the maximum token limit.
            ZEN_DEFAULT_MODEL (str): Sets the default model.
            ZEN_CACHE_DIR (str): Sets the response cache directory.
        """
        if os.environ.get("COMPACT_MODE") == "1":
            self.config.compact_mode = True

        if os.environ.get("ZEN_MAX_TOKENS"):
            self.config.max_tokens = int(os.environ["ZEN_MAX_TOKENS"])

        if os.environ.get("ZEN_DEFAULT_MODEL"):
            self.config.default_model = os.environ["ZEN_DEFAULT_MODEL"]

        if os.environ.get("ZEN_CACHE_DIR"):
            self.config.cache_dir = os.environ["ZEN_CACHE_DIR"]

    def optimize_request(self, prompt: str, model: str, **kwargs) -> Dict[str, Any]:
        """
        Prepare a request using cached results or mobile-appropriate settings.
        
        Parameters:
            prompt (str): The request text used for cache lookup.
            model (str): The requested model.
            **kwargs: Additional request options to preserve or optimize.
        
        Returns:
            Dict[str, Any]: A cached response with its cache status, or optimized model and request parameters.
        """
        # Check cache first
        cached = self.cache.get(prompt, model, **kwargs)
        if cached:
            return {"response": cached, "cached": True, "model": model}

        # Optimize model selection based on battery
        optimized_model = self.battery.get_optimal_model(model)

        # Apply mobile optimizations to kwargs
        mobile_kwargs = {
            **kwargs,
            "max_tokens": min(
                kwargs.get("max_tokens", self.config.max_tokens), self.config.max_tokens
            ),
            "temperature": kwargs.get("temperature", self.config.temperature),
            "timeout": self.config.request_timeout,
        }

        return {"model": optimized_model, "kwargs": mobile_kwargs, "cached": False}

    def optimize_response(self, response: str, compress: bool = True) -> str:
        """
        Optimize response text for mobile use, optionally stripping Markdown and compressing the result.
        
        Parameters:
            response (str): The response text to optimize.
            compress (bool): Whether compression is allowed.
        
        Returns:
            str: The optimized response text, compressed when enabled by the argument and configuration.
        """
        if self.config.strip_markdown:
            response = self.data.strip_markdown(response)

        if compress and self.config.compress_responses:
            # For storage/transmission, not display
            return self.data.compress_text(response)

        return response

    def should_sleep(self) -> bool:
        """Check if we should sleep between requests."""
        return self.battery.should_use_eco_mode()

    def get_sleep_duration(self) -> float:
        """
        Determine the delay to apply between requests based on the current battery mode.
        
        Returns:
            float: The configured inter-request delay, increased when eco mode is active.
        """
        return self.battery.get_sleep_duration()

    def cache_response(self, prompt: str, model: str, response: str, **kwargs):
        """Cache a model response for the specified prompt and request options.
        
        Parameters:
            prompt (str): The input prompt associated with the response.
            model (str): The model that generated the response.
            response (str): The response content to cache.
            **kwargs: Additional request options used to identify the cached response.
        """
        self.cache.set(prompt, model, response, **kwargs)

    def get_stats(self) -> Dict[str, Any]:
        """Return cache, battery, and configuration statistics for the optimizer.
        
        Returns:
            Dict[str, Any]: A mapping containing cache statistics, the current battery
            level and eco-mode status, and the optimizer configuration.
        """
        return {
            "cache": self.cache.get_stats(),
            "battery": {"level": self.battery.check_battery(), "eco_mode": self.battery.eco_mode},
            "config": asdict(self.config),
        }


# Singleton instance
_optimizer: Optional[MobileOptimizer] = None


def get_optimizer() -> MobileOptimizer:
    """
    Get the shared mobile optimizer instance.
    
    Returns:
        MobileOptimizer: The module-level mobile optimizer instance.
    """
    global _optimizer
    if _optimizer is None:
        _optimizer = MobileOptimizer()
    return _optimizer


# Convenience functions
def is_mobile() -> bool:
    """Determine whether the application is running in a mobile environment.
    
    Returns:
        bool: `True` when Termux, compact mode, or the Termux application path is detected; `False` otherwise.
    """
    return (
        os.environ.get("TERMUX_VERSION") is not None
        or os.environ.get("COMPACT_MODE") == "1"
        or os.path.exists("/data/data/com.termux")
    )


def optimize_for_mobile(func):
    """
    Decorate an asynchronous function with mobile-specific model, token, and pacing adjustments.
    
    Parameters:
        func: The asynchronous function to optimize.
    
    Returns:
        The wrapped asynchronous function.
    """
    from functools import wraps

    @wraps(func)
    async def wrapper(*args, **kwargs):
        """
        Adapt a wrapped asynchronous function for mobile execution.
        
        On mobile, adjusts the model and token limit when provided and pauses after
        execution when battery-saving behavior requires it.
        
        Returns:
            The result produced by the wrapped function.
        """
        if not is_mobile():
            return await func(*args, **kwargs)

        optimizer = get_optimizer()

        # Apply optimizations
        if "model" in kwargs:
            kwargs["model"] = optimizer.battery.get_optimal_model(kwargs["model"])

        if "max_tokens" in kwargs:
            kwargs["max_tokens"] = min(kwargs["max_tokens"], optimizer.config.max_tokens)

        # Execute with sleep if needed
        result = await func(*args, **kwargs)

        if optimizer.should_sleep():
            time.sleep(optimizer.get_sleep_duration())

        return result

    return wrapper
