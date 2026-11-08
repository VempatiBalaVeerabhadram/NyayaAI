import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Search,
  Scale,
  Sparkles,
  Calendar,
  Globe,
  Loader2,
  BookOpen,
  CheckCircle2,
  AlertCircle,
  FileText,
  ChevronDown,
  ChevronUp,
  Download,
  ExternalLink,
  Layers,
  Award,
} from 'lucide-react';
import { api } from '../api/client';

export default function Home() {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialQuery = searchParams.get('q') || '';

  const [query, setQuery] = useState(initialQuery);
  const [incidentDate, setIncidentDate] = useState('2024-08-15');
  const [language, setLanguage] = useState('auto');
  const [mode, setMode] = useState('researcher'); // 'user' or 'researcher'
  
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [openPassages, setOpenPassages] = useState({ 0: true }); // First passage open by default
  const [showEnglish, setShowEnglish] = useState(false);

  // Check if date is post-BNS transition (1 July 2024)
  const isBNS = new Date(incidentDate) >= new Date('2024-07-01');

  const sampleQueries = [
    { label: 'Anticipatory Bail Grounds', text: 'What are the mandatory conditions and principles governing anticipatory bail under Section 438?' },
    { label: 'Theft Elements & Punishment', text: 'What are the essential ingredients of theft under Indian Penal Code and what is the punishment?' },
    { label: 'Cheating vs Criminal Breach of Trust', text: 'When does an offence of cheating under Section 420 IPC also constitute criminal breach of trust?' },
    { label: 'Arrest Guidelines (Arnesh Kumar)', text: 'What guidelines did the Supreme Court lay down in Arnesh Kumar regarding arrest for offences punishable up to 7 years?' },
    { label: 'Telugu (తెలుగు) Query', text: 'దొంగతనం నేరం యొక్క ముఖ్యమైన అంశాలు మరియు బెయిల్ నిబంధనలు ఏమిటి?' },
    { label: 'Hindi (हिन्दी) Query', text: 'अग्रिम जमानत के लिए अदालत की क्या शर्तें हैं और गिरफ्तारी के नियम क्या हैं?' },
  ];

  // Auto-run if query param is passed from Precedents or Bare Acts
  useEffect(() => {
    if (initialQuery && initialQuery.trim()) {
      setQuery(initialQuery);
      handleSearch(initialQuery);
    }
  }, [initialQuery]);

  const handleSearch = async (targetQuery) => {
    const q = (targetQuery !== undefined ? targetQuery : query).trim();
    if (!q) return;

    setIsLoading(true);
    setError(null);
    setResponse(null);
    setOpenPassages({ 0: true, 1: true }); // Open top 2 passages by default

    try {
      const res = await api.queryLegalAI({
        query: q,
        mode: mode,
        top_k: 5,
        alpha: 0.5,
      });

      if (res && res.data) {
        setResponse(res.data);
      } else {
        throw new Error('No legal analysis received from AI service');
      }
    } catch (err) {
      console.error('Query failed:', err);
      setError(
        err.response?.data?.detail ||
        err.message ||
        'Failed to connect to NyayaAI service. Ensure AI backend is running on port 8000.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const togglePassage = (idx) => {
    setOpenPassages((prev) => ({
      ...prev,
      [idx]: !prev[idx],
    }));
  };

  const toggleAllPassages = (expandAll) => {
    if (!response?.evidence_chunks) return;
    const newState = {};
    response.evidence_chunks.forEach((_, idx) => {
      newState[idx] = expandAll;
    });
    setOpenPassages(newState);
  };

  const handleExport = () => {
    if (!response?.answer) return;
    const blob = new Blob([response.answer], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `nyaya_legal_analysis_${new Date().toISOString().slice(0, 10)}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto">
        
        {/* Clean Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-xs font-semibold text-blue-400 mb-4">
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span>AI Legal Intelligence Grounded in Indian Law</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-2">
            Ask Any Indian Legal Question
          </h1>
          <p className="text-sm sm:text-base text-slate-400 max-w-2xl mx-auto">
            Get instant answers grounded in 146 Supreme Court judgments, the complete Indian Penal Code (IPC 1860), and the new Bharatiya Nyaya Sanhita (BNS 2023).
          </p>
        </div>

        {/* Input Card */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 sm:p-6 shadow-2xl mb-8">
          
          {/* Main Query Textarea */}
          <div className="mb-4">
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              Your Legal Question (English, Telugu, or Hindi):
            </label>
            <textarea
              rows={3}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g. Can police arrest without warrant for theft? What are the requirements for anticipatory bail?"
              className="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-blue-500 transition-colors resize-none"
            />
          </div>

          {/* Controls: Date of Incident, Language, Mode */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-5">
            
            {/* Incident Date */}
            <div>
              <label className="block text-[11px] font-medium text-slate-400 mb-1 flex items-center gap-1">
                <Calendar className="w-3 h-3 text-blue-400" />
                Date of Incident / Offence:
              </label>
              <input
                type="date"
                value={incidentDate}
                onChange={(e) => setIncidentDate(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
              />
              <div className="mt-1">
                {isBNS ? (
                  <span className="text-[10px] text-emerald-400 font-semibold">⚡ BNS 2023 In-Force (Post-July 2024)</span>
                ) : (
                  <span className="text-[10px] text-blue-400 font-semibold">🏛️ IPC 1860 Applicable (Pre-July 2024)</span>
                )}
              </div>
            </div>

            {/* Language */}
            <div>
              <label className="block text-[11px] font-medium text-slate-400 mb-1 flex items-center gap-1">
                <Globe className="w-3 h-3 text-amber-400" />
                Language:
              </label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
              >
                <option value="auto">🌐 Auto-detect (EN / TE / HI)</option>
                <option value="en">English</option>
                <option value="te">Telugu (తెలుగు)</option>
                <option value="hi">Hindi (हिन्दी)</option>
              </select>
              <div className="mt-1 text-[10px] text-slate-500">61 Legal terms shielded before translation</div>
            </div>

            {/* Explanation Depth */}
            <div>
              <label className="block text-[11px] font-medium text-slate-400 mb-1 flex items-center gap-1">
                <FileText className="w-3 h-3 text-indigo-400" />
                Response Detail:
              </label>
              <div className="grid grid-cols-2 gap-1.5 p-1 bg-slate-950 border border-slate-800 rounded-lg">
                <button
                  type="button"
                  onClick={() => setMode('user')}
                  className={`py-1 text-[11px] font-medium rounded-md transition-colors cursor-pointer ${
                    mode === 'user' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  Simple
                </button>
                <button
                  type="button"
                  onClick={() => setMode('researcher')}
                  className={`py-1 text-[11px] font-medium rounded-md transition-colors cursor-pointer ${
                    mode === 'researcher' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  Detailed Brief
                </button>
              </div>
              <div className="mt-1 text-[10px] text-slate-500">{mode === 'researcher' ? 'Full legal ratios, sections, & evidence' : 'Direct summary'}</div>
            </div>

          </div>

          {/* Action Button */}
          <button
            type="button"
            onClick={() => handleSearch()}
            disabled={isLoading || !query.trim()}
            className="w-full py-3.5 px-4 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-semibold text-sm shadow-lg shadow-blue-600/25 flex items-center justify-center gap-2 transition-all cursor-pointer"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Searching 1,078 Chunks & Precedents...</span>
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                <span>Get Legal Answer & Evidence</span>
              </>
            )}
          </button>

          {/* Quick-Pick Sample Chips */}
          <div className="mt-5 pt-4 border-t border-slate-800/80">
            <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Or Click A Landmark Scenario To Analyze:
            </div>
            <div className="flex flex-wrap gap-2">
              {sampleQueries.map((sample, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => {
                    setQuery(sample.text);
                    handleSearch(sample.text);
                  }}
                  className="px-3 py-1.5 rounded-lg bg-slate-950 hover:bg-slate-800 border border-slate-800 text-xs text-slate-300 hover:text-white transition-colors text-left cursor-pointer"
                >
                  {sample.label}
                </button>
              ))}
            </div>
          </div>

        </div>

        {/* Error Notification */}
        {error && (
          <div className="p-4 rounded-xl bg-red-950/50 border border-red-800 text-red-200 text-sm flex items-start gap-3 mb-8">
            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <div className="font-semibold">Unable to process query</div>
              <div className="text-xs text-red-300 mt-0.5">{error}</div>
            </div>
          </div>
        )}

        {/* Result Card */}
        {response && (
          <div className="space-y-8 mb-10">
            
            {/* 1. Grounded Analysis Card */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl">
              
              {/* Result Header & Status */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-5 border-b border-slate-800 mb-6">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-blue-400 uppercase tracking-wider">
                      {response.legal_domain || 'Criminal Law'}
                    </span>
                    <span className="text-slate-600">•</span>
                    <span className="text-xs text-slate-300 font-medium">
                      {response.legal_issue || 'Judicial Analysis'}
                    </span>
                  </div>
                  <h2 className="text-lg font-bold text-white mt-1">
                    Legal Analysis & Precedent Findings
                  </h2>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={handleExport}
                    className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium flex items-center gap-1.5 transition-colors cursor-pointer"
                    title="Export analysis as Markdown"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Export Brief</span>
                  </button>
                  <div className="px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>100% Grounded</span>
                  </div>
                </div>
              </div>

              {/* Applicable Sections & Precedents Pills */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-6">
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                  <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                    Governing Statutory Acts & Sections:
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {response.applicable_acts?.map((act, i) => (
                      <span key={i} className="px-2.5 py-1 rounded-md bg-blue-900/40 border border-blue-500/30 text-blue-300 text-xs font-medium">
                        {act}
                      </span>
                    ))}
                    {response.applicable_sections?.filter(Boolean).map((sec, i) => (
                      <span key={i} className="px-2.5 py-1 rounded-md bg-indigo-900/40 border border-indigo-500/30 text-indigo-300 text-xs font-medium">
                        {sec}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                  <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                    Cited Landmark Supreme Court Judgments:
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {response.relevant_judgments && response.relevant_judgments.length > 0 ? (
                      response.relevant_judgments.map((caseName, i) => (
                        <span key={i} className="px-2.5 py-1 rounded-md bg-amber-900/30 border border-amber-500/30 text-amber-300 text-xs font-medium">
                          🏛️ {caseName}
                        </span>
                      ))
                    ) : (
                      <span className="text-xs text-slate-500">Statutory text reference</span>
                    )}
                  </div>
                </div>
              </div>

              {/* Language Notice & Toggle for Multilingual Queries */}
              {response.answer_english && (
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 p-3 rounded-xl bg-blue-950/40 border border-blue-800/40">
                  <div className="flex items-center gap-2 text-xs text-blue-300">
                    <Globe className="w-4 h-4 text-amber-400 flex-shrink-0" />
                    <span>
                      Answered in <strong>{response.detected_language === 'te' ? 'Telugu (తెలుగు)' : response.detected_language === 'hi' ? 'Hindi (हिन्दी)' : 'Regional Language'}</strong> (Statutory provisions & case citations preserved)
                    </span>
                  </div>
                  <button
                    type="button"
                    onClick={() => setShowEnglish(!showEnglish)}
                    className="px-3 py-1 rounded-lg bg-blue-600/30 hover:bg-blue-600/50 text-blue-200 text-xs font-semibold transition-colors self-start cursor-pointer"
                  >
                    {showEnglish ? 'Show Regional Language Answer' : 'Show Original English Legal Brief'}
                  </button>
                </div>
              )}

              {/* Formatted Legal Answer */}
              <div className="text-slate-200 text-sm sm:text-base leading-relaxed bg-slate-950/80 p-5 rounded-xl border border-slate-800 whitespace-pre-wrap font-sans">
                {showEnglish && response.answer_english ? response.answer_english : response.answer}
              </div>

            </div>

            {/* 2. Primary Evidence Sources Section (Prominent, Always Readable) */}
            {response.evidence_chunks && response.evidence_chunks.length > 0 && (
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl">
                
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-800 mb-5">
                  <div>
                    <h3 className="text-base font-bold text-white flex items-center gap-2">
                      <BookOpen className="w-5 h-5 text-blue-400" />
                      Primary Evidence Sources & Verified Court Passages
                    </h3>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Exact judicial ratios and statutory text extracted from official Supreme Court records ({response.evidence_chunks.length} chunks retrieved)
                    </p>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => toggleAllPassages(true)}
                      className="px-2.5 py-1 rounded-md bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 hover:text-white transition-colors cursor-pointer"
                    >
                      Expand All
                    </button>
                    <button
                      type="button"
                      onClick={() => toggleAllPassages(false)}
                      className="px-2.5 py-1 rounded-md bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 hover:text-white transition-colors cursor-pointer"
                    >
                      Collapse All
                    </button>
                  </div>
                </div>

                <div className="space-y-4">
                  {response.evidence_chunks.map((chunk, idx) => {
                    const isOpen = openPassages[idx] !== false; // Default true if not explicitly false
                    return (
                      <div
                        key={idx}
                        className="border border-slate-800 rounded-xl bg-slate-950 overflow-hidden shadow-sm hover:border-blue-500/40 transition-colors"
                      >
                        {/* Passage Header */}
                        <div
                          onClick={() => togglePassage(idx)}
                          className="p-4 flex items-center justify-between cursor-pointer hover:bg-slate-900/60 transition-colors"
                        >
                          <div className="flex items-center gap-3">
                            <span className="w-6 h-6 rounded-full bg-blue-600/20 border border-blue-500/40 text-blue-400 text-xs font-bold flex items-center justify-center flex-shrink-0">
                              #{idx + 1}
                            </span>
                            <div>
                              <div className="text-sm font-bold text-white flex items-center gap-2">
                                <span>{chunk.case_name || chunk.document_id}</span>
                                {chunk.section && (
                                  <span className="px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800 text-[11px] font-mono">
                                    {chunk.section}
                                  </span>
                                )}
                              </div>
                              <div className="text-[11px] text-slate-400 mt-0.5 flex flex-wrap items-center gap-2">
                                <span>Page {chunk.page}, Para {chunk.paragraph_number}</span>
                                <span>•</span>
                                <span className="text-slate-500 font-mono">
                                  Hybrid Score: {(chunk.hybrid_score || 0).toFixed(4)} (BM25: {(chunk.bm25_score || 0).toFixed(4)}, SBERT: {(chunk.semantic_score || 0).toFixed(4)})
                                </span>
                              </div>
                            </div>
                          </div>

                          <button
                            type="button"
                            className="p-1 rounded text-slate-400 hover:text-white"
                          >
                            {isOpen ? (
                              <ChevronUp className="w-4 h-4 text-slate-400" />
                            ) : (
                              <ChevronDown className="w-4 h-4 text-slate-400" />
                            )}
                          </button>
                        </div>

                        {/* Passage Text Body */}
                        {isOpen && (
                          <div className="px-4 pb-4 pt-1 border-t border-slate-900 bg-slate-900/30">
                            <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800/80 text-xs text-slate-200 font-mono leading-relaxed whitespace-pre-wrap">
                              {chunk.text}
                            </div>
                            {chunk.source_url && (
                              <div className="mt-2 text-[11px] text-slate-500 flex items-center gap-1">
                                <span>Source:</span>
                                <a
                                  href={chunk.source_url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-blue-400 hover:underline flex items-center gap-0.5"
                                >
                                  {chunk.source_url} <ExternalLink className="w-3 h-3" />
                                </a>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>

              </div>
            )}

          </div>
        )}

        {/* Minimal Legal Disclaimer */}
        <div className="text-center text-[11px] text-slate-500 py-4 border-t border-slate-900">
          ⚖️ <span className="font-semibold text-slate-400">Legal Decision-Support Disclaimer:</span> NyayaAI answers are synthesized strictly from official Indian statutory gazettes and Supreme Court records. This tool provides legal intelligence and research support, not formal legal advice under the Advocates Act, 1961.
        </div>

      </div>
    </div>
  );
}
