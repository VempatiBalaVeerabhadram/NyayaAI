/**
 * NyayaAI — Query Controller
 * Dispatches grounded RAG legal queries to the AI service.
 */

const axios = require('axios');
const logger = require('../utils/logger');

const AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://localhost:8000';

/**
 * Process a legal question through the evidence-first RAG pipeline
 */
exports.query = async (req, res, next) => {
  try {
    const {
      query,
      mode = 'researcher',
      top_k = 5,
      alpha = 0.5,
      graph_expansion_depth = 1,
      legal_domain,
    } = req.body;

    if (!query || query.trim().length === 0) {
      return res.status(400).json({ success: false, message: 'Query cannot be empty' });
    }

    const response = await axios.post(
      `${AI_SERVICE_URL}/ai/query`,
      {
        query,
        mode: mode.toLowerCase() === 'user' ? 'user' : 'researcher',
        top_k: parseInt(top_k, 10) || 5,
        alpha: parseFloat(alpha) !== undefined ? parseFloat(alpha) : 0.5,
        graph_expansion_depth: parseInt(graph_expansion_depth, 10) || 1,
        legal_domain: legal_domain || null,
      },
      { timeout: 60000 }
    );

    res.status(200).json({
      success: true,
      data: response.data,
    });
  } catch (error) {
    if (error.response) {
      return res.status(error.response.status).json({
        success: false,
        message: error.response.data.detail || 'Query processing failed',
      });
    }
    logger.error(`Query controller error: ${error.message}`);
    res.status(503).json({
      success: false,
      message: 'AI Service is currently unreachable. Ensure ai-service is running on port 8000.',
    });
  }
};
