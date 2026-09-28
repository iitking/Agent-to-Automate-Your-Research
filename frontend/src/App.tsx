import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { DashboardView } from './components/DashboardView';
import { NewResearchModal } from './components/NewResearchModal';
import { ExecutionMonitor } from './components/ExecutionMonitor';
import { SourceExplorer } from './components/SourceExplorer';
import { FindingsClaimsView } from './components/FindingsClaimsView';
import { ReportViewer } from './components/ReportViewer';
import { SettingsModal } from './components/SettingsModal';
import { ResearchTask, ResearchSource, ResearchFinding, ClaimItem, ResearchReport } from './types';
import { api } from './services/api';

export function App() {
  const [currentTab, setCurrentTab] = useState<string>('dashboard');
  const [tasks, setTasks] = useState<ResearchTask[]>([]);
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
  const [activeTopic, setActiveTopic] = useState<string>('');

  // Loaded child data for active task
  const [sources, setSources] = useState<ResearchSource[]>([]);
  const [findings, setFindings] = useState<ResearchFinding[]>([]);
  const [claims, setClaims] = useState<ClaimItem[]>([]);
  const [report, setReport] = useState<ResearchReport | null>(null);

  // Modals
  const [isNewModalOpen, setIsNewModalOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  // Refresh tasks
  const refreshTasks = async () => {
    try {
      const data = await api.listResearch();
      setTasks(data);
      if (!activeTaskId && data.length > 0) {
        setActiveTaskId(data[0].id);
        setActiveTopic(data[0].topic);
      }
    } catch (e) {
      // quiet poll
    }
  };

  useEffect(() => {
    refreshTasks();
    const interval = setInterval(refreshTasks, 4000);
    return () => clearInterval(interval);
  }, [activeTaskId]);

  // Load task sub-data when activeTaskId changes
  useEffect(() => {
    if (!activeTaskId) return;

    api.getResearchSources(activeTaskId).then(setSources).catch(() => setSources([]));
    api.getResearchFindings(activeTaskId).then(setFindings).catch(() => setFindings([]));
    api.getResearchClaims(activeTaskId).then(setClaims).catch(() => setClaims([]));
    api.getResearchReport(activeTaskId).then(setReport).catch(() => setReport(null));
  }, [activeTaskId, currentTab]);

  const handleSelectTask = (
    taskId: string,
    view: 'monitor' | 'sources' | 'findings' | 'report'
  ) => {
    setActiveTaskId(taskId);
    const found = tasks.find((t) => t.id === taskId);
    if (found) setActiveTopic(found.topic);
    setCurrentTab(view);
  };

  const handleCreateResearch = async (data: {
    topic: string;
    research_depth: string;
    max_sources: number;
    include_academic_papers: boolean;
    output_formats: string[];
  }) => {
    const res = await api.createResearch(data);
    setActiveTaskId(res.research_id);
    setActiveTopic(data.topic);
    setCurrentTab('monitor');
    await refreshTasks();
  };

  const handleDeleteTask = async (taskId: string) => {
    if (window.confirm('Are you sure you want to delete this research task?')) {
      await api.deleteResearch(taskId);
      if (activeTaskId === taskId) {
        setActiveTaskId(null);
        setActiveTopic('');
      }
      await refreshTasks();
    }
  };

  const hasActiveTask = tasks.some((t) => t.status === 'running' || t.status === 'queued');

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900">
      <Navbar
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        openNewResearch={() => setIsNewModalOpen(true)}
        openSettings={() => setIsSettingsOpen(true)}
        hasActiveTask={hasActiveTask}
        activeTopic={activeTopic}
      />

      <main className="flex-1 pb-16">
        {currentTab === 'dashboard' && (
          <DashboardView
            tasks={tasks}
            onSelectTask={handleSelectTask}
            onOpenNewResearch={() => setIsNewModalOpen(true)}
            onDeleteTask={handleDeleteTask}
          />
        )}

        {currentTab === 'monitor' && activeTaskId && (
          <ExecutionMonitor
            taskId={activeTaskId}
            topic={activeTopic}
            onViewReport={() => setCurrentTab('report')}
            onViewSources={() => setCurrentTab('sources')}
          />
        )}

        {currentTab === 'sources' && (
          <SourceExplorer
            sources={sources}
            topic={activeTopic}
          />
        )}

        {currentTab === 'findings' && (
          <FindingsClaimsView
            findings={findings}
            claims={claims}
            topic={activeTopic}
          />
        )}

        {currentTab === 'report' && (
          <ReportViewer
            report={report}
            topic={activeTopic}
            taskId={activeTaskId || ''}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-2">
          <div>
            <span className="font-semibold text-slate-700">ResearchAgent</span> — Autonomous Multi-Agent AI Research Automation Platform
          </div>
          <div className="flex items-center space-x-4">
            <span>Real Integrations Only</span>
            <span>•</span>
            <span>No Mock Data</span>
            <span>•</span>
            <span>MIT License</span>
          </div>
        </div>
      </footer>

      {/* Modals */}
      <NewResearchModal
        isOpen={isNewModalOpen}
        onClose={() => setIsNewModalOpen(false)}
        onSubmit={handleCreateResearch}
      />

      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
      />
    </div>
  );
}
