const express = require('express');
const router = express.Router();
const queryController = require('../controllers/queryController');

// POST /api/query
router.post('/', queryController.query);

module.exports = router;
