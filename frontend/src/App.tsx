import { Routes, Route, Navigate } from 'react-router-dom';
import { useEffect } from 'react';
import { useAuthStore } from '@/hooks/useAuth';
import { api } from '@/api/client';
import Layout from '@/components/Layout';
import Dashboard from '@/pages/Dashboard';
import Sessions from '@/pages/Sessions';
import SessionDetail from '@/pages/SessionDetail';
import Decisions from '@/pages/Decisions';
import PRDs from '@/pages/PRDs';
import PRDDetail from '@/pages/PRDDetail';
import Issues from '@/pages/Issues';
import Verification from '@/pages/Verification';
import Login from '@/pages/Login';
import Callback from '@/pages/Callback';

function App() {
  const { setUser, setLoading, isAuthenticated } = useAuthStore();

  useEffect(() => {
    api.loadToken();
    // In demo mode, auto-authenticate
    if (!isAuthenticated) {
      const demoUser = {
        id: 'demo',
        keycloak_sub: 'demo-user',
        email: 'demo@cobaltforge.local',
        name: 'Demo User',
        role: 'admin' as const,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      setUser(demoUser);
    }
    setLoading(false);
  }, [setUser, setLoading, isAuthenticated]);

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/callback" element={<Callback />} />
      <Route element={<Layout />}>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/sessions" element={<Sessions />} />
        <Route path="/sessions/:id" element={<SessionDetail />} />
        <Route path="/decisions" element={<Decisions />} />
        <Route path="/prds" element={<PRDs />} />
        <Route path="/prds/:id" element={<PRDDetail />} />
        <Route path="/issues" element={<Issues />} />
        <Route path="/verification" element={<Verification />} />
      </Route>
    </Routes>
  );
}

export default App;