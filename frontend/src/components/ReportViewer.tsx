import React, { useState } from 'react';
import {
  Download,
  Copy,
  Check,
  FileText,
  FileCode,
  BookOpen,
  Share2,
} from 'lucide-react';
import { ResearchReport } from '../types';
import { api } from '../services/api';

interface ReportViewerProps {
  report: ResearchReport | null;
  topic: string;
  taskId: string;
}

export const ReportViewer: React.FC<ReportViewerProps> = ({
  report,
  topic,
  taskId,
}) => {
  const [copied, setCopied] = useState(false);

  if (!report) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <FileText className="w-12 h-12 text-slate-300 mx-auto mb-3" />
        <h2 className="text-lg font-bold text-slate-900">Report Not Generated Yet</h2>
        <p className="text-xs text-slate-500 mt-1">
          The autonomous multi-agent pipeline is either still processing or hasn't finished writing the final report.
        </p>
      </div>
    );
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(report.markdown_content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Basic clean Markdown renderer for smooth presentation
  const renderMarkdown = (content: string) => {
    const lines = content.split('\n');
    const elements: React.ReactNode[] = [];
    let inCode = false;
    let codeBuffer: string[] = [];

    lines.forEach((line, index) => {
      const stripped = line.trim();

      if (stripped.startsWith('```')) {
        if (inCode) {
          elements.push(
            <pre key={`code-${index}`} className="p-4 bg-slate-900 text-slate-200 rounded-xl font-mono text-xs overflow-x-auto my-3">
              {codeBuffer.join('\n')}
            </pre>
          );
          codeBuffer = [];
          inCode = false;
        } else {
          inCode = true;
        }
        return;
      }

      if (inCode) {
        codeBuffer.push(line);
        return;
      }

      if (!stripped) {
        elements.push(<div key={`empty-${index}`} className="h-3" />);
        return;
      }

      if (stripped.startsWith('# ')) {
        elements.push(
          <h1 key={index} className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight mt-6 mb-3 pb-2 border-b border-slate-200">
            {stripped.slice(2)}
          </h1>
        );
      } else if (stripped.startsWith('## ')) {
        elements.push(
          <h2 key={index} className="text-lg sm:text-xl font-bold text-slate-900 mt-6 mb-2 pb-1 border-b border-slate-100 flex items-center">
            <span className="w-1.5 h-4 bg-sky-600 rounded-full mr-2" />
            {stripped.slice(3)}
          </h2>
        );
      } else if (stripped.startsWith('### ')) {
        elements.push(
          <h3 key={index} className="text-base font-bold text-slate-800 mt-4 mb-1">
            {stripped.slice(4)}
          </h3>
        );
      } else if (stripped.startsWith('> ')) {
        elements.push(
          <blockquote key={index} className="border-l-4 border-sky-500 pl-4 py-1 italic text-slate-700 bg-sky-50/40 rounded-r-lg my-2 text-sm">
            {stripped.slice(2)}
          </blockquote>
        );
      } else if (stripped.startsWith('- ') || stripped.startsWith('* ')) {
        elements.push(
          <li key={index} className="text-sm text-slate-700 ml-5 list-disc my-1 leading-relaxed">
            {stripped.slice(2)}
          </li>
        );
      } else if (/^\d+\.\s+/.test(stripped)) {
        elements.push(
          <li key={index} className="text-sm text-slate-700 ml-5 list-decimal my-1 leading-relaxed">
            {stripped.replace(/^\d+\.\s+/, '')}
          </li>
        );
      } else {
        elements.push(
          <p key={index} className="text-sm text-slate-700 leading-relaxed my-2">
            {stripped}
          </p>
        );
      }
    });

    return elements;
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Action Bar / Export Center */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded uppercase tracking-wider">
            Canonical Report Ready
          </span>
          <h1 className="text-xl font-bold text-slate-900 mt-1">{topic}</h1>
          <div className="flex items-center space-x-3 text-xs text-slate-500 mt-1">
            <span>{report.word_count.toLocaleString()} words</span>
            <span>•</span>
            <span>{report.references_count} verified citations</span>
            <span>•</span>
            <span>Generated {new Date(report.created_at).toLocaleDateString()}</span>
          </div>
        </div>

        {/* Download Buttons */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={handleCopy}
            className="px-3 py-2 rounded-xl text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 transition flex items-center space-x-1.5"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? 'Copied' : 'Copy'}</span>
          </button>

          <a
            href={api.getExportUrl(taskId, 'pdf')}
            download
            className="px-3.5 py-2 rounded-xl text-xs font-semibold text-white bg-sky-600 hover:bg-sky-700 shadow-sm transition flex items-center space-x-1.5"
          >
            <Download className="w-3.5 h-3.5" />
            <span>PDF</span>
          </a>

          <a
            href={api.getExportUrl(taskId, 'docx')}
            download
            className="px-3.5 py-2 rounded-xl text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 transition flex items-center space-x-1.5"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Word (.docx)</span>
          </a>

          <a
            href={api.getExportUrl(taskId, 'markdown')}
            download
            className="px-3 py-2 rounded-xl text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 transition flex items-center space-x-1.5"
          >
            <FileCode className="w-3.5 h-3.5" />
            <span>Markdown</span>
          </a>
        </div>
      </div>

      {/* Main Document Body */}
      <div className="bg-white p-8 sm:p-12 rounded-2xl border border-slate-200 shadow-sm prose prose-slate max-w-none">
        {renderMarkdown(report.markdown_content)}
      </div>
    </div>
  );
};
