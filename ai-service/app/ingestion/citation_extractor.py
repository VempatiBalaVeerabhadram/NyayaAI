"""
NyayaAI — Citation Extractor for Indian Legal Judgments
Identifies, extracts, and normalizes standard Indian legal citations:
- Supreme Court Cases (SCC): (2020) 5 SCC 123
- All India Reporter (AIR): AIR 2020 SC 123, AIR 1980 SC 1632
- Supreme Court Reports (SCR): [2020] 1 SCR 123
- SCC OnLine: 2020 SCC OnLine SC 123
- Case Titles: [Petitioner] v. [Respondent]
"""

import re
from typing import List, Dict, Any, Optional


class LegalCitationExtractor:
    """Extracts and normalizes Indian legal citations from judgment text."""

    # Indian Citation Regular Expressions
    SCC_PATTERN = re.compile(
        r"(?:\[|\()(\d{4})(?:\]|\))\s*(\d+)?\s*SCC\s*(?:\([A-Za-z&]+\)\s*)?(\d+)",
        re.IGNORECASE,
    )
    AIR_PATTERN = re.compile(
        r"\bAIR\s+(\d{4})\s+([A-Z][a-zA-Z\s]{1,15})\s+(\d+)\b",
        re.IGNORECASE,
    )
    SCR_PATTERN = re.compile(
        r"(?:\[|\()(\d{4})(?:\]|\))\s*(\d+)?\s*S\.?C\.?R\.?\s*(\d+)",
        re.IGNORECASE,
    )
    SCC_ONLINE_PATTERN = re.compile(
        r"(?:\[|\()?\b(\d{4})(?:\]|\))?\s+SCC\s+OnLine\s+([A-Z][a-zA-Z\s]{1,15})\s+(\d+)\b",
        re.IGNORECASE,
    )
    CASE_TITLE_PATTERN = re.compile(
        r"([A-Z][A-Za-z0-9\s.,'()\-]+?)\s+(?:v\.|vs\.|versus)\s+([A-Z][A-Za-z0-9\s.,'()\-]+?)(?=[,;\n.]|\s+(?:reported\s+in|\(20|\(19|AIR))",
        re.MULTILINE,
    )

    def extract_citations(self, text: str, page_number: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Extracts all citation instances from text, returning structured metadata:
        - raw_citation
        - normalized_citation
        - reporter (SCC, AIR, SCR, SCC_ONLINE)
        - year
        - page_number (where the citation occurred)
        """
        if not text:
            return []

        citations: List[Dict[str, Any]] = []
        seen = set()

        # 1. Extract SCC citations
        for match in self.SCC_PATTERN.finditer(text):
            year, volume, page = match.groups()
            raw = match.group(0).strip()
            vol_str = f" {volume}" if volume else ""
            normalized = f"({year}){vol_str} SCC {page}"
            if normalized not in seen:
                seen.add(normalized)
                citations.append({
                    "raw_citation": raw,
                    "normalized_citation": normalized,
                    "reporter": "SCC",
                    "year": int(year),
                    "volume": volume,
                    "page_or_id": page,
                    "page_number": page_number,
                })

        # 2. Extract AIR citations
        for match in self.AIR_PATTERN.finditer(text):
            year, court, page = match.groups()
            raw = match.group(0).strip()
            court_clean = court.strip().upper()
            normalized = f"AIR {year} {court_clean} {page}"
            if normalized not in seen:
                seen.add(normalized)
                citations.append({
                    "raw_citation": raw,
                    "normalized_citation": normalized,
                    "reporter": "AIR",
                    "year": int(year),
                    "court": court_clean,
                    "page_or_id": page,
                    "page_number": page_number,
                })

        # 3. Extract SCC OnLine citations
        for match in self.SCC_ONLINE_PATTERN.finditer(text):
            year, court, number = match.groups()
            raw = match.group(0).strip()
            court_clean = court.strip().upper()
            normalized = f"{year} SCC OnLine {court_clean} {number}"
            if normalized not in seen:
                seen.add(normalized)
                citations.append({
                    "raw_citation": raw,
                    "normalized_citation": normalized,
                    "reporter": "SCC_ONLINE",
                    "year": int(year),
                    "court": court_clean,
                    "page_or_id": number,
                    "page_number": page_number,
                })

        # 4. Extract SCR citations
        for match in self.SCR_PATTERN.finditer(text):
            year, volume, page = match.groups()
            raw = match.group(0).strip()
            vol_str = f" {volume}" if volume else ""
            normalized = f"[{year}]{vol_str} SCR {page}"
            if normalized not in seen:
                seen.add(normalized)
                citations.append({
                    "raw_citation": raw,
                    "normalized_citation": normalized,
                    "reporter": "SCR",
                    "year": int(year),
                    "volume": volume,
                    "page_or_id": page,
                    "page_number": page_number,
                })

        return citations

    def extract_case_titles(self, text: str) -> List[str]:
        """Extracts cited case titles ('Party A v. Party B')."""
        if not text:
            return []

        titles: List[str] = []
        seen = set()

        for match in self.CASE_TITLE_PATTERN.finditer(text):
            petitioner = match.group(1).strip()
            respondent = match.group(2).strip()

            # Clean procedural tags common in Indian judgments
            petitioner = re.sub(r"(?i)\s*(?:\.{2,}|\b)\s*(?:appellants?|petitioners?|applicants?|accused)\b", "", petitioner).strip()
            respondent = re.sub(r"(?i)\s*(?:\.{2,}|\b)\s*(?:respondents?)\b", "", respondent).strip()

            # Filter out non-case false positives
            if len(petitioner) < 3 or len(respondent) < 3 or len(petitioner) > 80 or len(respondent) > 80:
                continue
            if any(term in petitioner.lower() for term in ["section", "article", "order", "rule", "clause"]):
                continue

            title = f"{petitioner} v. {respondent}"
            if title not in seen:
                seen.add(title)
                titles.append(title)

        return titles
