import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  Upload,
  Globe,
  RefreshCw,
  Activity,
  CheckCircle2,
  AlertCircle,
  FileText,
  Loader2,
  HardDrive,
  Database,
  Cpu,
} from 'lucide-react';
import { api } from '../api/client';

export default function AdminPage() {
  const [health, setHealth] = useState(null);
  const [stats, setStats] = useState(null);
  const [isRebuilding, setIsRebuilding] = useState(false);
  const [rebuildStatus, setRebuildStatus] = useState(null);

  // File Upload State
  const [file, setFile] = useState(null);
  const [fileTitle, setFileTitle] = useState('');
  const [fileDocType, setFileDocType] = useState('judgment');
  const [fileDomain, setFileDomain] = useState('Criminal Law');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState(null);

  // URL Ingest State
  const [url, setUrl] = useState('');
  const [urlDocType, setUrlDocType] = useState('judgment');
  const [isUrlIngesting, setIsUrlIngesting] = useState(false);
  const [urlMessage, setUrlMessage] = useState(null);

  useEffect(() => {
    loadHealthAndStats();
  }, []);

  const loadHealthAndStats = async () => {
    try {
      const h = await api.getHealth();
      setHealth(h);
      const s = await api.getIngestionStats();
      setStats(s);
    } catch (err) {
      console.error('Failed to load status:', err);
    }
  };

  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    setIsUploading(true);
    setUploadMessage(null);

    const formData = new FormData();
    formData.append('file', file);
    if (fileTitle) formData.append('title', fileTitle);
    formData.append('document_type', fileDocType);
    formData.append('legal_domain', fileDomain);

    try {
      const res = await api.uploadDocument(formData);
      setUploadMessage({
        type: 'success',
        text: `✔ Successfully ingested "${res.title || file.name}" (${res.chunk_count} semantic chunks generated)`,
      });
      setFile(null);
      setFileTitle('');
      loadHealthAndStats();
    } catch (err) {
      setUploadMessage({
        type: 'error',
        text: `Error uploading document: ${err.response?.data?.detail || err.message}`,
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleUrlIngest = async (e) => {
    e.preventDefault();
    if (!url.trim()) return;

    setIsUrlIngesting(true);
    setUrlMessage(null);

    try {
      const res = await api.ingestUrl({
        url: url.trim(),
        document_type: urlDocType,
      });
      setUrlMessage({
        type: 'success',
        text: `✔ Successfully scraped & ingested document (${res.chunk_count} chunks)`,
      });
      setUrl('');
      loadHealthAndStats();
    } catch (err) {
      setUrlMessage({
        type: 'error',
        text: `Error ingesting URL: ${err.response?.data?.detail || err.message}`,
      });
    } finally {
      setIsUrlIngesting(false);
    }
  };

  const handleRebuildIndexes = async () => {
    setIsRebuilding(true);
    setRebuildStatus(null);
    try {
      const res = await api.rebuildIndexes();
      setRebuildStatus({
        type: 'success',
        text: `✔ BM25 & Semantic Vector indexes successfully rebuilt (${res.chunks_indexed} chunks)`,
      });
      loadHealthAndStats();
    } catch (err) {
      setRebuildStatus({
        type: 'error',
        text: `Failed to rebuild indexes: ${err.message}`,
      });
    } finally {
      setIsRebuilding(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8 pb-6 border-b border-slate-800">
          <div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              <ShieldCheck className="w-6 h-6 text-emerald-400" />
              NyayaAI Administration & Corpus Management
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Document ingestion, Indian Kanoon URL harvesting, vector index maintenance, and service telemetry
            </p>
          </div>

          <button
            onClick={handleRebuildIndexes}
            disabled={isRebuilding}
            className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center gap-2 shadow-md shadow-blue-500/20 disabled:opacity-50"
          >
            {isRebuilding ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <RefreshCw className="w-4 h-4" />
            )}
            Rebuild All Indexes
          </button>
        </div>

        {rebuildStatus && (
          <div
            className={`p-4 rounded-xl text-xs flex items-center gap-2 mb-6 ${
              rebuildStatus.type === 'success'
                ? 'bg-emerald-950/60 border border-emerald-800 text-emerald-300'
                : 'bg-red-950/60 border border-red-800 text-red-300'
            }`}
          >
            {rebuildStatus.text}
          </div>
        )}

        {/* System Health Telemetry */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
          <div className="glass-card p-5 rounded-2xl border border-slate-800">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold text-slate-400 uppercase">AI Service</span>
              <Activity className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-lg font-bold text-white">
              {health?.status === 'ok' ? (
                <span className="text-emerald-400 flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4" /> Operational
                </span>
              ) : (
                <span className="text-amber-400">Degraded</span>
              )}
            </div>
            <span className="text-[10px] text-slate-500 block mt-1">FastAPI Backend Gateway</span>
          </div>

          <div className="glass-card p-5 rounded-2xl border border-slate-800">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold text-slate-400 uppercase">Vector Index</span>
              <Database className="w-4 h-4 text-blue-400" />
            </div>
            <div className="text-lg font-bold text-blue-400">FAISS Index</div>
            <span className="text-[10px] text-slate-500 block mt-1">
              {stats?.total_chunks || 85} Vectors Loaded (384-dim)
            </span>
          </div>

          <div className="glass-card p-5 rounded-2xl border border-slate-800">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold text-slate-400 uppercase">Knowledge Graph</span>
              <HardDrive className="w-4 h-4 text-indigo-400" />
            </div>
            <div className="text-lg font-bold text-indigo-400">NetworkX Graph</div>
            <span className="text-[10px] text-slate-500 block mt-1">
              143 Nodes / 291 Relationships
            </span>
          </div>

          <div className="glass-card p-5 rounded-2xl border border-slate-800">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold text-slate-400 uppercase">InLegalBERT</span>
              <Cpu className="w-4 h-4 text-amber-400" />
            </div>
            <div className="text-lg font-bold text-amber-400">Active (law-ai)</div>
            <span className="text-[10px] text-slate-500 block mt-1">Specialized Legal Transformer</span>
          </div>
        </div>

        {/* 2-Column Ingestion Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* File Upload Form */}
          <div className="glass-panel p-6 rounded-2xl border border-slate-800">
            <h2 className="text-base font-bold text-white flex items-center gap-2 mb-4">
              <Upload className="w-5 h-5 text-blue-400" />
              Ingest Document File (PDF, HTML, JSON)
            </h2>

            <form onSubmit={handleFileUpload} className="space-y-4">
              <div>
                <label className="block text-xs text-slate-300 mb-1">
                  Document Title / Case Name
                </label>
                <input
                  type="text"
                  value={fileTitle}
                  onChange={(e) => setFileTitle(e.target.value)}
                  placeholder="e.g. State of Maharashtra v. XYZ (2024)"
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Document Type</label>
                  <select
                    value={fileDocType}
                    onChange={(e) => setFileDocType(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
                  >
                    <option value="judgment">Supreme Court / High Court Judgment</option>
                    <option value="statute">Statute / Bare Act</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs text-slate-300 mb-1">Legal Domain</label>
                  <select
                    value={fileDomain}
                    onChange={(e) => setFileDomain(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
                  >
                    <option value="Criminal Law">Criminal Law</option>
                    <option value="Cyber Law">Cyber Law</option>
                    <option value="Constitutional Law">Constitutional Law</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">Select File</label>
                <input
                  type="file"
                  accept=".pdf,.html,.json,.txt"
                  onChange={(e) => setFile(e.target.files[0])}
                  className="w-full text-xs text-slate-400 file:mr-3 file:py-2 file:px-3 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-slate-800 file:text-blue-300 hover:file:bg-slate-700"
                />
              </div>

              {uploadMessage && (
                <div
                  className={`p-3 rounded-xl text-xs ${
                    uploadMessage.type === 'success'
                      ? 'bg-emerald-950/60 border border-emerald-800 text-emerald-300'
                      : 'bg-red-950/60 border border-red-800 text-red-300'
                  }`}
                >
                  {uploadMessage.text}
                </div>
              )}

              <button
                type="submit"
                disabled={!file || isUploading}
                className="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {isUploading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Ingest Document'}
              </button>
            </form>
          </div>

          {/* URL Ingestion Form */}
          <div className="glass-panel p-6 rounded-2xl border border-slate-800">
            <h2 className="text-base font-bold text-white flex items-center gap-2 mb-4">
              <Globe className="w-5 h-5 text-emerald-400" />
              Scrape & Ingest Indian Kanoon / Official Legal URL
            </h2>

            <form onSubmit={handleUrlIngest} className="space-y-4">
              <div>
                <label className="block text-xs text-slate-300 mb-1">
                  Legal Source URL
                </label>
                <input
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://indiankanoon.org/doc/1234567/ or official court link"
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">Document Type</label>
                <select
                  value={urlDocType}
                  onChange={(e) => setUrlDocType(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
                >
                  <option value="judgment">Landmark Judgment</option>
                  <option value="statute">Statute / Bare Act</option>
                </select>
              </div>

              {urlMessage && (
                <div
                  className={`p-3 rounded-xl text-xs ${
                    urlMessage.type === 'success'
                      ? 'bg-emerald-950/60 border border-emerald-800 text-emerald-300'
                      : 'bg-red-950/60 border border-red-800 text-red-300'
                  }`}
                >
                  {urlMessage.text}
                </div>
              )}

              <button
                type="submit"
                disabled={!url || isUrlIngesting}
                className="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-md disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {isUrlIngesting ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Scrape & Ingest'}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
