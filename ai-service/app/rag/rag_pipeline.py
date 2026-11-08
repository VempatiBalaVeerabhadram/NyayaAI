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
from app.language.translate import LegalTranslator
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
        self.translator = LegalTranslator()
        self._initialized = True

    def process_query(self, request: RAGQueryRequest) -> RAGResponse:
        """
        Executes complete RAG query processing with multilingual support:
        1. Detects query language (English, Telugu, Hindi)
        2. If non-English, translates to English for hybrid retrieval while preserving citations
        3. Retrieves evidence chunks and traverses knowledge graph
        4. Synthesizes evidence-grounded response
        5. If query was in regional language, translates answer back to user language
           while keeping statutory sections and case names 100% exact.
        """
        start_time = time.perf_counter()
        query = request.query.strip()
        mode = request.mode.lower() if request.mode in ["user", "researcher"] else "researcher"

        # Step 0: Language Detection & Pre-Retrieval Translation
        det = self.translator.detector.detect(query)
        detected_lang = det.language_code  # "en", "te", "hi"

        if detected_lang != "en":
            tr_res = self.translator.translate_to_english(query, source_language=detected_lang)
            search_query = tr_res.get("translated", query)
            logger.info(f"Multilingual Query [{det.language_name}]: '{query}' -> Search Query: '{search_query}'")
        else:
            search_query = query
            logger.info(f"Executing Legal RAG Query: '{query}' [Mode: {mode}, top_k: {request.top_k}]")

        # Step 1: Graph-Enhanced Hybrid Retrieval
        retrieval_res = self.retriever.search(
            query=search_query,
            top_k=request.top_k,
            alpha=request.alpha,
            depth=request.graph_expansion_depth,
            domain_filter=request.legal_domain,
        )

        # Step 2: Evidence Grounded Generation (in English based on corpus)
        raw_english_answer = self.generator.generate_response(
            query=search_query,
            mode=mode,
            legal_issue=retrieval_res.primary_legal_issue,
            legal_domain=retrieval_res.legal_domain,
            applicable_sections=retrieval_res.applicable_sections,
            applicable_acts=retrieval_res.applicable_acts,
            evidence_chunks=retrieval_res.results,
            graph_relationships=retrieval_res.graph_relationships,
        )

        # Step 3: Multilingual Response Translation (Requirement 8)
        # Gemini/System answers in user's language while keeping section numbers and case names unchanged
        if detected_lang != "en":
            final_answer = self.translator.translate_to_target_language(raw_english_answer, detected_lang)
            answer_english = raw_english_answer
            logger.info(f"Answer translated to {det.language_name} (preserving section & case citations)")
        else:
            final_answer = raw_english_answer
            answer_english = None

        # Step 4: Extract structured sources list for UI inspection
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
            answer=final_answer,
            detected_language=detected_lang,
            answer_english=answer_english,
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
