"""
NyayaAI — Comprehensive Ingestion Pipeline Tests
Tests text cleaning, PDF parsing with page boundaries, citation extraction,
legal entity recognition, and semantic chunking.
"""

import pytest
import os
import sys
import tempfile
from pathlib import Path

# Add ai-service to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.ingestion.text_cleaner import LegalTextCleaner
from app.ingestion.citation_extractor import LegalCitationExtractor
from app.ingestion.legal_entity_extractor import LegalEntityExtractor
from app.ingestion.metadata_extractor import LegalMetadataExtractor
from app.ingestion.chunker import LegalSemanticChunker
from app.ingestion.pdf_parser import LegalPDFParser
from app.ingestion.document_loader import LegalDocumentLoader


@pytest.fixture
def cleaner():
    return LegalTextCleaner()


@pytest.fixture
def citation_extractor():
    return LegalCitationExtractor()


@pytest.fixture
def entity_extractor():
    return LegalEntityExtractor()


@pytest.fixture
def chunker():
    return LegalSemanticChunker(target_chunk_size=100, overlap_size=20)


def test_text_cleaner_unicode_and_whitespace(cleaner):
    raw = "IN THE SUPREME COURT OF INDIA\n\n\nPage 1 of 10\n\njurisdic-\ntion   under   ‘Section 438’."
    cleaned = cleaner.clean_text(raw)
    assert "jurisdiction" in cleaned
    assert "'Section 438'" in cleaned
    assert "Page 1 of 10" not in cleaned


def test_citation_extractor(citation_extractor):
    text = (
        "In Gurbaksh Singh Sibbia v. State of Punjab (1980) 2 SCC 565 and AIR 1980 SC 1632, "
        "as reaffirmed in Sushila Aggarwal v. State (NCT of Delhi) 2020 SCC OnLine SC 98, "
        "the Constitution Bench settled the law on anticipatory bail."
    )
    citations = citation_extractor.extract_citations(text, page_number=2)
    assert len(citations) >= 2

    scc = next((c for c in citations if c["reporter"] == "SCC"), None)
    assert scc is not None
    assert scc["year"] == 1980
    assert scc["normalized_citation"] == "(1980) 2 SCC 565"
    assert scc["page_number"] == 2

    air = next((c for c in citations if c["reporter"] == "AIR"), None)
    assert air is not None
    assert air["year"] == 1980
    assert air["court"] == "SC"

    titles = citation_extractor.extract_case_titles(text)
    assert any("Gurbaksh Singh Sibbia" in t for t in titles)


def test_legal_entity_extractor(entity_extractor):
    text = (
        "The appellant sought anticipatory bail under Section 438 of the Code of Criminal Procedure, 1973 "
        "in connection with allegations of cheating under Section 420 and criminal breach of trust under Section 406 IPC. "
        "Reliance was placed on Article 21 of the Constitution of India."
    )
    acts = entity_extractor.extract_acts(text)
    assert "Code of Criminal Procedure, 1973" in acts
    assert "Indian Penal Code, 1860" in acts
    assert "Constitution of India, 1950" in acts

    sections = entity_extractor.extract_sections(text)
    assert "438" in sections
    assert "420" in sections
    assert "406" in sections

    articles = entity_extractor.extract_articles(text)
    assert "21" in articles

    issues = entity_extractor.infer_legal_issues(text)
    assert "Anticipatory Bail" in issues or "Cheating" in issues


def test_semantic_chunker(chunker):
    pages = [
        {
            "page_number": 1,
            "text": "1. The accused filed an application under Section 438 CrPC for grant of anticipatory bail in a criminal proceeding."
        },
        {
            "page_number": 2,
            "text": "14. We have considered the rival submissions. The right to personal liberty under Article 21 cannot be denied lightly."
        }
    ]
    chunks = chunker.chunk_pages(
        pages=pages,
        case_id="CASE_TEST_001",
        document_id="DOC_TEST_001",
        case_name="Test v. State",
        legal_domain="Criminal Law"
    )
    assert len(chunks) == 2
    assert chunks[0]["page"] == 1
    assert chunks[0]["case_id"] == "CASE_TEST_001"
    assert chunks[1]["page"] == 2
    assert "Section 438" in chunks[0]["text"]


def test_pdf_parser_real_file():
    pdf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "judgments", "sushila_aggarwal_2020.pdf"))
    if not os.path.exists(pdf_path):
        pytest.skip("Sample PDF not found")

    parser = LegalPDFParser()
    pages = parser.parse_pdf(pdf_path, clean=True)
    assert len(pages) == 3
    assert pages[0]["page_number"] == 1
    assert pages[1]["page_number"] == 2
    assert pages[2]["page_number"] == 3
    assert "Sushila Aggarwal" in pages[0]["text"]
    assert "Section 438" in pages[0]["text"]


def test_document_loader_end_to_end():
    json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "judgments", "gurbaksh_singh_sibbia_1980.json"))
    loader = LegalDocumentLoader()
    result = loader.process_document(json_path)

    assert result["status"] == "PROCESSED"
    assert result["document_id"] == "DOC_SC_1980_GURBAKSH_SIBBIA"
    assert result["metadata"]["court"] == "Supreme Court of India"
    assert "438" in result["metadata"]["sections"]
    assert result["total_chunks"] > 0
