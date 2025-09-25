"""
Agent base class and registry for zenOS.
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

from zen.utils.template import TemplateEngine
from zen.utils.config import Config


@dataclass
class AgentManifest:
    """Agent manifest data structure."""
    name: str
    description: str
    version: str = "1.0.0"
    author: str = ""
    tags: List[str] = None
    variables: Dict[str, Any] = None
    modules: Dict[str, List[str]] = None
    prompt_template: str = ""
    
    @classmethod
    def from_yaml(cls, yaml_path: Path) -> "AgentManifest":
        """Load agent manifest from YAML file."""
        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f)
        
        return cls(
            name=data.get("name", yaml_path.stem),
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
            author=data.get("author", ""),
            tags=data.get("tags", []),
            variables=data.get("variables", {}),
            modules=data.get("modules", {}),
            prompt_template=data.get("prompt_template", ""),
        )


class Agent(ABC):
    """Base class for all zenOS agents."""
    
    def __init__(self, manifest: AgentManifest):
        self.manifest = manifest
        self.template_engine = TemplateEngine()
        self.config = Config()
    
    @abstractmethod
    def execute(self, prompt: str, variables: Dict[str, Any]) -> Any:
        """Execute the agent with the given prompt and variables."""
        pass
    
    def render_prompt(self, prompt: str, variables: Dict[str, Any]) -> str:
        """Render the final prompt using templates and modules."""
        # Merge variables
        all_vars = {
            **(self.manifest.variables or {}),
            **variables,
            "user_prompt": prompt,
            "prompt": prompt,  # Also add as 'prompt' for template compatibility
        }
        
        # Load and render modules
        rendered_modules = {}
        if self.manifest.modules:
            for module_type, module_names in self.manifest.modules.items():
                rendered_modules[module_type] = []
                for module_name in module_names:
                    module_content = self.load_module(module_type, module_name)
                    rendered_content = self.template_engine.render(module_content, all_vars)
                    rendered_modules[module_type].append(rendered_content)
        
        # Combine everything into final prompt
        final_vars = {
            **all_vars,
            **rendered_modules,
        }
        
        if self.manifest.prompt_template:
            return self.template_engine.render(self.manifest.prompt_template, final_vars)
        else:
            # Default template
            parts = []
            if "roles" in rendered_modules:
                parts.extend(rendered_modules["roles"])
            if "contexts" in rendered_modules:
                parts.extend(rendered_modules["contexts"])
            if "tasks" in rendered_modules:
                parts.extend(rendered_modules["tasks"])
            parts.append(prompt)
            if "constraints" in rendered_modules:
                parts.extend(rendered_modules["constraints"])
            
            return "\n\n".join(parts)
    
    def load_module(self, module_type: str, module_name: str) -> str:
        """Load a module from the modules directory."""
        module_path = self.config.modules_dir / module_type / f"{module_name}.md"
        if module_path.exists():
            return module_path.read_text()
        else:
            # Try loading from built-in modules
            builtin_path = Path(__file__).parent.parent / "modules" / module_type / f"{module_name}.md"
            if builtin_path.exists():
                return builtin_path.read_text()
            else:
                raise FileNotFoundError(f"Module not found: {module_type}/{module_name}")


class YAMLAgent(Agent):
    """Agent defined by a YAML manifest file."""
    
    def execute(self, prompt: str, variables: Dict[str, Any]) -> str:
        """Execute the agent by rendering the prompt."""
        return self.render_prompt(prompt, variables)


class PythonAgent(Agent):
    """Agent defined by Python code."""
    
    def __init__(self, manifest: AgentManifest, execute_func):
        super().__init__(manifest)
        self.execute_func = execute_func
    
    def execute(self, prompt: str, variables: Dict[str, Any]) -> Any:
        """Execute the agent using the provided function."""
        rendered_prompt = self.render_prompt(prompt, variables)
        return self.execute_func(rendered_prompt, variables)


class AgentRegistry:
    """Registry for managing agents."""
    
    def __init__(self):
        self.config = Config()
        self._agents: Dict[str, Agent] = {}
        self._load_agents()
    
    def _load_agents(self) -> None:
        """Load all available agents."""
        # Load YAML agents from agents directory
        agents_dir = self.config.agents_dir
        if agents_dir.exists():
            for yaml_file in agents_dir.glob("*.yaml"):
                try:
                    manifest = AgentManifest.from_yaml(yaml_file)
                    self._agents[manifest.name] = YAMLAgent(manifest)
                except Exception as e:
                    print(f"Failed to load agent {yaml_file}: {e}")
        
        # Load built-in agents
        self._load_builtin_agents()
    
    def _load_builtin_agents(self) -> None:
        """Load built-in agents."""
        # These will be Python-based agents
        from zen.agents import builtin_agents
        for name, agent in builtin_agents.items():
            self._agents[name] = agent
    
    def get_agent(self, name: str) -> Agent:
        """Get an agent by name."""
        if name not in self._agents:
            raise ValueError(f"Agent not found: {name}")
        return self._agents[name]
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all available agents."""
        agents = []
        for name, agent in self._agents.items():
            agents.append({
                "name": name,
                "description": agent.manifest.description,
                "type": "builtin" if isinstance(agent, PythonAgent) else "custom",
                "version": agent.manifest.version,
                "author": agent.manifest.author,
                "tags": agent.manifest.tags,
            })
        return agents
    
    def create_agent(self, name: str) -> Path:
        """Create a new agent from template."""
        agent_path = self.config.agents_dir / f"{name}.yaml"
        
        if agent_path.exists():
            raise ValueError(f"Agent already exists: {name}")
        
        # Create agents directory if it doesn't exist
        self.config.agents_dir.mkdir(parents=True, exist_ok=True)
        
        # Create agent template
        template = {
            "name": name,
            "description": f"Description for {name} agent",
            "version": "1.0.0",
            "author": "Your Name",
            "tags": ["custom"],
            "variables": {
                "example_var": "example_value",
            },
            "modules": {
                "roles": [],
                "contexts": [],
                "tasks": [],
                "constraints": [],
            },
            "prompt_template": "# {name} Agent\n\n{user_prompt}",
        }
        
        with open(agent_path, "w") as f:
            yaml.dump(template, f, default_flow_style=False, sort_keys=False)
        
        return agent_path
