import { usePRDStore } from '@/hooks/usePRD';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

export default function PRDDetail() {
  const { current, fetchPRDs, error } = usePRDStore();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">PRD Detail</h1>
          <p className="text-slate-600 mt-1">View and manage PRD content</p>
        </div>
        <Button onClick={() => fetchPRDs('')}>Refresh</Button>
      </div>

      <Card>
        <CardHeader className="flex items-center justify-between">
          <CardTitle>PRD Content</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="prose max-w-none">
            <pre className="whitespace-pre-wrap text-sm">{current?.content || 'No content'}</pre>
          </div>
        </CardContent>
      </Card>

      {error && <div className="fixed bottom-4 right-4 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg shadow-lg">{error}</div>}
    </div>
  );
}