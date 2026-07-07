import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Sparkles, Bell, Sun, Moon, Laptop, LogOut, User as UserIcon, Shield, Menu, CheckCircle2, AlertTriangle } from 'lucide-react';
import { useAuthStore } from '../../shared/stores/useAuthStore';
import { useThemeStore } from '../../shared/stores/useThemeStore';
import { useAppStore } from '../../shared/stores/useAppStore';
import { Badge, Button, DomainSelector, CacheStatusBadge, toast } from '../../shared/components';

export const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout, simulatedRole } = useAuthStore();
  const { theme, setTheme } = useThemeStore();
  const toggleSidebar = useAppStore((s) => s.toggleSidebar);

  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [isNotifOpen, setIsNotifOpen] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);
  const notifRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(e.target as Node)) {
        setIsUserMenuOpen(false);
      }
      if (notifRef.current && !notifRef.current.contains(e.target as Node)) {
        setIsNotifOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = async () => {
    await logout();
    toast.info('Signed Out', 'You have been logged out of BusinessLens AI.');
    navigate('/login');
  };

  const cycleTheme = () => {
    if (theme === 'light') setTheme('dark');
    else if (theme === 'dark') setTheme('system');
    else setTheme('light');
  };

  const activeRoleName = simulatedRole || user?.role || 'EXECUTIVE';

  return (
    <header className="sticky top-0 z-40 w-full h-16 border-b border-border bg-card/80 backdrop-blur-md px-4 sm:px-6 flex items-center justify-between shadow-sm">
      {/* Left section: Hamburger & Logo */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => toggleSidebar()}
          className="p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted transition-colors focus:outline-none focus:ring-2 focus:ring-ring"
          aria-label="Toggle Navigation Sidebar"
        >
          <Menu className="w-5 h-5" />
        </button>

        <Link to="/" className="flex items-center gap-2.5 group">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-primary to-purple-600 flex items-center justify-center text-white shadow-md group-hover:scale-105 transition-transform">
            <Sparkles className="w-5 h-5" />
          </div>
          <div className="hidden sm:flex flex-col">
            <span className="font-extrabold text-base leading-tight tracking-tight text-foreground group-hover:text-primary transition-colors">
              BusinessLens <span className="text-primary">AI</span>
            </span>
            <span className="text-[10px] text-muted-foreground font-semibold uppercase tracking-widest">
              Enterprise v3.2
            </span>
          </div>
        </Link>
      </div>

      {/* Middle section: Domain Selector & Cache Status */}
      <div className="hidden md:flex items-center gap-4">
        <DomainSelector />
        <CacheStatusBadge
          status={{
            isCached: true,
            statusText: 'LIVE',
            cachedAt: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
            lastUpdated: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
            ttlSeconds: 3600,
          }}
        />
      </div>

      {/* Right section: Theme, Notifications, User Menu */}
      <div className="flex items-center gap-2 sm:gap-3">
        {/* Theme Toggle Button */}
        <button
          onClick={cycleTheme}
          className="p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted transition-colors focus:outline-none focus:ring-2 focus:ring-ring relative"
          title={`Current theme: ${theme}. Click to switch.`}
          aria-label="Toggle color theme"
        >
          {theme === 'light' && <Sun className="w-5 h-5 text-amber-500" />}
          {theme === 'dark' && <Moon className="w-5 h-5 text-purple-500" />}
          {theme === 'system' && <Laptop className="w-5 h-5 text-blue-500" />}
        </button>

        {/* Notifications Bell */}
        <div className="relative" ref={notifRef}>
          <button
            onClick={() => setIsNotifOpen(!isNotifOpen)}
            className="p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted transition-colors relative focus:outline-none focus:ring-2 focus:ring-ring"
            aria-label="View notifications"
          >
            <Bell className="w-5 h-5" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-destructive animate-ping" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-destructive" />
          </button>

          {isNotifOpen && (
            <div className="absolute right-0 mt-2 w-80 sm:w-96 rounded-xl border border-border bg-card shadow-2xl p-4 space-y-3 z-50 animate-in fade-in-0 zoom-in-95">
              <div className="flex items-center justify-between pb-2 border-b border-border">
                <span className="text-sm font-bold text-foreground">Platform Notifications</span>
                <Badge variant="purple" size="sm">2 New</Badge>
              </div>
              <div className="space-y-2.5 max-h-80 overflow-y-auto">
                <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-xs space-y-1">
                  <div className="flex items-center gap-1.5 font-bold text-emerald-600 dark:text-emerald-400">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Schema Scan Complete</span>
                  </div>
                  <p className="text-muted-foreground">PostgreSQL retail_analytics_db metadata extracted successfully (14 tables).</p>
                </div>
                <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/20 text-xs space-y-1">
                  <div className="flex items-center gap-1.5 font-bold text-amber-600 dark:text-amber-400">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    <span>Business Rule Triggered</span>
                  </div>
                  <p className="text-muted-foreground">Low inventory warning on Wireless Headphones (42 units remaining).</p>
                </div>
              </div>
              <Button variant="outline" size="sm" className="w-full text-xs" onClick={() => setIsNotifOpen(false)}>
                Mark All as Read
              </Button>
            </div>
          )}
        </div>

        {/* User Profile Dropdown */}
        <div className="relative" ref={userMenuRef}>
          <button
            onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
            className="flex items-center gap-2 p-1 rounded-full sm:rounded-lg sm:px-2 sm:py-1 hover:bg-muted transition-colors focus:outline-none focus:ring-2 focus:ring-ring"
          >
            <img
              src={user?.avatarUrl || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80'}
              alt="User avatar"
              className="w-8 h-8 rounded-full object-cover border border-primary/30"
            />
            <div className="hidden sm:flex flex-col text-left">
              <span className="text-xs font-bold text-foreground leading-none">{user?.name || 'Alex Rivera'}</span>
              <span className="text-[10px] text-muted-foreground mt-0.5 leading-none">{activeRoleName}</span>
            </div>
          </button>

          {isUserMenuOpen && (
            <div className="absolute right-0 mt-2 w-64 rounded-xl border border-border bg-card shadow-2xl p-2 space-y-1 z-50 animate-in fade-in-0 zoom-in-95">
              <div className="p-3 border-b border-border space-y-1">
                <p className="text-xs font-bold text-foreground">{user?.name || 'Alex Rivera'}</p>
                <p className="text-[11px] font-mono text-muted-foreground truncate">{user?.email || 'admin@businesslens.ai'}</p>
                <div className="pt-1 flex items-center gap-1.5">
                  <Badge variant="purple" size="sm">Role: {activeRoleName}</Badge>
                </div>
              </div>

              <Link
                to="/profile"
                onClick={() => setIsUserMenuOpen(false)}
                className="flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium text-foreground hover:bg-muted transition-colors"
              >
                <UserIcon className="w-4 h-4 text-primary" />
                <span>Account Profile & Settings</span>
              </Link>

              <Link
                to="/profile"
                onClick={() => setIsUserMenuOpen(false)}
                className="flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium text-foreground hover:bg-muted transition-colors"
              >
                <Shield className="w-4 h-4 text-purple-500" />
                <span>RBAC Role Simulator</span>
              </Link>

              <div className="border-t border-border pt-1">
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-semibold text-destructive hover:bg-destructive/10 transition-colors text-left"
                >
                  <LogOut className="w-4 h-4" />
                  <span>Sign Out of Platform</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
