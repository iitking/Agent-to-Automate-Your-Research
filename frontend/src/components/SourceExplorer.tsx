import React, { useState } from 'react';
import {
  ExternalLink,
  BookOpen,
  Globe,
  FileText,
  Search,
  CheckCircle,
  AlertTriangle,
  FileCheck,
} from 'lucide-react';
import { ResearchSource } from '../types';

interface SourceExplorerProps {
  sources: ResearchSource[];
  topic: string;
}

export const SourceExplorer: React.FC<SourceExplorerProps> = ({ sources, topic }) => {
  const [filterType, setFilterType] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const filteredSources = sources.filter((s) => {
    if (filterType !== 'all') {
      if (filterType === 'academic' && s.source_type !== 'academic') return false;
      if (filterType === 'web' && s.source_type !== 'web') return false;
      if (filterType === 'extracted' && s.extraction_status !== 'success') return false;
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchTitle = (s.title || '').toLowerCase().includes(q);
      const matchSnippet = (s.snippet || '').toLowerCase().includes(q);
      const matchDomain = (s.domain || '').toLowerCase().includes(q);
      const matchAuthor = (s.author || '').toLowerCase().includes(q);
      return matchTitle || matchSnippet || matchDomain || matchAuthor;
    }
    return true;
  });

  const getProviderBadge = (provider: string) => {
    switch (provider) {
      case 'arxiv':
        return <span className="px-2 py-0.5 rounded bg-red-50 text-red-700 border border-red-200 text-[10px] font-bold">arXiv</span>;
      case 'crossref':
        return <span className="px-2 py-0.5 rounded bg-amber-50 text-amber-700 border border-amber-200 text-[10px] font-bold">Crossref</span>;
      case 'semantic_scholar':
        return <span className="px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200 text-[10px] font-bold">Semantic Scholar</span>;
      case 'tavily':
        return <span className="px-2 py-0.5 rounded bg-purple-50 text-purple-700 border border-purple-200 text-[10px] font-bold">Tavily</span>;
      case 'brave':
        return <span className="px-2 py-0.5 rounded bg-orange-50 text-orange-700 border border-orange-200 text-[10px] font-bold">Brave</span>;
      default:
        return <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 text-[10px] font-bold">{provider}</span>;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'success':
        return (
          <span className="inline-flex items-center text-xs text-emerald-600 font-medium">
            <CheckCircle className="w-3.5 h-3.5 mr-1" />
            Full Article Extracted
          </span>
        );
      case 'snippet_only':
        return (
          <span className="inline-flex items-center text-xs text-amber-600 font-medium">
            <FileCheck className="w-3.5 h-3.5 mr-1" />
            Abstract / Snippet Grounded
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center text-xs text-slate-400">
            <AlertTriangle className="w-3.5 h-3.5 mr-1" />
            {status}
          </span>
        );
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Top Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Source Explorer</h1>
          <p className="text-xs text-slate-500 mt-1">
            Real retrieved web pages and academic records for: <span className="font-semibold text-slate-700">{topic || 'All Topics'}</span>
          </p>
        </div>

        {/* Filter buttons */}
        <div className="flex flex-wrap gap-2">
          {['all', 'academic', 'web', 'extracted'].map((ft) => (
            <button
              key={ft}
              onClick={() => setFilterType(ft)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold capitalize transition ${
                filterType === ft
                  ? 'bg-sky-600 text-white shadow-sm'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {ft}
            </button>
          ))}
        </div>
      </div>

      {/* Search Input */}
      <div className="relative">
        <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Filter sources by title, author, domain, or snippet keyword..."
          className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500"
        />
      </div>

      {/* Sources List */}
      {filteredSources.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center">
          <Globe className="w-10 h-10 text-slate-300 mx-auto mb-2" />
          <p className="text-sm font-medium text-slate-600">No sources found matching this filter.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredSources.map((source) => (
            <div
              key={source.id}
              className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm hover:border-slate-300 transition flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <div className="flex items-center space-x-2">
                    {getProviderBadge(source.provider)}
                    <span className="text-[11px] text-slate-400 font-mono truncate max-w-[140px]">
                      {source.domain || 'web'}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-[11px] px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-700 font-semibold border border-emerald-100">
                      Rel: {Math.round((source.relevance_score || 0) * 100)}%
                    </span>
                    <span className="text-[11px] px-2 py-0.5 rounded-md bg-sky-50 text-sky-700 font-semibold border border-sky-100">
                      Cred: {Math.round((source.credibility_score || 0) * 100)}%
                    </span>
                  </div>
                </div>

                <a
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="font-bold text-slate-900 text-sm hover:text-sky-600 transition flex items-start group"
                >
                  <span className="line-clamp-2">{source.title}</span>
                  <ExternalLink className="w-3.5 h-3.5 ml-1 text-slate-400 group-hover:text-sky-600 shrink-0 mt-0.5" />
                </a>

                {source.author && (
                  <p className="text-xs text-slate-500 mt-1">
                    Author: <span className="font-medium text-slate-700">{source.author}</span>
                    {source.published_at && ` · Published: ${source.published_at}`}
                  </p>
                )}

                {source.snippet && (
                  <p className="text-xs text-slate-600 mt-2.5 line-clamp-3 leading-relaxed bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                    "{source.snippet}"
                  </p>
                )}

                {source.evaluation_notes && (
                  <p className="text-[11px] text-slate-500 italic mt-2">
                    Note: {source.evaluation_notes}
                  </p>
                )}
              </div>

              <div className="pt-4 mt-4 border-t border-slate-100 flex items-center justify-between">
                <div>{getStatusBadge(source.extraction_status)}</div>
                {source.content_length > 0 && (
                  <span className="text-[11px] text-slate-400 font-mono">
                    {source.content_length.toLocaleString()} chars
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
