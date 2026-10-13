import { usePRDStore } from '@/hooks/usePRD';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';

export default function PRDs() {
  const { prds, fetchPRDs, loading, error } = usePRDStore();

  const f = prds.filter(p => p.status === 'finalized').length;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">PRDs</h1>
          <p className="text-slate-600 mt-1">Product Requirements Documents</p>
        </div>
        <Button onClick={() => fetchPRDs('')}>Refresh</Button>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card><CardContent className="p-6"><p className="text-sm text-slate-600">Total PRDs</p><p className="text-2xl font-bold text-slate-900 mt-1">{prds.length}</p></CardContent></Card>
        <Card><CardContent className="p-6"><p className="text-sm text-slate-600">Finalized</p><p className="text-2xl font-bold text-slate-900 mt-1">{f}</p></CardContent></Card>
      </div>

      <Card>
        <CardHeader className="flex items-center justify-between">
          <CardTitle>PRDs</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-4">{[1,2,3].map(i => <div key={i} className="h-16 animate-pulse bg-slate-100 rounded" />)}</div>
          ) : prds.length > 0 ? (
            <div className="space-y-3">
              {prds.map(p => (
                <div key={p.id} className="p-4 border border-slate-200 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-slate-900">{p.title}</p>
                      <p className="text-sm text-slate-500">{p.content?.slice(0, 100) || 'No content'}</p>
                    </div>
                    <Badge variant={p.status === 'finalized' ? 'success' : 'primary'}>{p.status}</Badge>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-slate-500 text-center py-8">No PRDs yet</p>
          )}
        </CardContent>
      </Card>

      {error && <div className="fixed bottom-4 right-4 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg shadow-lg">{error}</div>}
    </div>
  );
}