/**
 * NyayaAI — Search & Retrieval Controller
 * Dispatches search queries (BM25, Semantic, Hybrid) to the AI service.
 */

const axios = require('axios');
const logger = require('../utils/logger');

const AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://localhost:8000';

/**
 * Execute Hybrid Search (or BM25 / Semantic depending on mode)
 */
exports.search = async (req, res, next) => {
  try {
    const { query, mode = 'hybrid', top_k = 10, alpha = 0.5, legal_domain, document_type } = req.body;

    if (!query || query.trim().length === 0) {
      return res.status(400).json({ success: false, message: 'Search query cannot be empty' });
    }

    const endpointMap = {
      bm25: '/ai/search/bm25',
      semantic: '/ai/search/semantic',
      hybrid: '/ai/search/hybrid',
    };

    const targetEndpoint = endpointMap[mode.toLowerCase()] || endpointMap.hybrid;

    const response = await axios.post(
      `${AI_SERVICE_URL}${targetEndpoint}`,
      {
        query,
        top_k: parseInt(top_k, 10) || 10,
        alpha: parseFloat(alpha) !== undefined ? parseFloat(alpha) : 0.5,
        legal_domain: legal_domain || null,
        document_type: document_type || null,
      },
      { timeout: 30000 }
    );

    res.status(200).json({
      success: true,
      data: response.data,
    });
  } catch (error) {
    if (error.response) {
      return res.status(error.response.status).json({
        success: false,
        message: error.response.data.detail || 'Search execution failed',
      });
    }
    logger.error(`Search controller error: ${error.message}`);
    res.status(503).json({
      success: false,
      message: 'AI Retrieval Service is currently unreachable. Ensure ai-service is running on port 8000.',
    });
  }
};
