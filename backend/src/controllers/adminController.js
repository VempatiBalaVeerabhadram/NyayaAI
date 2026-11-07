/**
 * NyayaAI — Admin Ingestion & Management Controller
 */

const axios = require('axios');
const fs = require('fs');
const path = require('path');
const logger = require('../utils/logger');

const AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://localhost:8000';
const DATA_DIR = path.resolve(__dirname, '../../../data');

/**
 * Get system and dataset statistics
 */
exports.getStatistics = async (req, res, next) => {
  try {
    try {
      const response = await axios.get(`${AI_SERVICE_URL}/ai/documents/statistics`, { timeout: 5000 });
      return res.status(200).json({
        success: true,
        data: response.data,
      });
    } catch (aiErr) {
      logger.warn(`AI service unreachable for statistics, calculating from files: ${aiErr.message}`);
    }

    const metadataDir = path.join(DATA_DIR, 'metadata');
    const chunksDir = path.join(DATA_DIR, 'chunks');

    const metaFiles = fs.existsSync(metadataDir)
      ? fs.readdirSync(metadataDir).filter((f) => f.endsWith('_metadata.json'))
      : [];
    const chunkFiles = fs.existsSync(chunksDir)
      ? fs.readdirSync(chunksDir).filter((f) => f.endsWith('_chunks.json'))
      : [];

    let totalChunks = 0;
    chunkFiles.forEach((cf) => {
      try {
        const c = JSON.parse(fs.readFileSync(path.join(chunksDir, cf), 'utf-8'));
        totalChunks += c.length;
      } catch (e) {}
    });

    res.status(200).json({
      success: true,
      data: {
        total_documents: metaFiles.length,
        total_chunks: totalChunks,
        processed_count: metaFiles.length,
        failed_count: 0,
      },
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Ingest document via URL (Method B)
 */
exports.ingestUrl = async (req, res, next) => {
  try {
    const { source_url, document_type, case_name, court, judgment_date } = req.body;

    if (!source_url) {
      return res.status(400).json({ success: false, message: 'source_url is required' });
    }

    const response = await axios.post(`${AI_SERVICE_URL}/ai/ingest/url`, {
      source_url,
      document_type: document_type || 'judgment',
      case_name,
      court,
      judgment_date,
    });

    res.status(200).json({
      success: true,
      message: 'Document ingested successfully from URL',
      data: response.data,
    });
  } catch (error) {
    if (error.response) {
      return res.status(error.response.status).json({
        success: false,
        message: error.response.data.detail || 'URL ingestion failed',
      });
    }
    next(error);
  }
};

/**
 * Trigger directory batch processing
 */
exports.processDirectory = async (req, res, next) => {
  try {
    const { input_directory = 'data/raw/', document_type = 'auto', dry_run = false } = req.body;

    const response = await axios.post(`${AI_SERVICE_URL}/ai/ingest/directory`, {
      input_directory,
      document_type,
      dry_run,
    });

    res.status(200).json({
      success: true,
      data: response.data,
    });
  } catch (error) {
    if (error.response) {
      return res.status(error.response.status).json({
        success: false,
        message: error.response.data.detail || 'Batch processing failed',
      });
    }
    next(error);
  }
};
