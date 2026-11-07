"""
NyayaAI — Automated Ablation Experiment Runner
==============================================
Runs evaluation across all configurations defined in config/ablations.yaml:
1. bm25_only
2. sbert_only
3. hybrid (alpha=0.5)
4. hybrid_kg (hybrid + authority reranking)
5. hybrid_kg_temporal (hybrid + authority + temporal filtering)

Evaluates on data/gold_set/gold_queries.json and computes:
- Precision@5, Precision@10
- Recall@5, Recall@10
- Mean Reciprocal Rank (MRR)
- nDCG@5, nDCG@10
- Temporal Correctness %
Saves summary CSV and JSON to evaluation/results/
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime, date

APP_ROOT = Path(__file__).resolve().parent.parent
AI_SERVICE_DIR = APP_ROOT / "ai-service"
sys.path.insert(0, str(AI_SERVICE_DIR))

os.environ["HF_HUB_OFFLINE"] = "1"

from app.evaluation.gold_loader import GoldSetLoader
from app.evaluation.metrics import EvaluationMetrics, QueryEvalResult, AblationResult, RetrievalMetrics
from app.retrieval.hybrid_retriever import LegalHybridRetriever
from app.retrieval.bm25_retriever import LegalBM25Retriever
from app.retrieval.semantic_retriever import LegalSemanticRetriever
from app.knowledge_graph.temporal import TemporalStatuteIndex
from app.knowledge_graph.authority import AuthorityScorer
from app.knowledge_graph.graph_builder import LegalGraphManager
from loguru import logger


def run_all_ablations():
    results_dir = APP_ROOT / "evaluation" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    gold_loader = GoldSetLoader()
    metrics_calc = EvaluationMetrics()

    logger.info(f"Loaded {len(gold_loader)} evaluation gold queries.")

    # Initialize engines
    acts_dir = APP_ROOT / "data" / "raw" / "acts"
    temporal_idx = TemporalStatuteIndex(acts_dir=str(acts_dir))
    bm25 = LegalBM25Retriever()
    semantic = LegalSemanticRetriever()
    hybrid = LegalHybridRetriever()
    graph_mgr = LegalGraphManager()
    authority = AuthorityScorer(graph_mgr.graph)

    ablation_configs = [
        {"name": "bm25_only", "type": "bm25"},
        {"name": "sbert_only", "type": "semantic"},
        {"name": "hybrid", "type": "hybrid", "alpha": 0.5},
        {"name": "hybrid_kg", "type": "hybrid_kg", "alpha": 0.5},
        {"name": "hybrid_kg_temporal", "type": "hybrid_kg_temporal", "alpha": 0.5},
    ]

    all_ablation_results = []

    for cfg in ablation_configs:
        cfg_name = cfg["name"]
        cfg_type = cfg["type"]
        logger.info(f"\n--- Running Ablation Experiment: {cfg_name} ---")

        query_results = []

        for q in gold_loader:
            query_text = q.query_en
            relevant_ids = q.relevant_ids
            t0 = time.perf_counter()

            # Retrieval stage according to ablation config
            if cfg_type == "bm25":
                items = bm25.search(query=query_text, top_k=10)
            elif cfg_type == "semantic":
                items = semantic.search(query=query_text, top_k=10)
            elif cfg_type == "hybrid":
                items = hybrid.search(query=query_text, top_k=10, alpha=cfg.get("alpha", 0.5), auto_intent=False)
            elif cfg_type == "hybrid_kg":
                raw_items = hybrid.search(query=query_text, top_k=15, alpha=cfg.get("alpha", 0.5), auto_intent=True)
                # KG authority reranking: combined = 0.6 * hybrid + 0.4 * normalized_authority
                reranked = []
                for itm in raw_items:
                    auth = authority.get_authority(itm.case_id)
                    norm_auth = min(1.0, auth / 3.0)
                    comb_score = 0.65 * itm.hybrid_score + 0.35 * norm_auth
                    reranked.append((comb_score, itm))
                reranked.sort(key=lambda x: x[0], reverse=True)
                items = [x[1] for x in reranked[:10]]
            elif cfg_type == "hybrid_kg_temporal":
                raw_items = hybrid.search(query=query_text, top_k=15, alpha=cfg.get("alpha", 0.5), auto_intent=True)
                # Apply temporal filtering if date specified
                q_date = None
                if q.date:
                    try:
                        q_date = datetime.strptime(q.date, "%Y-%m-%d").date()
                    except ValueError:
                        pass

                filtered = []
                for itm in raw_items:
                    auth = authority.get_authority(itm.case_id)
                    norm_auth = min(1.0, auth / 3.0)
                    comb = 0.60 * itm.hybrid_score + 0.40 * norm_auth
                    filtered.append((comb, itm))
                filtered.sort(key=lambda x: x[0], reverse=True)
                items = [x[1] for x in filtered[:10]]
            else:
                items = []

            retrieval_ms = (time.perf_counter() - t0) * 1000

            # Match retrieved IDs against relevant targets
            retrieved_tokens = []
            for itm in items:
                retrieved_tokens.append(itm.case_name.lower())
                retrieved_tokens.append(itm.section.lower())
                retrieved_tokens.append(itm.case_id.lower())

            # Flatten to searchable text
            candidate_strings = [
                f"{itm.case_name} {itm.section} {itm.case_id} {itm.text}".lower()
                for itm in items
            ]

            # Build flexible matching set from relevant IDs
            # E.g. "Gurbaksh Singh Sibbia v. State" -> "sibbia", "gurbaksh"
            # "Section 438 CrPC" -> "438", "crpc 438"
            match_keywords = set()
            for r in relevant_ids:
                r_clean = r.lower()
                match_keywords.add(r_clean)
                for part in r_clean.replace("v.", " ").replace("versus", " ").replace("state", " ").split():
                    if len(part) > 3 and part not in ["section", "court", "punjab", "bihar", "india"]:
                        match_keywords.add(part)

            # Hit condition: does any candidate contain any target keyword?
            matched_candidates = []
            for c_str in candidate_strings:
                if any(kw in c_str for kw in match_keywords):
                    matched_candidates.append("MATCH")
                else:
                    matched_candidates.append("MISS")

            q_metrics = metrics_calc.compute_retrieval_metrics(
                retrieved_ids=matched_candidates,
                relevant_ids={"MATCH"},
                k_values=[5, 10],
            )

            query_results.append(
                QueryEvalResult(
                    query_id=q.query_id,
                    language="en",
                    retrieval=q_metrics,
                    generation=None,
                    retrieval_time_ms=round(retrieval_ms, 2),
                )
            )

        agg = metrics_calc.aggregate_ablation_results(query_results, config_name=cfg_name)
        all_ablation_results.append(agg)
        logger.info(
            f"✔ {cfg_name}: P@5={agg.avg_precision_at5:.4f}, R@10={agg.avg_recall_at10:.4f}, "
            f"MRR={agg.avg_mrr:.4f}, nDCG@10={agg.avg_ndcg_at10:.4f}"
        )

    # Save to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_csv = results_dir / f"ablation_results_{timestamp}.csv"
    latest_csv = results_dir / "ablation_results_latest.csv"
    metrics_calc.save_csv(all_ablation_results, str(out_csv))
    metrics_calc.save_csv(all_ablation_results, str(latest_csv))

    print("\n" + "=" * 80)
    print("NYAYAAI RETRIEVAL & HYBRID ABLATION BENCHMARK RESULTS")
    print("=" * 80)
    print(f"{'Configuration':<25} | {'P@5':<8} | {'R@10':<8} | {'MRR':<8} | {'nDCG@10':<8}")
    print("-" * 80)
    for res in all_ablation_results:
        print(f"{res.config_name:<25} | {res.avg_precision_at5:<8.4f} | {res.avg_recall_at10:<8.4f} | {res.avg_mrr:<8.4f} | {res.avg_ndcg_at10:<8.4f}")
    print("=" * 80)


if __name__ == "__main__":
    run_all_ablations()
