import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Settings {
  theme: 'dark' | 'light';
  voiceEnabled: boolean;
  autoSave: boolean;
  notifications: boolean;
  batteryOptimization: boolean;
  defaultCategory: string;
  maxPlugins: number;
}

interface SettingsSliceState {
  settings: Settings;
  isLoaded: boolean;
}

const initialState: SettingsSliceState = {
  settings: {
    theme: 'dark',
    voiceEnabled: true,
    autoSave: true,
    notifications: true,
    batteryOptimization: true,
    defaultCategory: 'all',
    maxPlugins: 8,
  },
  isLoaded: false,
};

const settingsSlice = createSlice({
  name: 'settings',
  initialState,
  reducers: {
    updateSetting: (state, action: PayloadAction<{ key: keyof Settings; value: any }>) => {
      state.settings[action.payload.key] = action.payload.value;
    },
    updateSettings: (state, action: PayloadAction<Partial<Settings>>) => {
      state.settings = { ...state.settings, ...action.payload };
    },
    resetSettings: (state) => {
      state.settings = initialState.settings;
    },
    setLoaded: (state, action: PayloadAction<boolean>) => {
      state.isLoaded = action.payload;
    },
  },
});

export const {
  updateSetting,
  updateSettings,
  resetSettings,
  setLoaded,
} = settingsSlice.actions;

export default settingsSlice.reducer;
