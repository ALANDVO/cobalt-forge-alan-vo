import { create } from 'zustand';
import type { PRD, PRDCoverageReport, Issue } from '@/types';
import { api } from '@/api/client';

interface S {
  prds: PRD[];
  current: PRD | null;
  issues: Issue[];
  cov: PRDCoverageReport | null;
  loading: boolean;
  error: string | null;
  fetchPRDs: (sid: string) => Promise<void>;
  createPRD: (sid: string, t: string) => Promise<PRD | null>;
  select: (p: PRD) => void;
  generatePRD: (pid: string) => Promise<PRD | null>;
  finalizePRD: (pid: string) => Promise<void>;
  checkCoverage: (pid: string) => Promise<PRDCoverageReport | null>;
  fetchIssues: (pid: string) => Promise<void>;
  createIssue: (pid: string, d: any) => Promise<Issue | null>;
  updateIssueStatus: (iid: string, s: string) => Promise<void>;
  completeIssue: (iid: string, sha: string) => Promise<void>;
  getFrontier: (pid: string) => Promise<Issue[]>;
  generateIssues: (pid: string) => Promise<Issue[]>;
  clearError: () => void;
}

export const usePRDStore = create<S>((set) => ({
  prds: [], current: null, issues: [], cov: null, loading: false, error: null,
  clearError: () => set({ error: null }),
  fetchPRDs: async (sid) => { set({ loading: true, error: null }); try { const r = await api.listPRDs(sid); set({ prds: r.data, loading: false }); } catch (e) { set({ error: (e as Error).message, loading: false }); } },
  createPRD: async (sid, t) => { set({ loading: true, error: null }); try { const r = await api.createPRD(sid, t); const p = r.data; set(s => ({ prds: [p, ...s.prds], current: p, loading: false })); return p; } catch (e) { set({ error: (e as Error).message, loading: false }); return null; } },
  select: (p) => set({ current: p }),
  generatePRD: async (pid) => { set({ loading: true, error: null }); try { const r = await api.genPRD(pid); const p = r.data; set(s => ({ prds: s.prds.map(x => x.id === pid ? p : x), current: s.current?.id === pid ? p : s.current, loading: false })); return p; } catch (e) { set({ error: (e as Error).message, loading: false }); return null; } },
  finalizePRD: async (pid) => { set({ loading: true, error: null }); try { const r = await api.finPRD(pid); const p = r.data; set(s => ({ prds: s.prds.map(x => x.id === pid ? p : x), current: s.current?.id === pid ? p : s.current, loading: false })); } catch (e) { set({ error: (e as Error).message, loading: false }); } },
  checkCoverage: async (pid) => { try { const r = await api.checkPRDCov(pid); const c = r.data; set({ cov: c }); return c; } catch (e) { set({ error: (e as Error).message }); return null; } },
  fetchIssues: async (pid) => { set({ loading: true, error: null }); try { const r = await api.listIssues(pid); set({ issues: r.data, loading: false }); } catch (e) { set({ error: (e as Error).message, loading: false }); } },
  createIssue: async (pid, d) => { try { const r = await api.createIssue(pid, d); set(s => ({ issues: [r.data, ...s.issues] })); return r.data; } catch (e) { set({ error: (e as Error).message }); return null; } },
  updateIssueStatus: async (iid, s) => { try { await api.updIssueStatus(iid, s); set(x => ({ issues: x.issues.map(i => i.id === iid ? { ...i, status: s as Issue['status'] } : i) })); } catch (e) { set({ error: (e as Error).message }); } },
  completeIssue: async (iid, sha) => { try { await api.compIssue(iid, sha); set(x => ({ issues: x.issues.map(i => i.id === iid ? { ...i, status: 'done', commit_ref: sha } : i) })); } catch (e) { set({ error: (e as Error).message }); } },
  getFrontier: async (pid) => { try { const r = await api.getFrontier(pid); return r.data; } catch (e) { set({ error: (e as Error).message }); return []; } },
  generateIssues: async (pid) => { set({ loading: true, error: null }); try { const r = await api.genIssues(pid); const is = r.data.issues; set(s => ({ issues: [...is, ...s.issues], loading: false })); return is; } catch (e) { set({ error: (e as Error).message, loading: false }); return []; } },
}));