import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { Plugin } from '../../types/plugin';
import { pluginService } from '../../services/pluginService';

interface PluginSliceState {
  plugins: Plugin[];
  installedPlugins: Plugin[];
  activePlugins: Plugin[];
  loading: boolean;
  error: string | null;
  searchQuery: string;
  selectedCategory: string;
}

const initialState: PluginSliceState = {
  plugins: [],
  installedPlugins: [],
  activePlugins: [],
  loading: false,
  error: null,
  searchQuery: '',
  selectedCategory: 'all',
};

// Mock data for prototype
const mockPlugins: Plugin[] = [
  {
    id: 'text-processor',
    name: 'Text Processor',
    description: 'Process text with various transformations',
    author: 'zenOS Team',
    version: '1.0.0',
    category: 'text-processing',
    tags: ['text', 'nlp', 'transformation'],
    repository: 'zenos/text-processor',
    stars: 42,
    forks: 8,
    lastUpdated: '2024-01-15T10:30:00Z',
    screenshots: ['https://via.placeholder.com/300x200/4CAF50/white?text=Text+Processor'],
    featured: true,
    installed: false,
    configurable: true,
  },
  {
    id: 'voice-analyzer',
    name: 'Voice Analyzer',
    description: 'Analyze voice input and extract insights',
    author: 'zenOS Team',
    version: '1.2.0',
    category: 'voice-processing',
    tags: ['voice', 'analysis', 'ai'],
    repository: 'zenos/voice-analyzer',
    stars: 89,
    forks: 15,
    lastUpdated: '2024-01-14T15:45:00Z',
    screenshots: ['https://via.placeholder.com/300x200/FF9800/white?text=Voice+Analyzer'],
    featured: true,
    installed: false,
    configurable: true,
  },
  {
    id: 'image-generator',
    name: 'AI Image Generator',
    description: 'Generate images from text descriptions',
    author: 'zenOS Team',
    version: '2.1.0',
    category: 'image-processing',
    tags: ['image', 'generation', 'ai', 'art'],
    repository: 'zenos/image-generator',
    stars: 156,
    forks: 32,
    lastUpdated: '2024-01-13T09:20:00Z',
    screenshots: ['https://via.placeholder.com/300x200/9C27B0/white?text=Image+Generator'],
    featured: false,
    installed: false,
    configurable: true,
  },
  {
    id: 'data-analyzer',
    name: 'Data Analyzer',
    description: 'Analyze and visualize data',
    author: 'zenOS Team',
    version: '1.5.0',
    category: 'data-analysis',
    tags: ['data', 'analysis', 'visualization'],
    repository: 'zenos/data-analyzer',
    stars: 73,
    forks: 12,
    lastUpdated: '2024-01-12T14:10:00Z',
    screenshots: ['https://via.placeholder.com/300x200/2196F3/white?text=Data+Analyzer'],
    featured: false,
    installed: true,
    configurable: true,
  },
];

// Async thunks
export const searchPlugins = createAsyncThunk(
  'plugins/search',
  async ({ query, category }: { query: string; category: string }) => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    let filteredPlugins = mockPlugins;
    
    if (query) {
      filteredPlugins = filteredPlugins.filter(plugin =>
        plugin.name.toLowerCase().includes(query.toLowerCase()) ||
        plugin.description.toLowerCase().includes(query.toLowerCase()) ||
        plugin.tags.some(tag => tag.toLowerCase().includes(query.toLowerCase()))
      );
    }
    
    if (category !== 'all') {
      filteredPlugins = filteredPlugins.filter(plugin => plugin.category === category);
    }
    
    return filteredPlugins;
  }
);

export const installPlugin = createAsyncThunk(
  'plugins/install',
  async (pluginId: string) => {
    // Simulate installation
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const plugin = mockPlugins.find(p => p.id === pluginId);
    if (!plugin) {
      throw new Error('Plugin not found');
    }
    
    return { ...plugin, installed: true };
  }
);

export const removePlugin = createAsyncThunk(
  'plugins/remove',
  async (pluginId: string) => {
    // Simulate removal
    await new Promise(resolve => setTimeout(resolve, 1000));
    return pluginId;
  }
);

export const addToRack = createAsyncThunk(
  'plugins/addToRack',
  async (pluginId: string) => {
    const plugin = mockPlugins.find(p => p.id === pluginId);
    if (!plugin) {
      throw new Error('Plugin not found');
    }
    return plugin;
  }
);

export const removeFromRack = createAsyncThunk(
  'plugins/removeFromRack',
  async (pluginId: string) => {
    return pluginId;
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
    loadMockData: (state) => {
      state.plugins = mockPlugins;
      state.installedPlugins = mockPlugins.filter(p => p.installed);
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
        // Update plugins list
        const index = state.plugins.findIndex(p => p.id === action.payload.id);
        if (index !== -1) {
          state.plugins[index].installed = true;
        }
      })
      // Remove plugin
      .addCase(removePlugin.fulfilled, (state, action) => {
        state.installedPlugins = state.installedPlugins.filter(
          plugin => plugin.id !== action.payload
        );
        // Update plugins list
        const index = state.plugins.findIndex(p => p.id === action.payload);
        if (index !== -1) {
          state.plugins[index].installed = false;
        }
      })
      // Add to rack
      .addCase(addToRack.fulfilled, (state, action) => {
        if (!state.activePlugins.find(p => p.id === action.payload.id)) {
          state.activePlugins.push(action.payload);
        }
      })
      // Remove from rack
      .addCase(removeFromRack.fulfilled, (state, action) => {
        state.activePlugins = state.activePlugins.filter(
          plugin => plugin.id !== action.payload
        );
      });
  },
});

export const { 
  setSearchQuery, 
  setSelectedCategory, 
  clearError, 
  loadMockData 
} = pluginSlice.actions;

export default pluginSlice.reducer;
