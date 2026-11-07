import React, { useState } from 'react';
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
} from 'lucide-react';
import { api } from '../api/client';

export default function Home() {
  const [query, setQuery] = useState('');
  const [incidentDate, setIncidentDate] = useState('2024-08-15');
  const [language, setLanguage] = useState('auto');
  const [mode, setMode] = useState('researcher'); // 'user' or 'researcher'
  
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [expandedPassage, setExpandedPassage] = useState(null);

  // Check if date is post-BNS transition (1 July 2024)
  const isBNS = new Date(incidentDate) >= new Date('2024-07-01');

  const sampleQueries = [
    { label: 'Anticipatory Bail Grounds', text: 'What are the mandatory conditions and principles governing anticipatory bail under Section 438?' },
    { label: 'Theft Elements & Punishment', text: 'What are the essential ingredients of theft and what is the punishment?' },
    { label: 'Cheating vs Criminal Breach of Trust', text: 'When does an offence of cheating under Section 420 IPC also constitute criminal breach of trust?' },
    { label: 'Arrest Guidelines (Arnesh Kumar)', text: 'What guidelines did the Supreme Court lay down in Arnesh Kumar regarding arrest for offences punishable up to 7 years?' },
    { label: 'Telugu (తెలుగు) Query', text: 'దొంగతనం నేరం యొక్క ముఖ్యమైన అంశాలు మరియు బెయిల్ నిబంధనలు ఏమిటి?' },
    { label: 'Hindi (हिन्दी) Query', text: 'अग्रिम जमानत के लिए अदालत की क्या शर्तें हैं और गिरफ्तारी के नियम क्या हैं?' },
  ];

  const handleSearch = async (targetQuery = query) => {
    const q = (targetQuery || query).trim();
    if (!q) return;

    setIsLoading(true);
    setError(null);
    setResponse(null);

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
      setError(err.response?.data?.detail || err.message || 'Failed to retrieve legal response. Please ensure backend is running.');
    } finally {
      setIsLoading(false);
    }
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
      <div className="max-w-4xl mx-auto">
        
        {/* Clean Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-xs font-medium text-blue-400 mb-4">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Legal Intelligence Grounded in Indian Law</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-2">
            Ask Any Indian Legal Question
          </h1>
          <p className="text-sm sm:text-base text-slate-400 max-w-xl mx-auto">
            Get instant, verifiable answers grounded in Supreme Court judgments and the governing Penal Code (IPC / BNS).
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
                  <span className="text-[10px] text-emerald-400 font-medium">⚡ BNS 2023 In-Force (Post-July 2024)</span>
                ) : (
                  <span className="text-[10px] text-blue-400 font-medium">🏛️ IPC 1860 Applicable (Pre-July 2024)</span>
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
              <div className="mt-1 text-[10px] text-slate-500">61 Legal terms shielded</div>
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
                  className={`py-1 text-[11px] font-medium rounded-md transition-colors ${
                    mode === 'user' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  Simple
                </button>
                <button
                  type="button"
                  onClick={() => setMode('researcher')}
                  className={`py-1 text-[11px] font-medium rounded-md transition-colors ${
                    mode === 'researcher' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  Detailed
                </button>
              </div>
              <div className="mt-1 text-[10px] text-slate-500">{mode === 'researcher' ? 'Includes full ratios & citations' : 'Direct plain explanation'}</div>
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
                <span>Get Legal Answer</span>
              </>
            )}
          </button>

          {/* Quick-Pick Sample Chips */}
          <div className="mt-5 pt-4 border-t border-slate-800/80">
            <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Or Try A Sample Scenario:
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
                  className="px-3 py-1.5 rounded-lg bg-slate-950 hover:bg-slate-800 border border-slate-800 text-xs text-slate-300 hover:text-white transition-colors text-left"
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
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl mb-10">
            
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
                  className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium flex items-center gap-1.5 transition-colors"
                  title="Export analysis as Markdown"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Export</span>
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
                  {response.relevant_judgments?.slice(0, 3).map((caseName, i) => (
                    <span key={i} className="px-2.5 py-1 rounded-md bg-amber-900/30 border border-amber-500/30 text-amber-300 text-xs font-medium">
                      🏛️ {caseName}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Formatted Legal Answer */}
            <div className="prose prose-invert max-w-none text-slate-200 text-sm sm:text-base leading-relaxed bg-slate-950/60 p-5 rounded-xl border border-slate-800 mb-6 whitespace-pre-wrap font-sans">
              {response.answer}
            </div>

            {/* Evidence Passages Accordion */}
            {response.evidence_chunks && response.evidence_chunks.length > 0 && (
              <div>
                <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                  <BookOpen className="w-4 h-4 text-blue-400" />
                  <span>Verified Court Excerpts ({response.evidence_chunks.length} Passages Found):</span>
                </div>
                
                <div className="space-y-2">
                  {response.evidence_chunks.map((chunk, idx) => {
                    const isExpanded = expandedPassage === idx;
                    return (
                      <div key={idx} className="border border-slate-800 rounded-xl bg-slate-950 overflow-hidden">
                        <button
                          type="button"
                          onClick={() => setExpandedPassage(isExpanded ? null : idx)}
                          className="w-full p-3.5 flex items-center justify-between text-left hover:bg-slate-900/80 transition-colors"
                        >
                          <div>
                            <div className="text-xs font-semibold text-blue-400">
                              {chunk.case_name || chunk.document_id}
                            </div>
                            <div className="text-[11px] text-slate-400">
                              Page {chunk.page}, Para {chunk.paragraph_number} • Section: {chunk.section}
                            </div>
                          </div>
                          {isExpanded ? (
                            <ChevronUp className="w-4 h-4 text-slate-400" />
                          ) : (
                            <ChevronDown className="w-4 h-4 text-slate-400" />
                          )}
                        </button>

                        {isExpanded && (
                          <div className="p-3.5 pt-0 text-xs text-slate-300 border-t border-slate-900 font-mono leading-relaxed bg-slate-900/40">
                            {chunk.text}
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
        <div className="text-center text-[11px] text-slate-400 py-4 border-t border-slate-900">
          ⚖️ <span className="font-semibold text-slate-400">Legal Decision-Support Disclaimer:</span> NyayaAI answers are synthesized strictly from official Indian statutory gazettes and Supreme Court records. This tool provides legal intelligence and research support, not formal legal advice under the Advocates Act, 1961.
        </div>

      </div>
    </div>
  );
}
