const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const rateLimit = require('express-rate-limit');

const config = require('./config');
const connectDB = require('./config/database');
const routes = require('./routes');
const { errorHandler, notFound } = require('./middleware/errorHandler');
const logger = require('./utils/logger');

/**
 * Initialize and start the NyayaAI Express server.
 */
const startServer = async () => {
  const app = express();

  // ========================
  // Security Middleware
  // ========================
  app.use(helmet());

  // CORS — allow frontend origin
  app.use(
    cors({
      origin: process.env.FRONTEND_URL || 'http://localhost:5173',
      credentials: true,
      methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
      allowedHeaders: ['Content-Type', 'Authorization'],
    })
  );

  // Rate limiting
  const limiter = rateLimit({
    windowMs: config.rateLimitWindowMs,
    max: config.rateLimitMax,
    message: {
      success: false,
      data: null,
      message: 'Too many requests. Please try again later.',
    },
    standardHeaders: true,
    legacyHeaders: false,
  });
  app.use('/api/', limiter);

  // ========================
  // Body Parsing
  // ========================
  app.use(express.json({ limit: '10mb' }));
  app.use(express.urlencoded({ extended: true, limit: '10mb' }));

  // ========================
  // Request Logging
  // ========================
  const morganFormat = config.nodeEnv === 'production' ? 'combined' : 'dev';
  app.use(
    morgan(morganFormat, {
      stream: {
        write: (message) => logger.http(message.trim()),
      },
    })
  );

  // ========================
  // API Routes
  // ========================
  app.use('/api', routes);

  // Root endpoint
  app.get('/', (req, res) => {
    res.json({
      success: true,
      data: {
        name: 'NyayaAI Backend',
        version: '1.0.0',
        description:
          'Hybrid Legal Intelligence Platform for Precedent Discovery, Legal Assistance and Knowledge Graph-Based Reasoning',
      },
      message: 'NyayaAI API is running',
    });
  });

  // ========================
  // Error Handling
  // ========================
  app.use(notFound);
  app.use(errorHandler);

  // ========================
  // Database & Server Start
  // ========================
  try {
    await connectDB();
    logger.info('Database connected successfully');
  } catch (error) {
    logger.warn(`Starting without MongoDB: ${error.message}`);
    logger.warn('Some features will be unavailable until MongoDB is connected.');
  }

  const server = app.listen(config.port, () => {
    logger.info(`
  ╔══════════════════════════════════════════════════╗
  ║                                                  ║
  ║         NyayaAI Backend Server                   ║
  ║         Running on port ${config.port}                    ║
  ║         Environment: ${config.nodeEnv.padEnd(23)}║
  ║                                                  ║
  ╚══════════════════════════════════════════════════╝
    `);
  });

  // Graceful shutdown
  const shutdown = async (signal) => {
    logger.info(`${signal} received. Shutting down gracefully...`);
    server.close(async () => {
      try {
        await require('mongoose').connection.close();
        logger.info('MongoDB connection closed.');
      } catch (e) {
        // Connection might not exist
      }
      process.exit(0);
    });
  };

  process.on('SIGTERM', () => shutdown('SIGTERM'));
  process.on('SIGINT', () => shutdown('SIGINT'));

  return server;
};

startServer().catch((error) => {
  console.error('Failed to start NyayaAI backend:', error);
  process.exit(1);
});
