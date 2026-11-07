#!/usr/bin/env python3
"""
NyayaAI — Production Legal Document Ingestion Script
Processes documents from data/raw/ and populates the pipeline.

Usage:
    python scripts/ingest.py --input data/raw/
    python scripts/ingest.py --input data/raw/judgments/ --type judgment
    python scripts/ingest.py --input data/raw/acts/ --type act
"""

import argparse
import sys
import os
import json
from pathlib import Path

# Add ai-service to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "ai-service"))

from app.ingestion.document_loader import LegalDocumentLoader
from loguru import logger


def ingest_directory(input_path: str, doc_type: str = "auto", dry_run: bool = False):
    loader = LegalDocumentLoader()
    path = Path(input_path)

    if not path.exists():
        logger.error(f"Provided path does not exist: {input_path}")
        return

    files_to_process = []
    if path.is_file():
        files_to_process.append(path)
    else:
        for ext in ["*.pdf", "*.json", "*.html", "*.htm", "*.txt"]:
            files_to_process.extend(path.rglob(ext))

    logger.info(f"Discovered {len(files_to_process)} documents for ingestion.")

    summary = {
        "total_documents": len(files_to_process),
        "processed": 0,
        "failed": 0,
        "total_chunks": 0,
        "records": [],
    }

    for file_path in files_to_process:
        resolved_path = str(file_path.resolve())
        # Infer type if auto
        determined_type = doc_type
        if determined_type == "auto":
            if "acts" in resolved_path.lower():
                determined_type = "act"
            else:
                determined_type = "judgment"

        if dry_run:
            logger.info(f"[DRY-RUN] Would process: {file_path.name} as {determined_type}")
            continue

        try:
            logger.info(f"Processing: {file_path.name} ({determined_type})...")
            result = loader.process_document(
                file_path=resolved_path,
                document_type=determined_type,
            )
            saved_file = loader.save_processed_document(result)

            summary["processed"] += 1
            summary["total_chunks"] += result["total_chunks"]
            summary["records"].append({
                "document_id": result["document_id"],
                "case_name": result["metadata"].get("case_name", ""),
                "court": result["metadata"].get("court", ""),
                "chunks": result["total_chunks"],
                "file": file_path.name,
                "status": "SUCCESS",
            })
            logger.info(f"✔ Successfully ingested {file_path.name} -> {result['total_chunks']} chunks")
        except Exception as e:
            logger.error(f"❌ Failed to process {file_path.name}: {e}")
            summary["failed"] += 1
            summary["records"].append({
                "file": file_path.name,
                "status": "FAILED",
                "error": str(e),
            })

    # Save ingestion summary manifest
    summary_path = ROOT_DIR / "data" / "processed" / "ingestion_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print("  NYAYAAI INGESTION SUMMARY REPORT")
    print("=" * 60)
    print(f"  Total Documents Found : {summary['total_documents']}")
    print(f"  Successfully Ingested : {summary['processed']}")
    print(f"  Failed Documents      : {summary['failed']}")
    print(f"  Total Semantic Chunks : {summary['total_chunks']}")
    print(f"  Summary Report Saved  : {summary_path}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="NyayaAI Legal Document Ingestion Pipeline")
    parser.add_argument("--input", "-i", required=True, help="Input directory or file path")
    parser.add_argument(
        "--type", "-t",
        choices=["judgment", "act", "order", "auto"],
        default="auto",
        help="Document type (default: auto-detect)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview without saving")

    args = parser.parse_args()
    ingest_directory(input_path=args.input, doc_type=args.type, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
