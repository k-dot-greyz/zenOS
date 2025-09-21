# 🔌 zenOS Plugin System Specification
## GitHub Repository as VST Plugin Architecture

*"Every GitHub repo is a potential AI tool, every commit is a new feature, every pull request is a collaboration"*

---

## 📋 Plugin Manifest Specification

### Core Manifest Structure
```yaml
# zenos-plugin.yaml (required in repo root)
plugin:
  # Basic Information
  id: "com.github.username.plugin-name"  # Unique identifier
  name: "Human Readable Name"
  version: "1.2.3"  # Semantic versioning
  author: "Author Name"
  email: "author@example.com"
  description: "Brief description of what this plugin does"
  homepage: "https://github.com/username/plugin-name"
  license: "MIT"  # SPDX license identifier
  
  # Plugin Classification
  category: "text-processing"  # Primary category
  subcategories: ["nlp", "translation", "summarization"]
  tags: ["ai", "mobile", "voice", "offline"]
  
  # Compatibility Matrix
  compatibility:
    min_zenos_version: "1.0.0"
    max_zenos_version: "2.0.0"  # Optional, for breaking changes
    platforms: ["android", "ios", "web"]
    architectures: ["arm64", "x86_64"]
    python_version: ">=3.8"
  
  # Plugin Capabilities
  capabilities:
    - "text_processing"
    - "api_integration"
    - "file_handling"
    - "voice_processing"
    - "image_processing"
    - "data_analysis"
    - "web_scraping"
    - "database_operations"
  
  # Entry Points (like VST plugin entry points)
  entry_points:
    main: "src/main.py"           # Primary entry point
    mobile: "src/mobile.py"       # Mobile-optimized version
    web: "src/web.py"             # Web interface
    cli: "src/cli.py"             # Command-line interface
    api: "src/api.py"             # REST API endpoint
  
  # Dependencies
  dependencies:
    python:
      - "requests>=2.28.0"
      - "transformers>=4.20.0"
      - "torch>=1.12.0"
    system:
      - "ffmpeg"                  # For audio processing
      - "tesseract"               # For OCR
    zenos:
      - "zenos-core>=1.0.0"
      - "zenos-mobile>=1.0.0"
  
  # Configuration Schema
  config_schema:
    api_key:
      type: "string"
      required: true
      sensitive: true
      description: "API key for external service"
      validation:
        pattern: "^[a-zA-Z0-9]{32,}$"
    model_size:
      type: "enum"
      options: ["small", "medium", "large"]
      default: "medium"
      description: "Size of AI model to use"
    batch_size:
      type: "integer"
      min: 1
      max: 100
      default: 10
      description: "Number of items to process in batch"
    enable_caching:
      type: "boolean"
      default: true
      description: "Enable response caching"
  
  # Mobile-Specific Optimizations
  mobile:
    battery_aware: true           # Adjust behavior based on battery
    offline_capable: false        # Can work without internet
    voice_input: true             # Supports voice input
    gesture_support:              # Supported gestures
      - "swipe_left"
      - "swipe_right"
      - "pinch_zoom"
      - "long_press"
    ui_components:                # Custom UI components
      main_screen: "ui/main_screen.jsx"
      settings: "ui/settings.jsx"
      gesture_handler: "ui/gestures.jsx"
    performance_profile: "balanced"  # battery, balanced, performance
  
  # Security & Permissions
  permissions:
    - "internet"                  # Network access
    - "file_system_read"          # Read files
    - "file_system_write"         # Write files
    - "camera"                    # Camera access
    - "microphone"                # Audio recording
    - "location"                  # GPS location
    - "contacts"                  # Contact list access
  
  # Plugin Lifecycle Hooks
  lifecycle:
    on_install: "hooks/install.py"
    on_uninstall: "hooks/uninstall.py"
    on_update: "hooks/update.py"
    on_activate: "hooks/activate.py"
    on_deactivate: "hooks/deactivate.py"
  
  # Procedures (like VST presets)
  procedures:
    - id: "plugin.summarize"
      name: "Smart Summarization"
      description: "Summarize any text intelligently"
      input_types: ["text", "url", "file"]
      output_types: ["text", "markdown"]
      parameters:
        max_length:
          type: "integer"
          default: 200
          description: "Maximum summary length"
        style:
          type: "enum"
          options: ["bullet", "paragraph", "outline"]
          default: "bullet"
    
    - id: "plugin.translate"
      name: "Real-time Translation"
      description: "Translate text between languages"
      input_types: ["text", "voice"]
      output_types: ["text", "voice"]
      parameters:
        target_language:
          type: "string"
          required: true
          description: "Target language code"
        preserve_formatting:
          type: "boolean"
          default: true
  
  # Plugin Marketplace Info
  marketplace:
    featured: false
    price: 0.00                  # Free by default
    currency: "USD"
    screenshots:
      - "screenshots/main.png"
      - "screenshots/settings.png"
    demo_video: "https://youtube.com/watch?v=demo"
    documentation: "https://github.com/username/plugin-name/wiki"
    support_url: "https://github.com/username/plugin-name/issues"
    
  # Analytics & Metrics
  analytics:
    track_usage: true
    track_errors: true
    track_performance: true
    privacy_policy: "https://example.com/privacy"
    
  # Development Info
  development:
    repository: "https://github.com/username/plugin-name"
    issues: "https://github.com/username/plugin-name/issues"
    discussions: "https://github.com/username/plugin-name/discussions"
    contributing: "https://github.com/username/plugin-name/blob/main/CONTRIBUTING.md"
    changelog: "https://github.com/username/plugin-name/blob/main/CHANGELOG.md"
```

---

## 🐍 Plugin Interface Classes

### Base Plugin Interface
```python
# zenos_plugin/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
import asyncio

@dataclass
class PluginContext:
    """Context information passed to plugins"""
    user_id: str
    session_id: str
    device_info: Dict[str, Any]
    mobile_context: Optional['MobileContext'] = None
    zenos_config: Dict[str, Any] = None

@dataclass
class PluginResult:
    """Standardized result from plugin processing"""
    success: bool
    data: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    performance_metrics: Dict[str, float] = None

class BasePlugin(ABC):
    """Base class for all zenOS plugins"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.manifest = self._load_manifest()
        self.is_initialized = False
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the plugin"""
        pass
    
    @abstractmethod
    async def process(self, input_data: Any, context: PluginContext) -> PluginResult:
        """Main processing function - like VST process()"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> bool:
        """Cleanup resources"""
        pass
    
    def get_manifest(self) -> Dict[str, Any]:
        """Get plugin manifest"""
        return self.manifest
    
    def get_capabilities(self) -> List[str]:
        """Get plugin capabilities"""
        return self.manifest.get('capabilities', [])
    
    def get_procedures(self) -> List[Dict[str, Any]]:
        """Get available procedures"""
        return self.manifest.get('procedures', [])
    
    def validate_config(self) -> bool:
        """Validate plugin configuration"""
        # Implementation for config validation
        pass
    
    def _load_manifest(self) -> Dict[str, Any]:
        """Load plugin manifest"""
        # Implementation for manifest loading
        pass
```

### Mobile Plugin Interface
```python
# zenos_plugin/mobile.py
from zenos_plugin.base import BasePlugin, PluginContext, PluginResult
from typing import Any, Dict, List, Optional
import asyncio

class MobilePlugin(BasePlugin):
    """Base class for mobile-optimized plugins"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.mobile_config = config.get('mobile', {})
        self.battery_aware = self.mobile_config.get('battery_aware', False)
        self.offline_capable = self.mobile_config.get('offline_capable', False)
    
    async def process(self, input_data: Any, context: PluginContext) -> PluginResult:
        """Main processing with mobile optimizations"""
        try:
            # Check mobile context
            if context.mobile_context:
                if self.battery_aware and context.mobile_context.battery_level < 20:
                    return await self._low_battery_mode(input_data, context)
                
                if not context.mobile_context.has_internet and not self.offline_capable:
                    return PluginResult(
                        success=False,
                        data=None,
                        error="Internet required but not available"
                    )
            
            # Process with mobile optimizations
            return await self._process_mobile(input_data, context)
            
        except Exception as e:
            return PluginResult(
                success=False,
                data=None,
                error=str(e)
            )
    
    async def _process_mobile(self, input_data: Any, context: PluginContext) -> PluginResult:
        """Mobile-optimized processing - override in subclasses"""
        return await self.process(input_data, context)
    
    async def _low_battery_mode(self, input_data: Any, context: PluginContext) -> PluginResult:
        """Low battery mode processing - override in subclasses"""
        return await self.process(input_data, context)
    
    async def on_voice_input(self, audio_data: bytes, context: PluginContext) -> PluginResult:
        """Handle voice input specifically"""
        # Convert audio to text
        text = await self._speech_to_text(audio_data)
        return await self.process(text, context)
    
    async def on_gesture(self, gesture: str, data: Dict[str, Any], context: PluginContext) -> PluginResult:
        """Handle mobile gestures"""
        gesture_handlers = {
            'swipe_left': self._handle_swipe_left,
            'swipe_right': self._handle_swipe_right,
            'pinch_zoom': self._handle_pinch_zoom,
            'long_press': self._handle_long_press
        }
        
        handler = gesture_handlers.get(gesture)
        if handler:
            return await handler(data, context)
        
        return PluginResult(
            success=False,
            data=None,
            error=f"Unsupported gesture: {gesture}"
        )
    
    def get_ui_components(self) -> Dict[str, str]:
        """Return mobile UI components"""
        return self.mobile_config.get('ui_components', {})
    
    def get_gesture_support(self) -> List[str]:
        """Get supported gestures"""
        return self.mobile_config.get('gesture_support', [])
    
    # Gesture handlers - override in subclasses
    async def _handle_swipe_left(self, data: Dict[str, Any], context: PluginContext) -> PluginResult:
        """Handle swipe left gesture"""
        pass
    
    async def _handle_swipe_right(self, data: Dict[str, Any], context: PluginContext) -> PluginResult:
        """Handle swipe right gesture"""
        pass
    
    async def _handle_pinch_zoom(self, data: Dict[str, Any], context: PluginContext) -> PluginResult:
        """Handle pinch zoom gesture"""
        pass
    
    async def _handle_long_press(self, data: Dict[str, Any], context: PluginContext) -> PluginResult:
        """Handle long press gesture"""
        pass
    
    async def _speech_to_text(self, audio_data: bytes) -> str:
        """Convert speech to text - override in subclasses"""
        # Default implementation
        return "Voice input not supported"
```

---

## 🔧 Plugin Development Kit (PDK)

### CLI Tools
```bash
# Install zenOS Plugin SDK
npm install -g @zenos/plugin-sdk

# Create new plugin
zenos create-plugin my-awesome-tool
# Creates:
# ├── zenos-plugin.yaml
# ├── src/
# │   ├── main.py
# │   ├── mobile.py
# │   └── web.py
# ├── ui/
# │   ├── main_screen.jsx
# │   └── settings.jsx
# ├── tests/
# ├── docs/
# └── README.md

# Test plugin locally
zenos test-plugin ./my-awesome-tool
# Runs:
# - Unit tests
# - Integration tests
# - Mobile compatibility tests
# - Security scan

# Publish plugin
zenos publish-plugin ./my-awesome-tool
# Publishes to GitHub with proper tags

# Install plugin from GitHub
zenos install-plugin github.com/username/plugin-name

# Update plugin
zenos update-plugin plugin-name

# List installed plugins
zenos list-plugins

# Remove plugin
zenos remove-plugin plugin-name
```

### Plugin Template
```python
# src/mobile.py - Generated template
from zenos_plugin.mobile import MobilePlugin, PluginContext, PluginResult
from typing import Any, Dict
import asyncio

class MyAwesomeTool(MobilePlugin):
    """My Awesome Tool - Generated from template"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key')
        self.model_size = config.get('model_size', 'medium')
    
    async def initialize(self) -> bool:
        """Initialize the plugin"""
        try:
            # Your initialization code here
            self.is_initialized = True
            return True
        except Exception as e:
            print(f"Initialization failed: {e}")
            return False
    
    async def _process_mobile(self, input_data: Any, context: PluginContext) -> PluginResult:
        """Mobile-optimized processing"""
        try:
            # Your main processing logic here
            result = await self.awesome_processing(input_data)
            
            return PluginResult(
                success=True,
                data=result,
                metadata={
                    'processing_time': 0.5,
                    'model_used': self.model_size
                }
            )
        except Exception as e:
            return PluginResult(
                success=False,
                data=None,
                error=str(e)
            )
    
    async def awesome_processing(self, input_data: Any) -> Any:
        """Your awesome processing logic"""
        # Implement your AI magic here
        return f"Processed: {input_data}"
    
    async def _handle_swipe_left(self, data: Dict[str, Any], context: PluginContext) -> PluginResult:
        """Handle swipe left gesture"""
        # Implement swipe left behavior
        return PluginResult(success=True, data="Swiped left")
    
    async def _handle_swipe_right(self, data: Dict[str, Any], context: PluginContext) -> PluginResult:
        """Handle swipe right gesture"""
        # Implement swipe right behavior
        return PluginResult(success=True, data="Swiped right")
    
    async def cleanup(self) -> bool:
        """Cleanup resources"""
        try:
            # Your cleanup code here
            return True
        except Exception as e:
            print(f"Cleanup failed: {e}")
            return False
```

---

## 🔒 Security & Sandboxing

### Plugin Sandbox Architecture
```python
# zenos_plugin/sandbox.py
import asyncio
import subprocess
import tempfile
import os
from typing import Any, Dict
from pathlib import Path

class PluginSandbox:
    """Security sandbox for plugin execution"""
    
    def __init__(self, plugin_id: str, permissions: List[str]):
        self.plugin_id = plugin_id
        self.permissions = permissions
        self.sandbox_dir = self._create_sandbox()
        self.resource_limits = {
            'max_memory': '512MB',
            'max_cpu_time': 30,  # seconds
            'max_disk_space': '100MB'
        }
    
    def _create_sandbox(self) -> Path:
        """Create isolated sandbox directory"""
        sandbox_path = Path(tempfile.mkdtemp(prefix=f"zenos_plugin_{self.plugin_id}_"))
        
        # Create restricted directory structure
        (sandbox_path / "input").mkdir()
        (sandbox_path / "output").mkdir()
        (sandbox_path / "temp").mkdir()
        (sandbox_path / "cache").mkdir()
        
        return sandbox_path
    
    async def execute_plugin(self, plugin_path: str, input_data: Any) -> Any:
        """Execute plugin in sandboxed environment"""
        try:
            # Copy plugin to sandbox
            await self._copy_plugin_to_sandbox(plugin_path)
            
            # Set up resource limits
            process = await asyncio.create_subprocess_exec(
                'python', '-m', 'plugin.main',
                cwd=self.sandbox_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                limit=self.resource_limits['max_memory']
            )
            
            # Execute with timeout
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.resource_limits['max_cpu_time']
            )
            
            if process.returncode != 0:
                raise Exception(f"Plugin execution failed: {stderr.decode()}")
            
            return stdout.decode()
            
        except asyncio.TimeoutError:
            raise Exception("Plugin execution timed out")
        except Exception as e:
            raise Exception(f"Sandbox execution failed: {e}")
        finally:
            # Cleanup sandbox
            await self._cleanup_sandbox()
    
    async def _copy_plugin_to_sandbox(self, plugin_path: str):
        """Copy plugin files to sandbox"""
        # Implementation for copying plugin files
        pass
    
    async def _cleanup_sandbox(self):
        """Clean up sandbox directory"""
        # Implementation for cleanup
        pass
```

---

## 📊 Plugin Analytics & Metrics

### Performance Tracking
```python
# zenos_plugin/analytics.py
import time
import psutil
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class PluginMetrics:
    """Plugin performance metrics"""
    execution_time: float
    memory_usage: float
    cpu_usage: float
    success_rate: float
    error_count: int
    cache_hit_rate: float

class PluginAnalytics:
    """Analytics tracking for plugins"""
    
    def __init__(self, plugin_id: str):
        self.plugin_id = plugin_id
        self.metrics = PluginMetrics(
            execution_time=0.0,
            memory_usage=0.0,
            cpu_usage=0.0,
            success_rate=0.0,
            error_count=0,
            cache_hit_rate=0.0
        )
    
    def start_execution(self):
        """Start tracking execution"""
        self.start_time = time.time()
        self.start_memory = psutil.Process().memory_info().rss
    
    def end_execution(self, success: bool):
        """End tracking execution"""
        self.end_time = time.time()
        self.end_memory = psutil.Process().memory_info().rss
        
        # Update metrics
        self.metrics.execution_time = self.end_time - self.start_time
        self.metrics.memory_usage = self.end_memory - self.start_memory
        
        if success:
            self.metrics.success_rate = (self.metrics.success_rate + 1) / 2
        else:
            self.metrics.error_count += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return {
            'plugin_id': self.plugin_id,
            'execution_time': self.metrics.execution_time,
            'memory_usage': self.metrics.memory_usage,
            'success_rate': self.metrics.success_rate,
            'error_count': self.metrics.error_count,
            'cache_hit_rate': self.metrics.cache_hit_rate
        }
```

---

## 🚀 Plugin Discovery & Installation

### GitHub Integration
```python
# zenos_plugin/discovery.py
import asyncio
import aiohttp
from typing import List, Dict, Any
from github import Github

class PluginDiscovery:
    """Discover and install plugins from GitHub"""
    
    def __init__(self, github_token: str):
        self.github = Github(github_token)
        self.session = aiohttp.ClientSession()
    
    async def search_plugins(self, query: str, category: str = None) -> List[Dict[str, Any]]:
        """Search for plugins on GitHub"""
        search_query = f"{query} zenos-plugin.yaml"
        if category:
            search_query += f" category:{category}"
        
        repositories = self.github.search_repositories(
            search_query,
            sort="stars",
            order="desc"
        )
        
        plugins = []
        for repo in repositories[:50]:  # Limit to top 50
            try:
                manifest = await self._get_plugin_manifest(repo)
                if manifest:
                    plugins.append({
                        'repository': repo.full_name,
                        'manifest': manifest,
                        'stars': repo.stargazers_count,
                        'forks': repo.forks_count,
                        'last_updated': repo.updated_at
                    })
            except Exception as e:
                print(f"Error processing {repo.full_name}: {e}")
        
        return plugins
    
    async def _get_plugin_manifest(self, repo) -> Dict[str, Any]:
        """Get plugin manifest from repository"""
        try:
            manifest_file = repo.get_contents("zenos-plugin.yaml")
            manifest_content = manifest_file.decoded_content.decode()
            
            import yaml
            return yaml.safe_load(manifest_content)
        except Exception:
            return None
    
    async def install_plugin(self, repo_name: str, version: str = "latest") -> bool:
        """Install plugin from GitHub repository"""
        try:
            repo = self.github.get_repo(repo_name)
            
            # Clone repository
            clone_url = repo.clone_url
            install_path = f"~/.zenos/plugins/{repo_name.replace('/', '_')}"
            
            # Clone and install
            subprocess.run([
                'git', 'clone', clone_url, install_path
            ], check=True)
            
            # Install dependencies
            requirements_file = f"{install_path}/requirements.txt"
            if os.path.exists(requirements_file):
                subprocess.run([
                    'pip', 'install', '-r', requirements_file
                ], check=True)
            
            return True
            
        except Exception as e:
            print(f"Installation failed: {e}")
            return False
```

---

## 🎯 Next Steps

This specification provides the foundation for building a VST-like plugin system using GitHub repositories. The key innovations are:

1. **GitHub as Plugin Store** - No app store approval needed
2. **VST-Style Interface** - Familiar patterns for developers
3. **Mobile-First Design** - Optimized for mobile development
4. **Security Sandboxing** - Safe plugin execution
5. **Community Driven** - Open source by default

Ready to start building? Let's create the first plugin! 🚀

