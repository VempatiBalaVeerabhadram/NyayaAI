"""
NyayaAI AI Service — Main FastAPI Application
Entry point for the Python AI service.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import sys

from app.config import settings
from app.api.health import router as health_router
from app.api.ingest import router as ingest_router
from app.api.documents import router as documents_router
from app.api.search import router as search_router
from app.api.nlp import router as nlp_router
from app.api.graph import router as graph_router
from app.api.query import router as query_router


# Configure Loguru
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.log_level,
)
logger.add(
    "logs/ai_service.log",
    rotation="10 MB",
    retention="7 days",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — runs on startup and shutdown."""
    logger.info("=" * 60)
    logger.info("  NyayaAI AI Service Starting")
    logger.info(f"  Embedding Model: {settings.embedding_model}")
    logger.info(f"  InLegalBERT Model: {settings.inlegalbert_model}")
    logger.info(f"  Qdrant URL: {settings.qdrant_url}")
    logger.info(f"  Neo4j URI: {settings.neo4j_uri}")
    logger.info(f"  Hybrid Alpha: {settings.hybrid_alpha}")
    logger.info("=" * 60)

    # Future: Initialize models, database connections, etc.
    # These will be loaded in subsequent stages.

    yield

    # Cleanup on shutdown
    logger.info("NyayaAI AI Service shutting down...")


# Create FastAPI application
app = FastAPI(
    title="NyayaAI AI Service",
    description=(
        "AI/ML service for NyayaAI — Hybrid Legal Intelligence Platform. "
        "Provides document processing, NLP, embeddings, retrieval, "
        "knowledge graph operations, and RAG generation."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(health_router, tags=["Health"])
app.include_router(ingest_router)
app.include_router(documents_router)
app.include_router(search_router)
app.include_router(nlp_router)
app.include_router(graph_router)
app.include_router(query_router)

# Future routers (added in subsequent stages):
# app.include_router(query_router, prefix="/ai", tags=["Query"])
# app.include_router(search_router, prefix="/ai", tags=["Search"])
# app.include_router(embed_router, prefix="/ai", tags=["Embeddings"])
# app.include_router(process_router, prefix="/ai", tags=["Processing"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "NyayaAI AI Service",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }
