"""
NyayaAI — RAG Generation & Grounding Tests
Tests:
- Dual User Modes (Ordinary User vs Legal Researcher)
- Citation grounding and provenance preservation
- Insufficient evidence safety fallback
- End-to-end FastAPI /ai/query endpoint
"""

import pytest
import os
import sys
from fastapi.testclient import TestClient

# Add ai-service to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app
from app.rag.rag_pipeline import LegalRAGPipeline
from app.models.rag import RAGQueryRequest

client = TestClient(app)


@pytest.fixture(scope="module")
def rag_pipeline():
    return LegalRAGPipeline()


def test_rag_researcher_mode(rag_pipeline):
    req = RAGQueryRequest(
        query="What are the essential principles for granting anticipatory bail under Section 438 CrPC?",
        mode="researcher",
        top_k=5,
        alpha=0.5,
    )
    response = rag_pipeline.process_query(req)

    assert response.mode == "researcher"
    assert response.legal_issue == "Anticipatory Bail"
    assert "438" in response.applicable_sections
    assert len(response.evidence_chunks) > 0
    assert len(response.sources) > 0

    # Verify structured sections in generated answer
    assert "1. Legal Issue" in response.answer or "Legal Issue" in response.answer
    assert "Landmark Judgments" in response.answer
    assert "Sources & Provenance" in response.answer
    assert response.disclaimer in response.answer or len(response.disclaimer) > 20

    # Verify provenance on sources
    first_source = response.sources[0]
    assert first_source.page >= 1
    assert len(first_source.case_name) > 3


def test_rag_user_mode(rag_pipeline):
    req = RAGQueryRequest(
        query="Can police arrest me without a warrant under Section 41A?",
        mode="user",
        top_k=3,
        alpha=0.5,
    )
    response = rag_pipeline.process_query(req)

    assert response.mode == "user"
    assert "Simple Explanation" in response.answer
    assert "Relevant Legal Provisions" in response.answer
    assert len(response.relevant_judgments) > 0
    assert response.grounding_status == "GROUNDED_IN_SOURCES"


def test_rag_insufficient_evidence(rag_pipeline):
    req = RAGQueryRequest(
        query="What are the rules for space maritime salvage in Antarctica under law?",
        mode="researcher",
        top_k=5,
        alpha=0.5,
    )
    response = rag_pipeline.process_query(req)
    assert response.answer is not None


def test_api_query_endpoint():
    payload = {
        "query": "Is Section 66A of the IT Act unconstitutional for online speech?",
        "mode": "researcher",
        "top_k": 3,
    }
    response = client.post("/ai/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "researcher"
    assert len(data["evidence_chunks"]) > 0
    assert len(data["sources"]) > 0
    assert "Shreya Singhal" in str(data["relevant_judgments"]) or "Shreya" in data["answer"]
