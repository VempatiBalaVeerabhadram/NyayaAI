"""
NyayaAI — Semantic Chunker for Indian Legal Documents
Splits judgments and statutes into semantically coherent segments
while strictly preserving:
- Page number provenance
- Paragraph boundaries and judicial headings
- Case identity and statutory context
"""

import re
from typing import List, Dict, Any, Optional
from loguru import logger


class LegalSemanticChunker:
    """Chunks legal documents by paragraphs and pages with overlap and full provenance."""

    def __init__(self, target_chunk_size: int = 800, overlap_size: int = 100):
        """
        :param target_chunk_size: Target size in approximate words/tokens.
        :param overlap_size: Overlap size in approximate words/tokens.
        """
        self.target_size = target_chunk_size
        self.overlap_size = overlap_size

    def chunk_pages(
        self,
        pages: List[Dict[str, Any]],
        case_id: str,
        document_id: str,
        case_name: str,
        legal_domain: str = "Criminal Law",
        source_url: str = "",
    ) -> List[Dict[str, Any]]:
        """
        Takes page objects: [{'page_number': int, 'text': str}]
        and returns a flat list of provenance-tracked chunks.
        """
        chunks: List[Dict[str, Any]] = []
        chunk_counter = 1

        for page in pages:
            page_num = page.get("page_number", 1)
            page_text = page.get("text", "").strip()

            if not page_text or len(page_text) < 50:
                continue

            # Split page text into candidate paragraphs
            paragraphs = self._split_paragraphs(page_text)

            current_chunk_words: List[str] = []
            current_paras: List[str] = []

            for para in paragraphs:
                para_words = para.split()
                if not para_words:
                    continue

                # If adding this paragraph exceeds target size and current chunk is not empty:
                if len(current_chunk_words) + len(para_words) > self.target_size and current_chunk_words:
                    chunk_text = " ".join(current_chunk_words)
                    chunk_id = f"{case_id}_P{page_num:03d}_C{chunk_counter:03d}"

                    # Detect if there's a heading or paragraph marker
                    para_marker = self._detect_para_marker(chunk_text)

                    chunks.append({
                        "chunk_id": chunk_id,
                        "case_id": case_id,
                        "document_id": document_id,
                        "case_name": case_name,
                        "page": page_num,
                        "paragraph_number": para_marker or str(chunk_counter),
                        "text": chunk_text,
                        "section": self._detect_section_context(chunk_text),
                        "legal_domain": legal_domain,
                        "word_count": len(current_chunk_words),
                        "source_url": source_url,
                    })
                    chunk_counter += 1

                    # Retain overlap from end of current chunk
                    overlap_words = current_chunk_words[-self.overlap_size:] if self.overlap_size > 0 else []
                    current_chunk_words = overlap_words + para_words
                else:
                    current_chunk_words.extend(para_words)

            # Flush any remaining text on the page
            if current_chunk_words:
                chunk_text = " ".join(current_chunk_words)
                chunk_id = f"{case_id}_P{page_num:03d}_C{chunk_counter:03d}"
                para_marker = self._detect_para_marker(chunk_text)

                chunks.append({
                    "chunk_id": chunk_id,
                    "case_id": case_id,
                    "document_id": document_id,
                    "case_name": case_name,
                    "page": page_num,
                    "paragraph_number": para_marker or str(chunk_counter),
                    "text": chunk_text,
                    "section": self._detect_section_context(chunk_text),
                    "legal_domain": legal_domain,
                    "word_count": len(current_chunk_words),
                    "source_url": source_url,
                })
                chunk_counter += 1

        logger.info(f"Generated {len(chunks)} semantic chunks for {case_id}")
        return chunks

    def _split_paragraphs(self, text: str) -> List[str]:
        """Splits on double newlines or numbered judicial paragraph markers."""
        # Normalize double newlines
        raw_paras = re.split(r"\n\s*\n", text)
        paras = []
        for p in raw_paras:
            clean = p.strip()
            if clean:
                paras.append(clean)
        return paras

    def _detect_para_marker(self, text: str) -> Optional[str]:
        """Detects standard judicial paragraph numbers: '12.', '[14]', 'Para 16'."""
        match = re.match(r"(?:Para(?:graph)?\s*)?\[?(\d{1,3})\]?[\.\)]", text[:50])
        if match:
            return match.group(1)
        return None

    def _detect_section_context(self, text: str) -> str:
        """Determines contextual section heading: Facts, Issues, Arguments, Reasoning, Order."""
        lower = text[:300].lower()
        if any(w in lower for w in ["reasoning", "we have considered", "in our considered view", "our analysis"]):
            return "Court Reasoning"
        elif any(w in lower for w in ["argument", "submission", "learned counsel"]):
            return "Arguments"
        elif any(w in lower for w in ["facts", "case of the prosecution", "allegations"]):
            return "Facts of the Case"
        elif any(w in lower for w in ["issue", "question for consideration", "reference"]):
            return "Legal Issues"
        elif any(w in lower for w in ["held", "order", "disposed of", "appeal allowed", "appeal dismissed"]):
            return "Operative Order / Holding"
        return "Judicial Discussion"
