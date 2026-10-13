import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import App from './App';

// Mock the auth store
vi.mock('./hooks/useAuth', () => ({
  useAuthStore: () => ({
    user: { id: 'test', email: 'test@test.com', name: 'Test', role: 'admin', created_at: '', updated_at: '' },
    isAuthenticated: true,
    isLoading: false,
    setUser: vi.fn(),
    setLoading: vi.fn(),
    logout: vi.fn(),
  }),
}));

// Mock the API client
vi.mock('./api/client', () => ({
  api: {
    loadToken: vi.fn(),
    health: vi.fn().mockResolvedValue({ data: { status: 'healthy' } }),
    listSessions: vi.fn().mockResolvedValue({ data: [] }),
  },
}));

describe('App', () => {
  it('renders without crashing', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    // Check for the main page heading (h1) to avoid matching nav links
    expect(screen.getByRole('heading', { name: 'Dashboard' })).toBeInTheDocument();
  });

  it('shows navigation links', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    // Check for nav links specifically - use getAllByRole since links appear in both sidebar and quick actions
    expect(screen.getAllByRole('link', { name: 'Sessions' }).length).toBeGreaterThan(0);
    expect(screen.getAllByRole('link', { name: 'Decisions' }).length).toBeGreaterThan(0);
    expect(screen.getAllByRole('link', { name: 'PRDs' }).length).toBeGreaterThan(0);
    expect(screen.getAllByRole('link', { name: 'Issues' }).length).toBeGreaterThan(0);
    expect(screen.getAllByRole('link', { name: 'Verification' }).length).toBeGreaterThan(0);
  });
});