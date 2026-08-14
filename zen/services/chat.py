"""Chat completions streamed as delta packets."""

from __future__ import annotations

from typing import AsyncIterator, Callable, Optional

from zen.services.errors import UnavailableError

Completer = Callable[[str, Optional[str]], AsyncIterator[str]]


class ChatService:
    """Stream chat tokens from OpenRouter or an injected completer."""

    def __init__(self, completer: Optional[Completer] = None) -> None:
        self._completer = completer

    async def stream(self, message: str, model: Optional[str] = None) -> AsyncIterator[str]:
        """Yield text chunks for a chat message."""
        if self._completer is not None:
            async for chunk in self._completer(message, model):
                yield chunk
            return
        try:
            from zen.providers.openrouter import OpenRouterProvider
        except Exception as exc:
            raise UnavailableError("Chat provider is not available", details={"error": str(exc)}) from exc
        try:
            async with OpenRouterProvider() as provider:
                async for chunk in provider.complete(message, model=model, stream=True):
                    yield chunk
        except ValueError as exc:
            raise UnavailableError(str(exc)) from exc
