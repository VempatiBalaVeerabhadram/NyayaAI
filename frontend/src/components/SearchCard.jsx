import React, { useState } from 'react';
import {
  BookOpen,
  FileText,
  Bookmark,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Copy,
  Check,
  Award,
} from 'lucide-react';

export default function SearchCard({ item, onSelectEvidence }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopy = (e) => {
    e.stopPropagation();
    navigator.clipboard.writeText(item.text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const isCase = item.document_type === 'judgment' || item.case_name || item.case_id;
  const score = item.hybrid_score || item.score || 0;
  const scorePercent = Math.min(Math.round(score * 100), 100);

  return (
    <div className="glass-card rounded-xl p-5 border border-slate-800/80 hover:border-blue-500/40 transition-all duration-200 group relative">
      {/* Top Header */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-center gap-2 flex-wrap">
          <span
            className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-semibold ${
              isCase
                ? 'bg-blue-950/80 text-blue-300 border border-blue-800/50'
                : 'bg-emerald-950/80 text-emerald-300 border border-emerald-800/50'
            }`}
          >
            {isCase ? <BookOpen className="w-3 h-3" /> : <FileText className="w-3 h-3" />}
            {isCase ? 'Landmark Precedent' : 'Statutory Provision'}
          </span>

          {item.legal_domain && (
            <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-slate-800 text-slate-300 border border-slate-700/60">
              {item.legal_domain}
            </span>
          )}

          {item.page && (
            <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-indigo-950/60 text-indigo-300 border border-indigo-800/40">
              Page {item.page}
            </span>
          )}

          {item.paragraph_number && (
            <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-purple-950/60 text-purple-300 border border-purple-800/40">
              Para {item.paragraph_number}
            </span>
          )}
        </div>

        {/* Confidence Badge */}
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-800/80 border border-slate-700/60 text-xs font-mono">
          <span className="text-slate-400 text-[10px]">Relevance</span>
          <span
            className={`font-semibold ${
              scorePercent > 70
                ? 'text-emerald-400'
                : scorePercent > 40
                ? 'text-amber-400'
                : 'text-blue-400'
            }`}
          >
            {scorePercent}%
          </span>
        </div>
      </div>

      {/* Title */}
      <h3 className="text-base font-semibold text-slate-100 group-hover:text-blue-300 transition-colors mb-2">
        {item.case_name || item.title || item.document_id}
      </h3>

      {/* Extracted Text Snippet */}
      <div className="text-sm text-slate-300/90 leading-relaxed relative">
        <p className={isExpanded ? '' : 'line-clamp-3'}>
          {item.text}
        </p>

        {item.text.length > 220 && (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="mt-2 text-xs font-medium text-blue-400 hover:text-blue-300 inline-flex items-center gap-1"
          >
            {isExpanded ? (
              <>
                Show less <ChevronUp className="w-3 h-3" />
              </>
            ) : (
              <>
                Show full extract <ChevronDown className="w-3 h-3" />
              </>
            )}
          </button>
        )}
      </div>

      {/* Action Footer */}
      <div className="mt-4 pt-3 border-t border-slate-800/60 flex items-center justify-between text-xs text-slate-400">
        <div className="flex items-center gap-3">
          <button
            onClick={handleCopy}
            className="flex items-center gap-1 hover:text-slate-200 transition-colors"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            {copied ? 'Copied' : 'Copy Text'}
          </button>

          {onSelectEvidence && (
            <button
              onClick={() => onSelectEvidence(item)}
              className="flex items-center gap-1 text-blue-400 hover:text-blue-300 transition-colors font-medium"
            >
              <Award className="w-3.5 h-3.5" />
              Inspect Provenance
            </button>
          )}
        </div>

        {item.source_url && (
          <a
            href={item.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 hover:text-blue-400 transition-colors"
          >
            Primary Source <ExternalLink className="w-3 h-3" />
          </a>
        )}
      </div>
    </div>
  );
}
