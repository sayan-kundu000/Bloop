import React from 'react';
import { Navigate, useLocation, Outlet } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { Spinner } from '../components/ui';

interface ProtectedRouteProps {
  children?: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuthStore();
  const location = useLocation();

  // Prevent flash or premature redirect while authenticating
  if (isLoading) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center space-y-4">
        <Spinner size="lg" label="Checking authentication..." />
        <p className="text-sm text-slate-400 font-medium">Verifying session...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    // Redirect to /login preserving target location for return navigation
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children ? <>{children}</> : <Outlet />;
};
