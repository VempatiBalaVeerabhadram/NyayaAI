const express = require('express');
const router = express.Router();
const actController = require('../controllers/actController');

// GET /api/acts
router.get('/', actController.getActs);

// GET /api/acts/:id
router.get('/:id', actController.getActById);

module.exports = router;
