"""
NyayaAI — Pydantic Schemas for Legal Query Understanding (InLegalBERT)
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class QueryAnalysisRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Natural language legal query or factual scenario")


class QueryAnalysisResponse(BaseModel):
    original_query: str
    primary_legal_issue: str
    legal_domain: str
    query_type: str = Field("precedent_discovery", description="'precedent_discovery', 'statutory_inquiry', 'concept_explanation', 'case_connection'")
    extracted_concepts: List[str]
    referenced_acts: List[str]
    referenced_sections: List[str]
    referenced_articles: List[str]
    normalized_expanded_query: str
    confidence_score: float = 0.95
