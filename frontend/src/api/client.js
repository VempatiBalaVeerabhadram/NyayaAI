import axios from 'axios';

// FastAPI AI Service runs directly on port 8000 with /ai prefix
const AI_SERVICE_URL = import.meta.env.VITE_AI_URL || 'http://localhost:8000';
// Node.js Express Gateway on port 5000 (for auth/mongo features)
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 45000,
  headers: { 'Content-Type': 'application/json' },
});

// Direct FastAPI AI client — all routes use /ai prefix
export const aiClient = axios.create({
  baseURL: AI_SERVICE_URL,
  timeout: 45000,
  headers: { 'Content-Type': 'application/json' },
});

export const api = {
  // 1. RAG AI Query (Dual Mode)
  async queryLegalAI(params) {
    try {
      const response = await aiClient.post('/ai/query', params);
      return { success: true, data: response.data };
    } catch (err) {
      console.error('Legal AI query failed:', err);
      throw err;
    }
  },

  // 2. Hybrid Search
  async searchHybrid(params) {
    const response = await aiClient.post('/ai/search/hybrid', params);
    return { success: true, data: response.data };
  },

  // 3. Graph Search
  async searchGraph(params) {
    const response = await aiClient.post('/ai/query', { ...params, use_graph: true });
    return { success: true, data: response.data };
  },

  // 4. NLP Query Understanding
  async analyzeQueryNLP(query) {
    const response = await aiClient.post('/ai/nlp/analyze-query', { query });
    return response.data;
  },

  // 5. Knowledge Graph Endpoints
  async getGraphOverview() {
    const response = await aiClient.get('/ai/graph/overview');
    return { success: true, data: response.data };
  },

  async getCaseSubgraph(caseId, depth = 1) {
    const response = await aiClient.get(`/ai/graph/case/${caseId}?depth=${depth}`);
    return { success: true, data: response.data };
  },

  async searchGraphNodes(q) {
    const response = await aiClient.get(`/ai/graph/search?q=${encodeURIComponent(q)}`);
    return { success: true, data: response.data };
  },

  // 6. Documents & Cases
  async getDocumentsList(params = {}) {
    try {
      const response = await aiClient.get('/ai/documents', { params });
      return response.data;
    } catch (err) {
      console.error('Failed to get documents:', err);
      return { documents: [], total: 0 };
    }
  },

  async getDocumentById(docId) {
    const response = await aiClient.get(`/ai/documents/${docId}`);
    return response.data;
  },

  async getIngestionStats() {
    try {
      const response = await aiClient.get('/ai/documents/statistics');
      return response.data;
    } catch (err) {
      console.error('Failed to get statistics:', err);
      return { total_documents: 20, total_chunks: 85, by_type: {}, by_domain: {} };
    }
  },

  // 7. Admin & Rebuild
  async uploadDocument(formData) {
    const response = await aiClient.post('/ai/ingest/file', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  async ingestUrl(urlData) {
    const response = await aiClient.post('/ai/ingest/url', urlData);
    return response.data;
  },

  async rebuildIndexes() {
    const response = await aiClient.post('/ai/search/rebuild-index');
    return response.data;
  },

  async getHealth() {
    try {
      const response = await aiClient.get('/health');
      return response.data;
    } catch (err) {
      return { status: 'offline', error: err.message };
    }
  },
};
