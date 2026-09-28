import React, { useState } from 'react';
import {
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  XCircle,
  ExternalLink,
  Brain,
  ShieldCheck,
  ChevronRight,
} from 'lucide-react';
import { ResearchFinding, ClaimItem } from '../types';

interface FindingsClaimsViewProps {
  findings: ResearchFinding[];
  claims: ClaimItem[];
  topic: string;
}

export const FindingsClaimsView: React.FC<FindingsClaimsViewProps> = ({
  findings,
  claims,
  topic,
}) => {
  const [activeTab, setActiveTab] = useState<'claims' | 'findings'>('claims');

  const getClaimBadge = (status: string) => {
    switch (status) {
      case 'supported':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
            <CheckCircle2 className="w-3.5 h-3.5 mr-1 text-emerald-600" />
            Supported
          </span>
        );
      case 'partially_supported':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
            <AlertCircle className="w-3.5 h-3.5 mr-1 text-amber-600" />
            Partially Supported
          </span>
        );
      case 'contradicted':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200">
            <XCircle className="w-3.5 h-3.5 mr-1 text-rose-600" />
            Contradicted
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 border border-slate-200">
            <HelpCircle className="w-3.5 h-3.5 mr-1 text-slate-500" />
            Insufficient Evidence
          </span>
        );
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Findings & Evidence Verification</h1>
          <p className="text-xs text-slate-500 mt-1">
            Grounding analysis for: <span className="font-semibold text-slate-700">{topic || 'Research'}</span>
          </p>
        </div>

        {/* Tab switch */}
        <div className="flex bg-slate-100 p-1 rounded-xl">
          <button
            onClick={() => setActiveTab('claims')}
            className={`flex items-center space-x-1.5 px-4 py-2 rounded-lg text-xs font-semibold transition ${
              activeTab === 'claims'
                ? 'bg-white text-slate-900 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>Verified Claims ({claims.length})</span>
          </button>
          <button
            onClick={() => setActiveTab('findings')}
            className={`flex items-center space-x-1.5 px-4 py-2 rounded-lg text-xs font-semibold transition ${
              activeTab === 'findings'
                ? 'bg-white text-slate-900 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Brain className="w-4 h-4 text-sky-600" />
            <span>Question Findings ({findings.length})</span>
          </button>
        </div>
      </div>

      {activeTab === 'claims' ? (
        <div className="space-y-4">
          {claims.length === 0 ? (
            <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center text-slate-500 text-sm">
              No claims verified for this research task yet.
            </div>
          ) : (
            claims.map((claim) => (
              <div
                key={claim.id}
                className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm hover:border-slate-300 transition space-y-3"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center space-x-2">
                    {getClaimBadge(claim.verification_status)}
                    <span className="text-xs text-slate-400 font-mono">
                      confidence: {Math.round((claim.confidence_score || 0.9) * 100)}%
                    </span>
                  </div>
                  {claim.source_url && (
                    <a
                      href={claim.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center text-xs text-sky-600 hover:text-sky-700 font-medium"
                    >
                      <span>{claim.source_title || 'Source Citation'}</span>
                      <ExternalLink className="w-3 h-3 ml-1" />
                    </a>
                  )}
                </div>

                <div className="text-sm font-semibold text-slate-900">
                  {claim.claim_text}
                </div>

                {claim.supporting_passage && (
                  <div className="bg-slate-50 p-3 rounded-xl border border-slate-100 text-xs text-slate-600 leading-relaxed">
                    <span className="font-semibold text-slate-700 block mb-1">Supporting Evidence Passage:</span>
                    "{claim.supporting_passage}"
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {findings.length === 0 ? (
            <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center text-slate-500 text-sm">
              No synthesized findings yet.
            </div>
          ) : (
            findings.map((finding) => (
              <div
                key={finding.id}
                className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3"
              >
                <div className="flex items-center space-x-2 text-xs font-bold text-sky-700 uppercase tracking-wider">
                  <ChevronRight className="w-4 h-4 text-sky-500" />
                  <span>Sub-Question</span>
                </div>
                <h3 className="text-base font-bold text-slate-900">{finding.question}</h3>
                <div className="p-4 bg-sky-50/40 border border-sky-100 rounded-xl text-sm text-slate-800 leading-relaxed">
                  {finding.finding}
                </div>
                {finding.source_ids && finding.source_ids.length > 0 && (
                  <div className="text-xs text-slate-500 flex items-center space-x-1 font-mono">
                    <span>Grounded in source IDs:</span>
                    <span className="text-slate-700">{finding.source_ids.join(', ')}</span>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};
