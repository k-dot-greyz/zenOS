import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Workflow {
  id: string;
  name: string;
  description: string;
  procedures: string[];
  createdAt: string;
  lastUsed: string;
}

interface WorkflowSliceState {
  workflows: Workflow[];
  activeWorkflow: Workflow | null;
  isExecuting: boolean;
}

const initialState: WorkflowSliceState = {
  workflows: [],
  activeWorkflow: null,
  isExecuting: false,
};

const workflowSlice = createSlice({
  name: 'workflows',
  initialState,
  reducers: {
    createWorkflow: (state, action: PayloadAction<Omit<Workflow, 'id' | 'createdAt' | 'lastUsed'>>) => {
      const newWorkflow: Workflow = {
        ...action.payload,
        id: Date.now().toString(),
        createdAt: new Date().toISOString(),
        lastUsed: new Date().toISOString(),
      };
      state.workflows.push(newWorkflow);
    },
    updateWorkflow: (state, action: PayloadAction<{ id: string; updates: Partial<Workflow> }>) => {
      const index = state.workflows.findIndex(w => w.id === action.payload.id);
      if (index !== -1) {
        state.workflows[index] = { ...state.workflows[index], ...action.payload.updates };
      }
    },
    deleteWorkflow: (state, action: PayloadAction<string>) => {
      state.workflows = state.workflows.filter(w => w.id !== action.payload);
    },
    setActiveWorkflow: (state, action: PayloadAction<Workflow | null>) => {
      state.activeWorkflow = action.payload;
    },
    setExecuting: (state, action: PayloadAction<boolean>) => {
      state.isExecuting = action.payload;
    },
  },
});

export const {
  createWorkflow,
  updateWorkflow,
  deleteWorkflow,
  setActiveWorkflow,
  setExecuting,
} = workflowSlice.actions;

export default workflowSlice.reducer;
