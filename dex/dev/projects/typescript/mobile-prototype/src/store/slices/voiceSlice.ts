import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface VoiceMessage {
  id: string;
  input: string;
  output: string;
  timestamp: string;
  plugin?: string;
}

interface VoiceSliceState {
  messages: VoiceMessage[];
  isListening: boolean;
  isProcessing: boolean;
  isEnabled: boolean;
}

const initialState: VoiceSliceState = {
  messages: [],
  isListening: false,
  isProcessing: false,
  isEnabled: true,
};

const voiceSlice = createSlice({
  name: 'voice',
  initialState,
  reducers: {
    addMessage: (state, action: PayloadAction<Omit<VoiceMessage, 'id' | 'timestamp'>>) => {
      const newMessage: VoiceMessage = {
        ...action.payload,
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
      };
      state.messages.unshift(newMessage);
    },
    setListening: (state, action: PayloadAction<boolean>) => {
      state.isListening = action.payload;
    },
    setProcessing: (state, action: PayloadAction<boolean>) => {
      state.isProcessing = action.payload;
    },
    setEnabled: (state, action: PayloadAction<boolean>) => {
      state.isEnabled = action.payload;
    },
    clearMessages: (state) => {
      state.messages = [];
    },
    removeMessage: (state, action: PayloadAction<string>) => {
      state.messages = state.messages.filter(m => m.id !== action.payload);
    },
  },
});

export const {
  addMessage,
  setListening,
  setProcessing,
  setEnabled,
  clearMessages,
  removeMessage,
} = voiceSlice.actions;

export default voiceSlice.reducer;
