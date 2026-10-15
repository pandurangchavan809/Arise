import React, { useState, useEffect } from 'react';
import { NavLink, Outlet, Link, useLocation } from 'react-router-dom';
import { 
  Brain, 
  MessageSquare, 
  Database, 
  ShieldCheck, 
  FileCode2, 
  ChevronRight, 
  ExternalLink,
  Menu,
  X,
  Activity,
  ArrowLeft,
  Sparkles
} from 'lucide-react';
import { api } from '../api/client';

export default function AppLayout() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [healthStatus, setHealthStatus] = useState({ status: 'checking', version: '1.2.0' });
  const location = useLocation();

  useEffect(() => {
    let mounted = true;
    api.getHealth().then((h) => {
      if (mounted && h) setHealthStatus(h);
    });
    return () => { mounted = false; };
  }, []);

  const navItems = [
    {
      name: 'Agent Assistant',
      path: '/app/assistant',
      icon: MessageSquare,
      badge: 'Live Demo',
      desc: 'Interactive chat & voice demo',
    },
    {
      name: 'Memory Browser',
      path: '/app/memory',
      icon: Database,
      badge: null,
      desc: 'Inspect 4 cognitive memory tiers',
    },
    {
      name: 'Quality Inspector',
      path: '/app/quality',
      icon: ShieldCheck,
      badge: 'MQM Engine',
      desc: 'Recall evaluation & trust scoring',
    },
    {
      name: 'Developer Docs',
      path: '/app/developer',
      icon: FileCode2,
      badge: 'API & SDK',
      desc: 'Python SDK & REST API reference',
    },
  ];

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden font-sans">
      
      {/* Sidebar for Desktop */}
      <aside className="hidden md:flex flex-col w-64 bg-slate-950 border-r border-slate-800/80 shrink-0">
        
        {/* Branding */}
        <div className="p-4 border-b border-slate-800/80 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/30 group-hover:scale-105 transition-transform">
              <Brain className="w-4 h-4" />
            </div>
            <div>
              <span className="font-bold text-sm text-white tracking-tight block">Adaptive Memory</span>
              <span className="text-[10px] text-blue-400 font-mono">Runtime v{healthStatus.version || '1.2.0'}</span>
            </div>
          </Link>
          <Link 
            to="/" 
            className="text-slate-500 hover:text-slate-300 p-1 rounded hover:bg-slate-900 transition-colors"
            title="Return to Landing Page"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
        </div>

        {/* Runtime Status Pill */}
        <div className="px-4 py-3 bg-slate-900/60 border-b border-slate-800/60 flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-slate-300 font-medium">Memory Engine</span>
          </div>
          <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
            Active
          </span>
        </div>

        {/* Navigation list */}
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          <div className="px-3 py-1.5 text-[10px] font-mono uppercase tracking-wider text-slate-500 font-semibold">
            Product Consoles
          </div>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname.startsWith(item.path);

            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-blue-600/15 text-blue-400 border border-blue-500/30 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/80'
                  }`
                }
              >
                <div className="flex items-center gap-2.5">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-blue-400' : 'text-slate-400'}`} />
                  <span>{item.name}</span>
                </div>
                {item.badge && (
                  <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 border border-slate-700/60">
                    {item.badge}
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Bottom Banner */}
        <div className="p-4 border-t border-slate-800/80 bg-slate-900/30">
          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs">
            <div className="flex items-center gap-1.5 text-blue-400 font-semibold mb-1">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Core Principle</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-snug">
              Memory Runtime IS the product. Chat and voice are demo interfaces.
            </p>
          </div>
        </div>

      </aside>

      {/* Main Workspace Area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        
        {/* Top Navbar Header */}
        <header className="h-16 border-b border-slate-800/80 bg-slate-950/70 backdrop-blur-md px-4 sm:px-6 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-lg bg-slate-900 text-slate-400 hover:text-white"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-white">Adaptive Memory Runtime</span>
              <span className="text-slate-600 hidden sm:inline">•</span>
              <span className="text-xs text-slate-400 hidden sm:inline">Plug-and-Play Memory Intelligence</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 text-xs font-mono text-slate-400 bg-slate-900/80 px-3 py-1.5 rounded-lg border border-slate-800">
              <Activity className="w-3.5 h-3.5 text-emerald-400" />
              <span>Edge Budget: Active</span>
            </div>
            <Link
              to="/app/developer"
              className="inline-flex items-center gap-1 text-xs font-medium text-slate-300 hover:text-blue-400 bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-800 transition-colors"
            >
              <span>API Reference</span>
              <ExternalLink className="w-3 h-3" />
            </Link>
          </div>
        </header>

        {/* Mobile dropdown menu */}
        {mobileMenuOpen && (
          <div className="md:hidden border-b border-slate-800 bg-slate-950 p-4 space-y-2 z-30">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={() => setMobileMenuOpen(false)}
                className="flex items-center justify-between p-2.5 rounded-lg text-sm text-slate-300 hover:bg-slate-900"
              >
                <div className="flex items-center gap-2">
                  <item.icon className="w-4 h-4 text-blue-400" />
                  <span>{item.name}</span>
                </div>
                {item.badge && (
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                    {item.badge}
                  </span>
                )}
              </NavLink>
            ))}
          </div>
        )}

        {/* Content Outlet */}
        <main className="flex-1 overflow-y-auto bg-slate-950">
          <Outlet />
        </main>
      </div>

    </div>
  );
}
