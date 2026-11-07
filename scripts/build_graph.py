#!/usr/bin/env python3
"""
NyayaAI — Production Script to Build Legal Knowledge Graph
Constructs Case, Act, Section, Court, Judge, LegalIssue, and Document nodes and relationships.

Usage:
    python scripts/build_graph.py
"""

import sys
import os
from pathlib import Path

# Add ai-service to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "ai-service"))

from app.knowledge_graph.graph_builder import LegalGraphManager
from loguru import logger


def main():
    logger.info("=" * 60)
    logger.info("  NyayaAI Knowledge Graph Construction")
    logger.info("=" * 60)

    manager = LegalGraphManager()
    num_nodes, num_edges = manager.build_graph_from_metadata()
    overview = manager.get_overview()

    print("\n" + "=" * 60)
    print("  NYAYAAI KNOWLEDGE GRAPH CONSTRUCTION COMPLETE")
    print("=" * 60)
    print(f"  Total Nodes        : {overview.total_nodes}")
    print(f"  Total Relationships: {overview.total_relationships}")
    print(f"  Active Backend     : {overview.active_backend}")
    print("\n  Nodes Breakdown:")
    for label, count in overview.node_counts_by_label.items():
        print(f"    - {label:<15}: {count}")
    print("\n  Relationships Breakdown:")
    for rel_type, count in overview.relationship_counts_by_type.items():
        print(f"    - {rel_type:<15}: {count}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
