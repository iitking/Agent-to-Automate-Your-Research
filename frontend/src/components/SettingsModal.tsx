import React, { useEffect, useState } from 'react';
import { X, Key, CheckCircle2, AlertCircle, Save, Database, Server } from 'lucide-react';
import { ConfigStatus } from '../types';
import { api } from '../services/api';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose }) => {
  const [config, setConfig] = useState<ConfigStatus | null>(null);
  const [geminiKey, setGeminiKey] = useState('');
  const [openaiKey, setOpenaiKey] = useState('');
  const [tavilyKey, setTavilyKey] = useState('');
  const [braveKey, setBraveKey] = useState('');
  const [provider, setProvider] = useState('gemini');
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    if (isOpen) {
      api.getConfig().then((cfg) => {
        setConfig(cfg);
        setProvider(cfg.llm_provider || 'gemini');
      }).catch(() => {});
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMsg(null);
    try {
      await api.updateConfig({
        gemini_api_key: geminiKey || undefined,
        openai_api_key: openaiKey || undefined,
        tavily_api_key: tavilyKey || undefined,
        brave_api_key: braveKey || undefined,
        llm_provider: provider,
      });
      setMsg({ type: 'success', text: 'API keys updated successfully!' });
      const updated = await api.getConfig();
      setConfig(updated);
      setGeminiKey('');
      setOpenaiKey('');
      setTavilyKey('');
      setBraveKey('');
    } catch (err: any) {
      setMsg({ type: 'error', text: err.message || 'Failed to update settings.' });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-lg w-full p-6 sm:p-8 shadow-2xl border border-slate-200 relative animate-in fade-in zoom-in-95 duration-150">
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-1.5 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-slate-100 text-slate-700 flex items-center justify-center">
            <Key className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900 tracking-tight">API Keys & Provider Settings</h2>
            <p className="text-xs text-slate-500">Configure real integration credentials</p>
          </div>
        </div>

        {msg && (
          <div
            className={`mb-4 p-3 rounded-lg text-xs flex items-center space-x-2 ${
              msg.type === 'success'
                ? 'bg-emerald-50 border border-emerald-200 text-emerald-800'
                : 'bg-rose-50 border border-rose-200 text-rose-800'
            }`}
          >
            {msg.type === 'success' ? <CheckCircle2 className="w-4 h-4 shrink-0" /> : <AlertCircle className="w-4 h-4 shrink-0" />}
            <span>{msg.text}</span>
          </div>
        )}

        {/* Current status badges */}
        {config && (
          <div className="mb-6 p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
            <div className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">Live Provider Status</div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="flex items-center justify-between p-2 bg-white rounded-lg border border-slate-100">
                <span className="text-slate-600">Gemini LLM:</span>
                <span className={config.gemini_key_configured ? 'text-emerald-600 font-bold' : 'text-amber-600 font-medium'}>
                  {config.gemini_key_configured ? 'Active' : 'Missing'}
                </span>
              </div>
              <div className="flex items-center justify-between p-2 bg-white rounded-lg border border-slate-100">
                <span className="text-slate-600">Tavily Search:</span>
                <span className={config.tavily_key_configured ? 'text-emerald-600 font-bold' : 'text-amber-600 font-medium'}>
                  {config.tavily_key_configured ? 'Active' : 'Live Public Web'}
                </span>
              </div>
              <div className="flex items-center justify-between p-2 bg-white rounded-lg border border-slate-100">
                <span className="text-slate-600">arXiv & Crossref:</span>
                <span className="text-emerald-600 font-bold">Live Public</span>
              </div>
              <div className="flex items-center justify-between p-2 bg-white rounded-lg border border-slate-100">
                <span className="text-slate-600">Database:</span>
                <span className="text-emerald-600 font-bold uppercase">{config.database_url}</span>
              </div>
            </div>
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
              Active LLM Provider
            </label>
            <select
              value={provider}
              onChange={(e) => setProvider(e.target.value)}
              className="w-full px-3 py-2 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500"
            >
              <option value="gemini">Google Gemini (Recommended)</option>
              <option value="openai">OpenAI (GPT-4o)</option>
              <option value="ollama">Local Ollama</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
              Gemini API Key
            </label>
            <input
              type="password"
              value={geminiKey}
              onChange={(e) => setGeminiKey(e.target.value)}
              placeholder="Paste new GEMINI_API_KEY to update"
              className="w-full px-3 py-2 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500 font-mono"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
              Tavily API Key (Optional)
            </label>
            <input
              type="password"
              value={tavilyKey}
              onChange={(e) => setTavilyKey(e.target.value)}
              placeholder="Paste new TAVILY_API_KEY (or use default live search)"
              className="w-full px-3 py-2 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500 font-mono"
            />
          </div>

          <div className="pt-2 flex justify-end space-x-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100 transition"
            >
              Close
            </button>
            <button
              type="submit"
              disabled={saving}
              className="px-5 py-2 rounded-xl text-xs font-semibold text-white bg-sky-600 hover:bg-sky-700 shadow transition flex items-center space-x-1.5 disabled:opacity-50"
            >
              <Save className="w-3.5 h-3.5" />
              <span>{saving ? 'Saving...' : 'Save Settings'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
