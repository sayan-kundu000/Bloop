import React from 'react';
import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { ProtectedRoute } from '../../routes/ProtectedRoute';
import { NotFoundPage } from '../../pages/NotFoundPage';
import { useAuthStore } from '../../stores/authStore';

describe('Routing & Route Guard Foundation', () => {
  beforeEach(() => {
    localStorage.clear();
    useAuthStore.setState({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
    });
  });

  it('renders loading spinner while authentication state is resolving', () => {
    useAuthStore.setState({ isLoading: true, isAuthenticated: false });

    render(
      <MemoryRouter initialEntries={['/workspace']}>
        <Routes>
          <Route element={<ProtectedRoute />}>
            <Route path="/workspace" element={<div>Workspace Protected Content</div>} />
          </Route>
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(screen.getByText(/checking authentication/i)).toBeInTheDocument();
    expect(screen.queryByText('Workspace Protected Content')).not.toBeInTheDocument();
  });

  it('redirects unauthenticated user from protected route to /login', () => {
    useAuthStore.setState({ isLoading: false, isAuthenticated: false });

    render(
      <MemoryRouter initialEntries={['/workspace']}>
        <Routes>
          <Route element={<ProtectedRoute />}>
            <Route path="/workspace" element={<div>Workspace Protected Content</div>} />
          </Route>
          <Route path="/login" element={<div>Sign In Screen</div>} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('Sign In Screen')).toBeInTheDocument();
    expect(screen.queryByText('Workspace Protected Content')).not.toBeInTheDocument();
  });

  it('allows access to protected route when authenticated', () => {
    useAuthStore.setState({
      isLoading: false,
      isAuthenticated: true,
      token: 'valid-test-token',
      user: {
        id: 1,
        email: 'test@bloop.ai',
        is_active: true,
        is_superuser: false,
        created_at: '2026-09-17T00:00:00Z',
      },
    });

    render(
      <MemoryRouter initialEntries={['/workspace']}>
        <Routes>
          <Route element={<ProtectedRoute />}>
            <Route path="/workspace" element={<div>Workspace Protected Content</div>} />
          </Route>
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('Workspace Protected Content')).toBeInTheDocument();
  });

  it('renders NotFoundPage on unknown route', () => {
    render(
      <MemoryRouter initialEntries={['/non-existent-screen']}>
        <Routes>
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('Page Not Found')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /go to workspace/i })).toBeInTheDocument();
  });
});
