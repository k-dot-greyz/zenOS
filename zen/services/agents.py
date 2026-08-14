"""Agent list/get/execute use cases shared by CLI and HTTP."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from zen.core.agent import AgentRegistry
from zen.core.launcher import Launcher
from zen.services.errors import NotFoundError

logger = logging.getLogger(__name__)


class AgentService:
    """Orchestrate agent catalog and execution without terminal I/O."""

    def __init__(
        self,
        registry: Optional[AgentRegistry] = None,
        launcher: Optional[Launcher] = None,
        debug: bool = False,
    ) -> None:
        self._registry = registry
        self._launcher = launcher
        self.debug = debug

    def _get_registry(self) -> AgentRegistry:
        if self._registry is None:
            self._registry = AgentRegistry()
        return self._registry

    def list_agents(self) -> list[Dict[str, Any]]:
        """Return agent catalog entries."""
        return self._get_registry().list_agents()

    def get_agent(self, name: str) -> Dict[str, Any]:
        """Return one catalog entry or raise NotFoundError."""
        for entry in self.list_agents():
            if entry["name"] == name:
                return entry
        raise NotFoundError(f"Agent not found: {name}", details={"id": name})

    def _launcher_for(self, agent: Any) -> Launcher:
        if self._launcher is not None:
            self._launcher.current_agent = agent
            return self._launcher
        launcher = Launcher(debug=self.debug, registry=self._get_registry())
        launcher.current_agent = agent
        return launcher

    async def execute_async(
        self,
        name: str,
        prompt: str,
        variables: Optional[Dict[str, Any]] = None,
        *,
        no_critique: bool = True,
        upgrade_only: bool = False,
    ) -> Any:
        """Execute a named agent and return its raw result."""
        registry = self._get_registry()
        try:
            agent = registry.get_agent(name)
        except ValueError as exc:
            raise NotFoundError(f"Agent not found: {name}", details={"id": name}) from exc

        launcher = self._launcher_for(agent)
        vars_in = variables or {}
        if not no_critique:
            prompt = await launcher.critique_prompt_async(prompt)
            if upgrade_only:
                return {"upgraded_prompt": prompt}
        elif upgrade_only:
            return {"upgraded_prompt": prompt}
        return await launcher.execute_async(prompt, vars_in)

    def execute(
        self,
        name: str,
        prompt: str,
        variables: Optional[Dict[str, Any]] = None,
        *,
        no_critique: bool = True,
        upgrade_only: bool = False,
    ) -> Any:
        """Synchronous wrapper for execute_async."""
        import asyncio

        return asyncio.run(
            self.execute_async(
                name,
                prompt,
                variables,
                no_critique=no_critique,
                upgrade_only=upgrade_only,
            )
        )
