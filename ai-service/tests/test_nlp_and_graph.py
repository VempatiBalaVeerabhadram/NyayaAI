"""
NyayaAI — Tests for InLegalBERT Query Understanding & Knowledge Graph Engine
Tests:
- Query classification, concept and section extraction
- Graph construction, node counts, and relationship integrity
- Subgraph extraction and graph-enhanced hybrid retrieval
"""

import pytest
import os
import sys
from fastapi.testclient import TestClient

# Add ai-service to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app
from app.nlp.query_analyzer import LegalQueryAnalyzer
from app.knowledge_graph.graph_builder import LegalGraphManager
from app.retrieval.graph_retriever import LegalGraphEnhancedRetriever

client = TestClient(app)


@pytest.fixture(scope="module")
def analyzer():
    return LegalQueryAnalyzer()


@pytest.fixture(scope="module")
def graph_manager():
    manager = LegalGraphManager()
    manager.build_graph_from_metadata()
    return manager


@pytest.fixture(scope="module")
def graph_retriever():
    return LegalGraphEnhancedRetriever()


def test_query_analysis_anticipatory_bail(analyzer):
    query = "What is the procedure for seeking anticipatory bail under Section 438 CrPC?"
    res = analyzer.analyze_query(query)

    assert res.primary_legal_issue == "Anticipatory Bail"
    assert "438" in res.referenced_sections
    assert res.legal_domain == "Criminal Law"
    assert "Anticipatory Bail" in res.extracted_concepts


def test_query_analysis_cybercrime(analyzer):
    query = "Is Section 66A of the Information Technology Act valid for online posts?"
    res = analyzer.analyze_query(query)

    assert res.legal_domain == "Cyber Law"
    assert "66A" in res.referenced_sections or "66a" in [s.lower() for s in res.referenced_sections]
    assert "Section 66A" in res.extracted_concepts or "Cyber" in res.extracted_concepts or "Information Technology Act" in res.extracted_concepts


def test_knowledge_graph_structure(graph_manager):
    overview = graph_manager.get_overview()
    assert overview.total_nodes >= 50
    assert overview.total_relationships >= 50
    assert "Case" in overview.node_counts_by_label
    assert "Section" in overview.node_counts_by_label
    assert "Act" in overview.node_counts_by_label
    assert "CITES" in overview.relationship_counts_by_type
    assert "DISCUSSES" in overview.relationship_counts_by_type


def test_case_subgraph_retrieval(graph_manager):
    # Find a real case id in graph
    cases = [n for n, d in graph_manager.graph.nodes(data=True) if d.get("label") == "Case"]
    assert len(cases) > 0
    test_case_id = cases[0]

    subgraph = graph_manager.get_case_subgraph(test_case_id, depth=1)
    assert subgraph.total_nodes > 0
    assert subgraph.total_relationships >= 0
    assert any(n.id == test_case_id for n in subgraph.nodes)


def test_graph_enhanced_hybrid_retrieval(graph_retriever):
    query = "Landmark judgments on anticipatory bail and personal liberty"
    response = graph_retriever.search(query=query, top_k=5, alpha=0.5, depth=1)

    assert response.total_results > 0
    assert len(response.results) <= 5
    assert len(response.applicable_sections) > 0
    # Should include connected precedents and graph relationships
    assert isinstance(response.connected_precedents, list)
    assert isinstance(response.graph_relationships, list)


def test_api_nlp_endpoint():
    payload = {"query": "Can police arrest without notice under Section 41A?"}
    response = client.post("/ai/nlp/analyze-query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "primary_legal_issue" in data
    assert "41A" in data["referenced_sections"] or "41a" in [s.lower() for s in data["referenced_sections"]]


def test_api_graph_overview_and_search():
    # Overview
    ov_res = client.get("/ai/graph/overview")
    assert ov_res.status_code == 200
    ov_data = ov_res.json()
    assert ov_data["total_nodes"] > 0

    # Graph-Enhanced Search
    search_payload = {
        "query": "Bail is rule jail is exception Section 439",
        "top_k": 5,
        "alpha": 0.5,
        "graph_expansion_depth": 1,
    }
    search_res = client.post("/ai/graph/search", json=search_payload)
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert search_data["total_results"] > 0
    assert "graph_relationships" in search_data
