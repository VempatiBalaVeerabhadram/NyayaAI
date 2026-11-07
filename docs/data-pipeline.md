# NyayaAI Legal Document Ingestion & Processing Pipeline

## 1. Objective

To transform unstructured Indian legal artifacts (PDF judgments, India Code gazettes, Acts, Orders) into semantically enriched, provenance-tracked, and relational knowledge artifacts.

---

## 2. Ingestion Methods

### Method A — Local Document Directory Ingestion
Administrators can place source legal documents into `data/raw/`:
- `data/raw/judgments/` (Court decisions, orders)
- `data/raw/acts/` (Statutes, amending acts)
- `data/raw/orders/` (Tribunal / interlocutory rulings)

Running:
```bash
python scripts/ingest.py --input data/raw/judgments --type judgment
```
triggers parsing, cleaning, metadata extraction, citation linkage, and chunk indexing.

### Method B — Verified URL Ingestion
Allows administrators to provide:
- `document_url`
- `document_type`
- `court`
- `judgment_date`
- `case_name`
- `source`

The system validates the official domain (e.g., `main.sci.gov.in`, `judgments.ecourts.gov.in`, `indiacode.nic.in`), fetches content, and computes SHA-256 hashes to guarantee provenance.

---

## 3. Provenance and Chunk Schema

Every extracted chunk adheres to the following specification:

```json
{
  "chunk_id": "CASE_2020_SC_123_P14_C02",
  "document_id": "DOC_IN_SC_2020_123",
  "case_id": "CASE_2020_SC_123",
  "case_name": "Sushila Aggarwal and Others v. State (NCT of Delhi) and Another",
  "court": "Supreme Court of India",
  "judgment_date": "2020-01-29",
  "page_number": 14,
  "paragraph_number": "32",
  "section_context": "Reasoning on Anticipatory Bail Duration",
  "legal_domain": "Criminal Law",
  "text": "The protection granted under Section 438 Cr.P.C. should not be invariably limited to a fixed period. In normal circumstances, the protection continues till the end of the trial...",
  "acts_mentioned": ["Code of Criminal Procedure, 1973"],
  "sections_mentioned": ["438", "437"],
  "citations_detected": ["(1980) 2 SCC 565"],
  "source_url": "https://main.sci.gov.in/supremecourt/2018/...",
  "hash": "a4f89d..."
}
```

---

## 4. Extraction Submodules

| Module | Function |
|---|---|
| `document_loader.py` | Dispatches file formats (PDF, HTML, JSON) to appropriate parsers |
| `pdf_parser.py` | Extracts text while preserving strict page boundaries using `pdfplumber` |
| `html_parser.py` | Extracts legislation hierarchies (Chapters, Sections, Explanations) |
| `text_cleaner.py` | Removes court stamps, header watermarks, carriage returns, and hyphenated line-breaks |
| `metadata_extractor.py` | Identifies Bench, Petitioner, Respondent, Case Number, Date, and Legal Domain |
| `citation_extractor.py` | Detects Indian citation formats (`SCC`, `AIR`, `SCR`, `ILR`, `SCC OnLine`) |
| `legal_entity_extractor.py`| Identifies statutory enactments and section numbers using regex and InLegalBERT |
| `chunker.py` | Produces 500–1000 token semantically coherent chunks with overlap |
