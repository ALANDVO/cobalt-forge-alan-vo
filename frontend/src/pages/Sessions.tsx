import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useSessionsStore } from '@/hooks/useSessions';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Input } from '@/components/ui/Input';
import { Textarea } from '@/components/ui/Textarea';
import { Plus, GitBranch, Filter } from 'lucide-react';

export default function Sessions() {
  const { sessions, createSession, isLoading, error } = useSessionsStore();
  const [show, setShow] = useState(false);
  const [t, setT] = useState('');
  const [d, setD] = useState('');
  const [c, setC] = useState(false);

  const hc = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!t.trim()) return;
    setC(true);
    await createSession(t, d);
    setShow(false);
    setT('');
    setD('');
    setC(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Grilling Sessions</h1>
          <p className="text-slate-600 mt-1">Manage design interview sessions</p>
        </div>
        <Button onClick={() => setShow(true)}><Plus className="h-4 w-4" />New Session</Button>
      </div>

      <Card>
        <CardHeader className="flex items-center justify-between">
          <CardTitle>{sessions.length} Sessions</CardTitle>
          <div className="flex items-center gap-2">
            <Input placeholder="Search..." className="w-64" />
            <Button variant="ghost" size="sm"><Filter className="h-4 w-4" /></Button>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3, 4].map(i => <div key={i} className="h-16 animate-pulse bg-slate-100 rounded" />)}
            </div>
          ) : sessions.length > 0 ? (
            <div className="space-y-4">
              {sessions.map(s => (
                <Link key={s.id} to={`/sessions/${s.id}`} className="flex items-center justify-between p-4 hover:bg-slate-50 rounded-lg border border-slate-200">
                  <div className="flex items-center gap-4">
                    <div className="p-3 bg-primary-100 rounded-lg">
                      <GitBranch className="h-5 w-5 text-primary-600" />
                    </div>
                    <div>
                      <p className="font-medium text-slate-900">{s.title}</p>
                      <p className="text-sm text-slate-500">{s.description || 'No description'}</p>
                    </div>
                  </div>
                  <Badge variant={s.status === 'active' ? 'success' : 'primary'}>{s.status}</Badge>
                </Link>
              ))}
            </div>
          ) : (
            <p className="text-slate-500 text-center py-8">No sessions yet</p>
          )}
        </CardContent>
      </Card>

      {show && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50" onClick={() => setShow(false)}>
          <Card className="w-full max-w-md animate-in slide-in-from-top-4" onClick={e => e.stopPropagation()}>
            <CardHeader><CardTitle>New Grilling Session</CardTitle></CardHeader>
            <form onSubmit={hc} className="space-y-4 p-6">
              <Input label="Title" value={t} onChange={e => setT(e.target.value)} placeholder="e.g., User Auth Redesign" required />
              <Textarea label="Description" value={d} onChange={e => setD(e.target.value)} placeholder="Brief description..." rows={3} />
              <div className="flex justify-end gap-3 pt-4">
                <Button type="button" variant="secondary" onClick={() => setShow(false)}>Cancel</Button>
                <Button type="submit" disabled={c || !t.trim()}>{c ? 'Creating...' : 'Create'}</Button>
              </div>
            </form>
          </Card>
        </div>
      )}

      {error && <div className="fixed bottom-4 right-4 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg shadow-lg">{error}</div>}
    </div>
  );
}