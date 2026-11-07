"""
NyayaAI — Semantic Embedding & Vector Store Service
Handles embedding generation using Sentence Transformers with Qdrant vector database
and a fully transparent, zero-downtime local FAISS fallback.
"""

import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from loguru import logger

from app.config import settings


class EmbeddingService:
    """Manages sentence embedding models, Qdrant indexing, and FAISS fallback storage."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.model_name = settings.embedding_model
        self.vector_dim = 384  # Default for MiniLM / bge-small
        self.encoder = None
        self.qdrant_client = None
        self.use_qdrant = False
        self.faiss_index = None
        self.faiss_payloads: List[Dict[str, Any]] = []
        self.vector_store_dir = Path("data/vector_store")
        self.vector_store_dir.mkdir(parents=True, exist_ok=True)

        self._load_model()
        self._init_vector_backend()
        self._initialized = True

    def _load_model(self):
        """Loads the SentenceTransformer model."""
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading Sentence Transformer model: {self.model_name}...")
            self.encoder = SentenceTransformer(self.model_name)
            test_emb = self.encoder.encode("NyayaAI Legal Platform")
            self.vector_dim = len(test_emb)
            logger.info(f"✔ Sentence Transformer loaded. Dimension: {self.vector_dim}")
        except Exception as e:
            logger.error(f"Failed to load sentence transformer {self.model_name}: {e}")
            raise RuntimeError(f"Embedding model initialization failed: {e}")

    def _init_vector_backend(self):
        """Initializes Qdrant connection or falls back to FAISS."""
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.http import models as qmodels

            logger.info(f"Attempting connection to Qdrant at {settings.qdrant_url}...")
            client = QdrantClient(url=settings.qdrant_url, timeout=2.0)
            # Ping Qdrant
            collections = client.get_collections().collections
            self.qdrant_client = client
            self.use_qdrant = True

            # Ensure collection exists
            existing_names = [c.name for c in collections]
            if settings.qdrant_collection not in existing_names:
                self.qdrant_client.create_collection(
                    collection_name=settings.qdrant_collection,
                    vectors_config=qmodels.VectorParams(
                        size=self.vector_dim,
                        distance=qmodels.Distance.COSINE,
                    ),
                )
                logger.info(f"Created Qdrant collection: {settings.qdrant_collection}")
            else:
                logger.info(f"Qdrant collection exists: {settings.qdrant_collection}")

        except Exception as e:
            logger.warning(
                f"Qdrant unavailable at {settings.qdrant_url} ({e}). Switching to robust FAISS local fallback."
            )
            self.use_qdrant = False
            self._init_faiss()

    def _init_faiss(self):
        """Initializes local FAISS index from disk or creates a new one."""
        try:
            import faiss
            index_path = self.vector_store_dir / "faiss_index.bin"
            payload_path = self.vector_store_dir / "faiss_payload.json"

            if index_path.exists() and payload_path.exists():
                self.faiss_index = faiss.read_index(str(index_path))
                with open(payload_path, "r", encoding="utf-8") as f:
                    self.faiss_payloads = json.load(f)
                logger.info(f"✔ Loaded existing FAISS index with {self.faiss_index.ntotal} vectors.")
            else:
                self.faiss_index = faiss.IndexFlatIP(self.vector_dim)
                self.faiss_payloads = []
                logger.info(f"Initialized new empty FAISS IndexFlatIP (dim: {self.vector_dim}).")
        except Exception as e:
            logger.error(f"Failed to initialize FAISS: {e}")
            self.faiss_index = None

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Generates normalized vector embeddings for a list of strings."""
        if not texts or not self.encoder:
            return np.empty((0, self.vector_dim), dtype=np.float32)
        embeddings = self.encoder.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return np.array(embeddings, dtype=np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        """Embeds a single query string."""
        emb = self.encoder.encode([query], normalize_embeddings=True)
        return np.array(emb, dtype=np.float32)

    def index_chunks(self, chunks_dir: Optional[str] = None) -> int:
        """
        Loads all chunks from data/chunks/ and updates the active vector store (Qdrant or FAISS).
        """
        target_dir = Path(chunks_dir or settings.data_chunks_dir)
        if not target_dir.exists():
            logger.warning(f"Chunks directory not found: {target_dir}")
            return 0

        chunk_files = list(target_dir.glob("*_chunks.json"))
        all_chunks: List[Dict[str, Any]] = []

        for f in chunk_files:
            try:
                with open(f, "r", encoding="utf-8") as cf:
                    chunks = json.load(cf)
                    if isinstance(chunks, list):
                        all_chunks.extend(chunks)
            except Exception as e:
                logger.error(f"Error reading chunk file {f.name}: {e}")

        if not all_chunks:
            logger.warning("No chunks found to index.")
            return 0

        logger.info(f"Generating embeddings for {len(all_chunks)} legal chunks...")
        texts_to_embed = [
            f"{c.get('case_name', '')} {c.get('section', '')}: {c.get('text', '')}"
            for c in all_chunks
        ]
        embeddings = self.embed_texts(texts_to_embed)

        if self.use_qdrant and self.qdrant_client:
            from qdrant_client.http import models as qmodels
            points = []
            for idx, (chunk, emb) in enumerate(zip(all_chunks, embeddings)):
                points.append(
                    qmodels.PointStruct(
                        id=idx,
                        vector=emb.tolist(),
                        payload=chunk,
                    )
                )
            # Batch upsert in chunks of 100
            for i in range(0, len(points), 100):
                self.qdrant_client.upsert(
                    collection_name=settings.qdrant_collection,
                    points=points[i:i+100],
                )
            logger.info(f"✔ Successfully indexed {len(points)} vectors in Qdrant.")
        else:
            import faiss
            # Reset & rebuild FAISS index
            self.faiss_index = faiss.IndexFlatIP(self.vector_dim)
            self.faiss_index.add(embeddings)
            self.faiss_payloads = all_chunks

            # Persist FAISS index to disk
            index_path = self.vector_store_dir / "faiss_index.bin"
            payload_path = self.vector_store_dir / "faiss_payload.json"
            faiss.write_index(self.faiss_index, str(index_path))
            with open(payload_path, "w", encoding="utf-8") as f:
                json.dump(self.faiss_payloads, f, indent=2, ensure_ascii=False)
            logger.info(f"✔ Successfully saved {len(all_chunks)} vectors to local FAISS index.")

        return len(all_chunks)

    def search(
        self,
        query: str,
        top_k: int = 10,
        domain_filter: Optional[str] = None,
        document_type_filter: Optional[str] = None,
    ) -> List[Tuple[float, Dict[str, Any]]]:
        """
        Vector similarity search against Qdrant or FAISS.
        Returns list of tuples: (similarity_score, chunk_payload)
        """
        query_vec = self.embed_query(query)
        candidates: List[Tuple[float, Dict[str, Any]]] = []

        if self.use_qdrant and self.qdrant_client:
            from qdrant_client.http import models as qmodels
            q_filter = None
            conditions = []
            if domain_filter:
                conditions.append(
                    qmodels.FieldCondition(
                        key="legal_domain",
                        match=qmodels.MatchValue(value=domain_filter),
                    )
                )
            if conditions:
                q_filter = qmodels.Filter(must=conditions)

            search_result = self.qdrant_client.search(
                collection_name=settings.qdrant_collection,
                query_vector=query_vec[0].tolist(),
                limit=top_k * 2,
                query_filter=q_filter,
            )

            for hit in search_result:
                payload = hit.payload or {}
                if document_type_filter:
                    is_act = "act" in payload.get("document_id", "").lower() or "act" in payload.get("case_id", "").lower()
                    if document_type_filter == "act" and not is_act:
                        continue
                    if document_type_filter == "judgment" and is_act:
                        continue
                candidates.append((float(hit.score), payload))

        elif self.faiss_index and len(self.faiss_payloads) > 0:
            scores, indices = self.faiss_index.search(query_vec, min(top_k * 2, len(self.faiss_payloads)))
            for score, idx in zip(scores[0], indices[0]):
                if idx < 0 or idx >= len(self.faiss_payloads):
                    continue
                payload = self.faiss_payloads[idx]

                if domain_filter:
                    if domain_filter.lower() not in payload.get("legal_domain", "").lower():
                        continue
                if document_type_filter:
                    is_act = "act" in payload.get("document_id", "").lower() or "act" in payload.get("case_id", "").lower()
                    if document_type_filter == "act" and not is_act:
                        continue
                    if document_type_filter == "judgment" and is_act:
                        continue

                # Cosine similarity is in range [-1, 1], normalize to [0, 1]
                norm_score = float((score + 1.0) / 2.0)
                candidates.append((norm_score, payload))

        # Sort by similarity descending
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[:top_k]
