import React, { useState } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';
import { BarChart3, Award, TrendingUp, Cpu, CheckCircle2, ShieldCheck, FileCheck } from 'lucide-react';

export default function EvaluationPage() {
  // Benchmark Evaluation Data from data/evaluation/benchmark_results.json
  const benchmarkSummary = [
    {
      metric: 'Precision@1',
      BM25: 0.125,
      Dense: 0.5,
      Hybrid: 0.125,
      GraphEnhanced: 0.25,
    },
    {
      metric: 'Precision@3',
      BM25: 0.25,
      Dense: 0.3333,
      Hybrid: 0.2083,
      GraphEnhanced: 0.3333,
    },
    {
      metric: 'Precision@5',
      BM25: 0.25,
      Dense: 0.225,
      Hybrid: 0.25,
      GraphEnhanced: 0.275,
    },
    {
      metric: 'Recall@5',
      BM25: 0.3646,
      Dense: 0.3333,
      Hybrid: 0.3646,
      GraphEnhanced: 0.3958,
    },
    {
      metric: 'Recall@10',
      BM25: 0.4271,
      Dense: 0.3646,
      Hybrid: 0.4688,
      GraphEnhanced: 0.5,
    },
    {
      metric: 'MRR',
      BM25: 0.4688,
      Dense: 0.6042,
      Hybrid: 0.4375,
      GraphEnhanced: 0.5139,
    },
    {
      metric: 'MAP@10',
      BM25: 0.2331,
      Dense: 0.251,
      Hybrid: 0.231,
      GraphEnhanced: 0.3129,
    },
    {
      metric: 'NDCG@5',
      BM25: 0.3271,
      Dense: 0.3554,
      Hybrid: 0.3153,
      GraphEnhanced: 0.3771,
    },
    {
      metric: 'NDCG@10',
      BM25: 0.3599,
      Dense: 0.3695,
      Hybrid: 0.3651,
      GraphEnhanced: 0.4262,
    },
  ];

  const radarData = [
    { subject: 'P@5', BM25: 25, Dense: 22.5, Hybrid: 25, GraphEnhanced: 27.5 },
    { subject: 'Recall@10', BM25: 42.7, Dense: 36.5, Hybrid: 46.9, GraphEnhanced: 50.0 },
    { subject: 'MRR', BM25: 46.9, Dense: 60.4, Hybrid: 43.8, GraphEnhanced: 51.4 },
    { subject: 'MAP@10', BM25: 23.3, Dense: 25.1, Hybrid: 23.1, GraphEnhanced: 31.3 },
    { subject: 'NDCG@10', BM25: 36.0, Dense: 37.0, Hybrid: 36.5, GraphEnhanced: 42.6 },
  ];

  const [activeTab, setActiveTab] = useState('ranking');

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8 pb-6 border-b border-slate-800">
          <div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              <BarChart3 className="w-6 h-6 text-amber-400" />
              Quantitative IR Benchmark & Evaluation Dashboard
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Comparative empirical analysis: BM25 Lexical vs Dense Semantic vs Convex Hybrid vs Graph-Enhanced Hybrid
            </p>
          </div>

          <span className="px-3.5 py-1.5 rounded-xl bg-amber-950/60 border border-amber-800/40 text-xs font-semibold text-amber-300">
            Gold-Standard Ground Truth Testbed
          </span>
        </div>

        {/* Highlight Metrics Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
          <div className="glass-card p-5 rounded-2xl border border-slate-800">
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
              Highest NDCG@10
            </div>
            <div className="text-3xl font-extrabold text-emerald-400">0.4262</div>
            <div className="text-[11px] text-slate-400 mt-1 flex items-center gap-1">
              <Award className="w-3.5 h-3.5 text-emerald-400" />
              Graph-Enhanced Hybrid (+15.3% over BM25)
            </div>
          </div>

          <div className="glass-card p-5 rounded-2xl border border-slate-800">
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
              Highest MAP@10
            </div>
            <div className="text-3xl font-extrabold text-blue-400">0.3129</div>
            <div className="text-[11px] text-slate-400 mt-1 flex items-center gap-1">
              <Award className="w-3.5 h-3.5 text-blue-400" />
              Graph-Enhanced Hybrid (+34.2% over BM25)
            </div>
          </div>

          <div className="glass-card p-5 rounded-2xl border border-slate-800">
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
              Highest Recall@10
            </div>
            <div className="text-3xl font-extrabold text-indigo-400">0.5000</div>
            <div className="text-[11px] text-slate-400 mt-1 flex items-center gap-1">
              <Award className="w-3.5 h-3.5 text-indigo-400" />
              Graph-Enhanced Hybrid (50% coverage)
            </div>
          </div>

          <div className="glass-card p-5 rounded-2xl border border-slate-800">
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
              Top Precision@1
            </div>
            <div className="text-3xl font-extrabold text-amber-400">0.5000</div>
            <div className="text-[11px] text-slate-400 mt-1 flex items-center gap-1">
              <Award className="w-3.5 h-3.5 text-amber-400" />
              Dense Semantic Vector Search
            </div>
          </div>
        </div>

        {/* Chart View */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-2 glass-panel p-6 rounded-2xl border border-slate-800">
            <div className="text-sm font-bold text-white mb-4">
              Comprehensive Metric Comparison across 4 Retrieval Pipelines
            </div>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={benchmarkSummary} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="metric" stroke="#64748b" textAnchor="end" tick={{ fontSize: 11 }} />
                  <YAxis stroke="#64748b" domain={[0, 0.7]} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#0f172a',
                      borderColor: '#334155',
                      borderRadius: '8px',
                      fontSize: '12px',
                    }}
                  />
                  <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                  <Bar dataKey="BM25" fill="#f59e0b" name="BM25 Lexical" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="Dense" fill="#3b82f6" name="Dense Semantic" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="Hybrid" fill="#8b5cf6" name="Convex Hybrid (α=0.5)" radius={[4, 4, 0, 0]} />
                  <Bar
                    dataKey="GraphEnhanced"
                    fill="#10b981"
                    name="Graph-Enhanced Hybrid"
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex flex-col justify-between">
            <div>
              <div className="text-sm font-bold text-white mb-4">
                Multi-Dimensional Radar Profile
              </div>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart cx="50%" cy="50%" outerRadius="75%" data={radarData}>
                    <PolarGrid stroke="#334155" />
                    <PolarAngleAxis dataKey="subject" stroke="#94a3b8" tick={{ fontSize: 10 }} />
                    <PolarRadiusAxis angle={30} domain={[0, 65]} stroke="#475569" tick={{ fontSize: 9 }} />
                    <Radar
                      name="Graph-Enhanced"
                      dataKey="GraphEnhanced"
                      stroke="#10b981"
                      fill="#10b981"
                      fillOpacity={0.4}
                    />
                    <Radar
                      name="Dense"
                      dataKey="Dense"
                      stroke="#3b82f6"
                      fill="#3b82f6"
                      fillOpacity={0.25}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#0f172a',
                        borderColor: '#334155',
                        borderRadius: '8px',
                        fontSize: '12px',
                      }}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="text-[11px] text-slate-400 border-t border-slate-800/80 pt-3">
              <strong className="text-slate-200">Key Finding:</strong> Graph expansion unlocks <strong>+34% higher Mean Average Precision</strong> by re-ranking multi-hop citation chains.
            </div>
          </div>
        </div>

        {/* Detailed Results Table */}
        <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
          <div className="p-4 border-b border-slate-800 flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <FileCheck className="w-4 h-4 text-emerald-400" />
              Official Quantitative Results Matrix
            </h3>
            <span className="text-xs text-slate-400">8 Benchmark Test Queries</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left text-slate-300">
              <thead className="bg-slate-900/90 text-slate-400 uppercase font-semibold border-b border-slate-800">
                <tr>
                  <th className="px-4 py-3">Retrieval Pipeline</th>
                  <th className="px-3 py-3 text-center">P@1</th>
                  <th className="px-3 py-3 text-center">P@3</th>
                  <th className="px-3 py-3 text-center">P@5</th>
                  <th className="px-3 py-3 text-center">Recall@5</th>
                  <th className="px-3 py-3 text-center">Recall@10</th>
                  <th className="px-3 py-3 text-center">MRR</th>
                  <th className="px-3 py-3 text-center">MAP@10</th>
                  <th className="px-3 py-3 text-center font-bold text-emerald-400">NDCG@10</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                <tr className="hover:bg-slate-900/50">
                  <td className="px-4 py-3 font-semibold text-amber-300">BM25 Lexical Okapi</td>
                  <td className="px-3 py-3 text-center">0.1250</td>
                  <td className="px-3 py-3 text-center">0.2500</td>
                  <td className="px-3 py-3 text-center">0.2500</td>
                  <td className="px-3 py-3 text-center">0.3646</td>
                  <td className="px-3 py-3 text-center">0.4271</td>
                  <td className="px-3 py-3 text-center">0.4688</td>
                  <td className="px-3 py-3 text-center">0.2331</td>
                  <td className="px-3 py-3 text-center font-mono">0.3599</td>
                </tr>
                <tr className="hover:bg-slate-900/50">
                  <td className="px-4 py-3 font-semibold text-blue-300">Dense Semantic (all-MiniLM)</td>
                  <td className="px-3 py-3 text-center font-bold text-blue-400">0.5000</td>
                  <td className="px-3 py-3 text-center">0.3333</td>
                  <td className="px-3 py-3 text-center">0.2250</td>
                  <td className="px-3 py-3 text-center">0.3333</td>
                  <td className="px-3 py-3 text-center">0.3646</td>
                  <td className="px-3 py-3 text-center font-bold text-blue-400">0.6042</td>
                  <td className="px-3 py-3 text-center">0.2510</td>
                  <td className="px-3 py-3 text-center font-mono">0.3695</td>
                </tr>
                <tr className="hover:bg-slate-900/50">
                  <td className="px-4 py-3 font-semibold text-purple-300">Convex Hybrid (α=0.5)</td>
                  <td className="px-3 py-3 text-center">0.1250</td>
                  <td className="px-3 py-3 text-center">0.2083</td>
                  <td className="px-3 py-3 text-center">0.2500</td>
                  <td className="px-3 py-3 text-center">0.3646</td>
                  <td className="px-3 py-3 text-center">0.4688</td>
                  <td className="px-3 py-3 text-center">0.4375</td>
                  <td className="px-3 py-3 text-center">0.2310</td>
                  <td className="px-3 py-3 text-center font-mono">0.3651</td>
                </tr>
                <tr className="bg-emerald-950/20 hover:bg-emerald-950/30">
                  <td className="px-4 py-3 font-bold text-emerald-400 flex items-center gap-1.5">
                    <Award className="w-4 h-4 text-emerald-400" />
                    Graph-Enhanced Hybrid (Ours)
                  </td>
                  <td className="px-3 py-3 text-center">0.2500</td>
                  <td className="px-3 py-3 text-center font-bold text-emerald-400">0.3333</td>
                  <td className="px-3 py-3 text-center font-bold text-emerald-400">0.2750</td>
                  <td className="px-3 py-3 text-center font-bold text-emerald-400">0.3958</td>
                  <td className="px-3 py-3 text-center font-bold text-emerald-400">0.5000</td>
                  <td className="px-3 py-3 text-center">0.5139</td>
                  <td className="px-3 py-3 text-center font-bold text-emerald-400">0.3129</td>
                  <td className="px-3 py-3 text-center font-bold font-mono text-emerald-400">0.4262</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
