import React from 'react';
import {
  FileText,
  Search,
  CheckCircle2,
  AlertCircle,
  Clock,
  ArrowRight,
  ExternalLink,
  Trash2,
  Download,
  Database,
  ShieldCheck,
  Sparkles,
} from 'lucide-react';
import { ResearchTask } from '../types';
import { api } from '../services/api';

interface DashboardViewProps {
  tasks: ResearchTask[];
  onSelectTask: (taskId: string, view: 'monitor' | 'sources' | 'findings' | 'report') => void;
  onOpenNewResearch: () => void;
  onDeleteTask: (taskId: string) => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  tasks,
  onSelectTask,
  onOpenNewResearch,
  onDeleteTask,
}) => {
  const completedTasks = tasks.filter((t) => t.status === 'completed');
  const runningTasks = tasks.filter((t) => t.status === 'running' || t.status === 'queued');
  const failedTasks = tasks.filter((t) => t.status === 'failed');

  const totalSources = tasks.reduce((acc, t) => acc + (t.sources_count || 0), 0);
  const totalClaims = tasks.reduce((acc, t) => acc + (t.claims_count || 0), 0);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
            <CheckCircle2 className="w-3 h-3 mr-1" />
            Completed
          </span>
        );
      case 'running':
      case 'queued':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-50 text-amber-700 border border-amber-200 animate-pulse">
            <Clock className="w-3 h-3 mr-1" />
            In Progress
          </span>
        );
      case 'failed':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-rose-50 text-rose-700 border border-rose-200">
            <AlertCircle className="w-3 h-3 mr-1" />
            Failed
          </span>
        );
      default:
        return <span className="text-xs text-slate-500">{status}</span>;
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Hero Welcome & Quick Launch */}
      <div className="bg-gradient-to-r from-sky-900 via-slate-900 to-indigo-950 rounded-2xl p-6 sm:p-8 text-white shadow-xl relative overflow-hidden">
        <div className="absolute right-0 top-0 bottom-0 w-1/3 bg-gradient-to-l from-sky-500/10 to-transparent pointer-events-none" />
        <div className="max-w-2xl relative z-10">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-white/10 backdrop-blur text-sky-200 text-xs font-medium mb-3">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Multi-Agent System · Real Web & Academic Synthesis</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight mb-2">
            Automate In-Depth Research with Verified Evidence
          </h1>
          <p className="text-slate-300 text-sm sm:text-base mb-6 leading-relaxed">
            Submit any research question. Autonomous agents plan sub-questions, query live web and academic databases,
            extract content with Trafilatura & PyMuPDF, verify factual claims, and compile publication-ready reports.
          </p>
          <div className="flex flex-wrap gap-3">
            <button
              onClick={onOpenNewResearch}
              className="px-5 py-2.5 rounded-xl text-sm font-semibold text-slate-900 bg-white hover:bg-slate-100 shadow transition active:scale-95 inline-flex items-center space-x-2"
            >
              <span>Start New Research</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">Total Tasks</span>
            <div className="p-2 bg-sky-50 rounded-lg text-sky-600">
              <FileText className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-slate-900 mt-2">{tasks.length}</div>
          <div className="text-xs text-slate-500 mt-1">{completedTasks.length} completed reports</div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">In Progress</span>
            <div className="p-2 bg-amber-50 rounded-lg text-amber-600">
              <Clock className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-slate-900 mt-2">{runningTasks.length}</div>
          <div className="text-xs text-slate-500 mt-1">Active multi-agent workflows</div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">Real Sources</span>
            <div className="p-2 bg-indigo-50 rounded-lg text-indigo-600">
              <Database className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-slate-900 mt-2">{totalSources}</div>
          <div className="text-xs text-slate-500 mt-1">Web, arXiv, Crossref records</div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">Verified Claims</span>
            <div className="p-2 bg-emerald-50 rounded-lg text-emerald-600">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-slate-900 mt-2">{totalClaims}</div>
          <div className="text-xs text-slate-500 mt-1">Evidence-linked facts</div>
        </div>
      </div>

      {/* Research Tasks Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
          <h2 className="text-base font-bold text-slate-900">Research History & Reports</h2>
          <span className="text-xs text-slate-500">{tasks.length} total entries</span>
        </div>

        {tasks.length === 0 ? (
          <div className="p-12 text-center">
            <FileText className="w-12 h-12 text-slate-300 mx-auto mb-3" />
            <h3 className="text-sm font-semibold text-slate-900">No research tasks yet</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1 mb-4">
              Get started by submitting a research question. The agents will handle search, extraction, and report creation.
            </p>
            <button
              onClick={onOpenNewResearch}
              className="px-4 py-2 rounded-lg text-xs font-semibold text-white bg-sky-600 hover:bg-sky-700 transition"
            >
              Start First Research
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-600">
              <thead className="bg-slate-50 text-xs font-semibold text-slate-500 uppercase tracking-wider border-b border-slate-200">
                <tr>
                  <th className="px-6 py-3">Topic / Question</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Depth</th>
                  <th className="px-4 py-3">Sources</th>
                  <th className="px-4 py-3">Findings</th>
                  <th className="px-4 py-3">Created</th>
                  <th className="px-6 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {tasks.map((task) => (
                  <tr key={task.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="px-6 py-4 font-medium text-slate-900 max-w-md">
                      <div
                        className="truncate cursor-pointer hover:text-sky-600"
                        onClick={() => onSelectTask(task.id, task.status === 'completed' ? 'report' : 'monitor')}
                      >
                        {task.topic}
                      </div>
                      {task.current_agent && task.status === 'running' && (
                        <span className="text-[11px] text-amber-600 font-mono">
                          agent: {task.current_agent} ({task.progress_percentage}%)
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-4">{getStatusBadge(task.status)}</td>
                    <td className="px-4 py-4 text-xs font-medium capitalize text-slate-600">{task.research_depth}</td>
                    <td className="px-4 py-4 text-xs">{task.sources_count}</td>
                    <td className="px-4 py-4 text-xs">{task.findings_count}</td>
                    <td className="px-4 py-4 text-xs text-slate-400">
                      {new Date(task.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-right space-x-2 whitespace-nowrap">
                      {task.status === 'completed' ? (
                        <>
                          <button
                            onClick={() => onSelectTask(task.id, 'report')}
                            className="px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-medium transition"
                          >
                            Report
                          </button>
                          <button
                            onClick={() => onSelectTask(task.id, 'sources')}
                            className="px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-medium transition"
                          >
                            Sources ({task.sources_count})
                          </button>
                          <a
                            href={api.getExportUrl(task.id, 'pdf')}
                            download
                            className="inline-flex items-center px-2 py-1 rounded bg-sky-50 text-sky-700 hover:bg-sky-100 text-xs font-medium transition"
                            title="Download PDF"
                          >
                            <Download className="w-3.5 h-3.5 mr-1" />
                            PDF
                          </a>
                        </>
                      ) : (
                        <button
                          onClick={() => onSelectTask(task.id, 'monitor')}
                          className="px-2.5 py-1 rounded bg-amber-50 hover:bg-amber-100 text-amber-700 text-xs font-medium transition"
                        >
                          Live Progress
                        </button>
                      )}
                      <button
                        onClick={() => onDeleteTask(task.id)}
                        className="p-1 rounded text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition"
                        title="Delete task"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
