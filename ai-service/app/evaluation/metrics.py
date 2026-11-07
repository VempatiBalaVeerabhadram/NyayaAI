"""
NyayaAI — Evaluation Metrics Engine
===================================
Calculates standard and domain-specific information retrieval & legal metrics:
- Precision@K, Recall@K
- Mean Reciprocal Rank (MRR)
- Normalized Discounted Cumulative Gain (nDCG@K)
- Citation Accuracy (percentage of valid citations)
- Hallucination Rate (percentage of unverified/fabricated citations)
- Temporal Correctness (correct law regime applied for the given query date)
"""

import math
import csv
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Any
from loguru import logger


@dataclass
class RetrievalMetrics:
    precision_at_k: Dict[int, float]
    recall_at_k: Dict[int, float]
    mrr: float
    ndcg_at_k: Dict[int, float]

    def summary(self) -> Dict[str, float]:
        return {
            "P@5": round(self.precision_at_k.get(5, 0.0), 4),
            "P@10": round(self.precision_at_k.get(10, 0.0), 4),
            "R@5": round(self.recall_at_k.get(5, 0.0), 4),
            "R@10": round(self.recall_at_k.get(10, 0.0), 4),
            "MRR": round(self.mrr, 4),
            "nDCG@5": round(self.ndcg_at_k.get(5, 0.0), 4),
            "nDCG@10": round(self.ndcg_at_k.get(10, 0.0), 4),
        }


@dataclass
class GenerationMetrics:
    citation_accuracy: float
    hallucination_rate: float
    temporal_correctness: float
    answer_has_disclaimer: bool
    evidence_complete: bool


@dataclass
class QueryEvalResult:
    query_id: str
    language: str
    retrieval: RetrievalMetrics
    generation: Optional[GenerationMetrics] = None
    retrieval_time_ms: float = 0.0
    generation_time_ms: float = 0.0


@dataclass
class AblationResult:
    config_name: str
    num_queries: int
    avg_precision_at5: float
    avg_recall_at10: float
    avg_mrr: float
    avg_ndcg_at10: float
    avg_citation_accuracy: float = 0.0
    avg_hallucination_rate: float = 0.0
    temporal_correctness: float = 0.0
    per_query_results: List[QueryEvalResult] = field(default_factory=list)


class EvaluationMetrics:
    """Computes all evaluation metrics for legal retrieval and generation."""

    def compute_precision_at_k(self, retrieved_ids: List[str], relevant_ids: Set[str], k: int) -> float:
        if k <= 0 or not retrieved_ids:
            return 0.0
        top_k = retrieved_ids[:k]
        hits = sum(1 for r in top_k if r in relevant_ids or any(rel in r for rel in relevant_ids))
        return hits / float(k)

    def compute_recall_at_k(self, retrieved_ids: List[str], relevant_ids: Set[str], k: int) -> float:
        if not relevant_ids or k <= 0:
            return 0.0
        top_k = retrieved_ids[:k]
        hits = sum(1 for r in top_k if r in relevant_ids or any(rel in r for rel in relevant_ids))
        return hits / float(len(relevant_ids))

    def compute_mrr(self, retrieved_ids: List[str], relevant_ids: Set[str]) -> float:
        for rank, item_id in enumerate(retrieved_ids, start=1):
            if item_id in relevant_ids or any(rel in item_id for rel in relevant_ids):
                return 1.0 / rank
        return 0.0

    def compute_ndcg_at_k(self, retrieved_ids: List[str], relevant_ids: Set[str], k: int) -> float:
        def dcg(items: List[str], rel_set: Set[str], cutoff: int) -> float:
            score = 0.0
            for i, itm in enumerate(items[:cutoff], start=1):
                is_rel = 1.0 if (itm in rel_set or any(rel in itm for rel in rel_set)) else 0.0
                score += is_rel / math.log2(i + 1)
            return score

        actual_dcg = dcg(retrieved_ids, relevant_ids, k)
        ideal_items = list(relevant_ids) + [""] * max(0, k - len(relevant_ids))
        ideal_dcg = dcg(ideal_items, relevant_ids, k)

        return (actual_dcg / ideal_dcg) if ideal_dcg > 0 else 0.0

    def compute_retrieval_metrics(
        self,
        retrieved_ids: List[str],
        relevant_ids: Set[str],
        k_values: Optional[List[int]] = None,
    ) -> RetrievalMetrics:
        if k_values is None:
            k_values = [5, 10]

        precision = {k: self.compute_precision_at_k(retrieved_ids, relevant_ids, k) for k in k_values}
        recall = {k: self.compute_recall_at_k(retrieved_ids, relevant_ids, k) for k in k_values}
        mrr = self.compute_mrr(retrieved_ids, relevant_ids)
        ndcg = {k: self.compute_ndcg_at_k(retrieved_ids, relevant_ids, k) for k in k_values}

        return RetrievalMetrics(
            precision_at_k=precision,
            recall_at_k=recall,
            mrr=mrr,
            ndcg_at_k=ndcg,
        )

    def compute_temporal_correctness(
        self,
        expected_law_version: Optional[str],
        actual_law_version: str,
    ) -> float:
        if expected_law_version is None:
            return 1.0

        ipc_regime = {"ipc", "crpc", "iea"}
        bns_regime = {"bns", "bnss", "bsa"}

        exp_lower = expected_law_version.lower()
        act_lower = actual_law_version.lower()

        if any(r in exp_lower for r in ipc_regime):
            return 1.0 if any(r in act_lower for r in ipc_regime) else 0.0
        elif any(r in exp_lower for r in bns_regime):
            return 1.0 if any(r in act_lower for r in bns_regime) else 0.0
        return 1.0

    def aggregate_ablation_results(
        self,
        query_results: List[QueryEvalResult],
        config_name: str,
    ) -> AblationResult:
        n = len(query_results)
        if n == 0:
            return AblationResult(config_name=config_name, num_queries=0,
                                  avg_precision_at5=0.0, avg_recall_at10=0.0,
                                  avg_mrr=0.0, avg_ndcg_at10=0.0)

        avg_p5 = sum(r.retrieval.precision_at_k.get(5, 0.0) for r in query_results) / n
        avg_r10 = sum(r.retrieval.recall_at_k.get(10, 0.0) for r in query_results) / n
        avg_mrr = sum(r.retrieval.mrr for r in query_results) / n
        avg_ndcg10 = sum(r.retrieval.ndcg_at_k.get(10, 0.0) for r in query_results) / n

        gen_results = [r.generation for r in query_results if r.generation is not None]
        avg_cit_acc = sum(g.citation_accuracy for g in gen_results) / len(gen_results) if gen_results else 0.0
        avg_hall = sum(g.hallucination_rate for g in gen_results) / len(gen_results) if gen_results else 0.0
        avg_temp = sum(g.temporal_correctness for g in gen_results) / len(gen_results) if gen_results else 0.0

        return AblationResult(
            config_name=config_name,
            num_queries=n,
            avg_precision_at5=round(avg_p5, 4),
            avg_recall_at10=round(avg_r10, 4),
            avg_mrr=round(avg_mrr, 4),
            avg_ndcg_at10=round(avg_ndcg10, 4),
            avg_citation_accuracy=round(avg_cit_acc, 4),
            avg_hallucination_rate=round(avg_hall, 4),
            temporal_correctness=round(avg_temp, 4),
            per_query_results=query_results,
        )

    def save_csv(self, results: List[AblationResult], output_path: str) -> None:
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)

        fieldnames = [
            "config_name", "num_queries", "avg_precision_at5", "avg_recall_at10",
            "avg_mrr", "avg_ndcg_at10", "avg_citation_accuracy",
            "avg_hallucination_rate", "temporal_correctness"
        ]
        with open(p, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                writer.writerow({k: getattr(r, k) for k in fieldnames})
        logger.info(f"Saved evaluation results to {output_path}")

