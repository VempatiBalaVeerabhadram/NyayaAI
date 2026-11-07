/**
 * NyayaAI — Acts & Sections Controller
 */

const axios = require('axios');
const fs = require('fs');
const path = require('path');
const logger = require('../utils/logger');

const AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://localhost:8000';
const DATA_DIR = path.resolve(__dirname, '../../../data');

/**
 * List all statutory Acts
 */
exports.getActs = async (req, res, next) => {
  try {
    try {
      const response = await axios.get(`${AI_SERVICE_URL}/ai/documents`, {
        params: { doc_type: 'act' },
        timeout: 5000,
      });
      return res.status(200).json({
        success: true,
        count: response.data.length,
        data: response.data,
      });
    } catch (aiErr) {
      logger.warn(`AI service unreachable for getActs, reading from local store: ${aiErr.message}`);
    }

    const metadataDir = path.join(DATA_DIR, 'metadata');
    const files = fs.readdirSync(metadataDir).filter((f) => f.endsWith('_metadata.json'));
    const acts = [];

    for (const f of files) {
      const content = JSON.parse(fs.readFileSync(path.join(metadataDir, f), 'utf-8'));
      if (content.document_type === 'act') {
        acts.push(content);
      }
    }

    res.status(200).json({ success: true, count: acts.length, data: acts });
  } catch (error) {
    next(error);
  }
};

/**
 * Get single Act with all sections
 */
exports.getActById = async (req, res, next) => {
  try {
    const { id } = req.params;

    const processedFile = path.join(DATA_DIR, 'processed', `${id}_processed.json`);
    if (!fs.existsSync(processedFile)) {
      return res.status(404).json({ success: false, message: `Act not found: ${id}` });
    }

    const data = JSON.parse(fs.readFileSync(processedFile, 'utf-8'));
    res.status(200).json({ success: true, data });
  } catch (error) {
    next(error);
  }
};
