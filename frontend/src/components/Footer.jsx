import React from 'react';
import { Scale, ShieldAlert, ExternalLink, Cpu } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="border-t border-slate-800/80 bg-slate-950/90 text-slate-400 py-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <div className="md:col-span-2">
            <div className="flex items-center gap-2.5 mb-3">
              <div className="w-7 h-7 rounded-lg bg-blue-600 flex items-center justify-center">
                <Scale className="w-4 h-4 text-white" />
              </div>
              <span className="text-lg font-bold text-white">
                Nyaya<span className="text-blue-400">AI</span>
              </span>
            </div>
            <p className="text-sm text-slate-400 leading-relaxed max-w-md">
              A Hybrid Legal Intelligence Platform for Indian Statutory Law and Supreme Court Jurisprudence.
              Combines InLegalBERT query understanding, BM25 + Dense Hybrid Retrieval, Neo4j Knowledge Graphs,
              and Evidence-Grounded Generative AI.
            </p>
          </div>

          <div>
            <h4 className="text-xs font-semibold text-slate-200 uppercase tracking-wider mb-3">
              Core Technologies
            </h4>
            <ul className="space-y-2 text-xs">
              <li className="flex items-center gap-1.5 hover:text-slate-300">
                <Cpu className="w-3.5 h-3.5 text-blue-400" /> InLegalBERT Transformer
              </li>
              <li className="flex items-center gap-1.5 hover:text-slate-300">
                <Cpu className="w-3.5 h-3.5 text-amber-400" /> BM25 Okapi + Sentence Transformers
              </li>
              <li className="flex items-center gap-1.5 hover:text-slate-300">
                <Cpu className="w-3.5 h-3.5 text-indigo-400" /> Neo4j Knowledge Graph Engine
              </li>
              <li className="flex items-center gap-1.5 hover:text-slate-300">
                <Cpu className="w-3.5 h-3.5 text-emerald-400" /> Google Gemini RAG Architecture
              </li>
            </ul>
          </div>

          <div>
            <h4 className="text-xs font-semibold text-slate-200 uppercase tracking-wider mb-3">
              Statutory Coverage
            </h4>
            <ul className="space-y-2 text-xs">
              <li>CrPC 1973 & BNSS 2023</li>
              <li>IPC 1860 & BNS 2023</li>
              <li>Information Technology Act 2000</li>
              <li>Supreme Court Landmark Judgments</li>
            </ul>
          </div>
        </div>

        {/* Academic / Legal Disclaimer Banner */}
        <div className="pt-6 border-t border-slate-800/60 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-amber-500/80 flex-shrink-0" />
            <span>
              <strong>Academic & Research Disclaimer:</strong> NyayaAI is an AI-assisted legal exploration system. It is not a substitute for qualified professional legal advice.
            </span>
          </div>
          <div>
            &copy; {new Date().getFullYear()} NyayaAI Platform. All rights reserved.
          </div>
        </div>
      </div>
    </footer>
  );
}
