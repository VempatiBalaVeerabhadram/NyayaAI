"""
NyayaAI — Pydantic Schemas for Legal Documents and Ingestion
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class CitationModel(BaseModel):
    reporter: str
    year: Optional[int] = None
    volume: Optional[int] = None
    page: Optional[int] = None
    court: Optional[str] = None
    normalized_citation: str
    citation_text: str
    page_number: int = 1


class DocumentMetadataModel(BaseModel):
    document_id: str
    document_type: str = "judgment"
    case_id: str
    case_name: str
    court: str
    judgment_date: Optional[str] = None
    judges: List[str] = Field(default_factory=list)
    case_number: str = ""
    legal_domain: str = "Criminal Law"
    acts: List[str] = Field(default_factory=list)
    sections: List[str] = Field(default_factory=list)
    legal_issues: List[str] = Field(default_factory=list)
    citations: List[Dict[str, Any]] = Field(default_factory=list)
    source_url: str = ""
    file_path: str = ""
    language: str = "English"
    sha256: Optional[str] = None
    total_pages: int = 1


class ChunkModel(BaseModel):
    chunk_id: str
    case_id: str
    document_id: str
    case_name: str
    page: int
    paragraph_number: str
    text: str
    section: str
    legal_domain: str
    word_count: int
    source_url: str = ""


class ProcessedDocumentResponse(BaseModel):
    document_id: str
    metadata: DocumentMetadataModel
    total_chunks: int
    chunks: List[ChunkModel] = Field(default_factory=list)
    status: str = "PROCESSED"


class URLIngestRequest(BaseModel):
    source_url: str = Field(..., description="Direct URL to legal document (PDF, HTML, JSON)")
    document_type: str = Field("judgment", description="'judgment', 'act', or 'order'")
    case_name: Optional[str] = Field(None, description="Explicit case title (Petitioner v. Respondent)")
    court: Optional[str] = Field(None, description="Adjudicating court")
    judgment_date: Optional[str] = Field(None, description="Date in YYYY-MM-DD or DD.MM.YYYY")
    document_id: Optional[str] = Field(None, description="Custom document ID")


class DirectoryIngestRequest(BaseModel):
    input_directory: str = Field("data/raw/", description="Directory path containing raw legal documents")
    document_type: str = Field("auto", description="'judgment', 'act', 'order', or 'auto'")
    dry_run: bool = Field(False, description="Preview without saving")


class DocumentSummaryItem(BaseModel):
    document_id: str
    case_name: str
    document_type: str
    court: str
    judgment_date: Optional[str] = None
    legal_domain: str
    total_chunks: int
    acts_count: int
    sections_count: int
    citations_count: int
    source_url: str
    status: str


class IngestionStatisticsResponse(BaseModel):
    total_documents: int
    total_judgments: int
    total_acts: int
    total_chunks: int
    total_sections: int
    processed_count: int
    failed_count: int
