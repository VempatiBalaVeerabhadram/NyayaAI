/**
 * NyayaAI — Knowledge Graph Controller
 * Serves graph topology, neighborhood subgraphs, and expansion APIs to the frontend.
 */

const axios = require('axios');
const fs = require('fs');
const path = require('path');
const logger = require('../utils/logger');

const AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://localhost:8000';
const GRAPH_DIR = path.resolve(__dirname, '../../../data/knowledge_graph');

/**
 * Get Knowledge Graph Overview Metrics
 */
exports.getGraphOverview = async (req, res, next) => {
  try {
    try {
      const response = await axios.get(`${AI_SERVICE_URL}/ai/graph/overview`, { timeout: 5000 });
      return res.status(200).json({
        success: true,
        data: response.data,
      });
    } catch (aiErr) {
      logger.warn(`AI service unreachable for graph overview, reading local cache: ${aiErr.message}`);
    }

    // Local fallback
    const nodesFile = path.join(GRAPH_DIR, 'graph_nodes.json');
    const edgesFile = path.join(GRAPH_DIR, 'graph_edges.json');

    if (fs.existsSync(nodesFile) && fs.existsSync(edgesFile)) {
      const nodes = JSON.parse(fs.readFileSync(nodesFile, 'utf-8'));
      const edges = JSON.parse(fs.readFileSync(edgesFile, 'utf-8'));

      const nodeCounts = {};
      nodes.forEach((n) => {
        nodeCounts[n.label] = (nodeCounts[n.label] || 0) + 1;
      });

      const relCounts = {};
      edges.forEach((e) => {
        relCounts[e.type] = (relCounts[e.type] || 0) + 1;
      });

      return res.status(200).json({
        success: true,
        data: {
          total_nodes: nodes.length,
          total_relationships: edges.length,
          node_counts_by_label: nodeCounts,
          relationship_counts_by_type: relCounts,
          active_backend: 'local_cache',
        },
      });
    }

    res.status(200).json({
      success: true,
      data: { total_nodes: 0, total_relationships: 0, node_counts_by_label: {}, relationship_counts_by_type: {} },
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Get Subgraph for a specific case
 */
exports.getCaseSubgraph = async (req, res, next) => {
  try {
    const { id } = req.params;
    const depth = parseInt(req.query.depth, 10) || 1;

    try {
      const response = await axios.get(`${AI_SERVICE_URL}/ai/graph/case/${id}`, {
        params: { depth },
        timeout: 8000,
      });
      return res.status(200).json({
        success: true,
        data: response.data,
      });
    } catch (aiErr) {
      if (aiErr.response && aiErr.response.status === 404) {
        return res.status(404).json({ success: false, message: `Node not found: ${id}` });
      }
      logger.warn(`AI service fetch failed for case subgraph ${id}: ${aiErr.message}`);
    }

    // Local fallback
    const nodesFile = path.join(GRAPH_DIR, 'graph_nodes.json');
    const edgesFile = path.join(GRAPH_DIR, 'graph_edges.json');

    if (!fs.existsSync(nodesFile)) {
      return res.status(404).json({ success: false, message: 'Knowledge graph not initialized' });
    }

    const nodes = JSON.parse(fs.readFileSync(nodesFile, 'utf-8'));
    const edges = JSON.parse(fs.readFileSync(edgesFile, 'utf-8'));

    const rootNode = nodes.find((n) => n.id === id || n.properties.name === id);
    if (!rootNode) {
      return res.status(404).json({ success: false, message: `Case not found in graph: ${id}` });
    }

    const matchedEdges = edges.filter((e) => e.source_id === rootNode.id || e.target_id === rootNode.id);
    const connectedNodeIds = new Set([rootNode.id]);
    matchedEdges.forEach((e) => {
      connectedNodeIds.add(e.source_id);
      connectedNodeIds.add(e.target_id);
    });

    const matchedNodes = nodes.filter((n) => connectedNodeIds.has(n.id));

    res.status(200).json({
      success: true,
      data: {
        root_node_id: rootNode.id,
        depth: 1,
        nodes: matchedNodes,
        relationships: matchedEdges,
        total_nodes: matchedNodes.length,
        total_relationships: matchedEdges.length,
      },
    });
  } catch (error) {
    next(error);
  }
};
