import React, { useEffect, useState } from 'react';
import {
  Compass,
  Search,
  FileDown,
  Scale,
  Brain,
  ShieldCheck,
  FileText,
  PackageCheck,
  CheckCircle2,
  Clock,
  AlertCircle,
  ArrowRight,
} from 'lucide-react';
import { ExecutionLog } from '../types';
import { api } from '../services/api';

interface ExecutionMonitorProps {
  taskId: string;
  topic: string;
  onViewReport: () => void;
  onViewSources: () => void;
}

const PHASES = [
  { id: 'planner', name: 'Planning', icon: Compass, pct: 15 },
  { id: 'search_agent', name: 'Searching', icon: Search, pct: 35 },
  { id: 'extractor', name: 'Extracting', icon: FileDown, pct: 50 },
  { id: 'source_evaluator', name: 'Evaluating', icon: Scale, pct: 60 },
  { id: 'analyst', name: 'Analyzing', icon: Brain, pct: 75 },
  { id: 'fact_checker', name: 'Fact Checking', icon: ShieldCheck, pct: 85 },
  { id: 'report_writer', name: 'Writing', icon: FileText, pct: 92 },
  { id: 'export_generator', name: 'Exporting', icon: PackageCheck, pct: 100 },
];

export const ExecutionMonitor: React.FC<ExecutionMonitorProps> = ({
  taskId,
  topic,
  onViewReport,
  onViewSources,
}) => {
  const [progress, setProgress] = useState(10);
  const [status, setStatus] = useState('running');
  const [currentAgent, setCurrentAgent] = useState('planner');
  const [logs, setLogs] = useState<ExecutionLog[]>([]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Poll status and listen to SSE
  useEffect(() => {
    let active = true;

    const fetchStatus = async () => {
      try {
        const res = await api.getResearchStatus(taskId);
        if (!active) return;
        setProgress(res.progress || 10);
        setStatus(res.status);
        if (res.current_agent) setCurrentAgent(res.current_agent);
        if (res.message) setErrorMessage(res.message);
        if (res.logs && res.logs.length > 0) setLogs(res.logs);
      } catch (e) {
        // quiet poll
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 2500);

    // SSE connection
    const eventSource = new EventSource(`/api/research/${taskId}/events`);
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.progress !== undefined) setProgress(data.progress);
        if (data.status) setStatus(data.status);
        if (data.agent) setCurrentAgent(data.agent);
        if (data.message) {
          setLogs((prev) => [
            ...prev,
            {
              agent: data.agent,
              status: data.status,
              time: 0,
              message: data.message,
              created_at: data.timestamp,
            },
          ]);
        }
      } catch (err) {
        // parse error ignored
      }
    };

    return () => {
      active = false;
      clearInterval(interval);
      eventSource.close();
    };
  }, [taskId]);

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header Info */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-sky-700 bg-sky-50 px-2.5 py-1 rounded-md mb-2">
              <span className="w-2 h-2 rounded-full bg-sky-500 animate-ping" />
              <span>Multi-Agent Live Execution</span>
            </div>
            <h1 className="text-xl sm:text-2xl font-bold text-slate-900">{topic}</h1>
            <p className="text-xs text-slate-500 font-mono mt-1">Task ID: {taskId}</p>
          </div>

          <div className="flex items-center space-x-3">
            {status === 'completed' ? (
              <button
                onClick={onViewReport}
                className="px-5 py-2.5 rounded-xl text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-700 shadow-sm transition flex items-center space-x-2"
              >
                <span>View Full Report</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            ) : (
              <button
                onClick={onViewSources}
                className="px-4 py-2 rounded-xl text-xs font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 transition"
              >
                View Collected Sources
              </button>
            )}
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-6">
          <div className="flex justify-between text-xs font-semibold text-slate-700 mb-2">
            <span className="capitalize">
              {status === 'completed'
                ? 'Workflow Completed'
                : `Active Phase: ${currentAgent.replace('_', ' ')}`}
            </span>
            <span className="text-sky-600 font-bold">{progress}%</span>
          </div>
          <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden">
            <div
              className={`h-full transition-all duration-500 ease-out ${
                status === 'completed'
                  ? 'bg-emerald-500'
                  : status === 'failed'
                  ? 'bg-rose-500'
                  : 'bg-sky-500'
              }`}
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </div>

      {/* Stepper Pipeline */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <h2 className="text-sm font-bold text-slate-900 mb-4">Autonomous Agent Pipeline</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
          {PHASES.map((phase, idx) => {
            const Icon = phase.icon;
            const isDone = progress >= phase.pct;
            const isCurrent = currentAgent === phase.id || (!isDone && progress >= (PHASES[idx - 1]?.pct || 0));

            return (
              <div
                key={phase.id}
                className={`p-3 rounded-xl border flex flex-col items-center text-center transition ${
                  isDone
                    ? 'border-emerald-200 bg-emerald-50/40 text-emerald-900'
                    : isCurrent
                    ? 'border-sky-500 bg-sky-50 text-sky-950 font-semibold ring-2 ring-sky-200'
                    : 'border-slate-100 bg-slate-50/50 text-slate-400'
                }`}
              >
                <div
                  className={`w-8 h-8 rounded-lg flex items-center justify-center mb-1.5 ${
                    isDone
                      ? 'bg-emerald-100 text-emerald-700'
                      : isCurrent
                      ? 'bg-sky-100 text-sky-700 animate-pulse'
                      : 'bg-slate-100 text-slate-400'
                  }`}
                >
                  {isDone ? <CheckCircle2 className="w-4 h-4" /> : <Icon className="w-4 h-4" />}
                </div>
                <div className="text-[11px] font-medium leading-tight">{phase.name}</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Error Display */}
      {errorMessage && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-xs flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Real-Time Agent Activity Log */}
      <div className="bg-slate-900 text-slate-200 rounded-2xl p-5 shadow-lg border border-slate-800 font-mono text-xs">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-3">
          <div className="flex items-center space-x-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" />
            <span className="font-semibold text-slate-300">Live Agent Stream</span>
          </div>
          <span className="text-[10px] text-slate-500">{logs.length} events logged</span>
        </div>

        <div className="space-y-2 max-h-72 overflow-y-auto pr-2">
          {logs.length === 0 ? (
            <div className="text-slate-500 py-4 text-center font-sans">
              Awaiting agent events...
            </div>
          ) : (
            logs.map((log, i) => (
              <div key={i} className="flex items-start space-x-2 leading-relaxed">
                <span className="text-slate-500 text-[10px] shrink-0">
                  {log.created_at ? new Date(log.created_at).toLocaleTimeString() : 'now'}
                </span>
                <span className="text-sky-400 font-semibold shrink-0">
                  [{log.agent.toUpperCase()}]
                </span>
                <span className="text-slate-300">{log.message}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
