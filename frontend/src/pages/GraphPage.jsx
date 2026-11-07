import React, { useState, useEffect } from 'react';
import { Network, Search, Filter, Info, Loader2, Sparkles, BookOpen, Layers } from 'lucide-react';
import { api } from '../api/client';
import GraphCanvas from '../components/GraphCanvas';

export default function GraphPage() {
  const [graphData, setGraphData] = useState({ nodes: [], relationships: [] });
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilter, setActiveFilter] = useState('All');

  useEffect(() => {
    loadGraph();
  }, []);

  const loadGraph = async () => {
    setLoading(true);
    try {
      const res = await api.getGraphOverview();
      const data = res.data || res;
      setGraphData({
        nodes: data.nodes || [],
        relationships: data.relationships || [],
      });
    } catch (err) {
      console.error('Failed to load graph overview:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchNode = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      loadGraph();
      return;
    }
    setLoading(true);
    try {
      const res = await api.searchGraphNodes(searchQuery.trim());
      const data = res.data || res;
      setGraphData({
        nodes: data.nodes || [],
        relationships: data.relationships || [],
      });
    } catch (err) {
      console.error('Failed search in graph:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredNodes = graphData.nodes.filter((n) => {
    if (activeFilter === 'All') return true;
    return n.label === activeFilter;
  });

  const nodeCountByLabel = graphData.nodes.reduce((acc, node) => {
    acc[node.label] = (acc[node.label] || 0) + 1;
    return acc;
  }, {});

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6 pb-6 border-b border-slate-800">
          <div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              <Network className="w-6 h-6 text-indigo-400" />
              Indian Legal Knowledge Graph Visualizer
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Multi-entity topological graph connecting Acts, Sections, Judgments, Judges, and Legal Doctrines
            </p>
          </div>

          <div className="flex items-center gap-2 flex-wrap text-xs">
            <span className="px-3 py-1.5 rounded-xl bg-indigo-950/80 text-indigo-300 border border-indigo-800/50 font-semibold">
              {graphData.nodes.length} Nodes
            </span>
            <span className="px-3 py-1.5 rounded-xl bg-blue-950/80 text-blue-300 border border-blue-800/50 font-semibold">
              {graphData.relationships.length} Relationships
            </span>
          </div>
        </div>

        {/* Toolbar */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <form onSubmit={handleSearchNode} className="md:col-span-2 relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search graph nodes by name (e.g. Arnesh Kumar, Section 438, Criminal Law)..."
              className="w-full pl-10 pr-20 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-xs text-slate-200 placeholder-slate-400 focus:outline-none focus:border-indigo-500"
            />
            <button
              type="submit"
              className="absolute right-2 top-1/2 -translate-y-1/2 px-3 py-1 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
            >
              Filter
            </button>
          </form>

          <div>
            <select
              value={activeFilter}
              onChange={(e) => setActiveFilter(e.target.value)}
              className="w-full py-2.5 px-3 rounded-xl bg-slate-900 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
            >
              <option value="All">All Entity Labels</option>
              <option value="Act">Acts ({nodeCountByLabel['Act'] || 0})</option>
              <option value="Section">Sections ({nodeCountByLabel['Section'] || 0})</option>
              <option value="Case">Cases ({nodeCountByLabel['Case'] || 0})</option>
              <option value="Judge">Judges ({nodeCountByLabel['Judge'] || 0})</option>
              <option value="LegalIssue">Legal Issues ({nodeCountByLabel['LegalIssue'] || 0})</option>
            </select>
          </div>
        </div>

        {/* Visual Canvas & Inspector Side-by-Side */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Main Visualizer */}
          <div className="lg:col-span-3 h-[600px]">
            {loading ? (
              <div className="w-full h-full glass-panel rounded-2xl flex flex-col items-center justify-center text-slate-400 border border-slate-800">
                <Loader2 className="w-8 h-8 text-indigo-500 animate-spin mb-3" />
                <p className="text-xs">Rendering Legal Knowledge Graph Topology...</p>
              </div>
            ) : (
              <GraphCanvas
                nodes={filteredNodes}
                relationships={graphData.relationships}
                onSelectNode={(node) => setSelectedNode(node)}
              />
            )}
          </div>

          {/* Node Inspector Sidebar */}
          <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex flex-col justify-between h-[600px] overflow-y-auto">
            <div>
              <div className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-4 flex items-center gap-2">
                <Info className="w-4 h-4 text-indigo-400" />
                Entity Property Inspector
              </div>

              {selectedNode ? (
                <div className="space-y-4">
                  <div>
                    <span className="text-[10px] text-slate-400 font-semibold uppercase block">
                      Entity Type
                    </span>
                    <span className="inline-block px-2.5 py-1 rounded-md bg-indigo-950 text-indigo-300 border border-indigo-800/50 text-xs font-bold mt-1">
                      {selectedNode.label}
                    </span>
                  </div>

                  <div>
                    <span className="text-[10px] text-slate-400 font-semibold uppercase block">
                      Node Name / Title
                    </span>
                    <h3 className="text-sm font-bold text-white mt-0.5">
                      {selectedNode.name}
                    </h3>
                  </div>

                  <div>
                    <span className="text-[10px] text-slate-400 font-semibold uppercase block">
                      Graph Identifier
                    </span>
                    <code className="text-xs font-mono text-slate-300 bg-slate-900 px-2 py-1 rounded block mt-0.5 break-all">
                      {selectedNode.id}
                    </code>
                  </div>
                </div>
              ) : (
                <div className="text-center py-16 text-slate-500 text-xs">
                  <Network className="w-8 h-8 mx-auto mb-2 opacity-40 text-indigo-400" />
                  <p>Click on any node in the graph canvas to inspect its legal attributes and citations.</p>
                </div>
              )}
            </div>

            <div className="pt-4 border-t border-slate-800/60 text-[11px] text-slate-500">
              Backend: <strong>Neo4j & NetworkX High-Performance Graph Engine</strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
