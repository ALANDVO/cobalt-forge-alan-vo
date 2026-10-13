import { create } from 'zustand';
import type { VerificationEvidence, VerificationCoverageReport } from '@/types';
import { api } from '@/api/client';

interface VerificationState {
  evidence: VerificationEvidence[];
  coverage: VerificationCoverageReport | null;
  isLoading: boolean;
  error: string | null;
  addEvidence: (decisionId: string, data: {
    evidence_type: 'test_result' | 'code_review' | 'manual_verification' | 'automated_check' | 'commit';
    title: string;
    description?: string;
    artifact_ref?: string;
    passed: boolean;
    issue_id?: string;
  }) => Promise<VerificationEvidence | null>;
  fetchDecisionEvidence: (decisionId: string) => Promise<void>;
  fetchIssueEvidence: (issueId: string) => Promise<void>;
  getCoverage: (decisionIds: string[]) => Promise<VerificationCoverageReport | null>;
  clearError: () => void;
}

export const useVerificationStore = create<VerificationState>((set) => ({
  evidence: [],
  coverage: null,
  isLoading: false,
  error: null,

  clearError: () => set({ error: null }),

  addEvidence: async (decisionId: string, data) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.addEvidence(decisionId, data);
      const evidence = response.data;
      set((state) => ({ evidence: [evidence, ...state.evidence], isLoading: false }));
      return evidence;
    } catch (err: unknown) {
      const error = err as Error;
      set({ error: error.message, isLoading: false });
      return null;
    }
  },

  fetchDecisionEvidence: async (decisionId: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.getDecisionEvidence(decisionId);
      set({ evidence: response.data, isLoading: false });
    } catch (err: unknown) {
      const error = err as Error;
      set({ error: error.message, isLoading: false });
    }
  },

  fetchIssueEvidence: async (issueId: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.getIssueEvidence(issueId);
      set({ evidence: response.data, isLoading: false });
    } catch (err: unknown) {
      const error = err as Error;
      set({ error: error.message, isLoading: false });
    }
  },

  getCoverage: async (decisionIds: string[]) => {
    try {
      const response = await api.getVerificationCoverage(decisionIds);
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