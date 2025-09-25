# 🧘 zenOS: AI CLI Tool Architecture

## Vision: The AI Assistant That Lives in Your Terminal

zenOS is a Docker-powered AI CLI tool that combines the best of claude-cli, GitHub Copilot CLI, and agent-based systems into one beautiful, zen-like experience.

---

## 🎯 Core Features as an AI CLI Tool

### 1. **Primary Use Cases** (Like claude-cli, gemini, etc.)
```bash
# Quick questions
zen "explain this error" < error.log
zen "how do I fix merge conflicts?"

# Code generation
zen code "python function to parse JSON with error handling"
zen refactor "make this code more pythonic" main.py

# File context awareness
zen review changes.diff
zen explain src/complex_module.py
zen test "write tests for" user_service.py

# Interactive chat mode
zen chat
> What's the best way to implement caching?
> Show me an example with Redis
> Now convert it to use memcached

# Piping and composition
git diff | zen review
cat README.md | zen improve
zen generate "API docs" | tee api.md
```

### 2. **OpenRouter Integration**
```bash
# Model selection
zen --model claude-3-opus "complex reasoning task"
zen --model gpt-4-turbo "creative writing"
zen --model llama-2-70b "code generation"
zen --model mixtral-8x7b "quick question"

# Automatic routing based on task
zen auto "simple task"  # Routes to fast/cheap model
zen pro "complex analysis"  # Routes to powerful model

# Cost-aware routing
zen --max-cost 0.10 "analyze this codebase"
zen --prefer-cheap "bulk process these files"
```

### 3. **Agent Mode** (Our Special Sauce)
```bash
# Built-in specialized agents
zen agent troubleshoot "debug this error"
zen agent critic "review my prompt"
zen agent security "audit this code"
zen agent architect "design a microservice"

# Custom agents
zen agent custom-reviewer "check my PR"
zen create-agent "code-reviewer"
```

---

## 🐳 Docker Compose Architecture

### Service Structure
```yaml
# docker-compose.yml
version: '3.8'

services:
  # Core zenOS CLI service
  zen-cli:
    build: ./zen-cli
    image: zenos/cli:latest
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - ZEN_CONFIG_PATH=/config
    volumes:
      - ./config:/config
      - ./workspace:/workspace
      - ~/.zenOS:/home/zen/.zenOS
    networks:
      - zen-network
    stdin_open: true
    tty: true

  # Conversation history & vector DB
  zen-memory:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=zenos
      - POSTGRES_USER=zen
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - zen-data:/var/lib/postgresql/data
    networks:
      - zen-network

  # Redis for caching and rate limiting
  zen-cache:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - zen-cache:/data
    networks:
      - zen-network

  # Optional: Local embedding service
  zen-embeddings:
    image: zenos/embeddings:latest
    build: ./services/embeddings
    environment:
      - MODEL_NAME=all-MiniLM-L6-v2
    networks:
      - zen-network

  # Optional: Web UI
  zen-ui:
    image: zenos/ui:latest
    build: ./web-ui
    ports:
      - "3000:3000"
    environment:
      - API_URL=http://zen-cli:8080
    networks:
      - zen-network

volumes:
  zen-data:
  zen-cache:

networks:
  zen-network:
    driver: bridge
```

### Container Benefits
1. **Isolation**: Each service in its own container
2. **Portability**: Run anywhere Docker runs
3. **Scalability**: Easy to scale services independently
4. **Development**: Consistent environment across teams
5. **Deployment**: Simple `docker-compose up` deployment

---

## 🏗️ Implementation Architecture

### 1. **CLI Layer** (Python + Click + Rich)
```python
# zen/cli.py
import click
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown

@click.command()
@click.argument('prompt', required=False)
@click.option('--model', '-m', help='Specific model to use')
@click.option('--stream', '-s', is_flag=True, help='Stream response')
@click.option('--context', '-c', type=click.Path(), help='Include file context')
def zen(prompt, model, stream, context):
    """zenOS: Your AI assistant in the terminal"""
    if not prompt:
        # Enter interactive mode
        start_interactive_session()
    else:
        # Single query mode
        response = query_ai(prompt, model, context)
        display_response(response, stream)
```

### 2. **OpenRouter Provider**
```python
# zen/providers/openrouter.py
from typing import Optional, AsyncIterator
import httpx
from pydantic import BaseModel

class OpenRouterProvider:
    """Unified interface to all LLMs via OpenRouter"""
    
    BASE_URL = "https://openrouter.ai/api/v1"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient()
    
    async def complete(
        self,
        prompt: str,
        model: Optional[str] = None,
        stream: bool = True,
        max_tokens: int = 2000,
        temperature: float = 0.7
    ) -> AsyncIterator[str]:
        """Stream completion from OpenRouter"""
        
        # Auto-select model based on task complexity
        if not model:
            model = self.select_model(prompt)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/kasparsgreizis/zenOS",
            "X-Title": "zenOS CLI"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": stream,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        async with self.client.stream(
            "POST",
            f"{self.BASE_URL}/chat/completions",
            headers=headers,
            json=data
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    yield self.parse_sse(line)
    
    def select_model(self, prompt: str) -> str:
        """Intelligently route to appropriate model"""
        prompt_length = len(prompt)
        
        if "debug" in prompt.lower() or "error" in prompt.lower():
            return "anthropic/claude-3-opus"  # Best for debugging
        elif prompt_length < 100:
            return "anthropic/claude-3-haiku"  # Fast for simple queries
        elif "code" in prompt.lower():
            return "openai/gpt-4-turbo"  # Good for code generation
        else:
            return "anthropic/claude-3-sonnet"  # Balanced default
```

### 3. **Context Management**
```python
# zen/core/context.py
from pathlib import Path
from typing import List, Dict
import git

class ContextManager:
    """Manages file and project context for AI queries"""
    
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.repo = self._get_git_repo()
    
    def get_file_context(self, file_path: Path) -> str:
        """Get file content with syntax highlighting info"""
        content = file_path.read_text()
        language = self._detect_language(file_path)
        return f"```{language}\n{content}\n```"
    
    def get_diff_context(self) -> str:
        """Get current git diff"""
        if self.repo:
            return self.repo.git.diff()
        return ""
    
    def get_project_context(self) -> Dict:
        """Get project structure and key files"""
        return {
            "structure": self._get_tree(),
            "readme": self._get_readme(),
            "dependencies": self._get_dependencies(),
            "recent_changes": self.get_diff_context()
        }
```

### 4. **Conversation Management**
```python
# zen/core/conversation.py
from typing import List, Optional
from datetime import datetime
import asyncpg

class ConversationManager:
    """Manages conversation history and context"""
    
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.current_session: Optional[str] = None
    
    async def start_session(self) -> str:
        """Start a new conversation session"""
        session_id = generate_session_id()
        self.current_session = session_id
        
        async with asyncpg.connect(self.db_url) as conn:
            await conn.execute("""
                INSERT INTO sessions (id, started_at)
                VALUES ($1, $2)
            """, session_id, datetime.now())
        
        return session_id
    
    async def add_message(self, role: str, content: str):
        """Add message to conversation history"""
        async with asyncpg.connect(self.db_url) as conn:
            await conn.execute("""
                INSERT INTO messages (session_id, role, content, timestamp)
                VALUES ($1, $2, $3, $4)
            """, self.current_session, role, content, datetime.now())
    
    async def get_context(self, limit: int = 10) -> List[Dict]:
        """Get recent conversation context"""
        async with asyncpg.connect(self.db_url) as conn:
            rows = await conn.fetch("""
                SELECT role, content FROM messages
                WHERE session_id = $1
                ORDER BY timestamp DESC
                LIMIT $2
            """, self.current_session, limit)
        
        return [dict(row) for row in reversed(rows)]
```

---

## 🎨 Beautiful CLI Experience

### Rich Terminal UI
```python
# zen/ui/display.py
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
from rich.table import Table

console = Console()

def display_response(response: str, format: str = "markdown"):
    """Display AI response with beautiful formatting"""
    
    if format == "markdown":
        md = Markdown(response)
        console.print(Panel(md, title="🧘 zenOS", border_style="cyan"))
    elif format == "code":
        # Detect language and syntax highlight
        syntax = Syntax(response, "python", theme="monokai")
        console.print(Panel(syntax, title="Generated Code"))
    else:
        console.print(Panel(response, title="Response"))

def show_thinking():
    """Show a beautiful thinking animation"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[cyan]Contemplating your request..."),
        console=console
    ) as progress:
        task = progress.add_task("thinking", total=None)
        # This runs while waiting for API response
```

### Interactive Mode
```python
# zen/ui/interactive.py
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter

def start_interactive_session():
    """Start an interactive chat session"""
    
    console.print(Panel.fit(
        "[cyan]🧘 Welcome to zenOS Interactive Mode[/cyan]\n"
        "Type 'help' for commands, 'exit' to quit",
        border_style="green"
    ))
    
    history = FileHistory('.zen_history')
    completer = WordCompleter([
        'help', 'exit', 'clear', 'save', 'load',
        'model:', 'context:', 'agent:', 'mode:'
    ])
    
    while True:
        try:
            user_input = prompt(
                '🧘 > ',
                history=history,
                auto_suggest=AutoSuggestFromHistory(),
                completer=completer
            )
            
            if user_input.lower() == 'exit':
                break
            
            # Process and display response
            response = await process_query(user_input)
            display_response(response)
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Use 'exit' to quit[/yellow]")
```

---

## 🚀 Quick Start Experience

### 1. **Installation**
```bash
# One-liner with Docker
curl -sSL https://get.zenos.ai | bash

# This installs:
# - Docker images
# - Shell alias 'zen'
# - Config in ~/.zenOS/
```

### 2. **First Run**
```bash
# First time setup
zen init
> 🧘 Welcome to zenOS!
> Enter your OpenRouter API key: sk-or-...
> Select default model: [1] Claude 3 [2] GPT-4 [3] Auto
> Enable telemetry? [y/N]: n
> ✅ Setup complete! Try: zen "hello world"

# First query
zen "what is zenOS?"
> 🧘 zenOS is your AI assistant in the terminal...
```

### 3. **Daily Usage**
```bash
# Morning standup
zen standup "check my TODOs and recent commits"

# Debugging session
zen debug error.log --context src/

# Code review
git diff | zen review --style google

# Learning
zen explain "how do async functions work in Python?"
```

---

## 🔥 Unique Features That Set Us Apart

### 1. **Mindful Coding Mode**
```bash
zen mindful "refactor this function"
# Provides step-by-step reasoning
# Explains trade-offs
# Suggests alternatives
```

### 2. **Auto-Critique Everything**
```bash
zen --critique "generate a REST API"
# Generates code
# Automatically critiques it
# Provides improved version
```

### 3. **Project-Aware Context**
```bash
cd my-project/
zen understand
# Analyzes entire project structure
# Understands dependencies
# Learns your coding style
```

### 4. **Cost-Conscious Routing**
```bash
zen --budget 1.00 "process all files in src/"
# Automatically uses cheaper models
# Batches requests efficiently
# Shows cost breakdown
```

### 5. **Agent Marketplace**
```bash
zen marketplace search "testing"
# Browse community agents
# One-click install
# Rate and review
```

---

## 📊 Why This Architecture Wins

### For Users
- **Instant Value**: Works out of the box with minimal setup
- **Flexibility**: Use as simple Q&A or complex agent system
- **Cost Control**: OpenRouter gives transparency and choice
- **Beautiful UX**: Rich terminal output that's a joy to use

### For Developers
- **Docker Simplicity**: No dependency hell
- **Extensible**: Easy to add new providers, agents, features
- **Modern Python**: Async, type hints, clean architecture
- **Well-Tested**: Unit, integration, and e2e tests

### For the Business
- **Differentiation**: Unique features like mindful coding
- **Monetization**: Premium agents, team features, enterprise
- **Community**: Agent marketplace drives adoption
- **Analytics**: Usage patterns inform development

---

## 🎯 Implementation Priority

### Implementation Board: Core CLI
1. Basic Docker setup
2. OpenRouter integration
3. Simple query/response
4. Streaming output
5. Basic context (files)

### Implementation Board: Intelligence
1. Conversation history
2. Project understanding
3. Smart model routing
4. Cost tracking
5. Auto-critique

### Implementation Board: Polish
1. Beautiful Rich UI
2. Interactive mode
3. Shell completions
4. Error handling
5. Progress indicators

### Implementation Board: Launch
1. Documentation
2. Install script
3. Demo video
4. Community agents
5. Marketing site

---

**"zenOS: Where AI meets the command line, beautifully."** 🧘✨
