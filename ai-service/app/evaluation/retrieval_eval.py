"""
Evaluation Engine for NyayaAI Retrieval Subsystems.
Evaluates BM25, Dense Semantic, Convex Hybrid, and Graph-Enhanced Hybrid retrievers
using standard Information Retrieval metrics (P@K, R@K, MRR, MAP, NDCG@K).
"""

import json
import math
import os
from typing import Dict, List, Any, Optional
from loguru import logger

from app.retrieval.bm25_retriever import LegalBM25Retriever
from app.retrieval.semantic_retriever import LegalSemanticRetriever
from app.retrieval.hybrid_retriever import LegalHybridRetriever
from app.retrieval.graph_retriever import LegalGraphEnhancedRetriever


def precision_at_k(retrieved_doc_ids: List[str], relevant_doc_ids: List[str], k: int) -> float:
    """Compute Precision@K."""
    if k <= 0:
        return 0.0
    top_k = retrieved_doc_ids[:k]
    rel_set = set(relevant_doc_ids)
    hits = sum(1 for doc_id in top_k if doc_id in rel_set)
    return hits / k


def recall_at_k(retrieved_doc_ids: List[str], relevant_doc_ids: List[str], k: int) -> float:
    """Compute Recall@K."""
    if not relevant_doc_ids:
        return 0.0
    top_k = retrieved_doc_ids[:k]
    rel_set = set(relevant_doc_ids)
    hits = sum(1 for doc_id in top_k if doc_id in rel_set)
    return hits / len(rel_set)


def reciprocal_rank(retrieved_doc_ids: List[str], relevant_doc_ids: List[str]) -> float:
    """Compute Reciprocal Rank (RR) for the first relevant document."""
    rel_set = set(relevant_doc_ids)
    for rank, doc_id in enumerate(retrieved_doc_ids, start=1):
        if doc_id in rel_set:
            return 1.0 / rank
    return 0.0


def average_precision(retrieved_doc_ids: List[str], relevant_doc_ids: List[str], k: int = 10) -> float:
    """Compute Average Precision at K."""
    if not relevant_doc_ids:
        return 0.0
    rel_set = set(relevant_doc_ids)
    hits = 0
    sum_precisions = 0.0
    top_k = retrieved_doc_ids[:k]
    for i, doc_id in enumerate(top_k, start=1):
        if doc_id in rel_set:
            hits += 1
            sum_precisions += hits / i
    return sum_precisions / min(len(rel_set), k) if rel_set else 0.0


def ndcg_at_k(retrieved_doc_ids: List[str], relevant_doc_ids: List[str], k: int = 10) -> float:
    """Compute Normalized Discounted Cumulative Gain at K (binary relevance)."""
    if not relevant_doc_ids:
        return 0.0
    rel_set = set(relevant_doc_ids)
    top_k = retrieved_doc_ids[:k]

    # DCG
    dcg = 0.0
    for i, doc_id in enumerate(top_k, start=1):
        rel = 1.0 if doc_id in rel_set else 0.0
        dcg += rel / math.log2(i + 1)

    # IDCG (ideal DCG)
    ideal_hits = min(len(rel_set), k)
    idcg = sum(1.0 / math.log2(i + 1) for i in range(1, ideal_hits + 1))

    if idcg == 0.0:
        return 0.0
    return dcg / idcg


class RetrievalEvaluator:
    """
    Comprehensive Benchmark Evaluator for NyayaAI Retrieval pipeline.
    """

    def __init__(
        self,
        bm25_retriever: Optional[LegalBM25Retriever] = None,
        semantic_retriever: Optional[LegalSemanticRetriever] = None,
        hybrid_retriever: Optional[LegalHybridRetriever] = None,
        graph_retriever: Optional[LegalGraphEnhancedRetriever] = None,
    ):
        self.bm25 = bm25_retriever or LegalBM25Retriever()
        self.semantic = semantic_retriever or LegalSemanticRetriever()
        self.hybrid = hybrid_retriever or LegalHybridRetriever()
        self.graph_retriever = graph_retriever or LegalGraphEnhancedRetriever()

    def _extract_unique_doc_ids(self, items: List[Any]) -> List[str]:
        """Extract ordered unique document IDs from retrieved items."""
        doc_ids = []
        seen = set()
        for r in items:
            if hasattr(r, "document_id"):
                doc_id = r.document_id
            elif isinstance(r, dict):
                doc_id = r.get("document_id") or r.get("metadata", {}).get("document_id")
            else:
                doc_id = None

            if doc_id and doc_id not in seen:
                seen.add(doc_id)
                doc_ids.append(doc_id)
        return doc_ids

    def evaluate_query(
        self, query: str, relevant_doc_ids: List[str], top_k: int = 10
    ) -> Dict[str, Dict[str, float]]:
        """Evaluate a single query across all 4 retrieval modes."""
        # 1. BM25 Lexical
        bm25_res = self.bm25.search(query, top_k=top_k * 2)
        bm25_docs = self._extract_unique_doc_ids(bm25_res)

        # 2. Dense Semantic
        dense_res = self.semantic.search(query, top_k=top_k * 2)
        dense_docs = self._extract_unique_doc_ids(dense_res)

        # 3. Convex Hybrid
        hybrid_res = self.hybrid.search(query, top_k=top_k * 2, alpha=0.5)
        hybrid_docs = self._extract_unique_doc_ids(hybrid_res)

        # 4. Graph-Enhanced Hybrid
        graph_res = self.graph_retriever.search(query, top_k=top_k * 2)
        fused = getattr(graph_res, "results", [])
        graph_docs = self._extract_unique_doc_ids(fused)

        methods = {
            "BM25_Lexical": bm25_docs,
            "Dense_Semantic": dense_docs,
            "Convex_Hybrid": hybrid_docs,
            "Graph_Enhanced_Hybrid": graph_docs,
        }

        query_metrics = {}
        for name, retrieved_docs in methods.items():
            query_metrics[name] = {
                "P@1": round(precision_at_k(retrieved_docs, relevant_doc_ids, 1), 4),
                "P@3": round(precision_at_k(retrieved_docs, relevant_doc_ids, 3), 4),
                "P@5": round(precision_at_k(retrieved_docs, relevant_doc_ids, 5), 4),
                "R@5": round(recall_at_k(retrieved_docs, relevant_doc_ids, 5), 4),
                "R@10": round(recall_at_k(retrieved_docs, relevant_doc_ids, 10), 4),
                "MRR": round(reciprocal_rank(retrieved_docs, relevant_doc_ids), 4),
                "MAP@10": round(average_precision(retrieved_docs, relevant_doc_ids, 10), 4),
                "NDCG@5": round(ndcg_at_k(retrieved_docs, relevant_doc_ids, 5), 4),
                "NDCG@10": round(ndcg_at_k(retrieved_docs, relevant_doc_ids, 10), 4),
            }

        return query_metrics

    def run_benchmark(self, benchmark_file: str) -> Dict[str, Any]:
        """Run complete benchmark against a JSON file of test queries."""
        with open(benchmark_file, "r", encoding="utf-8") as f:
            queries = json.load(f)

        logger.info(f"Running retrieval benchmark on {len(queries)} evaluation queries...")
        per_query_results = []
        method_names = ["BM25_Lexical", "Dense_Semantic", "Convex_Hybrid", "Graph_Enhanced_Hybrid"]
        metric_keys = ["P@1", "P@3", "P@5", "R@5", "R@10", "MRR", "MAP@10", "NDCG@5", "NDCG@10"]

        accumulators = {m: {k: 0.0 for k in metric_keys} for m in method_names}

        for q in queries:
            q_id = q.get("query_id")
            q_text = q.get("query")
            relevant = q.get("relevant_doc_ids", [])

            metrics = self.evaluate_query(q_text, relevant)
            per_query_results.append({
                "query_id": q_id,
                "query": q_text,
                "category": q.get("category", ""),
                "metrics": metrics,
            })

            for m in method_names:
                for k in metric_keys:
                    accumulators[m][k] += metrics[m][k]

        num_queries = len(queries)
        mean_metrics = {}
        for m in method_names:
            mean_metrics[m] = {
                k: round(accumulators[m][k] / max(num_queries, 1), 4) for k in metric_keys
            }

        return {
            "num_queries": num_queries,
            "mean_metrics": mean_metrics,
            "per_query_results": per_query_results,
        }
