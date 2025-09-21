"""
Offline/Local Model Provider for zenOS
True offline AI - because your phone IS the computer
"""

import os
import sys
import json
import subprocess
import asyncio
from typing import Optional, Dict, Any, List, AsyncIterator
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class LocalModelType(Enum):
    """Supported local model backends."""
    OLLAMA = "ollama"
    LLAMACPP = "llamacpp"
    ONNX = "onnx"
    TFLITE = "tflite"  # For mobile!
    CANDLE = "candle"  # Rust-based, super fast


@dataclass
class LocalModel:
    """Local model configuration."""
    name: str
    backend: LocalModelType
    size_mb: int
    ram_required_mb: int
    quantization: str  # e.g., "q4_0", "q5_1", "q8_0"
    mobile_optimized: bool
    capabilities: List[str]  # ["chat", "code", "embeddings"]
    
    @property
    def is_mobile_friendly(self) -> bool:
        """Check if model can run on typical mobile device."""
        return self.ram_required_mb < 4000 and self.mobile_optimized


# Pre-configured models optimized for mobile
MOBILE_MODELS = {
    "phi-2": LocalModel(
        name="phi-2",
        backend=LocalModelType.OLLAMA,
        size_mb=1600,
        ram_required_mb=2000,
        quantization="q4_0",
        mobile_optimized=True,
        capabilities=["chat", "code"]
    ),
    "tinyllama": LocalModel(
        name="tinyllama",
        backend=LocalModelType.OLLAMA,
        size_mb=637,
        ram_required_mb=800,
        quantization="q4_0",
        mobile_optimized=True,
        capabilities=["chat"]
    ),
    "gemma-2b": LocalModel(
        name="gemma:2b",
        backend=LocalModelType.OLLAMA,
        size_mb=1400,
        ram_required_mb=1800,
        quantization="q4_0",
        mobile_optimized=True,
        capabilities=["chat", "code"]
    ),
    "stable-lm-2": LocalModel(
        name="stablelm2:1.6b",
        backend=LocalModelType.OLLAMA,
        size_mb=980,
        ram_required_mb=1200,
        quantization="q4_0",
        mobile_optimized=True,
        capabilities=["chat"]
    ),
    "qwen-0.5b": LocalModel(
        name="qwen:0.5b",
        backend=LocalModelType.OLLAMA,
        size_mb=395,
        ram_required_mb=512,
        quantization="q4_0",
        mobile_optimized=True,
        capabilities=["chat"]
    ),
}

# Larger models for desktop/powerful devices
DESKTOP_MODELS = {
    "llama3": LocalModel(
        name="llama3:8b",
        backend=LocalModelType.OLLAMA,
        size_mb=4500,
        ram_required_mb=8000,
        quantization="q4_0",
        mobile_optimized=False,
        capabilities=["chat", "code", "embeddings"]
    ),
    "mistral": LocalModel(
        name="mistral:7b",
        backend=LocalModelType.OLLAMA,
        size_mb=4100,
        ram_required_mb=7000,
        quantization="q4_0",
        mobile_optimized=False,
        capabilities=["chat", "code"]
    ),
    "codellama": LocalModel(
        name="codellama:7b",
        backend=LocalModelType.OLLAMA,
        size_mb=3800,
        ram_required_mb=6000,
        quantization="q4_0",
        mobile_optimized=False,
        capabilities=["code"]
    ),
}


class OllamaProvider:
    """
    Ollama backend for local models.
    Works on Termux with some effort!
    """
    
    def __init__(self):
        """Initialize Ollama provider."""
        self.base_url = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.models_dir = Path.home() / ".ollama" / "models"
        self.is_available = self._check_availability()
        
    def _check_availability(self) -> bool:
        """Check if Ollama is installed and running."""
        try:
            # Check if ollama binary exists
            result = subprocess.run(
                ["which", "ollama"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                return False
            
            # Check if server is running
            import requests
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    async def list_models(self) -> List[str]:
        """List installed models."""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return [model['name'] for model in data.get('models', [])]
        except:
            pass
        return []
    
    async def pull_model(self, model_name: str) -> bool:
        """Download a model."""
        try:
            process = await asyncio.create_subprocess_exec(
                "ollama", "pull", model_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            return process.returncode == 0
        except:
            return False
    
    async def generate(
        self,
        model: str,
        prompt: str,
        stream: bool = False,
        **kwargs
    ) -> AsyncIterator[str]:
        """Generate response from local model."""
        import aiohttp
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            **kwargs
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/generate",
                json=payload
            ) as resp:
                if stream:
                    async for line in resp.content:
                        if line:
                            try:
                                data = json.loads(line)
                                if 'response' in data:
                                    yield data['response']
                            except:
                                pass
                else:
                    data = await resp.json()
                    yield data.get('response', '')


class LlamaCppProvider:
    """
    llama.cpp backend - runs on literally anything!
    Perfect for Termux.
    """
    
    def __init__(self):
        """Initialize llama.cpp provider."""
        self.binary_path = self._find_binary()
        self.models_dir = Path.home() / ".cache" / "llama-models"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
    def _find_binary(self) -> Optional[Path]:
        """Find llama.cpp binary."""
        # Common locations
        candidates = [
            Path.home() / "llama.cpp" / "main",
            Path("/data/data/com.termux/files/usr/bin/llama"),
            Path("/usr/local/bin/llama"),
            Path("./llama"),
        ]
        
        for path in candidates:
            if path.exists() and path.is_file():
                return path
        
        # Try to find via which
        try:
            result = subprocess.run(
                ["which", "llama"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return Path(result.stdout.strip())
        except:
            pass
        
        return None
    
    async def generate(
        self,
        model_path: str,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate using llama.cpp."""
        if not self.binary_path:
            raise RuntimeError("llama.cpp not found")
        
        cmd = [
            str(self.binary_path),
            "-m", model_path,
            "-p", prompt,
            "-n", str(max_tokens),
            "--temp", str(temperature),
            "-t", "4",  # threads
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            return stdout.decode('utf-8')
        else:
            raise RuntimeError(f"llama.cpp error: {stderr.decode('utf-8')}")


class OfflineManager:
    """
    Manages offline/local model execution.
    Automatically selects best backend and model for device.
    """
    
    def __init__(self):
        """Initialize offline manager."""
        self.ollama = OllamaProvider()
        self.llamacpp = LlamaCppProvider()
        self.current_model = None
        self.is_mobile = self._detect_mobile()
        
        # Auto-select models based on device
        self.available_models = self._get_available_models()
        
    def _detect_mobile(self) -> bool:
        """Detect if running on mobile device."""
        return (
            os.environ.get("TERMUX_VERSION") is not None or
            os.path.exists("/data/data/com.termux") or
            os.environ.get("COMPACT_MODE") == "1"
        )
    
    def _get_available_models(self) -> Dict[str, LocalModel]:
        """Get models suitable for current device."""
        if self.is_mobile:
            return MOBILE_MODELS
        else:
            # Include both mobile and desktop models on desktop
            return {**MOBILE_MODELS, **DESKTOP_MODELS}
    
    def _get_device_ram(self) -> int:
        """Get available RAM in MB."""
        try:
            if sys.platform == "linux":
                with open("/proc/meminfo", "r") as f:
                    for line in f:
                        if line.startswith("MemAvailable:"):
                            # Convert KB to MB
                            return int(line.split()[1]) // 1024
            elif sys.platform == "darwin":
                # macOS
                result = subprocess.run(
                    ["sysctl", "hw.memsize"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    bytes_ram = int(result.stdout.split(":")[1].strip())
                    return bytes_ram // (1024 * 1024)
        except:
            pass
        
        # Default assumption
        return 4000 if self.is_mobile else 8000
    
    def select_best_model(self, task: str = "chat") -> Optional[LocalModel]:
        """Select best model for current device and task."""
        available_ram = self._get_device_ram()
        
        # Filter models that fit in RAM and support the task
        suitable = [
            model for model in self.available_models.values()
            if (model.ram_required_mb < available_ram * 0.7 and  # Leave 30% free
                task in model.capabilities)
        ]
        
        if not suitable:
            return None
        
        # Sort by capability (larger models generally better)
        suitable.sort(key=lambda m: m.ram_required_mb, reverse=True)
        
        return suitable[0]
    
    async def ensure_model(self, model: LocalModel) -> bool:
        """Ensure model is downloaded and ready."""
        # Check Ollama first
        if self.ollama.is_available and model.backend == LocalModelType.OLLAMA:
            installed = await self.ollama.list_models()
            if model.name not in installed:
                logger.info(f"Downloading {model.name} ({model.size_mb}MB)...")
                return await self.ollama.pull_model(model.name)
            return True
        
        # TODO: Add llama.cpp model download
        
        return False
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate response using best available offline model."""
        # Select model if not specified
        if model is None:
            selected = self.select_best_model("chat")
            if not selected:
                raise RuntimeError("No suitable offline model found")
            model = selected.name
        else:
            # Find model config
            selected = next(
                (m for m in self.available_models.values() if m.name == model),
                None
            )
            if not selected:
                raise ValueError(f"Unknown model: {model}")
        
        # Ensure model is ready
        if not await self.ensure_model(selected):
            raise RuntimeError(f"Failed to prepare model: {model}")
        
        # Generate based on backend
        if selected.backend == LocalModelType.OLLAMA and self.ollama.is_available:
            response_parts = []
            async for part in self.ollama.generate(model, prompt, stream=True, **kwargs):
                response_parts.append(part)
            return ''.join(response_parts)
        
        elif selected.backend == LocalModelType.LLAMACPP and self.llamacpp.binary_path:
            model_path = self.llamacpp.models_dir / f"{model}.gguf"
            return await self.llamacpp.generate(str(model_path), prompt, **kwargs)
        
        else:
            raise RuntimeError(f"No backend available for {model}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get offline system status."""
        return {
            "is_mobile": self.is_mobile,
            "available_ram_mb": self._get_device_ram(),
            "ollama_available": self.ollama.is_available,
            "llamacpp_available": self.llamacpp.binary_path is not None,
            "available_models": list(self.available_models.keys()),
            "recommended_model": self.select_best_model("chat").name if self.select_best_model("chat") else None
        }


class HybridProvider:
    """
    Intelligent hybrid online/offline provider.
    Uses online when available, falls back to offline seamlessly.
    """
    
    def __init__(self):
        """Initialize hybrid provider."""
        self.offline = OfflineManager()
        self.online_available = True
        self.prefer_offline = os.environ.get("ZEN_PREFER_OFFLINE", "false").lower() == "true"
        self._last_connectivity_check = 0
        
    def _check_connectivity(self) -> bool:
        """Check internet connectivity."""
        import time
        
        # Rate limit checks
        current_time = time.time()
        if current_time - self._last_connectivity_check < 30:
            return self.online_available
        
        self._last_connectivity_check = current_time
        
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            self.online_available = True
        except:
            self.online_available = False
        
        return self.online_available
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        force_offline: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate using best available method."""
        use_offline = (
            force_offline or
            self.prefer_offline or
            not self._check_connectivity()
        )
        
        if use_offline:
            # Use offline model
            try:
                response = await self.offline.generate(prompt, model, **kwargs)
                return {
                    "response": response,
                    "model": model or self.offline.select_best_model("chat").name,
                    "mode": "offline",
                    "cached": False
                }
            except Exception as e:
                if self._check_connectivity():
                    # Try online as fallback
                    logger.warning(f"Offline generation failed, trying online: {e}")
                else:
                    raise
        
        # Use online model (import here to avoid circular dependency)
        from zen.providers.openrouter import OpenRouterProvider
        provider = OpenRouterProvider()
        
        response = await provider.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            **kwargs
        )
        
        return {
            "response": response['choices'][0]['message']['content'],
            "model": response['model'],
            "mode": "online",
            "cached": False,
            "usage": response.get('usage', {})
        }


# Singleton instance
_offline_manager: Optional[OfflineManager] = None
_hybrid_provider: Optional[HybridProvider] = None


def get_offline_manager() -> OfflineManager:
    """Get or create offline manager instance."""
    global _offline_manager
    if _offline_manager is None:
        _offline_manager = OfflineManager()
    return _offline_manager


def get_hybrid_provider() -> HybridProvider:
    """Get or create hybrid provider instance."""
    global _hybrid_provider
    if _hybrid_provider is None:
        _hybrid_provider = HybridProvider()
    return _hybrid_provider


# CLI for testing and management
async def main():
    """CLI for offline model management."""
    import argparse
    
    parser = argparse.ArgumentParser(description="zenOS Offline Model Manager")
    parser.add_argument("command", choices=["status", "list", "download", "test"])
    parser.add_argument("--model", help="Model name")
    parser.add_argument("--prompt", help="Test prompt")
    
    args = parser.parse_args()
    
    manager = get_offline_manager()
    
    if args.command == "status":
        status = manager.get_status()
        print(json.dumps(status, indent=2))
    
    elif args.command == "list":
        models = manager.available_models
        for name, model in models.items():
            mobile_tag = "📱" if model.mobile_optimized else "🖥️"
            print(f"{mobile_tag} {name}: {model.size_mb}MB RAM, {model.quantization}")
    
    elif args.command == "download":
        if not args.model:
            print("Please specify --model")
            return
        
        model = manager.available_models.get(args.model)
        if not model:
            print(f"Unknown model: {args.model}")
            return
        
        success = await manager.ensure_model(model)
        if success:
            print(f"✅ {args.model} ready!")
        else:
            print(f"❌ Failed to prepare {args.model}")
    
    elif args.command == "test":
        prompt = args.prompt or "Hello! Tell me a joke."
        print(f"Testing with: {prompt}")
        
        response = await manager.generate(prompt, model=args.model)
        print(f"\nResponse:\n{response}")


if __name__ == "__main__":
    asyncio.run(main())
