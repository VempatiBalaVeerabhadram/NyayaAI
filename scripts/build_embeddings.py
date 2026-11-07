#!/usr/bin/env python3
"""
NyayaAI — Production Script to Build & Index Semantic Vector Embeddings
Populates Qdrant vector database or local FAISS index with embeddings for all document chunks.

Usage:
    python scripts/build_embeddings.py
    python scripts/build_embeddings.py --chunks data/chunks/
"""

import argparse
import sys
import os
import time
from pathlib import Path

# Add ai-service to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "ai-service"))

from app.embeddings.embedding_service import EmbeddingService
from loguru import logger


def main():
    parser = argparse.ArgumentParser(description="Build and index legal chunk embeddings")
    parser.add_argument(
        "--chunks",
        "-c",
        default="data/chunks/",
        help="Path to semantic chunks directory (default: data/chunks/)",
    )
    args = parser.parse_args()

    chunks_dir = Path(args.chunks)
    if not chunks_dir.is_absolute():
        chunks_dir = ROOT_DIR / args.chunks

    logger.info("=" * 60)
    logger.info("  NyayaAI Vector Embedding Builder")
    logger.info(f"  Target Chunks Directory: {chunks_dir}")
    logger.info("=" * 60)

    start_time = time.perf_counter()
    embedding_service = EmbeddingService()
    indexed_count = embedding_service.index_chunks(str(chunks_dir))
    elapsed_time = time.perf_counter() - start_time

    backend = "Qdrant Vector Database" if embedding_service.use_qdrant else "Local FAISS Index"

    print("\n" + "=" * 60)
    print("  NYAYAAI VECTOR EMBEDDING INDEXING COMPLETE")
    print("=" * 60)
    print(f"  Total Chunks Indexed : {indexed_count}")
    print(f"  Active Vector Backend: {backend}")
    print(f"  Vector Dimensions    : {embedding_service.vector_dim}")
    print(f"  Time Elapsed         : {elapsed_time:.2f} seconds")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
