import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { LogIn, Volume2, AlertCircle } from 'lucide-react';
import { useAuthStore } from '../stores/authStore';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuthStore();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);
    try {
      await login(email, password);
      const destination = (location.state as any)?.from?.pathname || '/dashboard';
      navigate(destination, { replace: true });
    } catch (err: any) {
      setError(err.message || 'Login failed. Please verify your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4 py-12">
      <div className="glass-panel w-full max-w-md rounded-2xl p-8 border border-white/10 shadow-2xl relative overflow-hidden">
        <div className="flex flex-col items-center text-center mb-6">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-bloop-600 via-bloop-500 to-quantum-500 flex items-center justify-center shadow-lg shadow-bloop-500/25 mb-3">
            <Volume2 className="w-6 h-6 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight font-['Outfit']">
            Welcome to <span className="gradient-text-bloop">Bloop</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">Sign in to access your speech history and favorites</p>
        </div>

        {error && (
          <div className="flex items-center space-x-2 p-3 mb-5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex flex-col gap-4 text-sm">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">Email Address</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@example.com"
              required
              className="w-full bg-slate-900/90 text-white rounded-xl p-3 border border-white/10 focus:outline-none focus:border-bloop-500 transition"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              className="w-full bg-slate-900/90 text-white rounded-xl p-3 border border-white/10 focus:outline-none focus:border-bloop-500 transition"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full mt-2 py-3 rounded-xl bg-bloop-600 hover:bg-bloop-500 text-white font-semibold shadow-lg shadow-bloop-600/30 transition flex items-center justify-center space-x-2"
          >
            {isLoading ? (
              <span>Signing In...</span>
            ) : (
              <>
                <LogIn className="w-4 h-4" />
                <span>Sign In</span>
              </>
            )}
          </button>
        </form>

        <div className="mt-6 text-center text-xs text-slate-400">
          Don't have an account yet?{' '}
          <Link to="/register" className="text-bloop-400 hover:text-bloop-300 font-semibold underline ml-1">
            Create an account
          </Link>
        </div>
      </div>
    </div>
  );
};
