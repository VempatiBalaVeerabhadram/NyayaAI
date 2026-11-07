"""
NyayaAI — Pydantic Schemas for Retrieval & Search
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Legal question or search query")
    top_k: int = Field(10, ge=1, le=50, description="Number of results to retrieve")
    alpha: float = Field(0.5, ge=0.0, le=1.0, description="Weight for BM25 (1-alpha for Semantic)")
    legal_domain: Optional[str] = Field(None, description="Optional filter by legal domain (e.g. Criminal Law)")
    document_type: Optional[str] = Field(None, description="Optional filter: 'judgment' or 'act'")


class RetrievedChunkItem(BaseModel):
    chunk_id: str
    case_id: str
    case_name: str
    document_id: str
    page: int
    paragraph_number: str
    text: str
    section: str
    legal_domain: str
    source_url: str
    bm25_score: float = 0.0
    semantic_score: float = 0.0
    hybrid_score: float = 0.0
    rank: int = 1


class SearchResponse(BaseModel):
    query: str
    retrieval_mode: str = Field("hybrid", description="'bm25', 'semantic', or 'hybrid'")
    total_results: int
    alpha: Optional[float] = None
    results: List[RetrievedChunkItem]
    execution_time_ms: float = 0.0


class RebuildIndexResponse(BaseModel):
    status: str = "SUCCESS"
    bm25_indexed_chunks: int
    vector_indexed_chunks: int
    vector_backend: str = "qdrant"  # or "faiss"
    execution_time_seconds: float
