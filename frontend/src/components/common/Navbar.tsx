import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Volume2,
  Atom,
  History,
  Star,
  User as UserIcon,
  LayoutDashboard,
  LogIn,
  LogOut,
  Sliders,
  Menu,
  X,
} from 'lucide-react';
import { useAuthStore } from '../../stores/authStore';

export const Navbar: React.FC = () => {
  const location = useLocation();
  const { user, isAuthenticated, logout } = useAuthStore();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Close mobile menu on route changes
  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [location.pathname]);

  // Close on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setIsMobileMenuOpen(false);
      }
    };
    if (isMobileMenuOpen) {
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isMobileMenuOpen]);

  const navLinks = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/workspace', label: 'Create Speech', icon: Volume2 },
    { path: '/history', label: 'History', icon: History },
    { path: '/favorites', label: 'Favorites', icon: Star },
    { path: '/quantum', label: 'Quantum Lab', icon: Atom, highlight: true },
  ];

  const isRouteActive = (targetPath: string): boolean => {
    const current = location.pathname;
    if (targetPath === '/dashboard') {
      return current === '/dashboard' || current === '/app' || current === '/app/dashboard' || current === '/';
    }
    if (targetPath === '/workspace') {
      return current === '/workspace' || current === '/app/workspace' || current === '/app/create';
    }
    if (targetPath === '/history') {
      return current.startsWith('/history') || current.startsWith('/app/history');
    }
    if (targetPath === '/favorites') {
      return current.startsWith('/favorites') || current.startsWith('/app/favorites');
    }
    if (targetPath === '/quantum') {
      return current.startsWith('/quantum') || current.startsWith('/app/quantum');
    }
    return current.startsWith(targetPath);
  };

  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-white/10" role="banner">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo */}
        <Link to="/dashboard" className="flex items-center space-x-3 group" aria-label="Bloop Dashboard Home">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-bloop-600 via-bloop-500 to-quantum-500 flex items-center justify-center shadow-lg shadow-bloop-500/25 group-hover:scale-105 transition-transform duration-200">
            <Volume2 className="w-5 h-5 text-white" aria-hidden="true" />
          </div>
          <div>
            <div className="flex items-center space-x-1.5">
              <span className="text-xl font-bold tracking-tight text-white font-['Outfit']">Bloop</span>
              <span className="text-xs px-1.5 py-0.5 rounded-full bg-quantum-500/20 text-quantum-300 font-mono border border-quantum-500/30">
                AI + Q
              </span>
            </div>
            <p className="text-[10px] text-slate-400 -mt-0.5 tracking-wider uppercase">Speech & Quantum</p>
          </div>
        </Link>

        {/* Desktop Navigation Links */}
        <nav className="hidden md:flex items-center space-x-1" aria-label="Main Navigation">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = isRouteActive(link.path);
            return (
              <Link
                key={link.path}
                to={link.path}
                aria-current={isActive ? 'page' : undefined}
                className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all duration-150 ${
                  isActive
                    ? link.highlight
                      ? 'bg-quantum-600/20 text-quantum-300 border border-quantum-500/40 shadow-sm'
                      : 'bg-bloop-600/20 text-bloop-300 border border-bloop-500/30 shadow-sm'
                    : 'text-slate-300 hover:text-white hover:bg-white/5 border border-transparent'
                }`}
              >
                <Icon className={`w-4 h-4 ${link.highlight ? 'text-quantum-400' : 'text-bloop-400'}`} aria-hidden="true" />
                <span>{link.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Desktop Auth / Profile Actions */}
        <div className="hidden md:flex items-center space-x-3">
          {isAuthenticated ? (
            <div className="flex items-center space-x-3">
              <Link
                to="/profile"
                className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 text-sm text-slate-200 border border-white/10 transition"
              >
                <UserIcon className="w-4 h-4 text-bloop-400" />
                <span className="font-medium truncate max-w-[120px]">
                  {user?.full_name || user?.email.split('@')[0]}
                </span>
              </Link>
              <Link
                to="/preferences"
                title="Application Preferences"
                className="p-2 rounded-lg text-slate-400 hover:text-bloop-400 hover:bg-white/5 transition"
              >
                <Sliders className="w-4 h-4" />
              </Link>
              <button
                onClick={logout}
                title="Sign Out"
                className="p-2 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="flex items-center space-x-2">
              <Link
                to="/login"
                className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg text-sm font-medium text-slate-300 hover:text-white hover:bg-white/5 transition"
              >
                <LogIn className="w-4 h-4" />
                <span>Sign In</span>
              </Link>
              <Link
                to="/register"
                className="px-3.5 py-1.5 rounded-lg text-sm font-medium bg-bloop-600 hover:bg-bloop-500 text-white shadow-md shadow-bloop-600/30 transition"
              >
                Get Started
              </Link>
            </div>
          )}
        </div>

        {/* Mobile Hamburger Menu Toggle */}
        <div className="flex md:hidden items-center space-x-2">
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="p-2 rounded-lg text-slate-300 hover:text-white hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-bloop-500"
            aria-expanded={isMobileMenuOpen}
            aria-controls="mobile-navigation"
            aria-label={isMobileMenuOpen ? 'Close menu' : 'Open menu'}
          >
            {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Navigation Drawer */}
      {isMobileMenuOpen && (
        <div
          id="mobile-navigation"
          className="md:hidden border-t border-white/10 bg-slate-950/95 backdrop-blur-xl px-4 pt-3 pb-6 animate-in slide-in-from-top duration-200"
        >
          <nav className="flex flex-col space-y-1.5 mb-4" aria-label="Mobile Navigation">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = isRouteActive(link.path);
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  onClick={() => setIsMobileMenuOpen(false)}
                  aria-current={isActive ? 'page' : undefined}
                  className={`flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition ${
                    isActive
                      ? link.highlight
                        ? 'bg-quantum-600/20 text-quantum-300 border border-quantum-500/40 shadow-sm'
                        : 'bg-bloop-600/20 text-bloop-300 border border-bloop-500/30 shadow-sm'
                      : 'text-slate-300 hover:text-white hover:bg-white/5 border border-transparent'
                  }`}
                >
                  <Icon className={`w-5 h-5 ${link.highlight ? 'text-quantum-400' : 'text-bloop-400'}`} aria-hidden="true" />
                  <span>{link.label}</span>
                </Link>
              );
            })}
          </nav>

          <div className="pt-3 border-t border-white/10">
            {isAuthenticated ? (
              <div className="flex flex-col space-y-2">
                <div className="flex items-center justify-between px-3 py-2 rounded-lg bg-slate-900 border border-slate-800">
                  <div className="flex items-center space-x-2.5">
                    <UserIcon className="w-4 h-4 text-bloop-400" />
                    <span className="text-sm font-medium text-slate-200">
                      {user?.full_name || user?.email}
                    </span>
                  </div>
                  <Link
                    to="/preferences"
                    onClick={() => setIsMobileMenuOpen(false)}
                    className="p-1.5 text-slate-400 hover:text-bloop-400"
                    title="Preferences"
                  >
                    <Sliders className="w-4 h-4" />
                  </Link>
                </div>
                <div className="flex gap-2">
                  <Link
                    to="/profile"
                    onClick={() => setIsMobileMenuOpen(false)}
                    className="flex-1 text-center py-2 px-3 rounded-lg text-xs font-medium bg-slate-800 text-slate-200 hover:bg-slate-700 transition"
                  >
                    Profile Settings
                  </Link>
                  <button
                    onClick={() => {
                      logout();
                      setIsMobileMenuOpen(false);
                    }}
                    className="py-2 px-4 rounded-lg text-xs font-medium text-rose-400 bg-rose-500/10 hover:bg-rose-500/20 transition flex items-center justify-center space-x-1.5"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                    <span>Sign Out</span>
                  </button>
                </div>
              </div>
            ) : (
              <div className="flex flex-col space-y-2">
                <Link
                  to="/login"
                  onClick={() => setIsMobileMenuOpen(false)}
                  className="w-full text-center py-2 px-4 rounded-lg text-sm font-medium text-slate-200 hover:bg-white/5 transition"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  onClick={() => setIsMobileMenuOpen(false)}
                  className="w-full text-center py-2 px-4 rounded-lg text-sm font-medium bg-bloop-600 hover:bg-bloop-500 text-white transition"
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>
        </div>
      )}
    </header>
  );
};
