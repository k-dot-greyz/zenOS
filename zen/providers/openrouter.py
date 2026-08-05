"""
OpenRouter Provider - Unified access to all LLMs through OpenRouter.
"""

import asyncio
import json
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, AsyncIterator, Dict, List, Optional

import aiohttp
from pydantic import BaseModel, Field
from rich.console import Console

console = Console()


class ModelTier(Enum):
    """Model tiers for routing decisions."""

    FAST = "fast"  # Quick, cheap models for simple tasks
    BALANCED = "balanced"  # Good balance of cost and capability
    POWERFUL = "powerful"  # Most capable models for complex tasks
    CUSTOM = "custom"  # User-specified model


@dataclass
class ModelConfig:
    """Configuration for a specific model."""

    name: str
    provider: str
    tier: ModelTier
    cost_per_1k_input: float
    cost_per_1k_output: float
    context_window: int
    strengths: List[str]


# Model registry with configurations
MODELS = {
    # Fast tier - for simple queries
    "anthropic/claude-3-haiku": ModelConfig(
        name="anthropic/claude-3-haiku",
        provider="Anthropic",
        tier=ModelTier.FAST,
        cost_per_1k_input=0.00025,
        cost_per_1k_output=0.00125,
        context_window=200000,
        strengths=["speed", "simple_tasks", "cost_effective"],
    ),
    "openai/gpt-3.5-turbo": ModelConfig(
        name="openai/gpt-3.5-turbo",
        provider="OpenAI",
        tier=ModelTier.FAST,
        cost_per_1k_input=0.0005,
        cost_per_1k_output=0.0015,
        context_window=16385,
        strengths=["speed", "general_purpose"],
    ),
    # Balanced tier - good for most tasks
    "anthropic/claude-3-sonnet": ModelConfig(
        name="anthropic/claude-3-sonnet",
        provider="Anthropic",
        tier=ModelTier.BALANCED,
        cost_per_1k_input=0.003,
        cost_per_1k_output=0.015,
        context_window=200000,
        strengths=["reasoning", "coding", "analysis"],
    ),
    "openai/gpt-4-turbo": ModelConfig(
        name="openai/gpt-4-turbo",
        provider="OpenAI",
        tier=ModelTier.BALANCED,
        cost_per_1k_input=0.01,
        cost_per_1k_output=0.03,
        context_window=128000,
        strengths=["coding", "creativity", "vision"],
    ),
    # Powerful tier - for complex tasks
    "anthropic/claude-3-opus": ModelConfig(
        name="anthropic/claude-3-opus",
        provider="Anthropic",
        tier=ModelTier.POWERFUL,
        cost_per_1k_input=0.015,
        cost_per_1k_output=0.075,
        context_window=200000,
        strengths=["complex_reasoning", "debugging", "analysis"],
    ),
    "openai/gpt-4": ModelConfig(
        name="openai/gpt-4",
        provider="OpenAI",
        tier=ModelTier.POWERFUL,
        cost_per_1k_input=0.03,
        cost_per_1k_output=0.06,
        context_window=8192,
        strengths=["reasoning", "consistency"],
    ),
}


class CompletionRequest(BaseModel):
    """Request model for OpenRouter completion."""

    model: str
    messages: List[Dict[str, str]]
    stream: bool = True
    max_tokens: Optional[int] = 2000
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 1.0
    frequency_penalty: Optional[float] = 0.0
    presence_penalty: Optional[float] = 0.0


class OpenRouterProvider:
    """
    Unified interface to all LLMs via OpenRouter.

    Features:
    - Automatic model selection based on task
    - Cost-aware routing
    - Streaming responses
    - Error handling and retries
    - Usage tracking
    """

    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the provider with an API key.
        
        Parameters:
            api_key (Optional[str]): API key to use. If omitted, the OPENROUTER_API_KEY environment variable is used.
        
        Raises:
            ValueError: If no API key is provided or found in the environment.
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key not found. Set OPENROUTER_API_KEY environment variable."
            )

        self.session: Optional[aiohttp.ClientSession] = None
        self.total_cost = 0.0
        self.request_count = 0

    async def __aenter__(self):
        """
        Initialize the HTTP session for context-managed use.
        
        Returns:
            OpenRouterProvider: This provider instance.
        """
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Close the HTTP session when exiting the asynchronous context manager.
        """
        if self.session:
            await self.session.close()

    def select_model(
        self, prompt: str, tier: Optional[ModelTier] = None, max_cost: Optional[float] = None
    ) -> str:
        """
        Select a model based on the requested tier and prompt characteristics.
        
        Parameters:
            prompt (str): The prompt used to determine the model when no tier is specified.
            tier (Optional[ModelTier]): Preferred model tier. The least expensive registered
                model in this tier is selected when available.
            max_cost (Optional[float]): Accepted for interface compatibility but does not
                affect model selection.
        
        Returns:
            str: The selected model identifier.
        """
        if tier:
            # Use specified tier
            tier_models = [m for m in MODELS.values() if m.tier == tier]
            if tier_models:
                return min(tier_models, key=lambda m: m.cost_per_1k_input).name

        # Analyze prompt for routing
        prompt_lower = prompt.lower()
        prompt_length = len(prompt)

        # Debugging or error analysis - use powerful model
        if any(word in prompt_lower for word in ["debug", "error", "bug", "fix", "broken"]):
            return "anthropic/claude-3-opus"

        # Code generation - use balanced model
        if any(word in prompt_lower for word in ["code", "function", "implement", "write"]):
            return "openai/gpt-4-turbo"

        # Simple questions - use fast model
        if prompt_length < 100 and "?" in prompt:
            return "anthropic/claude-3-haiku"

        # Complex analysis - use powerful model
        if any(word in prompt_lower for word in ["analyze", "explain", "compare", "evaluate"]):
            return "anthropic/claude-3-sonnet"

        # Default to balanced
        return "anthropic/claude-3-sonnet"

    async def complete(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        stream: bool = True,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs,
    ) -> AsyncIterator[str]:
        """
        Obtain a completion from OpenRouter.
        
        Parameters:
            prompt (str): The user prompt to send.
            model (Optional[str]): Model identifier; selected automatically when omitted.
            system (Optional[str]): Optional system prompt.
            stream (bool): Whether to yield incremental chunks instead of one complete response.
            max_tokens (int): Maximum number of response tokens.
            temperature (float): Sampling temperature.
            **kwargs: Additional completion request parameters.
        
        Returns:
            str: Response text, yielded incrementally when streaming or as one complete response otherwise.
        
        Raises:
            Exception: If the OpenRouter request or response handling fails.
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        # Auto-select model if not specified
        if not model:
            model = self.select_model(prompt)

        # Build messages
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        # Create request
        request = CompletionRequest(
            model=model,
            messages=messages,
            stream=stream,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs,
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/k-dot-greyz/zenOS",
            "X-Title": "zenOS CLI",
            "Content-Type": "application/json",
        }

        try:
            if stream:
                async for chunk in self._stream_completion(request.dict(), headers):
                    yield chunk
            else:
                response = await self._get_completion(request.dict(), headers)
                yield response
        except Exception as e:
            console.print(f"[red]Error calling OpenRouter: {e}[/red]")
            raise

    async def _stream_completion(
        self, data: Dict[str, Any], headers: Dict[str, str]
    ) -> AsyncIterator[str]:
        """
        Stream completion content from OpenRouter.
        
        Args:
            data: The chat-completion request payload.
            headers: HTTP headers for the request.
        
        Yields:
            Content fragments from the streamed completion.
        
        Raises:
            Exception: If OpenRouter returns a non-successful HTTP status.
        """
        async with self.session.post(
            f"{self.BASE_URL}/chat/completions", headers=headers, json=data
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"OpenRouter API error: {response.status} - {error_text}")

            async for line in response.content:
                line = line.decode("utf-8").strip()
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break

                    try:
                        data = json.loads(data_str)
                        if "choices" in data and len(data["choices"]) > 0:
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
                    except json.JSONDecodeError:
                        continue

    async def _get_completion(self, data: Dict[str, Any], headers: Dict[str, str]) -> str:
        """Retrieve a non-streaming completion from OpenRouter.
        
        Parameters:
        	data (Dict[str, Any]): The request payload.
        	headers (Dict[str, str]): HTTP headers for the request.
        
        Returns:
        	str: The content of the first completion choice.
        
        Raises:
        	Exception: If the API request fails or returns no completion.
        """
        data["stream"] = False

        async with self.session.post(
            f"{self.BASE_URL}/chat/completions", headers=headers, json=data
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"OpenRouter API error: {response.status} - {error_text}")

            result = await response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                raise Exception("No completion returned from OpenRouter")

    def estimate_cost(self, prompt: str, model: str, max_tokens: int = 2000) -> float:
        """
        Estimate the completion cost in US dollars.
        
        Parameters:
            prompt (str): Prompt text used to estimate input tokens.
            model (str): Model identifier from the model registry.
            max_tokens (int): Maximum number of output tokens.
        
        Returns:
            float: Estimated input and output cost in US dollars, or 0.0 for an unregistered model.
        """
        if model not in MODELS:
            return 0.0

        config = MODELS[model]

        # Rough token estimation (4 chars per token)
        input_tokens = len(prompt) / 4
        output_tokens = max_tokens

        input_cost = (input_tokens / 1000) * config.cost_per_1k_input
        output_cost = (output_tokens / 1000) * config.cost_per_1k_output

        return input_cost + output_cost

    def get_model_info(self, model: str) -> Optional[ModelConfig]:
        """Get information about a specific model."""
        return MODELS.get(model)

    def list_models(self, tier: Optional[ModelTier] = None) -> List[ModelConfig]:
        """
        List the available model configurations, optionally filtered by tier.
        
        Parameters:
            tier (Optional[ModelTier]): Restrict results to models in this tier.
        
        Returns:
            List[ModelConfig]: The matching model configurations.
        """
        models = list(MODELS.values())
        if tier:
            models = [m for m in models if m.tier == tier]
        return models
