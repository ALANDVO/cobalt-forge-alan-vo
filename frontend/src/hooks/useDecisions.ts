import { create } from 'zustand';
import type { DecisionRecord, CoverageReport } from '@/types';
import { api } from '@/api/client';

interface DecisionsState {
  decisions: DecisionRecord[];
  coverage: CoverageReport | null;
  isLoading: boolean;
  error: string | null;
  fetchDecisions: (sessionId: string) => Promise<void>;
  createDecision: (data: {
    question: string;
    answer: string;
    normalized_requirement: string;
    constraints?: string;
    tags?: string;
  }) => Promise<DecisionRecord | null>;
  getCoverage: (sessionId: string) => Promise<CoverageReport | null>;
  clearError: () => void;
}

export const useDecisionsStore = create<DecisionsState>((set) => ({
  decisions: [],
  coverage: null,
  isLoading: false,
  error: null,

  clearError: () => set({ error: null }),

  fetchDecisions: async (sessionId: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.listDecisions(sessionId);
      set({ decisions: response.data, isLoading: false });
    } catch (err: unknown) {
      const error = err as Error;
      set({ error: error.message, isLoading: false });
    }
  },

  createDecision: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.createDecision(data);
      const decision = response.data;
      set((state) => ({ decisions: [decision, ...state.decisions], isLoading: false }));
      return decision;
    } catch (err: unknown) {
      const error = err as Error;
      set({ error: error.message, isLoading: false });
      return null;
    }
  },

  getCoverage: async (sessionId: string) => {
    try {
      const response = await api.getCoverage(sessionId);
      const coverage = response.data;
      set({ coverage });
      return coverage;
    } catch (err: unknown) {
      const error = err as Error;
      set({ error: error.message });
      return null;
    }
  },
}));