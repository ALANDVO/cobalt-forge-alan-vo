import { Link } from 'react-router-dom';
import { useSessionsStore } from '@/hooks/useSessions';
import { useDecisionsStore } from '@/hooks/useDecisions';
import { usePRDStore } from '@/hooks/usePRD';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Plus, GitBranch, ListChecks, FileText, GitMerge, CheckCircle, CheckCircle2 } from 'lucide-react';

export default function Dashboard() {
  const { sessions } = useSessionsStore();
  const { decisions } = useDecisionsStore();
  const { prds, issues } = usePRDStore();

  const a = sessions.filter(s => s.status === 'active').length;
  const r = decisions.filter(d => d.status === 'resolved').length;
  const t = decisions.length;
  const f = prds.filter(p => p.status === 'finalized').length;
  const di = issues.filter(i => i.status === 'done').length;
  const ti = issues.length;

  const stats = [
    { l: 'Active Sessions', v: a, I: GitBranch, c: 'text-primary-600', b: 'bg-primary-100' },
    { l: 'Resolved', v: `${r}/${t}`, I: ListChecks, c: 'text-green-600', b: 'bg-green-100' },
    { l: 'PRDs Finalized', v: f, I: FileText, c: 'text-blue-600', b: 'bg-blue-100' },
    { l: 'Done Issues', v: `${di}/${ti}`, I: CheckCircle2, c: 'text-purple-600', b: 'bg-purple-100' },
  ];

  const quickActions = [
    { path: '/sessions', icon: Plus, bg: 'bg-primary-100', color: 'text-primary-600', label: 'Start Session' },
    { path: '/decisions', icon: ListChecks, bg: 'bg-green-100', color: 'text-green-600', label: 'Decision Ledger' },
    { path: '/prds', icon: FileText, bg: 'bg-blue-100', color: 'text-blue-600', label: 'Generate PRD' },
    { path: '/issues', icon: GitMerge, bg: 'bg-purple-100', color: 'text-purple-600', label: 'Manage Issues' },
    { path: '/verification', icon: CheckCircle, bg: 'bg-orange-100', color: 'text-orange-600', label: 'Verification' },
  ];

  const workflowSteps = [
    { label: 'Decision Ledger', icon: CheckCircle2, desc: `${r} of ${t} resolved`, color: 'green' },
    { label: 'PRDs', icon: FileText, desc: `${f} finalized`, color: 'blue' },
    { label: 'Issues', icon: GitMerge, desc: `${di} of ${ti} done`, color: 'purple' },
  ];

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Dashboard</h1>
          <p className="text-slate-600 mt-1">Traceable engineering workflow</p>
        </div>
        <Link to="/sessions">
          <Button><Plus className="h-4 w-4" />New Session</Button>
        </Link>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map(s => (
          <Card key={s.l}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-600">{s.l}</p>
                  <p className="text-2xl font-bold text-slate-900 mt-1">{s.v}</p>
                </div>
                <div className={`p-3 rounded-xl ${s.b}`}>
                  <s.I className={`h-6 w-6 ${s.c}`} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader className="flex items-center justify-between">
              <CardTitle>Recent Sessions</CardTitle>
              <Link to="/sessions"><Button variant="ghost" size="sm">View all</Button></Link>
            </CardHeader>
            <CardContent>
              {sessions.slice(0, 5).length > 0 ? (
                <div className="space-y-4">
                  {sessions.slice(0, 5).map(s => (
                    <Link key={s.id} to={`/sessions/${s.id}`} className="flex items-center justify-between p-4 hover:bg-slate-50 rounded-lg border border-slate-200">
                      <div className="flex items-center gap-4">
                        <div className="p-2 bg-primary-100 rounded-lg">
                          <GitBranch className="h-5 w-5 text-primary-600" />
                        </div>
                        <div>
                          <p className="font-medium text-slate-900">{s.title}</p>
                          <p className="text-sm text-slate-500">{s.description || 'No description'}</p>
                          <div className="flex items-center gap-2 mt-1">
                            <Badge variant={s.status === 'active' ? 'success' : 'primary'}>
                              {s.status}
                            </Badge>
                          </div>
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              ) : (
                <p className="text-slate-500 text-center py-8">No sessions yet</p>
              )}
            </CardContent>
          </Card>
        </div>
        <div>
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                {quickActions.map(a => (
                  <Link key={a.path} to={a.path}>
                    <Button variant="secondary" className="w-full justify-start gap-3">
                      <div className={`p-2 rounded-lg ${a.bg}`}>
                        <a.icon className={`h-5 w-5 ${a.color}`} />
                      </div>
                      <span>{a.label}</span>
                    </Button>
                  </Link>
                ))}
              </div>
            </CardContent>
          </Card>
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Workflow</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {workflowSteps.map(w => (
                <div key={w.label} className="flex items-center gap-3">
                  <div className={`p-2 bg-${w.color}-100 rounded-lg`}>
                    <w.icon className={`h-5 w-5 text-${w.color}-600`} />
                  </div>
                  <div>
                    <p className="font-medium text-slate-900">{w.label}</p>
                    <p className="text-sm text-slate-500">{w.desc}</p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}