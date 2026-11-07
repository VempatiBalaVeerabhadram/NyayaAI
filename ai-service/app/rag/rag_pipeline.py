"""
NyayaAI — Master RAG Pipeline Orchestrator
Coordinates the end-to-end Retrieval-Augmented Generation workflow:
1. InLegalBERT Query Understanding
2. Graph-Enhanced Hybrid Retrieval (BM25 + Dense Vectors + Knowledge Graph Expansion)
3. Verified Context Construction
4. Evidence-Grounded Gemini Generation
5. Provenance & Citation Verification
"""

import time
from typing import List, Dict, Any, Optional
from loguru import logger

from app.nlp.query_analyzer import LegalQueryAnalyzer
from app.retrieval.graph_retriever import LegalGraphEnhancedRetriever
from app.rag.generator import GeminiGenerator
from app.rag.prompt_templates import LEGAL_DISCLAIMER
from app.models.rag import (
    RAGQueryRequest,
    SourceCitationItem,
    RAGResponse,
)


class LegalRAGPipeline:
    """End-to-end evidence-first RAG pipeline for Indian legal intelligence."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(LegalRAGPipeline, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.analyzer = LegalQueryAnalyzer()
        self.retriever = LegalGraphEnhancedRetriever()
        self.generator = GeminiGenerator()
        self._initialized = True

    def process_query(self, request: RAGQueryRequest) -> RAGResponse:
        """
        Executes complete RAG query processing.
        """
        start_time = time.perf_counter()
        query = request.query.strip()
        mode = request.mode.lower() if request.mode in ["user", "researcher"] else "researcher"

        logger.info(f"Executing Legal RAG Query: '{query}' [Mode: {mode}, top_k: {request.top_k}]")

        # Step 1: Graph-Enhanced Hybrid Retrieval
        retrieval_res = self.retriever.search(
            query=query,
            top_k=request.top_k,
            alpha=request.alpha,
            depth=request.graph_expansion_depth,
            domain_filter=request.legal_domain,
        )

        # Step 2: Evidence Grounded Generation
        generated_answer = self.generator.generate_response(
            query=query,
            mode=mode,
            legal_issue=retrieval_res.primary_legal_issue,
            legal_domain=retrieval_res.legal_domain,
            applicable_sections=retrieval_res.applicable_sections,
            applicable_acts=retrieval_res.applicable_acts,
            evidence_chunks=retrieval_res.results,
            graph_relationships=retrieval_res.graph_relationships,
        )

        # Step 3: Extract structured sources list for UI inspection
        sources: List[SourceCitationItem] = []
        for chunk in retrieval_res.results:
            sources.append(
                SourceCitationItem(
                    case_name=chunk.case_name,
                    page=chunk.page,
                    paragraph_number=chunk.paragraph_number,
                    section=chunk.section,
                    court=chunk.section,
                    source_url=chunk.source_url,
                    chunk_id=chunk.chunk_id,
                )
            )

        unique_judgments = list(dict.fromkeys([c.case_name for c in retrieval_res.results if c.case_name]))
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return RAGResponse(
            query=query,
            mode=mode,
            legal_issue=retrieval_res.primary_legal_issue,
            legal_domain=retrieval_res.legal_domain,
            answer=generated_answer,
            applicable_sections=retrieval_res.applicable_sections,
            applicable_acts=retrieval_res.applicable_acts,
            relevant_judgments=unique_judgments,
            evidence_chunks=retrieval_res.results,
            graph_relationships=retrieval_res.graph_relationships,
            sources=sources,
            disclaimer=LEGAL_DISCLAIMER,
            grounding_status="GROUNDED_IN_SOURCES",
            execution_time_ms=round(elapsed_ms, 2),
        )
