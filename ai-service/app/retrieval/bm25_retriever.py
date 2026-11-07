"""
NyayaAI — BM25 Lexical Retrieval Engine
Implements keyword-based search over legal chunks using rank-bm25 with legal tokenization.
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Okapi
from loguru import logger

from app.config import settings
from app.models.retrieval import RetrievedChunkItem


class LegalBM25Retriever:
    """BM25 Lexical Retriever tailored for Indian statutory and judicial texts."""

    # Essential legal words that must NEVER be removed as stopwords
    LEGAL_KEYWORDS = {
        "bail", "anticipatory", "interim", "arrest", "custody", "quash", "quashing",
        "section", "act", "code", "crpc", "ipc", "bnss", "bns", "it", "fir",
        "cheating", "fraud", "trust", "breach", "cyber", "theft", "liberty", "speedy",
        "trial", "magistrate", "judge", "bench", "remand", "summons", "warrant",
        "cognizable", "non-cognizable", "bailable", "non-bailable", "438", "437", "439",
        "41a", "482", "154", "420", "406", "66a", "66c", "66d", "21", "19", "226", "32"
    }

    # Standard English stopwords (excluding legal keywords)
    STOPWORDS = {
        "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
        "any", "are", "as", "at", "be", "because", "been", "before", "being", "below",
        "between", "both", "but", "by", "could", "did", "do", "does", "doing", "down",
        "during", "each", "few", "for", "from", "further", "had", "has", "have", "having",
        "he", "her", "here", "hers", "herself", "him", "himself", "his", "how", "i", "if",
        "in", "into", "is", "it", "its", "itself", "me", "more", "most", "my", "myself",
        "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
        "our", "ours", "ourselves", "out", "over", "own", "same", "she", "should", "so",
        "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves",
        "then", "there", "these", "they", "this", "those", "through", "to", "too", "under",
        "until", "up", "very", "was", "we", "were", "what", "when", "where", "which",
        "while", "who", "whom", "why", "with", "would", "you", "your", "yours", "yourself",
        "yourselves"
    } - LEGAL_KEYWORDS

    def __init__(self, chunks_dir: Optional[str] = None):
        self.chunks_dir = Path(chunks_dir or settings.data_chunks_dir)
        self.corpus_chunks: List[Dict[str, Any]] = []
        self.tokenized_corpus: List[List[str]] = []
        self.bm25_index: Optional[BM25Okapi] = None
        self.load_and_index()

    def tokenize(self, text: str) -> List[str]:
        """
        Tokenizes legal text while preserving section alphanumeric codes (e.g., 41A, 66C)
        and filtering out non-legal stopwords.
        """
        if not text:
            return []
        # Lowercase and split on punctuation except hyphens/alphanumerics
        cleaned = re.sub(r"[^\w\s\-]", " ", text.lower())
        tokens = cleaned.split()
        return [t for t in tokens if t not in self.STOPWORDS and len(t) > 1]

    def load_and_index(self):
        """Loads all chunks from data/chunks/ and builds the BM25 index."""
        self.corpus_chunks = []
        self.tokenized_corpus = []

        if not self.chunks_dir.exists():
            logger.warning(f"Chunks directory does not exist: {self.chunks_dir}")
            return

        chunk_files = list(self.chunks_dir.glob("*_chunks.json"))
        logger.info(f"Loading {len(chunk_files)} chunk files for BM25 indexing...")

        for file_path in chunk_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    chunks = json.load(f)
                    if isinstance(chunks, list):
                        self.corpus_chunks.extend(chunks)
            except Exception as e:
                logger.error(f"Error loading {file_path.name} for BM25: {e}")

        for chunk in self.corpus_chunks:
            # Combine case name, section, and text for rich keyword matching
            full_searchable = f"{chunk.get('case_name', '')} {chunk.get('section', '')} {chunk.get('text', '')}"
            tokens = self.tokenize(full_searchable)
            self.tokenized_corpus.append(tokens)

        if self.tokenized_corpus:
            self.bm25_index = BM25Okapi(self.tokenized_corpus)
            logger.info(f"✔ BM25 index built successfully with {len(self.corpus_chunks)} chunks.")
        else:
            self.bm25_index = None
            logger.warning("No chunks available to build BM25 index.")

    def search(
        self,
        query: str,
        top_k: int = 10,
        domain_filter: Optional[str] = None,
        document_type_filter: Optional[str] = None,
    ) -> List[RetrievedChunkItem]:
        """
        Executes BM25 search for the query, returns normalized scored chunks.
        """
        if not self.bm25_index or not self.corpus_chunks:
            self.load_and_index()
            if not self.bm25_index:
                return []

        query_tokens = self.tokenize(query)
        if not query_tokens:
            return []

        # Get raw BM25 scores
        raw_scores = self.bm25_index.get_scores(query_tokens)

        # Pair scores with chunk objects
        scored_candidates = []
        for idx, score in enumerate(raw_scores):
            if score <= 0.0:
                continue

            chunk = self.corpus_chunks[idx]

            # Domain filtering
            if domain_filter:
                chunk_domain = chunk.get("legal_domain", "").lower()
                if domain_filter.lower() not in chunk_domain:
                    continue

            # Document type filtering
            if document_type_filter:
                is_act = "act" in chunk.get("document_id", "").lower() or "act" in chunk.get("case_id", "").lower()
                if document_type_filter == "act" and not is_act:
                    continue
                if document_type_filter == "judgment" and is_act:
                    continue

            scored_candidates.append((score, chunk))

        if not scored_candidates:
            return []

        # Sort descending by score
        scored_candidates.sort(key=lambda x: x[0], reverse=True)

        # Min-Max Normalization of top candidate scores
        max_score = scored_candidates[0][0]
        min_score = scored_candidates[-1][0]
        score_range = max_score - min_score if max_score > min_score else 1.0

        results: List[RetrievedChunkItem] = []
        for rank, (raw_score, chunk) in enumerate(scored_candidates[:top_k], start=1):
            norm_score = float((raw_score - min_score) / score_range) if max_score > min_score else 1.0
            # Ensure between 0.0 and 1.0
            norm_score = max(0.0, min(1.0, norm_score))

            results.append(
                RetrievedChunkItem(
                    chunk_id=chunk.get("chunk_id", ""),
                    case_id=chunk.get("case_id", ""),
                    case_name=chunk.get("case_name", ""),
                    document_id=chunk.get("document_id", ""),
                    page=chunk.get("page", 1),
                    paragraph_number=str(chunk.get("paragraph_number", "")),
                    text=chunk.get("text", ""),
                    section=chunk.get("section", "Judicial Discussion"),
                    legal_domain=chunk.get("legal_domain", "Criminal Law"),
                    source_url=chunk.get("source_url", ""),
                    bm25_score=round(norm_score, 4),
                    semantic_score=0.0,
                    hybrid_score=round(norm_score, 4),
                    rank=rank,
                )
            )

        return results
