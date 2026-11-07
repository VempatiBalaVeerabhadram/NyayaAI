const express = require('express');
const router = express.Router();
const adminController = require('../controllers/adminController');

// GET /api/admin/statistics
router.get('/statistics', adminController.getStatistics);

// POST /api/admin/documents (Method B: Ingest URL)
router.post('/documents', adminController.ingestUrl);

// POST /api/admin/process (Batch processing)
router.post('/process', adminController.processDirectory);

module.exports = router;
