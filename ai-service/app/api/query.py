"""
NyayaAI — RAG Query & Legal Assistance Endpoints
"""

from fastapi import APIRouter, HTTPException, status
from loguru import logger

from app.models.rag import RAGQueryRequest, RAGResponse
from app.rag.rag_pipeline import LegalRAGPipeline

router = APIRouter(prefix="/ai/query", tags=["Legal Q&A & RAG"])

pipeline = LegalRAGPipeline()


@router.post("", response_model=RAGResponse, summary="Execute Grounded Legal RAG Query")
async def execute_rag_query(request: RAGQueryRequest):
    """
    Retrieval-First, Evidence-Grounded Legal Intelligence Pipeline.
    1. Understands legal question via InLegalBERT
    2. Performs multi-stage Hybrid Retrieval (BM25 + Semantic Search)
    3. Expands precedent context using Knowledge Graph (depth 1–2)
    4. Generates structured response via Gemini grounded strictly in retrieved sources
    5. Formats response according to requested mode (User vs Researcher)
    """
    try:
        return pipeline.process_query(request)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"RAG query execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Legal query processing failed: {str(e)}")
