import { useSessionsStore } from '@/hooks/useSessions';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Plus, Check, Loader2, Flag } from 'lucide-react';

export default function SessionDetail() {
  const {
    currentSession,
    startRound,
    addAssumption,
    vetoAssumption,
    completeSession,
    answerQuestion,
    questions,
    assumptions,
    round,
    error,
  } = useSessionsStore();

  if (!currentSession) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
      </div>
    );
  }

  const pending = questions.filter((q) => q.status === 'pending');
  const answered = questions.filter((q) => q.status === 'answered');

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">{currentSession.title}</h1>
          <p className="text-slate-600 mt-1">{currentSession.description}</p>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant={currentSession.status === 'active' ? 'success' : 'primary'}>
            {currentSession.status}
          </Badge>
          {currentSession.status === 'active' && (
            <Button onClick={() => completeSession(currentSession.id)}>
              <Flag className="h-4 w-4" />
              Complete
            </Button>
          )}
        </div>
      </div>

      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-slate-900">Round {round}</h2>
            {round === 0 && currentSession.status === 'active' && (
              <Button onClick={() => startRound(currentSession.id)}>
                <Plus className="h-4 w-4" />
                Start Round
              </Button>
            )}
            {round > 0 && pending.length === 0 && answered.length > 0 && currentSession.status === 'active' && (
              <Button variant="secondary" onClick={() => startRound(currentSession.id)}>
                <Plus className="h-4 w-4" />
                Next Round
              </Button>
            )}
          </div>

          {(pending.length || answered.length) && (
            <div className="space-y-4">
              {answered.map((q) => (
                <div key={q.id} className="p-4 bg-green-50 border border-green-200 rounded-lg">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-medium px-2 py-0.5 bg-green-100 text-green-700 rounded">
                          {q.question_type === 'pivot' ? 'Pivot' : 'Detail'}
                        </span>
                        <span className="text-sm font-medium text-slate-900">Q{q.question_number}</span>
                      </div>
                      <p className="text-slate-700">{q.question_text}</p>
                      {q.detailed_explanation && <p className="text-sm text-slate-500 mt-1">{q.detailed_explanation}</p>}
                      {q.answer && <p className="text-sm text-green-700 mt-2"><strong>Answer:</strong> {q.answer}</p>}
                    </div>
                  </div>
                </div>
              ))}
              {pending.map((q) => (
                <div key={q.id} className="p-4 bg-slate-50 border border-slate-200 rounded-lg">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-medium px-2 py-0.5 bg-primary-100 text-primary-700 rounded">
                          {q.question_type === 'pivot' ? 'Pivot' : 'Detail'}
                        </span>
                        <span className="text-sm font-medium text-slate-900">Q{q.question_number}</span>
                      </div>
                      <p className="text-slate-700">{q.question_text}</p>
                      {q.detailed_explanation && <p className="text-sm text-slate-500 mt-1">{q.detailed_explanation}</p>}
                      {q.options && q.options.length > 0 && (
                        <div className="mt-3 space-y-2">
                          {q.options.map((opt: { label: string; text: string }, i: number) => (
                            <label key={i} className="flex items-center gap-2 cursor-pointer">
                              <input type="radio" name={`q-${q.id}`} className="text-primary-600" />
                              <span className="text-sm text-slate-700"><strong>{opt.label}.</strong> {opt.text}</span>
                            </label>
                          ))}
                        </div>
                      )}
                      {q.recommended_option && (
                        <p className="text-xs text-primary-600 mt-2"><strong>Recommended:</strong> {q.recommended_option} - {q.recommended_reason}</p>
                      )}
                    </div>
                    <Button size="sm" onClick={() => { const a = prompt(`Answer for Q${q.question_number}:`); if (a) answerQuestion(q.id, a); }}>Answer</Button>
                  </div>
                </div>
              ))}
            </div>
          )}
          {questions.length === 0 && round > 0 && (
            <div className="text-center py-8">
              <Check className="h-12 w-12 text-green-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-slate-900">All answered!</h3>
              <p className="text-slate-500 mt-1">Ready for next round or complete</p>
            </div>
          )}

          <div className="flex gap-3 mt-6 pt-6 border-t border-slate-200">
            {assumptions.length > 0 && (
              <div className="flex-1">
                <h3 className="text-sm font-medium text-slate-900 mb-2">Assumptions</h3>
                <div className="space-y-2">
                  {assumptions.map((a) => (
                    <div key={a.id} className="flex items-center justify-between p-3 bg-amber-50 border border-amber-200 rounded-lg">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-medium px-2 py-0.5 bg-amber-100 text-amber-700 rounded">A{a.assumption_number}</span>
                        <span className="text-sm text-slate-700">{a.assumption_text}</span>
                      </div>
                      {!a.vetoed && <Button size="sm" variant="ghost" onClick={() => vetoAssumption(a.id)}>Veto</Button>}
                    </div>
                  ))}
                </div>
              </div>
            )}
            <Button variant="secondary" onClick={() => { const t = prompt('Assumption:'); if (t) { const rid = questions[0]?.id || assumptions[0]?.id || ''; addAssumption(rid, t); } }}>Add Assumption</Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Decision Ledger</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-slate-500 text-sm">Decisions appear here after questions are answered.</p>
        </CardContent>
      </Card>

      {error && (
        <div className="fixed bottom-4 right-4 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg shadow-lg">
          {error}
        </div>
      )}
    </div>
  );
}