import React from 'react';
import { BookOpen, PlusCircle, Settings as SettingsIcon, Activity, Sparkles } from 'lucide-react';

interface NavbarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  openNewResearch: () => void;
  openSettings: () => void;
  hasActiveTask: boolean;
  activeTopic?: string;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentTab,
  setCurrentTab,
  openNewResearch,
  openSettings,
  hasActiveTask,
  activeTopic,
}) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'sources', label: 'Source Explorer' },
    { id: 'findings', label: 'Findings & Claims' },
    { id: 'report', label: 'Report & Exports' },
  ];

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Brand */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setCurrentTab('dashboard')}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-600 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-sky-500/20">
              <BookOpen className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg text-slate-900 tracking-tight">ResearchAgent</span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-sky-50 text-sky-700 border border-sky-200">
                  Autonomous Multi-Agent
                </span>
              </div>
              <p className="text-xs text-slate-500 hidden sm:block">Evidence-Verified AI Research Platform</p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => {
              const isActive = currentTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setCurrentTab(item.id)}
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-slate-100 text-sky-600 font-semibold'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  {item.label}
                </button>
              );
            })}
          </nav>

          {/* Action Buttons */}
          <div className="flex items-center space-x-3">
            {hasActiveTask && (
              <button
                onClick={() => setCurrentTab('monitor')}
                className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200 hover:bg-amber-100 transition animate-pulse"
                title={activeTopic}
              >
                <Activity className="w-3.5 h-3.5" />
                <span>Active Research</span>
              </button>
            )}

            <button
              onClick={openNewResearch}
              className="flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-semibold text-white bg-sky-600 hover:bg-sky-700 shadow-sm transition active:scale-95"
            >
              <PlusCircle className="w-4 h-4" />
              <span>New Research</span>
            </button>

            <button
              onClick={openSettings}
              className="p-2 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition"
              title="API Keys & Settings"
            >
              <SettingsIcon className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
