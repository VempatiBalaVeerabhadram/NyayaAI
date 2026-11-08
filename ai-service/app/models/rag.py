"""
NyayaAI — Pydantic Schemas for RAG & Evidence-Grounded Legal Generation
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from app.models.retrieval import RetrievedChunkItem
from app.models.graph_retrieval import GraphRelationshipTriple


class RAGQueryRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Legal question or inquiry")
    mode: str = Field("researcher", description="'user' (simple assistance) or 'researcher' (detailed legal research)")
    top_k: int = Field(5, ge=1, le=20, description="Number of evidence chunks to provide to LLM")
    alpha: float = Field(0.5, ge=0.0, le=1.0, description="Hybrid retrieval balance parameter")
    graph_expansion_depth: int = Field(1, ge=1, le=2, description="Knowledge graph traversal depth")
    legal_domain: Optional[str] = Field(None, description="Optional domain filter")


class SourceCitationItem(BaseModel):
    case_name: str
    page: int
    paragraph_number: str
    section: str
    court: str
    source_url: str
    chunk_id: str


class RAGResponse(BaseModel):
    query: str
    mode: str
    legal_issue: str
    legal_domain: str
    answer: str
    detected_language: str = "en"
    answer_english: Optional[str] = None
    applicable_sections: List[str]
    applicable_acts: List[str]
    relevant_judgments: List[str]
    evidence_chunks: List[RetrievedChunkItem]
    graph_relationships: List[GraphRelationshipTriple]
    sources: List[SourceCitationItem]
    disclaimer: str
    grounding_status: str = "GROUNDED_IN_SOURCES"
    execution_time_ms: float = 0.0
