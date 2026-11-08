import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  BookOpen,
  Search,
  Calendar,
  Scale,
  ExternalLink,
  Sparkles,
  Loader2,
  FileText,
} from 'lucide-react';
import { api } from '../api/client';

export default function CasesPage() {
  const navigate = useNavigate();
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchFilter, setSearchFilter] = useState('');
  const [domainFilter, setDomainFilter] = useState('All');

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    setLoading(true);
    try {
      const data = await api.getDocumentsList({ document_type: 'judgment' });
      const docs = Array.isArray(data) ? data : (data?.documents || []);
      setDocuments(docs);
    } catch (err) {
      console.error('Failed to load judgments:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredDocs = documents.filter((doc) => {
    const title = (doc.case_name || doc.title || doc.document_id || '').toLowerCase();
    const docId = (doc.document_id || '').toLowerCase();
    const q = searchFilter.toLowerCase();
    const matchesSearch = title.includes(q) || docId.includes(q);
    const matchesDomain = domainFilter === 'All' || doc.legal_domain === domainFilter;
    return matchesSearch && matchesDomain;
  });

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8 pb-6 border-b border-slate-800">
          <div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              <BookOpen className="w-6 h-6 text-blue-400" />
              Landmark Supreme Court Precedents
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Curated authoritative Indian case law corpus with authentic citations (AIR/SCC/SCR), holding ratios, and statutory references
            </p>
          </div>

          <div className="flex items-center gap-3">
            <span className="px-3.5 py-1.5 rounded-xl bg-blue-950/60 border border-blue-800/40 text-xs font-semibold text-blue-300">
              {filteredDocs.length} Landmark Judgments Available
            </span>
          </div>
        </div>

        {/* Filters & Search */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="md:col-span-2 relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchFilter}
              onChange={(e) => setSearchFilter(e.target.value)}
              placeholder="Search by case name (e.g. Arnesh Kumar, Bhajan Lal, Satender Kumar Antil, K.N. Mehra)..."
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-xs text-slate-200 placeholder-slate-400 focus:outline-none focus:border-blue-500"
            />
          </div>

          <div>
            <select
              value={domainFilter}
              onChange={(e) => setDomainFilter(e.target.value)}
              className="w-full py-2.5 px-3 rounded-xl bg-slate-900 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
            >
              <option value="All">All Legal Domains</option>
              <option value="Criminal Law">Criminal Law</option>
              <option value="Cyber Law">Cyber Law</option>
              <option value="Constitutional Law">Constitutional Law</option>
            </select>
          </div>
        </div>

        {/* Loading */}
        {loading && (
          <div className="py-20 text-center">
            <Loader2 className="w-8 h-8 text-blue-500 animate-spin mx-auto mb-3" />
            <p className="text-xs text-slate-400">Loading Supreme Court Precedents from Corpus...</p>
          </div>
        )}

        {/* Cases Grid */}
        {!loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {filteredDocs.map((doc) => {
              const caseTitle = doc.case_name || doc.title || doc.document_id;
              return (
                <div
                  key={doc.document_id}
                  className="bg-slate-900 rounded-2xl p-5 border border-slate-800 hover:border-blue-500/50 transition-all flex flex-col justify-between group shadow-lg"
                >
                  <div>
                    <div className="flex items-center justify-between gap-2 mb-3">
                      <span className="px-2.5 py-0.5 rounded-md text-[11px] font-semibold bg-blue-950/80 text-blue-300 border border-blue-800/40">
                        {doc.legal_domain || 'Criminal Law'}
                      </span>
                      <span className="text-[11px] font-mono text-slate-400 flex items-center gap-1">
                        <Calendar className="w-3 h-3 text-slate-500" />
                        {doc.judgment_date || doc.decision_date || 'Supreme Court'}
                      </span>
                    </div>

                    <h3 className="text-sm font-bold text-slate-100 group-hover:text-blue-300 transition-colors mb-2 line-clamp-2">
                      {caseTitle}
                    </h3>

                    {doc.court && (
                      <div className="flex items-center gap-1.5 text-xs text-slate-400 mb-2">
                        <Scale className="w-3.5 h-3.5 text-blue-400 flex-shrink-0" />
                        <span className="truncate">{doc.court}</span>
                      </div>
                    )}

                    <div className="flex items-center gap-3 text-[11px] text-slate-400 mb-3">
                      <span>{doc.total_chunks || 1} chunks</span>
                      <span>•</span>
                      <span>{doc.sections_count || 1} statutory provisions</span>
                    </div>
                  </div>

                  <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between">
                    <button
                      type="button"
                      onClick={() =>
                        navigate(`/?q=${encodeURIComponent(caseTitle)}`)
                      }
                      className="text-xs font-semibold text-blue-400 hover:text-blue-300 flex items-center gap-1 transition-colors cursor-pointer"
                    >
                      <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                      Analyze Precedent
                    </button>

                    {doc.source_url ? (
                      <a
                        href={doc.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-slate-400 hover:text-slate-200 flex items-center gap-1 transition-colors"
                      >
                        Record <ExternalLink className="w-3 h-3" />
                      </a>
                    ) : (
                      <span className="text-[10px] text-slate-500 font-mono">SC Record</span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
