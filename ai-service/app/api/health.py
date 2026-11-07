"""
NyayaAI AI Service — Health Check Endpoint
"""

from fastapi import APIRouter
from datetime import datetime, timezone
import sys
import platform

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    Returns service status and system info.
    """
    health = {
        "status": "healthy",
        "service": "nyayaai-ai-service",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "python_version": sys.version,
        "platform": platform.platform(),
        "components": {},
    }

    # Check PyTorch availability
    try:
        import torch
        health["components"]["pytorch"] = {
            "status": "available",
            "version": torch.__version__,
            "cuda_available": torch.cuda.is_available(),
            "device": "cuda" if torch.cuda.is_available() else "cpu",
        }
    except ImportError:
        health["components"]["pytorch"] = {"status": "not_installed"}

    # Check Transformers availability
    try:
        import transformers
        health["components"]["transformers"] = {
            "status": "available",
            "version": transformers.__version__,
        }
    except ImportError:
        health["components"]["transformers"] = {"status": "not_installed"}

    # Check Sentence Transformers availability
    try:
        import sentence_transformers
        health["components"]["sentence_transformers"] = {
            "status": "available",
            "version": sentence_transformers.__version__,
        }
    except ImportError:
        health["components"]["sentence_transformers"] = {"status": "not_installed"}

    # Check Qdrant client
    try:
        from qdrant_client import QdrantClient
        from app.config import settings
        client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key, timeout=5)
        collections = client.get_collections()
        health["components"]["qdrant"] = {
            "status": "connected",
            "collections": len(collections.collections),
        }
    except Exception as e:
        health["components"]["qdrant"] = {
            "status": "disconnected",
            "message": str(e),
        }

    # Check Neo4j
    try:
        from neo4j import GraphDatabase
        from app.config import settings
        if settings.neo4j_password:
            driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_username, settings.neo4j_password),
            )
            driver.verify_connectivity()
            driver.close()
            health["components"]["neo4j"] = {"status": "connected"}
        else:
            health["components"]["neo4j"] = {"status": "not_configured"}
    except Exception as e:
        health["components"]["neo4j"] = {
            "status": "disconnected",
            "message": str(e),
        }

    return health
