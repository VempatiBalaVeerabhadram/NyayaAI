const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '../../.env') });

const config = {
  // Server
  port: parseInt(process.env.PORT, 10) || 5000,
  nodeEnv: process.env.NODE_ENV || 'development',

  // MongoDB
  mongodbUri: process.env.MONGODB_URI || 'mongodb://localhost:27017/nyayaai',

  // JWT
  jwtSecret: process.env.JWT_SECRET || 'default_dev_secret_change_me',
  jwtExpiresIn: process.env.JWT_EXPIRES_IN || '7d',

  // AI Service
  aiServiceUrl: process.env.AI_SERVICE_URL || 'http://localhost:8000',

  // Neo4j
  neo4jUri: process.env.NEO4J_URI || 'bolt://localhost:7687',
  neo4jUsername: process.env.NEO4J_USERNAME || 'neo4j',
  neo4jPassword: process.env.NEO4J_PASSWORD || '',

  // Qdrant
  qdrantUrl: process.env.QDRANT_URL || 'http://localhost:6333',

  // Logging
  logLevel: process.env.LOG_LEVEL || 'info',

  // Rate Limiting
  rateLimitWindowMs: 15 * 60 * 1000, // 15 minutes
  rateLimitMax: 100,

  // File Upload
  maxFileSize: 50 * 1024 * 1024, // 50MB
  uploadDir: path.resolve(__dirname, '../../data/raw'),
};

module.exports = config;
