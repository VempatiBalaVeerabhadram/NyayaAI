const mongoose = require('mongoose');
const config = require('./index');
const logger = require('../utils/logger');

/**
 * Connect to MongoDB with non-blocking graceful fallback.
 */
const connectDB = async () => {
  try {
    const conn = await mongoose.connect(config.mongodbUri, {
      serverSelectionTimeoutMS: 2500,
    });
    logger.info(`MongoDB connected: ${conn.connection.host}`);
    return conn;
  } catch (error) {
    logger.warn(`MongoDB not available at ${config.mongodbUri} (${error.message}). Continuing in standalone gateway mode.`);
    return null;
  }
};

module.exports = connectDB;
