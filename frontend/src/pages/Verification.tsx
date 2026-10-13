import { useVerificationStore } from '@/hooks/useVerification';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';

export default function Verification() {
  const { coverage, getCoverage, isLoading, error } = useVerificationStore();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Verification</h1>
          <p className="text-slate-600 mt-1">Track verification coverage</p>
        </div>
        <Button onClick={() => getCoverage([])}>Refresh</Button>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card><CardContent className="p-6"><p className="text-sm text-slate-600">Total</p><p className="text-2xl font-bold text-slate-900 mt-1">{coverage?.total || 0}</p></CardContent></Card>
        <Card><CardContent className="p-6"><p className="text-sm text-slate-600">Verified</p><p className="text-2xl font-bold text-slate-900 mt-1">{coverage?.verified || 0}</p></CardContent></Card>
        <Card><CardContent className="p-6"><p className="text-sm text-slate-600">Failed</p><p className="text-2xl font-bold text-slate-900 mt-1">{coverage?.failed || 0}</p></CardContent></Card>
        <Card><CardContent className="p-6"><p className="text-sm text-slate-600">Pending</p><p className="text-2xl font-bold text-slate-900 mt-1">{coverage?.pending || 0}</p></CardContent></Card>
      </div>

      <Card>
        <CardHeader className="flex items-center justify-between">
          <CardTitle>Verification Coverage</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">{[1,2,3].map(i => <div key={i} className="h-16 animate-pulse bg-slate-100 rounded" />)}</div>
          ) : coverage && coverage.details.length > 0 ? (
            <div className="space-y-3">
              {coverage.details.map(d => (
                <div key={d.decision_id} className="p-4 border border-slate-200 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-slate-900">{d.decision_id.slice(0, 8)}</p>
                      <p className="text-sm text-slate-500">{d.status} - {d.evidence_count} evidence</p>
                    </div>
                    <Badge variant={d.status === 'verified' ? 'success' : d.status === 'failed' ? 'danger' : 'primary'}>{d.status}</Badge>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-slate-500 text-center py-8">No verification data</p>
          )}
        </CardContent>
      </Card>

      {error && <div className="fixed bottom-4 right-4 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg shadow-lg">{error}</div>}
    </div>
  );
}