import React from 'react';
import { X, BookOpen, FileText, CheckCircle2, ShieldAlert, Hash, Calendar, Scale } from 'lucide-react';

export default function EvidencePanel({ evidence, onClose }) {
  if (!evidence) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
      <div className="relative w-full max-w-2xl max-h-[85vh] overflow-y-auto glass-panel rounded-2xl p-6 border border-slate-700/80 shadow-2xl bg-slate-900/95">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-1.5 rounded-lg bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
            <Scale className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">
              Legal Evidence Provenance
            </h3>
            <p className="text-xs text-slate-400 font-mono">
              Chunk ID: {evidence.chunk_id || 'N/A'}
            </p>
          </div>
        </div>

        {/* Metadata Badges */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-6">
          <div className="p-3 rounded-xl bg-slate-800/60 border border-slate-700/50">
            <span className="text-[10px] text-slate-400 font-medium block">Document</span>
            <span className="text-xs font-bold text-slate-200 truncate block mt-0.5">
              {evidence.case_name || evidence.document_id}
            </span>
          </div>

          <div className="p-3 rounded-xl bg-slate-800/60 border border-slate-700/50">
            <span className="text-[10px] text-slate-400 font-medium block">Exact Page</span>
            <span className="text-xs font-bold text-indigo-300 block mt-0.5">
              {evidence.page ? `Page ${evidence.page}` : 'Section Text'}
            </span>
          </div>

          <div className="p-3 rounded-xl bg-slate-800/60 border border-slate-700/50">
            <span className="text-[10px] text-slate-400 font-medium block">Paragraph</span>
            <span className="text-xs font-bold text-purple-300 block mt-0.5">
              {evidence.paragraph_number ? `Para ${evidence.paragraph_number}` : 'N/A'}
            </span>
          </div>

          <div className="p-3 rounded-xl bg-slate-800/60 border border-slate-700/50">
            <span className="text-[10px] text-slate-400 font-medium block">Domain</span>
            <span className="text-xs font-bold text-amber-300 block mt-0.5">
              {evidence.legal_domain || 'General Law'}
            </span>
          </div>
        </div>

        {/* Verbatim Content */}
        <div className="mb-6">
          <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider block mb-2">
            Verbatim Legal Extract
          </label>
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-200 leading-relaxed max-h-60 overflow-y-auto font-sans">
            {evidence.text}
          </div>
        </div>

        {/* Retrieval Scoring Diagnostics */}
        <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/40 mb-4">
          <h4 className="text-xs font-semibold text-slate-300 mb-2">
            Retrieval Score Decomposition
          </h4>
          <div className="grid grid-cols-3 gap-2 text-center text-xs font-mono">
            <div className="p-2 rounded bg-slate-900/60">
              <span className="text-slate-400 text-[10px] block">BM25 Okapi</span>
              <span className="font-bold text-amber-400">
                {evidence.bm25_score !== undefined ? evidence.bm25_score.toFixed(3) : '0.000'}
              </span>
            </div>
            <div className="p-2 rounded bg-slate-900/60">
              <span className="text-slate-400 text-[10px] block">Dense Cosine</span>
              <span className="font-bold text-blue-400">
                {evidence.semantic_score !== undefined ? evidence.semantic_score.toFixed(3) : '0.000'}
              </span>
            </div>
            <div className="p-2 rounded bg-slate-900/60">
              <span className="text-slate-400 text-[10px] block">Fused Score</span>
              <span className="font-bold text-emerald-400">
                {evidence.hybrid_score !== undefined ? evidence.hybrid_score.toFixed(3) : '0.000'}
              </span>
            </div>
          </div>
        </div>

        {/* Close Button Footer */}
        <div className="flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl text-sm font-semibold bg-blue-600 hover:bg-blue-500 text-white transition-all shadow-md shadow-blue-600/20"
          >
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
}
