"""
NyayaAI AI Service — Configuration
Reads environment variables and provides typed settings via Pydantic.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # --- Service ---
    ai_service_host: str = Field(default="0.0.0.0", alias="AI_SERVICE_HOST")
    ai_service_port: int = Field(default=8000, alias="AI_SERVICE_PORT")
    debug: bool = Field(default=True, alias="DEBUG")

    # --- Embedding Model ---
    embedding_model: str = Field(
        default="all-MiniLM-L6-v2",
        alias="EMBEDDING_MODEL",
        description="Sentence Transformer model for embeddings",
    )
    embedding_dimension: int = Field(default=384, alias="EMBEDDING_DIMENSION")

    # --- InLegalBERT ---
    inlegalbert_model: str = Field(
        default="law-ai/InLegalBERT",
        alias="INLEGALBERT_MODEL",
        description="InLegalBERT model for legal query understanding",
    )

    # --- Retrieval ---
    bm25_top_k: int = Field(default=10, alias="BM25_TOP_K")
    semantic_top_k: int = Field(default=10, alias="SEMANTIC_TOP_K")
    hybrid_alpha: float = Field(
        default=0.5,
        alias="HYBRID_ALPHA",
        description="Weight for BM25 in hybrid scoring (0.0 = pure semantic, 1.0 = pure BM25)",
    )
    graph_depth: int = Field(default=1, alias="GRAPH_DEPTH")

    # --- Qdrant ---
    qdrant_url: str = Field(default="http://localhost:6333", alias="QDRANT_URL")
    qdrant_api_key: Optional[str] = Field(default=None, alias="QDRANT_API_KEY")
    qdrant_collection_name: str = Field(default="nyayaai_chunks", alias="QDRANT_COLLECTION")

    # --- Neo4j ---
    neo4j_uri: str = Field(default="bolt://localhost:7687", alias="NEO4J_URI")
    neo4j_username: str = Field(default="neo4j", alias="NEO4J_USERNAME")
    neo4j_password: str = Field(default="", alias="NEO4J_PASSWORD")

    # --- Gemini ---
    gemini_api_key: Optional[str] = Field(default=None, alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-1.5-flash", alias="GEMINI_MODEL")

    # --- Data Paths ---
    data_raw_dir: str = Field(
        default=str(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw"))),
        alias="DATA_RAW_DIR"
    )
    data_processed_dir: str = Field(
        default=str(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed"))),
        alias="DATA_PROCESSED_DIR"
    )
    data_chunks_dir: str = Field(
        default=str(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "chunks"))),
        alias="DATA_CHUNKS_DIR"
    )
    data_metadata_dir: str = Field(
        default=str(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "metadata"))),
        alias="DATA_METADATA_DIR"
    )

    # --- Chunking ---
    chunk_size: int = Field(default=800, alias="CHUNK_SIZE", description="Target chunk size in tokens")
    chunk_overlap: int = Field(default=100, alias="CHUNK_OVERLAP", description="Overlap between chunks in tokens")

    # --- Logging ---
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    model_config = SettingsConfigDict(
        env_file="../../.env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Singleton settings instance
settings = Settings()
