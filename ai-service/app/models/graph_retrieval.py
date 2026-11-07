"""
NyayaAI — Pydantic Schemas for Graph-Enhanced Hybrid Retrieval
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from app.models.retrieval import RetrievedChunkItem


class GraphEnhancedSearchRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Legal search query or issue description")
    top_k: int = Field(10, ge=1, le=50, description="Final number of evidence chunks")
    alpha: float = Field(0.5, ge=0.0, le=1.0, description="BM25 vs Semantic weighting")
    graph_expansion_depth: int = Field(1, ge=1, le=2, description="Graph neighborhood traversal depth")
    legal_domain: Optional[str] = Field(None, description="Optional domain filter")
    document_type: Optional[str] = Field(None, description="Optional document type filter")


class GraphRelationshipTriple(BaseModel):
    source: str
    relationship: str
    target: str
    source_type: str = "Case"
    target_type: str = "Section"


class GraphEnhancedSearchResponse(BaseModel):
    query: str
    primary_legal_issue: str
    legal_domain: str
    total_results: int
    results: List[RetrievedChunkItem]
    connected_precedents: List[str]
    applicable_sections: List[str]
    applicable_acts: List[str]
    graph_relationships: List[GraphRelationshipTriple]
    execution_time_ms: float = 0.0
