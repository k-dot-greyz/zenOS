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

export interface PluginResult {
  success: boolean;
  data: any;
  error?: string;
  metadata?: {
    processingTime?: number;
    modelUsed?: string;
    [key: string]: any;
  };
}
