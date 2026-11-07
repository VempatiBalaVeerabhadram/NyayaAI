const express = require('express');
const router = express.Router();
const graphController = require('../controllers/graphController');

// GET /api/graph/overview
router.get('/overview', graphController.getGraphOverview);

// GET /api/graph/case/:id
router.get('/case/:id', graphController.getCaseSubgraph);

module.exports = router;
