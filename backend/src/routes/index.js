const express = require('express');

const router = express.Router();

// Import route modules
const healthRoutes = require('./health');
const caseRoutes = require('./cases');
const actRoutes = require('./acts');
const adminRoutes = require('./admin');
const searchRoutes = require('./search');
const graphRoutes = require('./graph');
const queryRoutes = require('./query');

// Mount routes
router.use('/health', healthRoutes);
router.use('/cases', caseRoutes);
router.use('/acts', actRoutes);
router.use('/admin', adminRoutes);
router.use('/search', searchRoutes);
router.use('/graph', graphRoutes);
router.use('/query', queryRoutes);

// Placeholder routes for subsequent stages
// router.use('/auth', authRoutes);      // Stage 13
// router.use('/history', historyRoutes); // Stage 13

module.exports = router;
