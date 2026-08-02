# 🚀 Mobile zenOS Starter Template
## Ready-to-Use Development Foundation

*"Every great journey begins with a single step. Every great app begins with a single component."*

---

## 🎯 Quick Start Guide

### 1. **Project Initialization**
```bash
# Create new React Native project
npx react-native init MobileZenOS --template react-native-template-typescript

# Navigate to project
cd MobileZenOS

# Install additional dependencies
npm install @react-navigation/native @react-navigation/stack
npm install react-native-screens react-native-safe-area-context
npm install react-native-gesture-handler react-native-reanimated
npm install @reduxjs/toolkit react-redux
npm install react-native-elements react-native-vector-icons
npm install expo-av expo-speech
npm install react-native-svg
npm install axios

# Install development dependencies
npm install --save-dev @types/react @types/react-native
npm install --save-dev eslint @typescript-eslint/parser
npm install --save-dev prettier
```

### 2. **Backend Setup**
```bash
# Create backend directory
mkdir backend
cd backend

# Initialize Python project
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn
pip install sqlalchemy psycopg2-binary
pip install redis celery
pip install python-jose[cryptography] passlib[bcrypt]
pip install python-multipart
pip install aiofiles
pip install pyyaml
pip install requests

# Create requirements.txt
pip freeze > requirements.txt
```

### 3. **Project Structure Setup**
```bash
# Create directory structure
mkdir -p mobile/src/{components,screens,services,store,utils}
mkdir -p mobile/src/components/{common,plugin,workflow}
mkdir -p mobile/src/screens/{plugin-manager,tool-rack,procedure-chain,voice}
mkdir -p mobile/src/services/{api,plugin,voice,storage}
mkdir -p mobile/src/store/{slices,middleware}

mkdir -p backend/app/{api,core,models,services,plugins}
mkdir -p backend/plugins/{runtime,sandbox,discovery}
mkdir -p backend/tests

mkdir -p plugins/{examples,templates}
mkdir -p docs/{api,guides,examples}
mkdir -p scripts/{build,deploy,test}
```

---

## 📱 Mobile App Template

### Main App Component
```typescript
// mobile/src/App.tsx
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { Provider } from 'react-redux';
import { store } from './store/store';
import { StatusBar } from 'react-native';

// Screens
import PluginManagerScreen from './screens/plugin-manager/PluginManagerScreen';
import ToolRackScreen from './screens/tool-rack/ToolRackScreen';
import ProcedureChainScreen from './screens/procedure-chain/ProcedureChainScreen';
import VoiceInterfaceScreen from './screens/voice/VoiceInterfaceScreen';
import SettingsScreen from './screens/settings/SettingsScreen';

// Types
type RootStackParamList = {
  PluginManager: undefined;
  ToolRack: undefined;
  ProcedureChain: undefined;
  VoiceInterface: undefined;
  Settings: undefined;
};

const Stack = createStackNavigator<RootStackParamList>();

const App: React.FC = () => {
  return (
    <Provider store={store}>
      <NavigationContainer>
        <StatusBar barStyle="light-content" backgroundColor="#1a1a1a" />
        <Stack.Navigator
          initialRouteName="PluginManager"
          screenOptions={{
            headerStyle: {
              backgroundColor: '#1a1a1a',
            },
            headerTintColor: '#ffffff',
            headerTitleStyle: {
              fontWeight: 'bold',
            },
          }}
        >
          <Stack.Screen 
            name="PluginManager" 
            component={PluginManagerScreen}
            options={{ title: 'Plugin Manager' }}
          />
          <Stack.Screen 
            name="ToolRack" 
            component={ToolRackScreen}
            options={{ title: 'Tool Rack' }}
          />
          <Stack.Screen 
            name="ProcedureChain" 
            component={ProcedureChainScreen}
            options={{ title: 'Procedure Chain' }}
          />
          <Stack.Screen 
            name="VoiceInterface" 
            component={VoiceInterfaceScreen}
            options={{ title: 'Voice Interface' }}
          />
          <Stack.Screen 
            name="Settings" 
            component={SettingsScreen}
            options={{ title: 'Settings' }}
          />
        </Stack.Navigator>
      </NavigationContainer>
    </Provider>
  );
};

export default App;
```

### Redux Store Setup
```typescript
// mobile/src/store/store.ts
import { configureStore } from '@reduxjs/toolkit';
import pluginReducer from './slices/pluginSlice';
import workflowReducer from './slices/workflowSlice';
import voiceReducer from './slices/voiceSlice';
import settingsReducer from './slices/settingsSlice';

export const store = configureStore({
  reducer: {
    plugins: pluginReducer,
    workflows: workflowReducer,
    voice: voiceReducer,
    settings: settingsReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
```

### Plugin Slice (Redux)
```typescript
// mobile/src/store/slices/pluginSlice.ts
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { Plugin, PluginState } from '../../types/plugin';
import { pluginService } from '../../services/plugin/pluginService';

interface PluginSliceState {
  plugins: Plugin[];
  installedPlugins: Plugin[];
  loading: boolean;
  error: string | null;
  searchQuery: string;
  selectedCategory: string;
}

const initialState: PluginSliceState = {
  plugins: [],
  installedPlugins: [],
  loading: false,
  error: null,
  searchQuery: '',
  selectedCategory: 'all',
};

// Async thunks
export const searchPlugins = createAsyncThunk(
  'plugins/search',
  async ({ query, category }: { query: string; category: string }) => {
    const response = await pluginService.searchPlugins(query, category);
    return response;
  }
);

export const installPlugin = createAsyncThunk(
  'plugins/install',
  async (pluginId: string) => {
    const response = await pluginService.installPlugin(pluginId);
    return response;
  }
);

export const removePlugin = createAsyncThunk(
  'plugins/remove',
  async (pluginId: string) => {
    const response = await pluginService.removePlugin(pluginId);
    return response;
  }
);

const pluginSlice = createSlice({
  name: 'plugins',
  initialState,
  reducers: {
    setSearchQuery: (state, action: PayloadAction<string>) => {
      state.searchQuery = action.payload;
    },
    setSelectedCategory: (state, action: PayloadAction<string>) => {
      state.selectedCategory = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Search plugins
      .addCase(searchPlugins.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(searchPlugins.fulfilled, (state, action) => {
        state.loading = false;
        state.plugins = action.payload;
      })
      .addCase(searchPlugins.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Search failed';
      })
      // Install plugin
      .addCase(installPlugin.fulfilled, (state, action) => {
        state.installedPlugins.push(action.payload);
      })
      // Remove plugin
      .addCase(removePlugin.fulfilled, (state, action) => {
        state.installedPlugins = state.installedPlugins.filter(
          plugin => plugin.id !== action.payload
        );
      });
  },
});

export const { setSearchQuery, setSelectedCategory, clearError } = pluginSlice.actions;
export default pluginSlice.reducer;
```

### Plugin Service
```typescript
// mobile/src/services/plugin/pluginService.ts
import axios from 'axios';
import { Plugin } from '../../types/plugin';

const API_BASE_URL = 'http://localhost:8000/api';

class PluginService {
  private api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000,
  });

  async searchPlugins(query: string, category: string): Promise<Plugin[]> {
    try {
      const response = await this.api.get('/plugins/search', {
        params: { query, category },
      });
      return response.data;
    } catch (error) {
      console.error('Search plugins failed:', error);
      throw error;
    }
  }

  async getPluginDetails(pluginId: string): Promise<Plugin> {
    try {
      const response = await this.api.get(`/plugins/${pluginId}`);
      return response.data;
    } catch (error) {
      console.error('Get plugin details failed:', error);
      throw error;
    }
  }

  async installPlugin(pluginId: string): Promise<Plugin> {
    try {
      const response = await this.api.post(`/plugins/${pluginId}/install`);
      return response.data;
    } catch (error) {
      console.error('Install plugin failed:', error);
      throw error;
    }
  }

  async removePlugin(pluginId: string): Promise<void> {
    try {
      await this.api.delete(`/plugins/${pluginId}`);
    } catch (error) {
      console.error('Remove plugin failed:', error);
      throw error;
    }
  }

  async getInstalledPlugins(): Promise<Plugin[]> {
    try {
      const response = await this.api.get('/plugins/installed');
      return response.data;
    } catch (error) {
      console.error('Get installed plugins failed:', error);
      throw error;
    }
  }

  async updatePlugin(pluginId: string): Promise<Plugin> {
    try {
      const response = await this.api.post(`/plugins/${pluginId}/update`);
      return response.data;
    } catch (error) {
      console.error('Update plugin failed:', error);
      throw error;
    }
  }
}

export const pluginService = new PluginService();
```

### Plugin Types
```typescript
// mobile/src/types/plugin.ts
export interface Plugin {
  id: string;
  name: string;
  description: string;
  author: string;
  version: string;
  category: string;
  tags: string[];
  repository: string;
  stars: number;
  forks: number;
  lastUpdated: string;
  screenshots?: string[];
  featured?: boolean;
  installed?: boolean;
  configurable?: boolean;
}

export interface PluginConfig {
  [key: string]: any;
}

export interface PluginState {
  id: string;
  status: 'idle' | 'loading' | 'running' | 'error';
  config: PluginConfig;
  lastUsed: string;
  usageCount: number;
}

export interface PluginCapability {
  name: string;
  description: string;
  inputTypes: string[];
  outputTypes: string[];
  parameters: PluginParameter[];
}

export interface PluginParameter {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'enum';
  required: boolean;
  defaultValue?: any;
  options?: string[];
  description: string;
}
```

---

## 🐍 Backend API Template

### Main FastAPI App
```python
# backend/app/main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import uvicorn
from typing import List, Optional

from .api import plugins, workflows, voice
from .core.config import settings
from .core.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Mobile zenOS API",
    description="API for mobile zenOS plugin system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(plugins.router, prefix="/api/plugins", tags=["plugins"])
app.include_router(workflows.router, prefix="/api/workflows", tags=["workflows"])
app.include_router(voice.router, prefix="/api/voice", tags=["voice"])

@app.get("/")
async def root():
    return {"message": "Mobile zenOS API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Plugin API Endpoints
```python
# backend/app/api/plugins.py
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from ..models.plugin import Plugin, PluginInstall
from ..services.plugin_service import PluginService
from ..core.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/search")
async def search_plugins(
    query: str = Query(..., description="Search query"),
    category: str = Query("all", description="Plugin category"),
    limit: int = Query(50, description="Maximum results"),
    db: Session = Depends(get_db)
):
    """Search for plugins on GitHub"""
    try:
        plugin_service = PluginService(db)
        plugins = await plugin_service.search_plugins(query, category, limit)
        return plugins
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{plugin_id}")
async def get_plugin(
    plugin_id: str,
    db: Session = Depends(get_db)
):
    """Get plugin details"""
    try:
        plugin_service = PluginService(db)
        plugin = await plugin_service.get_plugin(plugin_id)
        if not plugin:
            raise HTTPException(status_code=404, detail="Plugin not found")
        return plugin
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{plugin_id}/install")
async def install_plugin(
    plugin_id: str,
    db: Session = Depends(get_db)
):
    """Install a plugin"""
    try:
        plugin_service = PluginService(db)
        plugin = await plugin_service.install_plugin(plugin_id)
        return plugin
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{plugin_id}")
async def remove_plugin(
    plugin_id: str,
    db: Session = Depends(get_db)
):
    """Remove a plugin"""
    try:
        plugin_service = PluginService(db)
        await plugin_service.remove_plugin(plugin_id)
        return {"message": "Plugin removed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/installed")
async def get_installed_plugins(
    db: Session = Depends(get_db)
):
    """Get all installed plugins"""
    try:
        plugin_service = PluginService(db)
        plugins = await plugin_service.get_installed_plugins()
        return plugins
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Plugin Service
```python
# backend/app/services/plugin_service.py
import asyncio
import aiohttp
import yaml
from typing import List, Optional
from sqlalchemy.orm import Session
from ..models.plugin import Plugin
from ..core.github_client import GitHubClient
from ..core.plugin_runtime import PluginRuntime

class PluginService:
    def __init__(self, db: Session):
        self.db = db
        self.github_client = GitHubClient()
        self.plugin_runtime = PluginRuntime()

    async def search_plugins(
        self, 
        query: str, 
        category: str, 
        limit: int = 50
    ) -> List[Plugin]:
        """Search for plugins on GitHub"""
        try:
            # Search GitHub repositories
            repos = await self.github_client.search_repositories(
                query=f"{query} zenos-plugin.yaml",
                sort="stars",
                order="desc",
                per_page=limit
            )
            
            plugins = []
            for repo in repos:
                try:
                    # Get plugin manifest
                    manifest = await self.github_client.get_file_content(
                        repo["full_name"], 
                        "zenos-plugin.yaml"
                    )
                    
                    if manifest:
                        plugin_data = yaml.safe_load(manifest)
                        plugin = Plugin(
                            id=plugin_data["plugin"]["id"],
                            name=plugin_data["plugin"]["name"],
                            description=plugin_data["plugin"]["description"],
                            author=plugin_data["plugin"]["author"],
                            version=plugin_data["plugin"]["version"],
                            category=plugin_data["plugin"]["category"],
                            tags=plugin_data["plugin"].get("tags", []),
                            repository=repo["full_name"],
                            stars=repo["stargazers_count"],
                            forks=repo["forks_count"],
                            lastUpdated=repo["updated_at"]
                        )
                        plugins.append(plugin)
                        
                except Exception as e:
                    print(f"Error processing repo {repo['full_name']}: {e}")
                    continue
            
            return plugins
            
        except Exception as e:
            print(f"Search plugins failed: {e}")
            raise

    async def get_plugin(self, plugin_id: str) -> Optional[Plugin]:
        """Get plugin by ID"""
        # Implementation for getting plugin details
        pass

    async def install_plugin(self, plugin_id: str) -> Plugin:
        """Install a plugin"""
        try:
            # Get plugin details
            plugin = await self.get_plugin(plugin_id)
            if not plugin:
                raise Exception("Plugin not found")
            
            # Clone repository
            await self.plugin_runtime.clone_plugin(plugin.repository)
            
            # Install dependencies
            await self.plugin_runtime.install_dependencies(plugin_id)
            
            # Save to database
            # Implementation for saving to database
            
            return plugin
            
        except Exception as e:
            print(f"Install plugin failed: {e}")
            raise

    async def remove_plugin(self, plugin_id: str) -> None:
        """Remove a plugin"""
        try:
            # Remove from plugin runtime
            await self.plugin_runtime.remove_plugin(plugin_id)
            
            # Remove from database
            # Implementation for removing from database
            
        except Exception as e:
            print(f"Remove plugin failed: {e}")
            raise

    async def get_installed_plugins(self) -> List[Plugin]:
        """Get all installed plugins"""
        # Implementation for getting installed plugins
        pass
```

---

## 🔌 Example Plugin Template

### Plugin Manifest
```yaml
# plugins/examples/text-processor/zenos-plugin.yaml
plugin:
  id: "com.example.text-processor"
  name: "Text Processor"
  version: "1.0.0"
  author: "Example Author"
  description: "A simple text processing plugin for mobile zenOS"
  homepage: "https://github.com/example/text-processor"
  license: "MIT"
  
  category: "text-processing"
  subcategories: ["nlp", "transformation"]
  tags: ["text", "processing", "mobile", "simple"]
  
  compatibility:
    min_zenos_version: "1.0.0"
    platforms: ["android", "ios"]
    python_version: ">=3.8"
  
  capabilities:
    - "text_processing"
    - "api_integration"
  
  entry_points:
    main: "src/main.py"
    mobile: "src/mobile.py"
  
  dependencies:
    python:
      - "requests>=2.28.0"
  
  config_schema:
    max_length:
      type: "integer"
      default: 1000
      description: "Maximum text length to process"
    preserve_formatting:
      type: "boolean"
      default: true
      description: "Preserve original formatting"
  
  mobile:
    battery_aware: true
    offline_capable: true
    voice_input: true
    gesture_support: ["swipe_left", "swipe_right"]
  
  permissions:
    - "internet"
    - "file_system_read"
  
  procedures:
    - id: "text.process"
      name: "Process Text"
      description: "Process text with various transformations"
      input_types: ["text"]
      output_types: ["text"]
      parameters:
        operation:
          type: "enum"
          options: ["uppercase", "lowercase", "reverse", "word_count"]
          default: "uppercase"
```

### Plugin Implementation
```python
# plugins/examples/text-processor/src/mobile.py
from zenos_plugin.mobile import MobilePlugin, PluginContext, PluginResult
from typing import Any, Dict
import asyncio

class TextProcessor(MobilePlugin):
    """Text Processor Plugin for Mobile zenOS"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.max_length = config.get('max_length', 1000)
        self.preserve_formatting = config.get('preserve_formatting', True)
    
    async def initialize(self) -> bool:
        """Initialize the plugin"""
        try:
            print("Text Processor plugin initialized")
            self.is_initialized = True
            return True
        except Exception as e:
            print(f"Initialization failed: {e}")
            return False
    
    async def _process_mobile(self, input_data: Any, context: PluginContext) -> PluginResult:
        """Mobile-optimized text processing"""
        try:
            if not isinstance(input_data, str):
                return PluginResult(
                    success=False,
                    data=None,
                    error="Input must be text"
                )
            
            # Check text length
            if len(input_data) > self.max_length:
                return PluginResult(
                    success=False,
                    data=None,
                    error=f"Text too long. Maximum {self.max_length} characters."
                )
            
            # Process text based on operation
            operation = context.get('operation', 'uppercase')
            processed_text = await self._process_text(input_data, operation)
            
            return PluginResult(
                success=True,
                data=processed_text,
                metadata={
                    'operation': operation,
                    'original_length': len(input_data),
                    'processed_length': len(processed_text)
                }
            )
            
        except Exception as e:
            return PluginResult(
                success=False,
                data=None,
                error=str(e)
            )
    
    async def _process_text(self, text: str, operation: str) -> str:
        """Process text with specified operation"""
        if operation == "uppercase":
            return text.upper()
        elif operation == "lowercase":
            return text.lower()
        elif operation == "reverse":
            return text[::-1]
        elif operation == "word_count":
            return str(len(text.split()))
        else:
            return text
    
    async def _handle_swipe_left(self, data: Dict[str, Any], context: PluginContext) -> PluginResult:
        """Handle swipe left gesture - previous operation"""
        operations = ["uppercase", "lowercase", "reverse", "word_count"]
        current_op = context.get('operation', 'uppercase')
        current_index = operations.index(current_op)
        next_index = (current_index - 1) % len(operations)
        next_operation = operations[next_index]
        
        return PluginResult(
            success=True,
            data=f"Switched to {next_operation}",
            metadata={'operation': next_operation}
        )
    
    async def _handle_swipe_right(self, data: Dict[str, Any], context: PluginContext) -> PluginResult:
        """Handle swipe right gesture - next operation"""
        operations = ["uppercase", "lowercase", "reverse", "word_count"]
        current_op = context.get('operation', 'uppercase')
        current_index = operations.index(current_op)
        next_index = (current_index + 1) % len(operations)
        next_operation = operations[next_index]
        
        return PluginResult(
            success=True,
            data=f"Switched to {next_operation}",
            metadata={'operation': next_operation}
        )
    
    async def cleanup(self) -> bool:
        """Cleanup resources"""
        try:
            print("Text Processor plugin cleaned up")
            return True
        except Exception as e:
            print(f"Cleanup failed: {e}")
            return False
```

---

## 🚀 Development Scripts

### Package.json Scripts
```json
{
  "scripts": {
    "start": "react-native start",
    "android": "react-native run-android",
    "ios": "react-native run-ios",
    "test": "jest",
    "lint": "eslint src --ext .ts,.tsx",
    "lint:fix": "eslint src --ext .ts,.tsx --fix",
    "type-check": "tsc --noEmit",
    "build:android": "cd android && ./gradlew assembleRelease",
    "build:ios": "cd ios && xcodebuild -workspace MobileZenOS.xcworkspace -scheme MobileZenOS -configuration Release",
    "clean": "react-native clean",
    "reset-cache": "react-native start --reset-cache"
  }
}
```

### Python Scripts
```python
# scripts/dev_server.py
import uvicorn
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
```

### Build Scripts
```bash
#!/bin/bash
# scripts/build.sh

echo "🚀 Building Mobile zenOS..."

# Build backend
echo "📦 Building backend..."
cd backend
pip install -r requirements.txt
python -m pytest tests/
echo "✅ Backend built successfully"

# Build mobile app
echo "📱 Building mobile app..."
cd ../mobile
npm install
npm run type-check
npm run lint
npm run test
echo "✅ Mobile app built successfully"

echo "🎉 Build completed successfully!"
```

---

## 🎯 Next Steps

1. **Clone this template** and customize it for your needs
2. **Set up your development environment** following the quick start guide
3. **Create your first plugin** using the example template
4. **Start building** the mobile interface components
5. **Iterate and improve** based on user feedback

**Ready to build the future of mobile AI development? Let's make it happen!** 🚀

---

*"The best way to predict the future is to build it. The best way to build the future is to start today."* - zenOS Philosophy

