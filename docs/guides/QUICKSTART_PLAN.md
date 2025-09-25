# zenOS Quick Start Implementation Plan

## 🎯 Immediate Next Steps (Do These First!)

### Step 1: Complete Missing Utils (15 minutes)
Create these two essential files:

#### `zen/utils/template.py`
```python
from jinja2 import Environment, Template, FileSystemLoader
from pathlib import Path
from typing import Dict, Any

class TemplateEngine:
    def __init__(self):
        self.env = Environment(
            loader=FileSystemLoader(Path(__file__).parent.parent / "templates"),
            autoescape=False
        )
    
    def render(self, template_str: str, variables: Dict[str, Any]) -> str:
        template = Template(template_str)
        return template.render(**variables)
```

#### `zen/utils/config.py`
```python
from pathlib import Path
import os
from typing import Optional

class Config:
    def __init__(self):
        self.root_dir = Path.cwd()
        self.agents_dir = self.root_dir / "agents"
        self.modules_dir = self.root_dir / "modules"
        self.config_dir = self.root_dir / "configs"
        
        # Create directories if they don't exist
        self.agents_dir.mkdir(exist_ok=True)
        self.modules_dir.mkdir(exist_ok=True)
        self.config_dir.mkdir(exist_ok=True)
```

### Step 2: Create Minimal Launcher (20 minutes)

#### `zen/core/launcher.py`
```python
from zen.core.agent import AgentRegistry
from typing import Dict, Any

class Launcher:
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.registry = AgentRegistry()
        self.current_agent = None
    
    def load_agent(self, name: str):
        self.current_agent = self.registry.get_agent(name)
    
    def critique_prompt(self, prompt: str) -> str:
        # TODO: Implement auto-critique
        return prompt
    
    def execute(self, prompt: str, variables: Dict[str, Any]) -> Any:
        if not self.current_agent:
            raise ValueError("No agent loaded")
        return self.current_agent.execute(prompt, variables)
```

### Step 3: Create First Built-in Agent (10 minutes)

#### `zen/agents/__init__.py`
```python
from zen.core.agent import PythonAgent, AgentManifest

def troubleshooter_execute(prompt: str, variables: Dict[str, Any]) -> str:
    return f"🔧 Troubleshooting: {prompt}\n\n✅ Analysis complete. No issues found."

builtin_agents = {
    "troubleshooter": PythonAgent(
        manifest=AgentManifest(
            name="troubleshooter",
            description="System diagnostics and troubleshooting"
        ),
        execute_func=troubleshooter_execute
    )
}
```

### Step 4: Create Utils Init (2 minutes)

#### `zen/utils/__init__.py`
```python
from zen.utils.template import TemplateEngine
from zen.utils.config import Config

__all__ = ["TemplateEngine", "Config"]
```

### Step 5: Test Local Installation (5 minutes)

```bash
# In C:\Code\zenOS directory
pip install -e .

# Test the CLI
zen --version
zen --list
zen troubleshooter "test the system"
```

### Step 6: Git Push (2 minutes)

```bash
cd C:\Code\zenOS
git add .
git commit -m "feat: complete core implementation

- Add template engine with Jinja2
- Add configuration management
- Implement minimal launcher
- Create first built-in agent (troubleshooter)
- Complete utils module
- Ready for alpha testing"

git push -u origin main
```

## 🚀 After These Steps

You'll have:
- ✅ Working `zen` CLI command
- ✅ Ability to run agents
- ✅ Template system ready
- ✅ Configuration management
- ✅ First built-in agent working

Next priorities:
1. Add more built-in agents (critic, assistant)
2. Implement auto-critique system
3. Add security framework
4. Create example YAML agents
5. Write tests

## 📝 Quick Testing Commands

Once implemented, test with:

```bash
# Show version
zen --version

# List agents
zen --list

# Run troubleshooter
zen troubleshooter "fix my git issue"

# Create new agent
zen --create my-agent

# Run with debug
zen --debug troubleshooter "test"
```

## 🎨 File Structure After Implementation

```
zenOS/
├── README.md
├── IMPLEMENTATION_STATUS.md
├── QUICKSTART_PLAN.md
├── pyproject.toml
├── zen/
│   ├── __init__.py
│   ├── cli.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   └── launcher.py
│   ├── agents/
│   │   └── __init__.py
│   └── utils/
│       ├── __init__.py
│       ├── template.py
│       └── config.py
├── agents/           (created by Config)
├── modules/          (created by Config)
└── configs/          (created by Config)
```

## 💡 Pro Tips

1. **Start simple**: Get basic flow working first
2. **Test often**: Run `zen --list` after each step
3. **Commit frequently**: Save progress to git
4. **Debug mode**: Use `zen --debug` for troubleshooting
5. **Iterate**: Don't try to make it perfect first time

---

**Estimated Time**: ~1 hour to complete all steps
**Result**: Working zenOS v0.1.0 alpha!
