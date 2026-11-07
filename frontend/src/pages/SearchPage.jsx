import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Search,
  SlidersHorizontal,
  UserCheck,
  Briefcase,
  Sparkles,
  BookOpen,
  FileText,
  Network,
  Cpu,
  ShieldAlert,
  Loader2,
  ChevronRight,
  ExternalLink,
  Layers,
  Award,
  Scale,
} from 'lucide-react';
import { api } from '../api/client';
import SearchCard from '../components/SearchCard';
import EvidencePanel from '../components/EvidencePanel';

export default function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialQuery = searchParams.get('q') || '';

  const [query, setQuery] = useState(initialQuery);
  const [userMode, setUserMode] = useState('user'); // 'user' or 'researcher'
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);

  // Advanced Filters
  const [showFilters, setShowFilters] = useState(false);
  const [alpha, setAlpha] = useState(0.5);
  const [depth, setDepth] = useState(1);
  const [domainFilter, setDomainFilter] = useState('');
  const [docTypeFilter, setDocTypeFilter] = useState('');

  // Selected Evidence for Modal
  const [selectedEvidence, setSelectedEvidence] = useState(null);

  const executeSearch = async (targetQuery = query) => {
    if (!targetQuery.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      const res = await api.queryLegalAI({
        query: targetQuery.trim(),
        user_mode: userMode,
        alpha: parseFloat(alpha),
        depth: parseInt(depth, 10),
        domain_filter: domainFilter || null,
        document_type_filter: docTypeFilter || null,
      });

      if (res && res.data) {
        setResponse(res.data);
      } else if (res && res.response) {
        setResponse(res);
      } else {
        throw new Error('Invalid response structure received');
      }
    } catch (err) {
      console.error('Search failed:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to complete legal query');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (initialQuery) {
      setQuery(initialQuery);
      executeSearch(initialQuery);
    }
  }, [initialQuery, userMode]);

  const handleSubmit = (e) => {
    e.preventDefault();
    setSearchParams({ q: query });
    executeSearch(query);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Top Header & Dual Mode Switcher */}
        <div className="flex flex-col md:flex-row items-center justify-between gap-4 mb-6 pb-6 border-b border-slate-800">
          <div>
            <h1 className="text-2xl font-extrabold text-white flex items-center gap-2">
              <Scale className="w-6 h-6 text-blue-400" />
              NyayaAI Legal Intelligence Search
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Multi-Stage Grounded Retrieval: InLegalBERT + Convex Hybrid + Neo4j Graph + Gemini RAG
            </p>
          </div>

          {/* Dual Mode Switch */}
          <div className="flex items-center p-1 rounded-xl bg-slate-900 border border-slate-700/80 shadow-inner">
            <button
              onClick={() => setUserMode('user')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
                userMode === 'user'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <UserCheck className="w-3.5 h-3.5" />
              Ordinary Citizen Mode
            </button>

            <button
              onClick={() => setUserMode('researcher')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
                userMode === 'researcher'
                  ? 'bg-gradient-to-r from-amber-600 to-amber-500 text-white shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Briefcase className="w-3.5 h-3.5" />
              Legal Researcher Mode
            </button>
          </div>
        </div>

        {/* Search Input Bar */}
        <form onSubmit={handleSubmit} className="mb-6">
          <div className="glass-panel p-2 rounded-2xl border border-slate-700 shadow-xl flex items-center gap-3 bg-slate-900/90 focus-within:border-blue-500 transition-colors">
            <Search className="w-5 h-5 text-slate-400 ml-3 flex-shrink-0" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={
                userMode === 'user'
                  ? 'Ask in plain English (e.g. Can police arrest me without warrant for cheating? What is anticipatory bail?)'
                  : 'Enter legal research query, section citations (e.g. Inherent powers under 482 CrPC, Twin conditions in PMLA)'
              }
              className="w-full bg-transparent border-none text-slate-100 placeholder-slate-400 text-sm focus:outline-none py-2"
            />

            <button
              type="button"
              onClick={() => setShowFilters(!showFilters)}
              className={`p-2.5 rounded-xl border text-xs font-medium flex items-center gap-1.5 transition-colors ${
                showFilters
                  ? 'bg-blue-600/20 text-blue-400 border-blue-500/40'
                  : 'bg-slate-800 text-slate-400 border-slate-700 hover:text-white'
              }`}
              title="Toggle Retrieval Hyperparameters"
            >
              <SlidersHorizontal className="w-4 h-4" />
              <span className="hidden sm:inline">Settings</span>
            </button>

            <button
              type="submit"
              disabled={isLoading}
              className="px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md shadow-blue-500/20 flex items-center gap-2 transition-all disabled:opacity-50"
            >
              {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Search'}
            </button>
          </div>
        </form>

        {/* Collapsible Retrieval Parameter Drawer */}
        {showFilters && (
          <div className="glass-card p-5 rounded-2xl border border-slate-800 mb-6 animate-fadeIn">
            <div className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-4 flex items-center gap-2">
              <Layers className="w-4 h-4 text-blue-400" />
              Retrieval Pipeline Configuration
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
              {/* Alpha Slider */}
              <div>
                <div className="flex items-center justify-between text-xs text-slate-300 mb-1">
                  <span>Hybrid Alpha (α):</span>
                  <span className="font-mono text-blue-400">{alpha}</span>
                </div>
                <input
                  type="range"
                  min="0.0"
                  max="1.0"
                  step="0.1"
                  value={alpha}
                  onChange={(e) => setAlpha(e.target.value)}
                  className="w-full accent-blue-500 cursor-pointer"
                />
                <div className="flex justify-between text-[10px] text-slate-500 mt-1">
                  <span>Dense (0.0)</span>
                  <span>Balanced (0.5)</span>
                  <span>BM25 (1.0)</span>
                </div>
              </div>

              {/* Graph Depth */}
              <div>
                <label className="block text-xs text-slate-300 mb-1.5">
                  Knowledge Graph Depth
                </label>
                <select
                  value={depth}
                  onChange={(e) => setDepth(e.target.value)}
                  className="w-full px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
                >
                  <option value={1}>Depth 1 (Direct Precedents & Sections)</option>
                  <option value={2}>Depth 2 (Multi-hop Citation Chains)</option>
                </select>
              </div>

              {/* Legal Domain Filter */}
              <div>
                <label className="block text-xs text-slate-300 mb-1.5">
                  Legal Domain
                </label>
                <select
                  value={domainFilter}
                  onChange={(e) => setDomainFilter(e.target.value)}
                  className="w-full px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
                >
                  <option value="">All Domains</option>
                  <option value="Criminal Law">Criminal Law (CrPC / BNSS / IPC / BNS)</option>
                  <option value="Cyber Law">Cyber Law (IT Act)</option>
                  <option value="Constitutional Law">Constitutional Law (Art 19/21)</option>
                </select>
              </div>

              {/* Document Type Filter */}
              <div>
                <label className="block text-xs text-slate-300 mb-1.5">
                  Document Type
                </label>
                <select
                  value={docTypeFilter}
                  onChange={(e) => setDocTypeFilter(e.target.value)}
                  className="w-full px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
                >
                  <option value="">All Types</option>
                  <option value="judgment">Landmark Supreme Court Judgments</option>
                  <option value="statute">Statutory Bare Acts & Codes</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {/* Loading Spinner */}
        {isLoading && (
          <div className="py-16 text-center">
            <Loader2 className="w-10 h-10 text-blue-500 animate-spin mx-auto mb-4" />
            <p className="text-sm font-semibold text-slate-200">
              Traversing Legal Knowledge Graph & Fusing Lexical/Semantic Embeddings...
            </p>
            <p className="text-xs text-slate-500 mt-1">
              Analyzing query through InLegalBERT & Grounding Gemini RAG in statutory citations
            </p>
          </div>
        )}

        {/* Error Alert */}
        {error && (
          <div className="p-4 rounded-xl bg-red-950/60 border border-red-800/80 text-red-300 text-xs flex items-center gap-3 mb-6">
            <ShieldAlert className="w-5 h-5 flex-shrink-0 text-red-400" />
            <div>
              <strong>Error executing search:</strong> {error}
            </div>
          </div>
        )}

        {/* Search Results Display */}
        {response && !isLoading && (
          <div className="space-y-8 animate-fadeIn">
            {/* 1. InLegalBERT Query Understanding Strip */}
            <div className="glass-card p-4 rounded-xl border border-slate-800 flex flex-wrap items-center justify-between gap-4 text-xs">
              <div className="flex items-center gap-2">
                <Cpu className="w-4 h-4 text-blue-400" />
                <span className="text-slate-400">Classified Issue:</span>
                <span className="font-semibold text-slate-200">
                  {response.primary_legal_issue || 'Indian Legal Interpretation'}
                </span>
              </div>

              {response.referenced_sections && response.referenced_sections.length > 0 && (
                <div className="flex items-center gap-1.5 flex-wrap">
                  <span className="text-slate-400">Sections Detected:</span>
                  {response.referenced_sections.map((sec, i) => (
                    <span
                      key={i}
                      className="px-2 py-0.5 rounded bg-purple-950/60 text-purple-300 border border-purple-800/40 font-mono text-[11px]"
                    >
                      {sec}
                    </span>
                  ))}
                </div>
              )}

              {response.confidence_score !== undefined && (
                <div className="flex items-center gap-1.5">
                  <span className="text-slate-400">Grounding Confidence:</span>
                  <span className="font-mono font-bold text-emerald-400">
                    {Math.round(response.confidence_score * 100)}%
                  </span>
                </div>
              )}
            </div>

            {/* 2. RAG Synthesized Answer */}
            <div
              className={`p-6 rounded-2xl border shadow-xl ${
                userMode === 'user'
                  ? 'bg-gradient-to-br from-slate-900 to-blue-950/40 border-blue-900/40'
                  : 'bg-gradient-to-br from-slate-900 to-amber-950/30 border-amber-900/40'
              }`}
            >
              <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <Sparkles
                    className={`w-5 h-5 ${
                      userMode === 'user' ? 'text-blue-400' : 'text-amber-400'
                    }`}
                  />
                  <h2 className="text-lg font-bold text-white">
                    {userMode === 'user'
                      ? 'NyayaAI Citizen Legal Explanation & Rights Guidance'
                      : 'NyayaAI Comprehensive Legal Research & Precedent Analysis'}
                  </h2>
                </div>

                <span className="px-2.5 py-1 rounded-md text-[10px] font-semibold uppercase tracking-wider bg-slate-800 text-slate-300 border border-slate-700">
                  {response.mode === 'researcher' ? 'Researcher Grounding' : 'Plain Explanation'}
                </span>
              </div>

              {/* Markdown Styled Output */}
              <div className="text-sm text-slate-200 leading-relaxed space-y-4 whitespace-pre-wrap font-sans">
                {response.response}
              </div>

              {/* Disclaimer */}
              <div className="mt-6 pt-4 border-t border-slate-800/60 text-[11px] text-slate-500 flex items-center gap-1.5">
                <ShieldAlert className="w-3.5 h-3.5 text-amber-400/80 flex-shrink-0" />
                <span>
                  All statements are grounded in Indian Supreme Court case law and bare statutory provisions. Always verify with official gazettes.
                </span>
              </div>
            </div>

            {/* 3. Discovered Precedents and Graph Connections */}
            {response.connected_precedents && response.connected_precedents.length > 0 && (
              <div className="glass-card p-5 rounded-2xl border border-slate-800">
                <div className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-3 flex items-center gap-2">
                  <Network className="w-4 h-4 text-indigo-400" />
                  Connected Precedent Citation Network
                </div>
                <div className="flex flex-wrap gap-2">
                  {response.connected_precedents.map((prec, i) => (
                    <button
                      key={i}
                      onClick={() => {
                        setQuery(prec);
                        executeSearch(prec);
                      }}
                      className="px-3 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-200 hover:text-white border border-slate-700 text-xs font-medium flex items-center gap-1.5 transition-all"
                    >
                      <BookOpen className="w-3 h-3 text-blue-400" />
                      {prec}
                      <ChevronRight className="w-3 h-3 text-slate-500" />
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* 4. Evidence Chunks Extracted */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <FileText className="w-4 h-4 text-amber-400" />
                  Primary Evidence Sources ({response.evidence_used?.length || 0})
                </h3>
                <span className="text-xs text-slate-400">
                  Exact page numbers & paragraphs from authentic records
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {response.evidence_used && response.evidence_used.map((item, idx) => (
                  <SearchCard
                    key={item.chunk_id || idx}
                    item={item}
                    onSelectEvidence={(ev) => setSelectedEvidence(ev)}
                  />
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Evidence Modal */}
        {selectedEvidence && (
          <EvidencePanel
            evidence={selectedEvidence}
            onClose={() => setSelectedEvidence(null)}
          />
        )}
      </div>
    </div>
  );
}
