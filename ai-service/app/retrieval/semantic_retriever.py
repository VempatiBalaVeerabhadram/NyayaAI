"""
NyayaAI — Semantic Vector Retriever
Performs dense vector retrieval using Sentence Transformers and Qdrant/FAISS.
"""

from typing import List, Optional
from loguru import logger

from app.embeddings.embedding_service import EmbeddingService
from app.models.retrieval import RetrievedChunkItem


class LegalSemanticRetriever:
    """Retrieves legal document chunks based on dense embedding semantic similarity."""

    def __init__(self):
        self.embedding_service = EmbeddingService()

    def search(
        self,
        query: str,
        top_k: int = 10,
        domain_filter: Optional[str] = None,
        document_type_filter: Optional[str] = None,
    ) -> List[RetrievedChunkItem]:
        """
        Executes semantic vector search and formats results.
        """
        candidates = self.embedding_service.search(
            query=query,
            top_k=top_k,
            domain_filter=domain_filter,
            document_type_filter=document_type_filter,
        )

        results: List[RetrievedChunkItem] = []
        for rank, (score, chunk) in enumerate(candidates, start=1):
            clamped_score = round(max(0.0, min(1.0, float(score))), 4)
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
                    bm25_score=0.0,
                    semantic_score=clamped_score,
                    hybrid_score=clamped_score,
                    rank=rank,
                )
            )

        return results
