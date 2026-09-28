import React, { useState } from 'react';
import { X, Sparkles, BookOpen, Layers, CheckSquare, ArrowRight, Loader2 } from 'lucide-react';

interface NewResearchModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: {
    topic: string;
    research_depth: string;
    max_sources: number;
    include_academic_papers: boolean;
    output_formats: string[];
  }) => Promise<void>;
}

export const NewResearchModal: React.FC<NewResearchModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
}) => {
  const [topic, setTopic] = useState('');
  const [depth, setDepth] = useState('comprehensive');
  const [maxSources, setMaxSources] = useState(15);
  const [includeAcademic, setIncludeAcademic] = useState(true);
  const [formats, setFormats] = useState<string[]>(['markdown', 'pdf', 'docx']);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const exampleTopics = [
    'Impact of Generative AI on Data Science Jobs',
    'Quantum Error Correction in Scalable Superconducting Qubits',
    'Solid-State Battery Breakthroughs in Electric Vehicles',
    'CRISPR Therapeutics & Base Editing in Clinical Medicine',
  ];

  const handleToggleFormat = (fmt: string) => {
    if (formats.includes(fmt)) {
      if (formats.length > 1) {
        setFormats(formats.filter((f) => f !== fmt));
      }
    } else {
      setFormats([...formats, fmt]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) {
      setError('Please enter a research topic or question.');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await onSubmit({
        topic: topic.trim(),
        research_depth: depth,
        max_sources: maxSources,
        include_academic_papers: includeAcademic,
        output_formats: formats,
      });
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to start research task.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-xl w-full p-6 sm:p-8 shadow-2xl border border-slate-200 relative animate-in fade-in zoom-in-95 duration-150">
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-1.5 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-sky-50 text-sky-600 flex items-center justify-center border border-sky-100">
            <BookOpen className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900 tracking-tight">Initiate Autonomous Research</h2>
            <p className="text-xs text-slate-500">Autonomous multi-agent research with verified evidence</p>
          </div>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-xs">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Topic Input */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
              Research Question or Topic
            </label>
            <textarea
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g. What is the impact of Generative AI on enterprise data science workflows?"
              rows={3}
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500 text-sm text-slate-900 placeholder-slate-400"
              required
            />

            {/* Example chips */}
            <div className="mt-2 flex flex-wrap gap-1.5 items-center">
              <span className="text-[11px] text-slate-400">Suggestions:</span>
              {exampleTopics.map((ex, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => setTopic(ex)}
                  className="text-[11px] px-2 py-0.5 rounded-md bg-slate-100 hover:bg-slate-200 text-slate-700 transition"
                >
                  {ex.length > 32 ? ex.substring(0, 32) + '...' : ex}
                </button>
              ))}
            </div>
          </div>

          {/* Depth Selection */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
              Research Depth
            </label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { id: 'quick', title: 'Quick', desc: '5-8 sources · Fast' },
                { id: 'standard', title: 'Standard', desc: '10-15 sources' },
                { id: 'comprehensive', title: 'Comprehensive', desc: 'Up to 20 sources' },
              ].map((item) => (
                <div
                  key={item.id}
                  onClick={() => {
                    setDepth(item.id);
                    if (item.id === 'quick') setMaxSources(8);
                    else if (item.id === 'standard') setMaxSources(14);
                    else setMaxSources(20);
                  }}
                  className={`p-3 rounded-xl border cursor-pointer text-center transition ${
                    depth === item.id
                      ? 'border-sky-500 bg-sky-50/50 text-sky-950 font-medium shadow-sm'
                      : 'border-slate-200 hover:border-slate-300 text-slate-600'
                  }`}
                >
                  <div className="text-xs font-bold">{item.title}</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">{item.desc}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Max Sources Slider */}
          <div>
            <div className="flex justify-between items-center text-xs font-semibold text-slate-700 mb-1">
              <span className="uppercase tracking-wider">Target Max Sources</span>
              <span className="text-sky-600 font-bold">{maxSources} sources</span>
            </div>
            <input
              type="range"
              min="5"
              max="25"
              step="1"
              value={maxSources}
              onChange={(e) => setMaxSources(Number(e.target.value))}
              className="w-full accent-sky-600"
            />
          </div>

          {/* Academic Papers Toggle */}
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 flex items-center justify-between">
            <div>
              <div className="text-xs font-semibold text-slate-900">Include Academic Indexes</div>
              <div className="text-[11px] text-slate-500">Query arXiv, Crossref, and Semantic Scholar</div>
            </div>
            <input
              type="checkbox"
              checked={includeAcademic}
              onChange={(e) => setIncludeAcademic(e.target.checked)}
              className="w-4 h-4 rounded text-sky-600 focus:ring-sky-500 border-slate-300"
            />
          </div>

          {/* Output Formats */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
              Generated Export Formats
            </label>
            <div className="flex items-center space-x-4">
              {['markdown', 'pdf', 'docx'].map((fmt) => (
                <label key={fmt} className="flex items-center space-x-2 text-xs text-slate-700 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formats.includes(fmt)}
                    onChange={() => handleToggleFormat(fmt)}
                    className="w-3.5 h-3.5 rounded text-sky-600 border-slate-300"
                  />
                  <span className="uppercase font-medium">{fmt}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Submit Button */}
          <div className="pt-2 flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2.5 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2.5 rounded-xl text-xs font-semibold text-white bg-sky-600 hover:bg-sky-700 shadow transition flex items-center space-x-2 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Launching Workflow...</span>
                </>
              ) : (
                <>
                  <span>Launch Research</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
