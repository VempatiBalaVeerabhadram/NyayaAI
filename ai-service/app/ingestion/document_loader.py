"""
NyayaAI — Unified Document Loader & Ingestion Pipeline
Supports:
- Method A: Local filesystem documents (PDF, HTML, JSON) from data/raw/
- Method B: Source URL ingestion with official court verification
Orchestrates parsing, cleaning, metadata extraction, and semantic chunking.
"""

import os
import json
import hashlib
from typing import Dict, Any, List, Optional
from loguru import logger

from app.ingestion.pdf_parser import LegalPDFParser
from app.ingestion.html_parser import LegalHTMLParser
from app.ingestion.text_cleaner import LegalTextCleaner
from app.ingestion.metadata_extractor import LegalMetadataExtractor
from app.ingestion.chunker import LegalSemanticChunker
from app.config import settings


class LegalDocumentLoader:
    """End-to-end ingestion pipeline for Indian legal documents."""

    def __init__(self):
        self.cleaner = LegalTextCleaner()
        self.pdf_parser = LegalPDFParser()
        self.html_parser = LegalHTMLParser()
        self.metadata_extractor = LegalMetadataExtractor()
        self.chunker = LegalSemanticChunker(
            target_chunk_size=settings.chunk_size,
            overlap_size=settings.chunk_overlap,
        )

    def compute_sha256(self, file_path: str) -> str:
        """Computes SHA-256 checksum to guarantee document provenance."""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for block in iter(lambda: f.read(65536), b""):
                hasher.update(block)
        return hasher.hexdigest()

    def process_document(
        self,
        file_path: str,
        document_id: Optional[str] = None,
        source_url: str = "",
        document_type: str = "judgment",
    ) -> Dict[str, Any]:
        """
        Processes a single document file through the full extraction pipeline:
        1. Parse file into pages / text blocks
        2. Clean text & normalize typography
        3. Extract case and statutory metadata
        4. Generate semantic chunks with page numbering
        5. Return standardized ingestion package
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_name = os.path.basename(file_path)
        ext = os.path.splitext(file_name)[1].lower()

        # Compute hash
        sha256_hash = self.compute_sha256(file_path)
        pages: List[Dict[str, Any]] = []

        if ext == ".pdf":
            pages = self.pdf_parser.parse_pdf(file_path, clean=True)
        elif ext in [".html", ".htm"]:
            parsed_html = self.html_parser.parse_file(file_path)
            pages = [{"page_number": 1, "text": parsed_html["full_text"]}]
        elif ext == ".json":
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not document_id and "document_id" in data:
                document_id = data["document_id"]
            # If JSON provides statutory sections as dicts (Act format)
            if "sections" in data and isinstance(data["sections"], list) and len(data["sections"]) > 0 and isinstance(data["sections"][0], dict):
                document_type = "act"
                pages = []
                for s_idx, sec in enumerate(data["sections"], start=1):
                    sec_num = sec.get("section_number", "")
                    sec_title = sec.get("section_title", "")
                    sec_text = sec.get("section_text", "")
                    act_name = data.get("act_name", "")
                    formatted_text = f"{act_name}\nSection {sec_num}: {sec_title}\n{sec_text}"
                    pages.append({
                        "page_number": s_idx,
                        "text": self.cleaner.clean_text(formatted_text),
                        "section_number": sec_num,
                        "section_title": sec_title,
                    })
            elif "pages" in data:
                pages = data["pages"]
            else:
                raw_text = data.get("text", "") or data.get("content", "")
                pages = [{"page_number": 1, "text": self.cleaner.clean_text(raw_text)}]
        else:
            # Fallback for plain text
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                raw_text = f.read()
            pages = [{"page_number": 1, "text": self.cleaner.clean_text(raw_text)}]

        # Ensure document_id is set
        if not document_id:
            base_id = os.path.splitext(file_name)[0]
            document_id = f"DOC_{base_id.upper().replace(' ', '_')[:32]}"

        # Combine text for full document metadata extraction
        full_text = "\n\n".join(p["text"] for p in pages if p.get("text"))

        # Extract structured metadata
        metadata = self.metadata_extractor.extract_metadata(
            text=full_text,
            document_id=document_id,
            document_type=document_type,
            source_url=source_url,
            file_path=file_path,
        )
        metadata["sha256"] = sha256_hash
        metadata["total_pages"] = len(pages)

        # Generate semantic chunks
        chunks = self.chunker.chunk_pages(
            pages=pages,
            case_id=metadata["case_id"],
            document_id=document_id,
            case_name=metadata["case_name"],
            legal_domain=metadata["legal_domain"],
            source_url=source_url,
        )

        return {
            "document_id": document_id,
            "metadata": metadata,
            "total_chunks": len(chunks),
            "chunks": chunks,
            "status": "PROCESSED",
        }

    def save_processed_document(self, processed_data: Dict[str, Any], output_dir: Optional[str] = None) -> str:
        """Saves processed document bundle and chunk files to data directories."""
        target_processed_dir = output_dir or settings.data_processed_dir
        os.makedirs(target_processed_dir, exist_ok=True)
        os.makedirs(settings.data_metadata_dir, exist_ok=True)
        os.makedirs(settings.data_chunks_dir, exist_ok=True)

        doc_id = processed_data["document_id"]

        # 1. Save metadata
        metadata_file = os.path.join(settings.data_metadata_dir, f"{doc_id}_metadata.json")
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(processed_data["metadata"], f, indent=2, ensure_ascii=False)

        # 2. Save chunks
        chunks_file = os.path.join(settings.data_chunks_dir, f"{doc_id}_chunks.json")
        with open(chunks_file, "w", encoding="utf-8") as f:
            json.dump(processed_data["chunks"], f, indent=2, ensure_ascii=False)

        # 3. Save complete bundle in processed
        processed_file = os.path.join(target_processed_dir, f"{doc_id}_processed.json")
        with open(processed_file, "w", encoding="utf-8") as f:
            json.dump(processed_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Successfully saved processed artifacts for {doc_id}")
        return processed_file
