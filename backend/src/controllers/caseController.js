/**
 * NyayaAI — Case Controller
 * Communicates with AI Service and local document store to serve structured judgment details.
 */

const axios = require('axios');
const fs = require('fs');
const path = require('path');
const logger = require('../utils/logger');

const AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://localhost:8000';
const DATA_DIR = path.resolve(__dirname, '../../../data');

/**
 * List all legal judgments with optional filtering
 */
exports.getCases = async (req, res, next) => {
  try {
    const { domain, search } = req.query;

    // Try fetching from AI Service first
    try {
      const response = await axios.get(`${AI_SERVICE_URL}/ai/documents`, {
        params: { doc_type: 'judgment', domain, search },
        timeout: 5000,
      });
      return res.status(200).json({
        success: true,
        count: response.data.length,
        data: response.data,
      });
    } catch (aiErr) {
      logger.warn(`AI service unreachable for getCases, reading from local metadata cache: ${aiErr.message}`);
    }

    // Local fallback
    const metadataDir = path.join(DATA_DIR, 'metadata');
    if (!fs.existsSync(metadataDir)) {
      return res.status(200).json({ success: true, count: 0, data: [] });
    }

    const files = fs.readdirSync(metadataDir).filter((f) => f.endsWith('_metadata.json'));
    const cases = [];

    for (const f of files) {
      const content = JSON.parse(fs.readFileSync(path.join(metadataDir, f), 'utf-8'));
      if (content.document_type === 'judgment') {
        if (domain && !content.legal_domain.toLowerCase().includes(domain.toLowerCase())) continue;
        if (search && !content.case_name.toLowerCase().includes(search.toLowerCase())) continue;

        cases.push({
          document_id: content.document_id,
          case_name: content.case_name,
          court: content.court,
          judgment_date: content.judgment_date,
          legal_domain: content.legal_domain,
          acts: content.acts || [],
          sections: content.sections || [],
          citations: content.citations || [],
          source_url: content.source_url || '',
        });
      }
    }

    res.status(200).json({
      success: true,
      count: cases.length,
      data: cases,
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Get single case details and metadata
 */
exports.getCaseById = async (req, res, next) => {
  try {
    const { id } = req.params;

    // Try AI Service
    try {
      const response = await axios.get(`${AI_SERVICE_URL}/ai/documents/${id}`, { timeout: 5000 });
      return res.status(200).json({
        success: true,
        data: response.data,
      });
    } catch (aiErr) {
      logger.warn(`AI service fetch failed for case ${id}, trying local cache: ${aiErr.message}`);
    }

    // Local fallback
    const processedFile = path.join(DATA_DIR, 'processed', `${id}_processed.json`);
    if (!fs.existsSync(processedFile)) {
      return res.status(404).json({
        success: false,
        message: `Case not found: ${id}`,
      });
    }

    const data = JSON.parse(fs.readFileSync(processedFile, 'utf-8'));
    res.status(200).json({
      success: true,
      data,
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Get case citations
 */
exports.getCaseCitations = async (req, res, next) => {
  try {
    const { id } = req.params;
    const metadataFile = path.join(DATA_DIR, 'metadata', `${id}_metadata.json`);

    if (!fs.existsSync(metadataFile)) {
      return res.status(404).json({ success: false, message: `Metadata not found for ${id}` });
    }

    const meta = JSON.parse(fs.readFileSync(metadataFile, 'utf-8'));
    res.status(200).json({
      success: true,
      case_id: meta.case_id,
      case_name: meta.case_name,
      citations: meta.citations || [],
    });
  } catch (error) {
    next(error);
  }
};
