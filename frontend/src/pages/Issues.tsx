import { usePRDStore } from '@/hooks/usePRD';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';

export default function Issues() {
  const { issues, fetchIssues, loading, error } = usePRDStore();

  const di = issues.filter(i => i.status === 'done').length;
  const ti = issues.length;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Issues</h1>
          <p className="text-slate-600 mt-1">Track implementation progress</p>
        </div>
        <Button onClick={() => fetchIssues('')}>Refresh</Button>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card><CardContent className="p-6"><p className="text-sm text-slate-600">Total Issues</p><p className="text-2xl font-bold text-slate-900 mt-1">{ti}</p></CardContent></Card>
        <Card><CardContent className="p-6"><p className="text-sm text-slate-600">Done</p><p className="text-2xl font-bold text-slate-900 mt-1">{di}</p></CardContent></Card>
      </div>

      <Card>
        <CardHeader className="flex items-center justify-between">
          <CardTitle>Issues</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-4">{[1,2,3].map(i => <div key={i} className="h-16 animate-pulse bg-slate-100 rounded" />)}</div>
          ) : issues.length > 0 ? (
            <div className="space-y-3">
              {issues.map(i => (
                <div key={i.id} className="p-4 border border-slate-200 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-slate-900">{i.title}</p>
                      <p className="text-sm text-slate-500">{i.description?.slice(0, 100) || 'No description'}</p>
                    </div>
                    <Badge variant={i.status === 'done' ? 'success' : 'primary'}>{i.status}</Badge>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-slate-500 text-center py-8">No issues yet</p>
          )}
        </CardContent>
      </Card>

      {error && <div className="fixed bottom-4 right-4 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg shadow-lg">{error}</div>}
    </div>
  );
}