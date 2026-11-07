"""
NyayaAI — Metadata Extractor for Indian Legal Documents
Extracts structured metadata:
- Case Name (Petitioner vs. Respondent)
- Court Name
- Judgment Date
- Judges / Bench
- Case Number / Appeal Number
- Legal Domain
- Referenced Acts & Sections
- Citations
"""

import os
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.ingestion.citation_extractor import LegalCitationExtractor
from app.ingestion.legal_entity_extractor import LegalEntityExtractor


class LegalMetadataExtractor:
    """Extracts high-level case and statutory metadata from legal text."""

    def __init__(self):
        self.citation_extractor = LegalCitationExtractor()
        self.entity_extractor = LegalEntityExtractor()

    # Court extraction patterns
    COURT_PATTERNS = [
        (re.compile(r"Supreme Court of India", re.IGNORECASE), "Supreme Court of India"),
        (re.compile(r"High Court of Delhi|Delhi High Court", re.IGNORECASE), "High Court of Delhi"),
        (re.compile(r"High Court of Judicature at Bombay|Bombay High Court", re.IGNORECASE), "High Court of Bombay"),
        (re.compile(r"High Court of Judicature at Allahabad|Allahabad High Court", re.IGNORECASE), "High Court of Allahabad"),
        (re.compile(r"High Court of Judicature at Madras|Madras High Court", re.IGNORECASE), "High Court of Madras"),
        (re.compile(r"High Court of Karnataka|Karnataka High Court", re.IGNORECASE), "High Court of Karnataka"),
        (re.compile(r"High Court of Punjab and Haryana", re.IGNORECASE), "High Court of Punjab and Haryana"),
        (re.compile(r"High Court of Calcutta|Calcutta High Court", re.IGNORECASE), "High Court of Calcutta"),
    ]

    # Date patterns (e.g., '29 January, 2020', '29.01.2020', 'January 29, 2020', 'Dated: 29-01-2020')
    DATE_PATTERNS = [
        re.compile(r"(?:Dated|Decided on|Judgment Date|Date\s*:)\s*(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})", re.IGNORECASE),
        re.compile(r"(\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December),?\s+\d{4})", re.IGNORECASE),
        re.compile(r"((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})", re.IGNORECASE),
    ]

    # Bench / Judge pattern
    JUDGE_PATTERNS = [
        re.compile(r"(?:Coram|Bench|Before|Present)\s*:\s*([^\n]+(?:\n[^\n]+)?)", re.IGNORECASE),
        re.compile(r"((?:Hon['’]ble\s+(?:Mr\.|Ms\.|Mrs\.)?\s*Justice\s+[A-Za-z\s.,]+(?:,|\band\b|;)?)+)", re.IGNORECASE),
    ]

    # Case number pattern
    CASE_NO_PATTERN = re.compile(
        r"(?:Criminal Appeal|Civil Appeal|Special Leave Petition|SLP\s*\(Crl\.\)|Writ Petition|W\.P\.)\s*(?:\([A-Za-z.\s]+\))?\s*No\.?\s*(\d+(?:-\d+)?\s+of\s+\d{4})",
        re.IGNORECASE,
    )

    def extract_court(self, text: str) -> str:
        """Identifies the court where the matter was adjudicated."""
        for pattern, court_name in self.COURT_PATTERNS:
            if pattern.search(text[:3000]):  # Focus on header portion
                return court_name
        return "Supreme Court of India"  # Default fallback for apex rulings

    def extract_date(self, text: str) -> Optional[str]:
        """Extracts and normalizes the date of judgment (YYYY-MM-DD format)."""
        header_text = text[:4000]
        for pattern in self.DATE_PATTERNS:
            match = pattern.search(header_text)
            if match:
                raw_date = match.group(1).strip()
                # Clean ordinal suffixes like 29th -> 29
                raw_date_clean = re.sub(r"(\d+)(?:st|nd|rd|th)", r"\1", raw_date)
                # Attempt standard date parses
                for fmt in ["%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y", "%d %B, %Y", "%d %B %Y", "%B %d, %Y", "%B %d %Y"]:
                    try:
                        parsed = datetime.strptime(raw_date_clean, fmt)
                        return parsed.strftime("%Y-%m-%d")
                    except ValueError:
                        continue
        return None

    def extract_case_name(self, text: str, fallback_filename: str = "") -> str:
        """Extracts the primary case title (Petitioner v. Respondent)."""
        titles = self.citation_extractor.extract_case_titles(text[:3000])
        if titles:
            return titles[0]

        # Fallback to sanitized filename if available
        if fallback_filename:
            base_filename = os.path.basename(fallback_filename)
            clean_name = re.sub(r"[_\-]+", " ", base_filename)
            clean_name = re.sub(r"\.(pdf|html|json)$", "", clean_name, flags=re.IGNORECASE)
            return clean_name.title()

        return "Unknown v. State"

    def extract_judges(self, text: str) -> List[str]:
        """Extracts the names of judges sitting on the bench."""
        judges: List[str] = []
        header_text = text[:3000]

        for pattern in self.JUDGE_PATTERNS:
            match = pattern.search(header_text)
            if match:
                raw = match.group(1)
                # Split multiple judges
                parts = re.split(r"[,;&]|\band\b", raw)
                for part in parts:
                    name = part.strip()
                    name = re.sub(r"(?i)^(?:hon['’]ble\s+)?(?:mr\.|ms\.|mrs\.)?\s*justice\s+", "", name)
                    name = re.sub(r"(?i)\s*,?\s*jj?\.?$", "", name).strip()
                    if len(name) > 3 and len(name) < 40 and not any(kw in name.lower() for kw in ["court", "appeal", "order"]):
                        judges.append(name)
                if judges:
                    break

        return list(dict.fromkeys(judges))  # Deduplicate while preserving order

    def extract_case_number(self, text: str) -> Optional[str]:
        """Extracts formal case registration or appeal number."""
        match = self.CASE_NO_PATTERN.search(text[:3000])
        if match:
            return match.group(0).strip()
        return None

    def extract_metadata(
        self,
        text: str,
        document_id: str,
        document_type: str = "judgment",
        source_url: str = "",
        file_path: str = "",
    ) -> Dict[str, Any]:
        """Assembles complete standardized metadata record."""
        case_name = self.extract_case_name(text, fallback_filename=file_path)
        court = self.extract_court(text)
        judgment_date = self.extract_date(text)
        judges = self.extract_judges(text)
        case_number = self.extract_case_number(text)
        acts = self.entity_extractor.extract_acts(text)
        sections = self.entity_extractor.extract_sections(text)
        legal_issues = self.entity_extractor.infer_legal_issues(text)
        citations = self.citation_extractor.extract_citations(text)

        # Primary legal domain inference
        acts_lower = [a.lower() for a in acts]
        text_lower = text.lower()
        if any("it act" in a or "information technology" in a for a in acts_lower) or "cyber" in text_lower or "section 66" in text_lower:
            domain = "Cyber Law"
        elif any("constitution" in a for a in acts_lower) or "article 21" in text_lower or "article 19" in text_lower:
            domain = "Constitutional Law"
        elif any("crpc" in a or "ipc" in a or "bnss" in a or "bns" in a for a in acts_lower) or any("bail" in issue.lower() or "cheating" in issue.lower() for issue in legal_issues):
            domain = "Criminal Law"
        else:
            domain = "General Law"

        return {
            "document_id": document_id,
            "document_type": document_type,
            "case_id": f"CASE_{document_id}",
            "case_name": case_name,
            "court": court,
            "judgment_date": judgment_date,
            "judges": judges,
            "case_number": case_number or "",
            "legal_domain": domain,
            "acts": acts,
            "sections": sections,
            "legal_issues": legal_issues,
            "citations": citations,
            "source_url": source_url,
            "file_path": file_path,
            "language": "English",
        }
