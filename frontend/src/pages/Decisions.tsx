import { useDecisionsStore } from '@/hooks/useDecisions';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';

export default function Decisions() {
  const { decisions, fetchDecisions, isLoading, error, coverage } = useDecisionsStore();

  const r = decisions.filter(d => d.status === 'resolved').length;
  const t = decisions.length;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Decision Ledger</h1>
          <p className="text-slate-600 mt-1">View and manage decision records</p>
        </div>
        <Button onClick={() => fetchDecisions('')}>Refresh</Button>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card><CardContent className="p-6"><p className="text-sm text-slate-600">Total Decisions</p><p className="text-2xl font-bold text-slate-900 mt-1">{t}</p></CardContent></Card>
        <Card><CardContent className="p-6"><p className="text-sm text-slate-600">Resolved</p><p className="text-2xl font-bold text-slate-900 mt-1">{r}</p></CardContent></Card>
        <Card><CardContent className="p-6"><p className="text-sm text-slate-600">Coverage</p><p className="text-2xl font-bold text-slate-900 mt-1">{coverage?.coverage_percentage || 0}%</p></CardContent></Card>
      </div>

      <Card>
        <CardHeader className="flex items-center justify-between">
          <CardTitle>Decisions</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">{[1,2,3].map(i => <div key={i} className="h-16 animate-pulse bg-slate-100 rounded" />)}</div>
          ) : decisions.length > 0 ? (
            <div className="space-y-3">
              {decisions.map(d => (
                <div key={d.id} className="p-4 border border-slate-200 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-slate-900">{d.stable_id}: {d.question.slice(0, 80)}</p>
                      <p className="text-sm text-slate-500">{d.normalized_requirement.slice(0, 100)}</p>
                    </div>
                    <Badge variant={d.status === 'resolved' ? 'success' : 'primary'}>{d.status}</Badge>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-slate-500 text-center py-8">No decisions yet</p>
          )}
        </CardContent>
      </Card>

      {error && <div className="fixed bottom-4 right-4 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg shadow-lg">{error}</div>}
    </div>
  );
}