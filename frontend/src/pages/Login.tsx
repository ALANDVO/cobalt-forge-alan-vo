import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '@/api/client';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { LogIn, Key } from 'lucide-react';

export default function Login() {
  const n = useNavigate();
  const [ld, setLd] = useState(false);
  const d = async () => { setLd(true); try { n('/dashboard'); } finally { setLd(false); } };
  const o = async () => { setLd(true); try { const r = await api.login(); const { auth_url, state, code_verifier, nonce } = r.data; sessionStorage.setItem('oidc_state', state); sessionStorage.setItem('oidc_code_verifier', code_verifier); sessionStorage.setItem('oidc_nonce', nonce); window.location.href = auth_url; } catch { setLd(false); } };
  return <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4"><Card className="w-full max-w-md"><CardHeader className="text-center"><div className="mx-auto mb-4 p-3 bg-primary-100 rounded-xl w-fit"><Key className="h-8 w-8 text-primary-600"/></div><CardTitle>Welcome to Cobalt Forge</CardTitle><p className="text-slate-600 mt-2">Traceable Engineering Workflow</p></CardHeader><CardContent className="space-y-4"><div className="relative"><div className="absolute inset-0 flex items-center"><div className="w-full border-t border-slate-200"/></div><div className="relative flex justify-center text-sm"><span className="px-2 bg-white text-slate-500">Or</span></div></div><div className="space-y-3"><Button variant="secondary" className="w-full justify-center gap-3" onClick={d} disabled={ld}><LogIn className="h-4 w-4"/>{ld?'Signing in...':'Demo User'}</Button><Button variant="ghost" className="w-full justify-center gap-3" onClick={o} disabled={ld}><LogIn className="h-4 w-4"/>{ld?'Redirecting...':'Keycloak (OIDC)'}</Button></div><div className="text-center text-sm text-slate-500"><p>Demo creates local user.</p><p className="mt-1">OIDC requires Keycloak.</p></div></CardContent></Card></div>;
}