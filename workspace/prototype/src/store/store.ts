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
