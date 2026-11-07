"""
NyayaAI — PDF Parser for Indian Legal Documents
Extracts text while strictly preserving page boundaries, page numbers,
and structural characteristics of court judgments.
"""

from typing import List, Dict, Any, Optional
import os
from loguru import logger

from app.ingestion.text_cleaner import LegalTextCleaner


class LegalPDFParser:
    """Extracts text page-by-page from court judgment PDFs."""

    def __init__(self):
        self.cleaner = LegalTextCleaner()

    def parse_pdf(self, file_path: str, clean: bool = True) -> List[Dict[str, Any]]:
        """
        Parses a PDF file and returns a list of page objects.
        Each page object contains:
            - page_number (1-indexed)
            - text (cleaned or raw)
            - char_count
            - has_content (bool)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        pages: List[Dict[str, Any]] = []

        # Attempt extraction using pdfplumber first (higher layout fidelity)
        try:
            pages = self._extract_with_pdfplumber(file_path, clean)
            if pages and any(p["char_count"] > 20 for p in pages):
                logger.info(f"Successfully extracted {len(pages)} pages using pdfplumber: {file_path}")
                return pages
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed for {file_path}: {e}. Falling back to PyPDF2.")

        # Fallback to PyPDF2
        try:
            pages = self._extract_with_pypdf2(file_path, clean)
            logger.info(f"Extracted {len(pages)} pages using PyPDF2 fallback: {file_path}")
            return pages
        except Exception as e:
            logger.error(f"PyPDF2 fallback also failed for {file_path}: {e}")
            raise RuntimeError(f"Unable to extract text from PDF: {file_path}. Error: {e}")

    def _extract_with_pdfplumber(self, file_path: str, clean: bool) -> List[Dict[str, Any]]:
        import pdfplumber

        results = []
        with pdfplumber.open(file_path) as pdf:
            for page_idx, page in enumerate(pdf.pages, start=1):
                raw_text = page.extract_text(layout=True) or ""
                processed_text = self.cleaner.clean_text(raw_text) if clean else raw_text

                results.append({
                    "page_number": page_idx,
                    "text": processed_text,
                    "char_count": len(processed_text),
                    "has_content": len(processed_text.strip()) > 0,
                })
        return results

    def _extract_with_pypdf2(self, file_path: str, clean: bool) -> List[Dict[str, Any]]:
        from PyPDF2 import PdfReader

        results = []
        reader = PdfReader(file_path)
        for page_idx, page in enumerate(reader.pages, start=1):
            raw_text = page.extract_text() or ""
            processed_text = self.cleaner.clean_text(raw_text) if clean else raw_text

            results.append({
                "page_number": page_idx,
                "text": processed_text,
                "char_count": len(processed_text),
                "has_content": len(processed_text.strip()) > 0,
            })
        return results
