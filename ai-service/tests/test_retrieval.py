"""
NyayaAI — Retrieval Engine Unit Tests
Tests BM25 lexical retriever, Dense Semantic Vector retriever, and Hybrid Fusion retriever.
"""

import pytest
import os
import sys

# Add ai-service to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.retrieval.bm25_retriever import LegalBM25Retriever
from app.embeddings.embedding_service import EmbeddingService
from app.retrieval.semantic_retriever import LegalSemanticRetriever
from app.retrieval.hybrid_retriever import LegalHybridRetriever


@pytest.fixture(scope="module")
def embedding_service():
    service = EmbeddingService()
    # Check if index already has chunks; if not, build it
    if hasattr(service, "faiss_index") and service.faiss_index is not None and service.faiss_index.ntotal > 0:
        return service
    service.index_chunks()
    return service


@pytest.fixture(scope="module")
def bm25_retriever():
    retriever = LegalBM25Retriever()
    retriever.load_and_index()
    return retriever


@pytest.fixture(scope="module")
def semantic_retriever():
    return LegalSemanticRetriever()


@pytest.fixture(scope="module")
def hybrid_retriever():
    return LegalHybridRetriever()


def test_bm25_anticipatory_bail_retrieval(bm25_retriever):
    query = "What judgments discuss anticipatory bail under Section 438?"
    results = bm25_retriever.search(query=query, top_k=5)
    assert len(results) > 0
    # Should retrieve anticipatory bail landmark cases
    case_names = [r.case_name.lower() for r in results]
    assert any("sushila aggarwal" in name or "sibbia" in name or "antil" in name for name in case_names)
    assert results[0].bm25_score >= 0.0
    assert results[0].bm25_score <= 1.0


def test_bm25_cheating_property_retrieval(bm25_retriever):
    query = "criminal breach of trust and cheating section 420 IPC"
    results = bm25_retriever.search(query=query, top_k=5)
    assert len(results) > 0
    top_text = " ".join([r.text.lower() for r in results])
    assert "cheating" in top_text or "420" in top_text or "trust" in top_text


def test_semantic_embedding_dimensions(embedding_service):
    query = "grant of bail in economic offences"
    vec = embedding_service.embed_query(query)
    assert vec.shape == (1, embedding_service.vector_dim)
    assert vec.dtype.name == "float32"


def test_semantic_retrieval(semantic_retriever):
    query = "Can the court quash criminal proceedings if parties reach a settlement?"
    results = semantic_retriever.search(query=query, top_k=5)
    assert len(results) > 0
    assert results[0].semantic_score >= 0.0
    assert results[0].semantic_score <= 1.0
    # Should find Gian Singh / Bhajan Lal / Neeharika
    matched_names = [r.case_name.lower() for r in results]
    assert any("gian singh" in m or "bhajan lal" in m or "neeharika" in m for m in matched_names)


def test_hybrid_retrieval_fusion(hybrid_retriever):
    query = "guidelines to prevent unnecessary arrest by police under Section 41A"
    results_05 = hybrid_retriever.search(query=query, top_k=5, alpha=0.5)
    assert len(results_05) > 0
    top_result = results_05[0]
    assert top_result.hybrid_score > 0.0
    assert top_result.bm25_score >= 0.0
    assert top_result.semantic_score >= 0.0
    # Check Arnesh Kumar / Satender Antil is in the results
    names = [r.case_name.lower() for r in results_05]
    assert any("arnesh kumar" in n or "satender" in n for n in names)


def test_hybrid_alpha_sensitivity(hybrid_retriever):
    query = "Section 66A Information Technology Act unconstitutional"
    results_bm25_heavy = hybrid_retriever.search(query=query, top_k=5, alpha=0.9)
    results_semantic_heavy = hybrid_retriever.search(query=query, top_k=5, alpha=0.1)

    assert len(results_bm25_heavy) > 0
    assert len(results_semantic_heavy) > 0
    # Both should retrieve Shreya Singhal
    assert any("shreya singhal" in r.case_name.lower() for r in results_bm25_heavy)
    assert any("shreya singhal" in r.case_name.lower() for r in results_semantic_heavy)
