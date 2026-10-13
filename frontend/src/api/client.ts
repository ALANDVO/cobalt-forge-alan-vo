import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios';

const B = (import.meta as any).env?.VITE_API_URL || '/api/v1';

class ApiClient {
  private c: AxiosInstance;
  private t: string | null = null;
  constructor() {
    this.c = axios.create({ baseURL: B, headers: { 'Content-Type': 'application/json' }, withCredentials: true });
    this.c.interceptors.request.use((cfg: InternalAxiosRequestConfig) => { if (this.t && cfg.headers) cfg.headers.Authorization = `Bearer ${this.t}`; return cfg; });
    this.c.interceptors.response.use(r => r, e => { if (e.response?.status === 401) { this.t = null; localStorage.removeItem('access_token'); window.location.href = '/login'; } return Promise.reject(e); });
  }
  setToken(t: string | null) { this.t = t; t ? localStorage.setItem('access_token', t) : localStorage.removeItem('access_token'); }
  loadToken() { const t = localStorage.getItem('access_token'); if (t) this.t = t; }

  health() { return this.c.get('/health'); }
  login() { return this.c.get('/auth/login'); }
  callback(c: string, s: string, v: string) { return this.c.get('/auth/callback', { params: { code: c, state: s, code_verifier: v } }); }
  getUserinfo(at: string) { return this.c.get('/auth/userinfo', { headers: { Authorization: `Bearer ${at}` } }); }

  createSession(d: { title: string; description?: string }) { return this.c.post('/sessions', d); }
  listSessions() { return this.c.get('/sessions'); }
  getSession(id: string) { return this.c.get(`/sessions/${id}`); }
  startRound(id: string) { return this.c.post(`/sessions/${id}/rounds`); }
  completeSession(id: string) { return this.c.post(`/sessions/${id}/complete`); }
  prepRound(id: string) { return this.c.get(`/sessions/${id}/prepare-round`); }

  addQuestion(rid: string, d: any) { return this.c.post(`/rounds/${rid}/questions`, d); }
  answerQuestion(qid: string, a: string) { return this.c.post(`/questions/${qid}/answer`, { answer: a }); }

  addAssumption(rid: string, t: string) { return this.c.post(`/rounds/${rid}/assumptions`, { assumption_text: t }); }
  vetoAssumption(aid: string) { return this.c.post(`/assumptions/${aid}/veto`); }

  createDecision(d: any) { return this.c.post('/decisions', d); }
  listDecisions(sid?: string) { return this.c.get('/decisions', { params: sid ? { session_id: sid } : {} }); }
  getDecision(id: string) { return this.c.get(`/decisions/${id}`); }
  getCoverage(sid: string) { return this.c.get(`/sessions/${sid}/coverage`); }

  createPRD(sid: string, t: string) { return this.c.post('/prds', { title: t }, { params: { session_id: sid } }); }
  listPRDs(sid: string) { return this.c.get('/prds', { params: { session_id: sid } }); }
  getPRD(id: string) { return this.c.get(`/prds/${id}`); }
  genPRD(id: string) { return this.c.post(`/prds/${id}/gen`); }
  finPRD(id: string) { return this.c.post(`/prds/${id}/fin`); }
  checkPRDCov(id: string) { return this.c.get(`/prds/${id}/cov`); }

  createIssue(pid: string, d: any) { return this.c.post('/issues', d, { params: { prd_id: pid } }); }
  listIssues(pid: string, s?: string) { return this.c.get('/issues', { params: { prd_id: pid, status: s } }); }
  getIssue(id: string) { return this.c.get(`/issues/${id}`); }
  updIssueStatus(id: string, s: string) { return this.c.patch(`/issues/${id}/status`, null, { params: { status: s } }); }
  compIssue(id: string, sha: string) { return this.c.post(`/issues/${id}/complete`, null, { params: { commit_sha: sha } }); }
  getFrontier(pid: string) { return this.c.get(`/prds/${pid}/frontier`); }
  genIssues(pid: string) { return this.c.post(`/prds/${pid}/generate-issues`); }

  addEvidence(did: string, d: any) { return this.c.post('/evidence', d, { params: { decision_id: did } }); }
  getDecEvidence(did: string) { return this.c.get(`/decisions/${did}/evidence`); }
  getIssueEvidence(iid: string) { return this.c.get(`/issues/${iid}/evidence`); }
  getVerCov(ids: string[]) { return this.c.get('/verification/coverage', { params: { decision_ids: ids.join(',') } }); }
  getDecisionEvidence(did: string) { return this.getDecEvidence(did); }
  getVerificationCoverage(ids: string[]) { return this.getVerCov(ids); }
}

export const api = new ApiClient();