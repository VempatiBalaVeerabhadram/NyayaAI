"""
NyayaAI — Search and Retrieval Endpoints
Provides BM25, Semantic Vector, and Hybrid search APIs.
"""

import time
from fastapi import APIRouter, HTTPException, status
from loguru import logger

from app.models.retrieval import (
    SearchRequest,
    SearchResponse,
    RebuildIndexResponse,
)
from app.retrieval.bm25_retriever import LegalBM25Retriever
from app.retrieval.semantic_retriever import LegalSemanticRetriever
from app.retrieval.hybrid_retriever import LegalHybridRetriever
from app.embeddings.embedding_service import EmbeddingService

router = APIRouter(prefix="/ai/search", tags=["Search & Retrieval"])

bm25_retriever = LegalBM25Retriever()
semantic_retriever = LegalSemanticRetriever()
hybrid_retriever = LegalHybridRetriever()
embedding_service = EmbeddingService()


@router.post("/bm25", response_model=SearchResponse, summary="BM25 Lexical Keyword Search")
async def search_bm25(request: SearchRequest):
    """Executes keyword-based BM25 retrieval over indexed legal chunks."""
    start_time = time.perf_counter()
    try:
        results = bm25_retriever.search(
            query=request.query,
            top_k=request.top_k,
            domain_filter=request.legal_domain,
            document_type_filter=request.document_type,
        )
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return SearchResponse(
            query=request.query,
            retrieval_mode="bm25",
            total_results=len(results),
            results=results,
            execution_time_ms=round(elapsed_ms, 2),
        )
    except Exception as e:
        logger.error(f"BM25 search error: {e}")
        raise HTTPException(status_code=500, detail=f"BM25 retrieval failed: {str(e)}")


@router.post("/semantic", response_model=SearchResponse, summary="Dense Semantic Vector Search")
async def search_semantic(request: SearchRequest):
    """Executes dense vector similarity search using Sentence Transformers and Qdrant/FAISS."""
    start_time = time.perf_counter()
    try:
        results = semantic_retriever.search(
            query=request.query,
            top_k=request.top_k,
            domain_filter=request.legal_domain,
            document_type_filter=request.document_type,
        )
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return SearchResponse(
            query=request.query,
            retrieval_mode="semantic",
            total_results=len(results),
            results=results,
            execution_time_ms=round(elapsed_ms, 2),
        )
    except Exception as e:
        logger.error(f"Semantic search error: {e}")
        raise HTTPException(status_code=500, detail=f"Semantic retrieval failed: {str(e)}")


@router.post("/hybrid", response_model=SearchResponse, summary="Hybrid (BM25 + Semantic) Retrieval")
async def search_hybrid(request: SearchRequest):
    """
    Executes hybrid retrieval combining BM25 keyword matching and dense vector search
    with configurable alpha weighting (default: 0.5).
    """
    start_time = time.perf_counter()
    try:
        results = hybrid_retriever.search(
            query=request.query,
            top_k=request.top_k,
            alpha=request.alpha,
            domain_filter=request.legal_domain,
            document_type_filter=request.document_type,
        )
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return SearchResponse(
            query=request.query,
            retrieval_mode="hybrid",
            total_results=len(results),
            alpha=request.alpha,
            results=results,
            execution_time_ms=round(elapsed_ms, 2),
        )
    except Exception as e:
        logger.error(f"Hybrid search error: {e}")
        raise HTTPException(status_code=500, detail=f"Hybrid retrieval failed: {str(e)}")


@router.post("/rebuild-index", response_model=RebuildIndexResponse, summary="Rebuild BM25 & Vector Indexes")
async def rebuild_indexes():
    """Rebuilds both the BM25 lexical index and the vector embeddings store for all chunks."""
    start_time = time.perf_counter()
    try:
        # Rebuild BM25
        bm25_retriever.load_and_index()
        bm25_count = len(bm25_retriever.corpus_chunks)

        # Rebuild Vector index
        vector_count = embedding_service.index_chunks()
        backend = "qdrant" if embedding_service.use_qdrant else "faiss"

        elapsed_sec = time.perf_counter() - start_time

        return RebuildIndexResponse(
            status="SUCCESS",
            bm25_indexed_chunks=bm25_count,
            vector_indexed_chunks=vector_count,
            vector_backend=backend,
            execution_time_seconds=round(elapsed_sec, 2),
        )
    except Exception as e:
        logger.error(f"Index rebuild failed: {e}")
        raise HTTPException(status_code=500, detail=f"Index rebuild failed: {str(e)}")
