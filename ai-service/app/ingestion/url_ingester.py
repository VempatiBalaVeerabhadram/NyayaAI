"""
NyayaAI — Source URL Ingestion Service (Method B)
Handles fetching, validating, and extracting Indian legal documents from external URLs.
Preserves official provenance, document URLs, courts, dates, and page structures.
"""

import os
import re
import tempfile
import urllib.parse
from typing import Dict, Any, Optional
import httpx
from loguru import logger

from app.ingestion.document_loader import LegalDocumentLoader


class LegalURLIngester:
    """Ingests legal documents via URL & metadata (Method B)."""

    ALLOWED_SCHEMES = ["http", "https"]
    DEFAULT_TIMEOUT = 30.0  # seconds

    def __init__(self):
        self.loader = LegalDocumentLoader()
        self.headers = {
            "User-Agent": "NyayaAI-Legal-Research-Agent/1.0 (+https://nyaya.ai/bot)",
            "Accept": "text/html,application/xhtml+xml,application/xml,application/pdf,application/json;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

    def validate_url(self, url: str) -> bool:
        """Validates that URL has http/https scheme and is well-formed."""
        try:
            parsed = urllib.parse.urlparse(url)
            return parsed.scheme in self.ALLOWED_SCHEMES and bool(parsed.netloc)
        except Exception:
            return False

    async def ingest_from_url(
        self,
        source_url: str,
        document_type: str = "judgment",
        case_name: Optional[str] = None,
        court: Optional[str] = None,
        judgment_date: Optional[str] = None,
        document_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Fetches document from source_url, saves temporary content,
        processes through the full extraction pipeline, and preserves metadata.
        """
        if not self.validate_url(source_url):
            raise ValueError(f"Invalid or unsupported source URL: {source_url}")

        logger.info(f"Initiating URL ingestion from: {source_url} (type: {document_type})")

        async with httpx.AsyncClient(timeout=self.DEFAULT_TIMEOUT, follow_redirects=True, headers=self.headers) as client:
            response = await client.get(source_url)
            if response.status_code != 200:
                raise RuntimeError(
                    f"Failed to retrieve document from URL {source_url}. HTTP Status: {response.status_code}"
                )

            content_type = response.headers.get("content-type", "").lower()
            content = response.content

        # Determine extension from URL or content-type
        parsed_path = urllib.parse.urlparse(source_url).path
        ext = os.path.splitext(parsed_path)[1].lower()

        if not ext:
            if "application/pdf" in content_type:
                ext = ".pdf"
            elif "application/json" in content_type:
                ext = ".json"
            elif "text/html" in content_type:
                ext = ".html"
            else:
                ext = ".txt"

        # Create temporary file for processing
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp_file:
            tmp_file.write(content)
            tmp_path = tmp_file.name

        try:
            # Process via Document Loader
            result = self.loader.process_document(
                file_path=tmp_path,
                document_id=document_id,
                source_url=source_url,
                document_type=document_type,
            )

            # Override with explicitly provided user metadata if given
            if case_name:
                result["metadata"]["case_name"] = case_name
            if court:
                result["metadata"]["court"] = court
            if judgment_date:
                result["metadata"]["judgment_date"] = judgment_date

            # Save processed artifacts
            self.loader.save_processed_document(result)

            logger.info(
                f"Successfully ingested URL: {source_url} -> {result['document_id']} ({result['total_chunks']} chunks)"
            )
            return result

        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
