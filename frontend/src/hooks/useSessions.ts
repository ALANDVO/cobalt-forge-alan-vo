import { create } from 'zustand';
import type { Session, Question, Assumption, DecisionRecord, PrepareRoundResponse } from '@/types';
import { api } from '@/api/client';

interface S {
  sessions: Session[];
  currentSession: Session | null;
  round: number;
  questions: Question[];
  assumptions: Assumption[];
  decisions: DecisionRecord[];
  isLoading: boolean;
  error: string | null;
  fetchSessions: () => Promise<void>;
  createSession: (t: string, d: string) => Promise<Session | null>;
  selectSession: (s: Session) => void;
  startRound: (id: string) => Promise<void>;
  prepareRound: (id: string) => Promise<PrepareRoundResponse | null>;
  addQuestion: (rid: string, d: any) => Promise<Question | null>;
  answerQuestion: (qid: string, a: string) => Promise<Question | null>;
  addAssumption: (rid: string, t: string) => Promise<Assumption | null>;
  vetoAssumption: (aid: string) => Promise<void>;
  completeSession: (sid: string) => Promise<void>;
  fetchDecisions: (sid: string) => Promise<void>;
  clearError: () => void;
}

export const useSessionsStore = create<S>((set) => ({
  sessions: [], currentSession: null, round: 0, questions: [], assumptions: [], decisions: [], isLoading: false, error: null,
  clearError: () => set({ error: null }),
  fetchSessions: async () => { set({ isLoading: true, error: null }); try { const r = await api.listSessions(); set({ sessions: r.data, isLoading: false }); } catch (e) { set({ error: (e as Error).message, isLoading: false }); } },
  createSession: async (t, d) => { set({ isLoading: true, error: null }); try { const r = await api.createSession({ title: t, description: d }); const s = r.data; set(x => ({ sessions: [s, ...x.sessions], currentSession: s, isLoading: false })); return s; } catch (e) { set({ error: (e as Error).message, isLoading: false }); return null; } },
  selectSession: (s) => set({ currentSession: s }),
  startRound: async (id) => { set({ isLoading: true, error: null }); try { const r = await api.startRound(id); set({ round: r.data.round_number, isLoading: false }); } catch (e) { set({ error: (e as Error).message, isLoading: false }); } },
  prepareRound: async (id) => { set({ isLoading: true, error: null }); try { const r = await api.prepRound(id); const d = r.data; set({ questions: d.questions.map((q: any) => ({ id: q.id, question_number: +q.number.slice(1), question_text: q.text, detailed_explanation: q.explanation, question_type: q.type, prerequisites: [], options: q.options, recommended_option: q.recommended, recommended_reason: q.recommended_reason, status: 'pending', answer: '', decision_record_id: null })), assumptions: d.assumptions.map((a: any) => ({ id: a.id, assumption_number: +a.number.slice(1), assumption_text: a.text, vetoed: a.vetoed })), isLoading: false }); return d; } catch (e) { set({ error: (e as Error).message, isLoading: false }); return null; } },
  addQuestion: async (rid, d) => { try { const r = await api.addQuestion(rid, d); set(x => ({ questions: [...x.questions, r.data] })); return r.data; } catch (e) { set({ error: (e as Error).message }); return null; } },
  answerQuestion: async (qid, a) => { try { const r = await api.answerQuestion(qid, a); set(x => ({ questions: x.questions.map(q => q.id === qid ? r.data : q) })); return r.data; } catch (e) { set({ error: (e as Error).message }); return null; } },
  addAssumption: async (rid, t) => { try { const r = await api.addAssumption(rid, t); set(x => ({ assumptions: [...x.assumptions, r.data] })); return r.data; } catch (e) { set({ error: (e as Error).message }); return null; } },
  vetoAssumption: async (aid) => { try { await api.vetoAssumption(aid); set(x => ({ assumptions: x.assumptions.map(a => a.id === aid ? { ...a, vetoed: true } : a) })); } catch (e) { set({ error: (e as Error).message }); } },
  completeSession: async (sid) => { set({ isLoading: true, error: null }); try { await api.completeSession(sid); set(x => ({ currentSession: x.currentSession?.id === sid ? { ...x.currentSession, status: 'completed' } : x.currentSession, sessions: x.sessions.map(s => s.id === sid ? { ...s, status: 'completed' } : s), isLoading: false })); } catch (e) { set({ error: (e as Error).message, isLoading: false }); } },
  fetchDecisions: async (sid) => { set({ isLoading: true, error: null }); try { const r = await api.listDecisions(sid); set({ decisions: r.data, isLoading: false }); } catch (e) { set({ error: (e as Error).message, isLoading: false }); } },
}));