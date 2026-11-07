const express = require('express');
const router = express.Router();
const caseController = require('../controllers/caseController');

// GET /api/cases
router.get('/', caseController.getCases);

// GET /api/cases/:id
router.get('/:id', caseController.getCaseById);

// GET /api/cases/:id/citations
router.get('/:id/citations', caseController.getCaseCitations);

module.exports = router;
