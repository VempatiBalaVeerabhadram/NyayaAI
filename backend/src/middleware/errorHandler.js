const logger = require('../utils/logger');

/**
 * Global error handling middleware.
 * Catches all errors and returns a consistent API response.
 * Does NOT expose stack traces in production.
 */
const errorHandler = (err, req, res, next) => {
  // Log the full error internally
  logger.error(`${err.message}`, {
    method: req.method,
    url: req.originalUrl,
    ip: req.ip,
    stack: err.stack,
  });

  // Determine status code
  const statusCode = err.statusCode || 500;

  // Build the response
  const response = {
    success: false,
    data: null,
    message: statusCode === 500 ? 'Internal Server Error' : err.message,
  };

  // Include validation errors if present
  if (err.errors) {
    response.errors = err.errors;
  }

  // In development, include stack trace
  if (process.env.NODE_ENV === 'development') {
    response.stack = err.stack;
  }

  return res.status(statusCode).json(response);
};

/**
 * Not Found middleware — catches requests to undefined routes.
 */
const notFound = (req, res, next) => {
  const error = new Error(`Route not found: ${req.originalUrl}`);
  error.statusCode = 404;
  next(error);
};

module.exports = { errorHandler, notFound };
