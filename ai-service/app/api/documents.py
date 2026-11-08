"""
NyayaAI — Document Inspection & Management Endpoints
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from loguru import logger

from app.config import settings
from app.models.document import (
    DocumentSummaryItem,
    ProcessedDocumentResponse,
    IngestionStatisticsResponse,
)

router = APIRouter(prefix="/ai/documents", tags=["Documents"])


@router.get("", response_model=List[DocumentSummaryItem], summary="List all processed documents")
async def list_documents(
    doc_type: Optional[str] = Query(None, description="Filter by document_type ('judgment' or 'act')"),
    document_type: Optional[str] = Query(None, description="Alias for doc_type"),
    domain: Optional[str] = Query(None, description="Filter by legal domain"),
    search: Optional[str] = Query(None, description="Search term in case_name or court"),
):
    """Returns metadata summary of all ingested documents in the repository."""
    filter_type = (document_type or doc_type or "").strip().lower()
    metadata_dir = Path(settings.data_metadata_dir)
    if not metadata_dir.exists():
        return []

    results: List[DocumentSummaryItem] = []

    for meta_file in metadata_dir.glob("*_metadata.json"):
        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                meta = json.load(f)

            # Check matching chunks file to get count
            doc_id = meta.get("document_id", "")
            chunks_file = Path(settings.data_chunks_dir) / f"{doc_id}_chunks.json"
            chunks_count = 0
            if chunks_file.exists():
                with open(chunks_file, "r", encoding="utf-8") as cf:
                    chunks_count = len(json.load(cf))

            # Apply filters
            if filter_type and meta.get("document_type", "").lower() != filter_type:
                continue
            if domain and domain.lower() not in meta.get("legal_domain", "").lower():
                continue
            if search:
                s_lower = search.lower()
                case_name = meta.get("case_name", "").lower()
                court = meta.get("court", "").lower()
                if s_lower not in case_name and s_lower not in court:
                    continue

            results.append(
                DocumentSummaryItem(
                    document_id=doc_id,
                    case_name=meta.get("case_name", "Unknown"),
                    document_type=meta.get("document_type", "judgment"),
                    court=meta.get("court", ""),
                    judgment_date=meta.get("judgment_date"),
                    legal_domain=meta.get("legal_domain", "Criminal Law"),
                    total_chunks=chunks_count,
                    acts_count=len(meta.get("acts", [])),
                    sections_count=len(meta.get("sections", [])),
                    citations_count=len(meta.get("citations", [])),
                    source_url=meta.get("source_url", ""),
                    status="PROCESSED",
                )
            )
        except Exception as e:
            logger.warning(f"Error reading metadata file {meta_file.name}: {e}")

    return sorted(results, key=lambda x: x.case_name)


@router.get("/statistics", response_model=IngestionStatisticsResponse, summary="Ingestion & dataset statistics")
async def get_statistics():
    """Returns dataset summary metrics for admin dashboard."""
    metadata_dir = Path(settings.data_metadata_dir)
    chunks_dir = Path(settings.data_chunks_dir)

    total_docs = 0
    total_judgments = 0
    total_acts = 0
    total_chunks = 0
    sections_set = set()

    if metadata_dir.exists():
        for mf in metadata_dir.glob("*_metadata.json"):
            try:
                with open(mf, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                total_docs += 1
                if meta.get("document_type") == "act":
                    total_acts += 1
                else:
                    total_judgments += 1

                for s in meta.get("sections", []):
                    sections_set.add(s)
            except Exception:
                continue

    if chunks_dir.exists():
        for cf in chunks_dir.glob("*_chunks.json"):
            try:
                with open(cf, "r", encoding="utf-8") as f:
                    total_chunks += len(json.load(f))
            except Exception:
                continue

    return IngestionStatisticsResponse(
        total_documents=total_docs,
        total_judgments=total_judgments,
        total_acts=total_acts,
        total_chunks=total_chunks,
        total_sections=len(sections_set),
        processed_count=total_docs,
        failed_count=0,
    )


@router.get("/{document_id}", response_model=ProcessedDocumentResponse, summary="Get full document bundle")
async def get_document(document_id: str):
    """Fetches complete processed document bundle, metadata, and all chunks."""
    processed_file = Path(settings.data_processed_dir) / f"{document_id}_processed.json"
    if not processed_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Document not found: {document_id}",
        )

    with open(processed_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data
