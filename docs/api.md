# NyayaAI REST API Reference

## Base URLs
- **Node.js Gateway:** `http://localhost:5000/api`
- **Python AI Microservice:** `http://localhost:8000/ai`

---

## 1. System & Health

### `GET /api/health`
Probes MongoDB, AI Microservice, Qdrant, and Neo4j connectivity.
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2026-09-29T18:30:00Z",
    "services": {
      "mongodb": { "status": "connected" },
      "aiService": { "status": "connected" },
      "qdrant": { "status": "connected", "collections": 1 },
      "neo4j": { "status": "connected" }
    }
  },
  "message": "Health check completed"
}
```

---

## 2. Query & Search

### `POST /api/query`
Main RAG inference endpoint.
**Request:**
```json
{
  "query": "What are the principles for grant of anticipatory bail?",
  "mode": "researcher",
  "alpha": 0.5,
  "top_k": 10
}
```
**Response:**
```json
{
  "success": true,
  "data": {
    "legal_issue": "Anticipatory Bail under Section 438 CrPC",
    "answer": {
      "summary": "...",
      "relevant_provisions": [...],
      "relevant_judgments": [...],
      "analysis": "...",
      "sources": [...]
    },
    "retrieved_cases": [...],
    "graph_relationships": [...],
    "scores": {
      "bm25": [...],
      "semantic": [...],
      "hybrid": [...]
    }
  },
  "message": "Query processed successfully"
}
```

---

## 3. Case & Statute Exploration

- `GET /api/cases`: Paginated list of indexed judgments with filters (`court`, `year`, `domain`).
- `GET /api/cases/:id`: Detailed case summary, ratio decidendi, citations, and full text with page navigation.
- `GET /api/cases/:id/graph`: Case precedent graph neighborhood (1-2 hops).
- `GET /api/acts`: Directory of Indian Central and State Acts.
- `GET /api/acts/:id`: Act details and section hierarchy.
- `GET /api/sections/:id`: Full statutory section text with jurisprudence cross-references.

---

## 4. Admin Management

- `POST /api/admin/documents/upload`: Multipart upload for legal PDFs / JSON.
- `POST /api/admin/process`: Triggers ingestion pipeline for pending records.
- `GET /api/admin/statistics`: Document counts, chunk statistics, vector collection size, and Neo4j node/edge counts.
