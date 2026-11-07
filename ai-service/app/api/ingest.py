"""
NyayaAI — Ingestion Endpoints (Method A & Method B)
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status
from loguru import logger

from app.ingestion.document_loader import LegalDocumentLoader
from app.ingestion.url_ingester import LegalURLIngester
from app.models.document import (
    URLIngestRequest,
    DirectoryIngestRequest,
    ProcessedDocumentResponse,
    IngestionStatisticsResponse,
)
from app.config import settings

router = APIRouter(prefix="/ai/ingest", tags=["Ingestion"])

loader = LegalDocumentLoader()
url_ingester = LegalURLIngester()


@router.post("/file", response_model=ProcessedDocumentResponse, summary="Ingest uploaded file (Method A)")
async def ingest_file(
    file: UploadFile = File(...),
    document_type: str = Form("judgment"),
    source_url: str = Form(""),
    case_name: str = Form(""),
):
    """
    Upload and ingest a single legal document file (PDF, JSON, HTML, TXT).
    Processes text, metadata, page-boundaries, and semantic chunks.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Empty filename provided")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf", ".json", ".html", ".htm", ".txt"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {ext}. Allowed: .pdf, .json, .html, .txt",
        )

    # Save to temp file
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name

    try:
        logger.info(f"Processing uploaded file: {file.filename} ({document_type})")
        result = loader.process_document(
            file_path=tmp_path,
            source_url=source_url,
            document_type=document_type,
        )

        if case_name:
            result["metadata"]["case_name"] = case_name

        loader.save_processed_document(result)
        return result

    except Exception as e:
        logger.error(f"Failed to ingest uploaded file {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@router.post("/url", response_model=ProcessedDocumentResponse, summary="Ingest document from URL (Method B)")
async def ingest_url(request: URLIngestRequest):
    """
    Ingest a legal document via source URL and metadata (Method B).
    Retrieves the document, cleans text, extracts metadata, creates chunks, and stores artifacts.
    """
    try:
        result = await url_ingester.ingest_from_url(
            source_url=request.source_url,
            document_type=request.document_type,
            case_name=request.case_name,
            court=request.court,
            judgment_date=request.judgment_date,
            document_id=request.document_id,
        )
        return result

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"URL ingestion failed for {request.source_url}: {e}")
        raise HTTPException(status_code=500, detail=f"URL ingestion failed: {str(e)}")


@router.post("/directory", summary="Run batch ingestion on a directory")
async def ingest_directory_endpoint(request: DirectoryIngestRequest):
    """
    Scans a local directory (e.g. data/raw/) and processes all raw legal documents.
    """
    raw_dir = Path(request.input_directory)
    if not raw_dir.is_absolute():
        raw_dir = Path(settings.data_raw_dir).parent / request.input_directory

    if not raw_dir.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Directory not found: {request.input_directory}",
        )

    files = []
    for ext in ["*.pdf", "*.json", "*.html", "*.htm", "*.txt"]:
        files.extend(raw_dir.rglob(ext))

    results = {"total_found": len(files), "processed": 0, "failed": 0, "records": []}

    for f in files:
        doc_type = request.document_type
        if doc_type == "auto":
            doc_type = "act" if "acts" in str(f).lower() else "judgment"

        if request.dry_run:
            results["records"].append({"file": f.name, "type": doc_type, "status": "DRY_RUN"})
            continue

        try:
            res = loader.process_document(file_path=str(f.resolve()), document_type=doc_type)
            loader.save_processed_document(res)
            results["processed"] += 1
            results["records"].append({
                "file": f.name,
                "document_id": res["document_id"],
                "chunks": res["total_chunks"],
                "status": "SUCCESS",
            })
        except Exception as e:
            results["failed"] += 1
            results["records"].append({
                "file": f.name,
                "status": "FAILED",
                "error": str(e),
            })

    return results
