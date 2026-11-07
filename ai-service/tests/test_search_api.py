"""
NyayaAI — Search API Tests
Tests FastAPI retrieval endpoints: /ai/search/bm25, /ai/search/semantic, /ai/search/hybrid, /ai/search/rebuild-index.
"""

import pytest
import os
import sys
from fastapi.testclient import TestClient

# Add ai-service to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app

client = TestClient(app)


def test_api_search_bm25():
    payload = {
        "query": "bail under Section 439 CrPC",
        "top_k": 5,
    }
    response = client.post("/ai/search/bm25", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["retrieval_mode"] == "bm25"
    assert data["total_results"] > 0
    assert len(data["results"]) <= 5
    first = data["results"][0]
    assert "chunk_id" in first
    assert "bm25_score" in first


def test_api_search_semantic():
    payload = {
        "query": "freedom of speech on social media and cyber law",
        "top_k": 5,
    }
    response = client.post("/ai/search/semantic", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["retrieval_mode"] == "semantic"
    assert data["total_results"] > 0
    assert len(data["results"]) <= 5
    first = data["results"][0]
    assert "semantic_score" in first


def test_api_search_hybrid():
    payload = {
        "query": "guidelines for quashing FIR under Section 482",
        "top_k": 5,
        "alpha": 0.5,
    }
    response = client.post("/ai/search/hybrid", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["retrieval_mode"] == "hybrid"
    assert data["alpha"] == 0.5
    assert data["total_results"] > 0
    first = data["results"][0]
    assert "hybrid_score" in first
    assert "bm25_score" in first
    assert "semantic_score" in first


def test_api_rebuild_indexes():
    response = client.post("/ai/search/rebuild-index")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["bm25_indexed_chunks"] >= 30
    assert data["vector_indexed_chunks"] >= 30
    assert data["vector_backend"] in ["qdrant", "faiss"]
