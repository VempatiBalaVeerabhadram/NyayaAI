const express = require('express');
const axios = require('axios');
const mongoose = require('mongoose');
const config = require('../config');
const { sendSuccess, sendError } = require('../utils/response');
const logger = require('../utils/logger');

const router = express.Router();

/**
 * GET /api/health
 * Returns health status of all services.
 */
router.get('/', async (req, res) => {
  const health = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    services: {},
  };

  // Check MongoDB
  try {
    const mongoState = mongoose.connection.readyState;
    health.services.mongodb = {
      status: mongoState === 1 ? 'connected' : 'disconnected',
      readyState: mongoState,
    };
  } catch (error) {
    health.services.mongodb = { status: 'error', message: error.message };
  }

  // Check AI Service
  try {
    const aiResponse = await axios.get(`${config.aiServiceUrl}/health`, {
      timeout: 5000,
    });
    health.services.aiService = {
      status: 'connected',
      data: aiResponse.data,
    };
  } catch (error) {
    health.services.aiService = {
      status: 'disconnected',
      message: 'AI service is not reachable',
    };
  }

  // Check Qdrant
  try {
    const qdrantResponse = await axios.get(`${config.qdrantUrl}/collections`, {
      timeout: 5000,
    });
    health.services.qdrant = {
      status: 'connected',
      collections: qdrantResponse.data?.result?.collections?.length || 0,
    };
  } catch (error) {
    health.services.qdrant = {
      status: 'disconnected',
      message: 'Qdrant is not reachable',
    };
  }

  // Check Neo4j (basic TCP check via config, detailed check via AI service)
  health.services.neo4j = {
    status: 'configured',
    uri: config.neo4jUri,
  };

  // Determine overall status
  const criticalServices = ['mongodb'];
  const hasCriticalFailure = criticalServices.some(
    (s) => health.services[s]?.status === 'error' || health.services[s]?.status === 'disconnected'
  );

  if (hasCriticalFailure) {
    health.status = 'degraded';
  }

  return sendSuccess(res, health, 'Health check completed');
});

module.exports = router;
