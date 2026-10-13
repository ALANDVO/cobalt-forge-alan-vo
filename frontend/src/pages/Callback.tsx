import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { api } from '@/api/client';
import { useAuthStore } from '@/hooks/useAuth';
import { Loader2, CheckCircle, AlertCircle, ArrowRight } from 'lucide-react';

export default function Callback() {
  const n = useNavigate();
  const [sp] = useSearchParams();
  const { setUser } = useAuthStore();
  const [st, setSt] = useState<'l'|'s'|'e'>('l');
  const [er, setEr] = useState<string|null>(null);

    useEffect(() => {
    const c = sp.get('code'), s = sp.get('state'), v = sessionStorage.getItem('oidc_code_verifier');
    if (!c || !s || !v) { setEr('Missing params'); setSt('e'); return; }
    if (s !== sessionStorage.getItem('oidc_state')) { setEr('Invalid state'); setSt('e'); return; }
    (async () => {
      try {
        const t = await api.callback(c, s, v);
        if (!t) throw new Error('Token exchange failed');
        const u = await api.getUserinfo(t.data.access_token);
        if (!u) throw new Error('Userinfo failed');
        setUser({ id: u.data.sub, keycloak_sub: u.data.sub, email: u.data.email||'', name: u.data.name||u.data.preferred_username||'User', role: 'operator', created_at: new Date().toISOString(), updated_at: new Date().toISOString() });
        setSt('s');
        sessionStorage.removeItem('oidc_state');
        sessionStorage.removeItem('oidc_code_verifier');
        sessionStorage.removeItem('oidc_nonce');
        setTimeout(()=>n('/dashboard'),1500);
      } catch (e) { setEr((e as Error).message); setSt('e'); }
    })();
  }, [sp, n, setUser]);

  if (st === 'l') return <div className="min-h-screen flex items-center justify-center bg-slate-50"><Loader2 className="h-12 w-12 animate-spin text-primary-600 mx-auto mb-4"/><p className="text-slate-600">Completing authentication...</p></div>;
  if (st === 's') return <div className="min-h-screen flex items-center justify-center bg-slate-50 text-center"><div className="mx-auto mb-4 p-3 bg-green-100 rounded-xl w-fit"><CheckCircle className="h-8 w-8 text-green-600"/></div><h1 className="text-2xl font-bold text-slate-900">Success</h1><p className="text-slate-600 mt-2">Redirecting...</p><div className="mt-6 flex items-center justify-center gap-2 text-primary-600"><ArrowRight className="h-5 w-5 animate-bounce"/></div></div>;
  return <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4"><div className="w-full max-w-md text-center"><div className="mx-auto mb-4 p-3 bg-red-100 rounded-xl w-fit"><AlertCircle className="h-8 w-8 text-red-600"/></div><h1 className="text-2xl font-bold text-slate-900">Failed</h1><p className="text-slate-600 mt-2">{er||'Unknown error'}</p><button onClick={()=>n('/login')} className="mt-6 inline-flex items-center justify-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">Try Again</button></div></div>;
}