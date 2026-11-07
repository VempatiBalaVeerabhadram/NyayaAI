"""
NyayaAI — Hybrid Retrieval Engine
Combines BM25 lexical keyword retrieval and Dense Semantic Vector retrieval
using a configurable convex combination:
    Hybrid Score = alpha * BM25_score + (1 - alpha) * Semantic_score
"""

from typing import List, Dict, Any, Optional
from loguru import logger

from app.config import settings
from app.retrieval.bm25_retriever import LegalBM25Retriever
from app.retrieval.semantic_retriever import LegalSemanticRetriever
from app.retrieval.intent import IntentClassifier
from app.models.retrieval import RetrievedChunkItem


class LegalHybridRetriever:
    """Hybrid Retrieval combining lexical BM25 and dense semantic vector search with intent-adaptive alpha."""

    def __init__(self, default_alpha: Optional[float] = None):
        self.default_alpha = default_alpha if default_alpha is not None else settings.hybrid_alpha
        self.bm25 = LegalBM25Retriever()
        self.semantic = LegalSemanticRetriever()
        self.intent_classifier = IntentClassifier()

    def search(
        self,
        query: str,
        top_k: int = 10,
        alpha: Optional[float] = None,
        domain_filter: Optional[str] = None,
        document_type_filter: Optional[str] = None,
        auto_intent: bool = True,
    ) -> List[RetrievedChunkItem]:
        """
        Executes hybrid retrieval by fusing BM25 and Semantic search results.
        If alpha is None and auto_intent is True, the alpha is determined dynamically
        by the intent classifier (statute_lookup=0.70, case_narrative=0.30, mixed=0.50).
        """
        if alpha is not None:
            effective_alpha = max(0.0, min(1.0, float(alpha)))
            intent_info = {"intent": "manual", "alpha": effective_alpha}
        elif auto_intent:
            intent_result = self.intent_classifier.classify(query)
            effective_alpha = intent_result.get("alpha", self.default_alpha)
            intent_info = intent_result
            logger.info(f"Dynamic intent: {intent_result.get('intent')} -> alpha={effective_alpha}")
        else:
            effective_alpha = self.default_alpha
            intent_info = {"intent": "default", "alpha": effective_alpha}

        # Retrieve larger candidate pools for robust fusion
        candidate_k = max(top_k * 2, 20)

        bm25_results = self.bm25.search(
            query=query,
            top_k=candidate_k,
            domain_filter=domain_filter,
            document_type_filter=document_type_filter,
        )

        semantic_results = self.semantic.search(
            query=query,
            top_k=candidate_k,
            domain_filter=domain_filter,
            document_type_filter=document_type_filter,
        )

        # Merge candidate pools by chunk_id
        merged_pool: Dict[str, Dict[str, Any]] = {}

        for item in bm25_results:
            merged_pool[item.chunk_id] = {
                "item": item,
                "bm25_score": item.bm25_score,
                "semantic_score": 0.0,
            }

        for item in semantic_results:
            if item.chunk_id in merged_pool:
                merged_pool[item.chunk_id]["semantic_score"] = item.semantic_score
            else:
                merged_pool[item.chunk_id] = {
                    "item": item,
                    "bm25_score": 0.0,
                    "semantic_score": item.semantic_score,
                }

        # Calculate hybrid scores
        ranked_candidates = []
        for chunk_id, data in merged_pool.items():
            b_score = data["bm25_score"]
            s_score = data["semantic_score"]
            h_score = (effective_alpha * b_score) + ((1.0 - effective_alpha) * s_score)
            ranked_candidates.append((h_score, b_score, s_score, data["item"]))

        # Sort descending by hybrid score
        ranked_candidates.sort(key=lambda x: x[0], reverse=True)

        # Assemble final results
        final_results: List[RetrievedChunkItem] = []
        for rank, (h_score, b_score, s_score, base_item) in enumerate(ranked_candidates[:top_k], start=1):
            final_results.append(
                RetrievedChunkItem(
                    chunk_id=base_item.chunk_id,
                    case_id=base_item.case_id,
                    case_name=base_item.case_name,
                    document_id=base_item.document_id,
                    page=base_item.page,
                    paragraph_number=base_item.paragraph_number,
                    text=base_item.text,
                    section=base_item.section,
                    legal_domain=base_item.legal_domain,
                    source_url=base_item.source_url,
                    bm25_score=round(b_score, 4),
                    semantic_score=round(s_score, 4),
                    hybrid_score=round(h_score, 4),
                    rank=rank,
                )
            )

        return final_results
