import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  Scale,
  Sparkles,
  BookOpen,
  Network,
  Cpu,
  ArrowRight,
  ShieldCheck,
  Award,
  Layers,
  CheckCircle2,
} from 'lucide-react';
import { api } from '../api/client';

export default function Home() {
  const navigate = useNavigate();
  const [queryInput, setQueryInput] = useState('');
  const [stats, setStats] = useState({
    total_documents: 20,
    total_chunks: 85,
    total_nodes: 143,
    total_relationships: 291,
  });

  useEffect(() => {
    // Load live platform stats
    api.getIngestionStats().then((data) => {
      if (data && data.total_documents) {
        setStats((prev) => ({
          ...prev,
          total_documents: data.total_documents,
          total_chunks: data.total_chunks || 85,
        }));
      }
    }).catch(() => {});
  }, []);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (queryInput.trim()) {
      navigate(`/search?q=${encodeURIComponent(queryInput.trim())}`);
    }
  };

  const sampleQueries = [
    'What are the mandatory conditions for anticipatory bail under CrPC 438 vs BNSS 482?',
    'Guidelines to prevent arbitrary arrest under Section 41A and Arnesh Kumar judgment',
    'Why was Section 66A of Information Technology Act struck down in Shreya Singhal?',
    'What are the principles for quashing an FIR under Section 482 CrPC in Bhajan Lal?',
    'Twin conditions for bail under Prevention of Money Laundering Act Section 45',
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-[#0a1128] to-slate-950 text-slate-100">
      {/* Hero Section */}
      <section className="relative pt-20 pb-24 overflow-hidden">
        {/* Glow Effects */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-blue-600/15 blur-[120px] pointer-events-none rounded-full" />
        <div className="absolute top-1/3 right-1/4 w-[350px] h-[250px] bg-amber-500/10 blur-[100px] pointer-events-none rounded-full" />

        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-900/30 border border-blue-500/30 text-xs font-semibold text-blue-300 mb-6 backdrop-blur-md">
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span>Hybrid Legal Intelligence for Indian Jurisprudence</span>
          </div>

          {/* Heading */}
          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight leading-[1.15] mb-6">
            Precision Indian Legal Reasoning with{' '}
            <span className="gold-gradient-text">Knowledge Graphs</span> &{' '}
            <span className="blue-gradient-text">Evidence RAG</span>
          </h1>

          <p className="text-lg sm:text-xl text-slate-300/90 max-w-3xl mx-auto mb-10 leading-relaxed font-normal">
            Discover landmark Supreme Court precedents, compare CrPC with BNSS, explore citation networks,
            and receive verifiable legal answers grounded strictly in authentic case law and bare acts.
          </p>

          {/* Main Search Bar */}
          <form onSubmit={handleSearchSubmit} className="max-w-3xl mx-auto mb-8 relative">
            <div className="glass-panel p-2 rounded-2xl border border-slate-700/80 shadow-2xl flex items-center gap-3 bg-slate-900/90 focus-within:border-blue-500 transition-colors">
              <Search className="w-6 h-6 text-slate-400 ml-3 flex-shrink-0" />
              <input
                type="text"
                value={queryInput}
                onChange={(e) => setQueryInput(e.target.value)}
                placeholder="Ask about bail, arrest guidelines, FIR quashing, IT Act, CrPC vs BNSS..."
                className="w-full bg-transparent border-none text-slate-100 placeholder-slate-400 text-base focus:outline-none py-2"
              />
              <button
                type="submit"
                className="px-6 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-sm font-semibold shadow-lg shadow-blue-500/25 flex items-center gap-2 transition-all flex-shrink-0"
              >
                Explore <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </form>

          {/* Quick Issue Chips */}
          <div className="flex items-center justify-center gap-2 flex-wrap text-xs text-slate-400 max-w-4xl mx-auto">
            <span className="font-semibold text-slate-300">Quick Topics:</span>
            {sampleQueries.map((q, idx) => (
              <button
                key={idx}
                onClick={() => navigate(`/search?q=${encodeURIComponent(q)}`)}
                className="px-3 py-1.5 rounded-lg bg-slate-900/80 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-800 hover:border-slate-700 transition-all text-left truncate max-w-xs"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Metrics & Architecture Highlights */}
      <section className="py-16 border-y border-slate-800/80 bg-slate-950/60">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
            <div className="glass-card p-6 rounded-2xl border border-slate-800/80">
              <div className="text-3xl sm:text-4xl font-extrabold text-blue-400 mb-1">
                {stats.total_documents}
              </div>
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Landmarks & Bare Acts
              </div>
            </div>

            <div className="glass-card p-6 rounded-2xl border border-slate-800/80">
              <div className="text-3xl sm:text-4xl font-extrabold text-amber-400 mb-1">
                {stats.total_chunks}
              </div>
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Indexed Semantic Chunks
              </div>
            </div>

            <div className="glass-card p-6 rounded-2xl border border-slate-800/80">
              <div className="text-3xl sm:text-4xl font-extrabold text-indigo-400 mb-1">
                {stats.total_nodes}
              </div>
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Knowledge Graph Nodes
              </div>
            </div>

            <div className="glass-card p-6 rounded-2xl border border-slate-800/80">
              <div className="text-3xl sm:text-4xl font-extrabold text-emerald-400 mb-1">
                {stats.total_relationships}
              </div>
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Citations & Relations
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 4 Pillars of NyayaAI Architecture */}
      <section className="py-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-white mb-4">
            Multi-Stage Hybrid Legal Intelligence Architecture
          </h2>
          <p className="text-slate-400 max-w-2xl mx-auto text-sm">
            Engineered specifically to solve hallucination, imprecise keyword queries, and complex citation chains in Indian Law.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="glass-card p-6 rounded-2xl border border-slate-800/80 hover:border-blue-500/50 transition-all group">
            <div className="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400 mb-4 group-hover:scale-110 transition-transform">
              <Cpu className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">1. InLegalBERT NLP</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Analyzes legal queries to extract referenced statutory sections, Acts, domains, and expands vocabulary with specialized Indian legal ontologies.
            </p>
          </div>

          <div className="glass-card p-6 rounded-2xl border border-slate-800/80 hover:border-amber-500/50 transition-all group">
            <div className="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 mb-4 group-hover:scale-110 transition-transform">
              <Layers className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">2. Convex Hybrid Search</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Fuses exact statutory BM25 Okapi lexical matching with Dense Sentence Transformers semantic embeddings using the formula: Score = α × BM25 + (1−α) × Dense.
            </p>
          </div>

          <div className="glass-card p-6 rounded-2xl border border-slate-800/80 hover:border-indigo-500/50 transition-all group">
            <div className="w-12 h-12 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mb-4 group-hover:scale-110 transition-transform">
              <Network className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">3. Neo4j Knowledge Graph</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Traverses multi-hop citation networks connecting cases, judges, overruled precedents, and statutory sections to discover hidden legal authorities.
            </p>
          </div>

          <div className="glass-card p-6 rounded-2xl border border-slate-800/80 hover:border-emerald-500/50 transition-all group">
            <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 mb-4 group-hover:scale-110 transition-transform">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">4. Grounded Dual-Mode RAG</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Generates verifiable answers tailored for Ordinary Citizens (rights & procedures) or Legal Researchers (precedents, ratio, paragraph citations).
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
