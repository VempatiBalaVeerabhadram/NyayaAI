"""
Benchmark Evaluation Script for NyayaAI.
Evaluates BM25 vs Dense vs Hybrid vs Graph-Enhanced Hybrid.
Outputs a detailed Markdown table and saves results to data/evaluation/benchmark_results.json.
"""

import os
import sys
import json
from pathlib import Path
from loguru import logger

# Add ai-service to path
current_dir = Path(__file__).resolve().parent
ai_service_dir = current_dir.parent / "ai-service"
sys.path.insert(0, str(ai_service_dir))

from app.evaluation.retrieval_eval import RetrievalEvaluator


def print_markdown_table(mean_metrics: dict):
    """Print benchmark summary in beautiful Markdown table format."""
    methods = list(mean_metrics.keys())
    metric_cols = ["P@1", "P@3", "P@5", "R@5", "R@10", "MRR", "MAP@10", "NDCG@5", "NDCG@10"]

    header = "| Retrieval Method | " + " | ".join(metric_cols) + " |"
    divider = "| :--- | " + " | ".join([":---:" for _ in metric_cols]) + " |"

    print("\n" + "=" * 80)
    print("  NYAYAAI RETRIEVAL BENCHMARK EVALUATION RESULTS")
    print("=" * 80)
    print(header)
    print(divider)

    for method in methods:
        row = f"| **{method.replace('_', ' ')}** | "
        vals = [f"{mean_metrics[method].get(col, 0.0):.4f}" for col in metric_cols]
        row += " | ".join(vals) + " |"
        print(row)
    print("=" * 80 + "\n")


def main():
    root_dir = current_dir.parent
    benchmarks_path = root_dir / "data" / "evaluation" / "queries.json"
    output_path = root_dir / "data" / "evaluation" / "benchmark_results.json"

    if not benchmarks_path.exists():
        logger.error(f"Benchmark queries file not found at: {benchmarks_path}")
        sys.exit(1)

    evaluator = RetrievalEvaluator()
    results = evaluator.run_benchmark(str(benchmarks_path))

    print_markdown_table(results["mean_metrics"])

    # Save output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    logger.info(f"✔ Benchmark results successfully saved to: {output_path}")


if __name__ == "__main__":
    main()
