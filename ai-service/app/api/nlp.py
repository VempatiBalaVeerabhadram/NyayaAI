"""
NyayaAI — NLP & InLegalBERT Query Understanding Endpoints
"""

from fastapi import APIRouter, HTTPException, status
from loguru import logger

from app.models.nlp import QueryAnalysisRequest, QueryAnalysisResponse
from app.nlp.query_analyzer import LegalQueryAnalyzer

router = APIRouter(prefix="/ai/nlp", tags=["NLP & Query Understanding"])

analyzer = LegalQueryAnalyzer()


@router.post("/analyze-query", response_model=QueryAnalysisResponse, summary="Analyze Legal Query (InLegalBERT)")
async def analyze_query_endpoint(request: QueryAnalysisRequest):
    """
    Analyzes legal questions: extracts legal issues, statutory sections, acts,
    key concepts, and generates an expanded retrieval query.
    """
    try:
        result = analyzer.analyze_query(request.query)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Query analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query analysis failed: {str(e)}")
