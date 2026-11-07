"""
NyayaAI — Ingestion and Document API Tests
Tests Method A file uploads, Method B URL ingestion, document inspection, and statistics.
"""

import pytest
import os
import sys
from fastapi.testclient import TestClient

# Add ai-service to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app

client = TestClient(app)


def test_documents_list():
    response = client.get("/ai/documents")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    first_doc = data[0]
    assert "document_id" in first_doc
    assert "case_name" in first_doc
    assert "total_chunks" in first_doc


def test_documents_statistics():
    response = client.get("/ai/documents/statistics")
    assert response.status_code == 200
    stats = response.json()
    assert stats["total_documents"] >= 15
    assert stats["total_chunks"] >= 30
    assert stats["total_acts"] >= 3
    assert stats["total_judgments"] >= 10


def test_get_single_document():
    # List docs first to get a real ID
    docs = client.get("/ai/documents").json()
    assert len(docs) > 0
    doc_id = docs[0]["document_id"]

    response = client.get(f"/ai/documents/{doc_id}")
    assert response.status_code == 200
    doc_data = response.json()
    assert doc_data["document_id"] == doc_id
    assert "metadata" in doc_data
    assert "chunks" in doc_data
    assert len(doc_data["chunks"]) > 0


def test_ingest_file_upload():
    sample_legal_text = (
        "REPORTABLE\nIN THE SUPREME COURT OF INDIA\n"
        "ABC v. STATE OF MAHARASHTRA\n"
        "Dated: 15.08.2023\n\n"
        "1. The appellant filed an application under Section 438 of the Code of Criminal Procedure, 1973 "
        "seeking anticipatory bail in connection with FIR under Section 420 of the Indian Penal Code, 1860.\n\n"
        "2. Having considered the principles laid down in Gurbaksh Singh Sibbia (1980) 2 SCC 565, "
        "we are of the view that anticipatory bail should be granted subject to cooperation."
    )
    files = {"file": ("test_appeal_2023.txt", sample_legal_text.encode("utf-8"), "text/plain")}
    data = {"document_type": "judgment", "case_name": "ABC v. State of Maharashtra"}

    response = client.post("/ai/ingest/file", files=files, data=data)
    assert response.status_code == 200
    res = response.json()
    assert res["status"] == "PROCESSED"
    assert res["metadata"]["case_name"] == "ABC v. State of Maharashtra"
    assert "438" in res["metadata"]["sections"]
    assert res["total_chunks"] >= 1
