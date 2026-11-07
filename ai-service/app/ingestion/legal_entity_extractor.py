"""
NyayaAI — Legal Entity Extractor for Indian Legal Documents
Extracts structured legal entities:
- Acts and Statutes (CrPC, IPC, BNSS, BNS, Constitution, IT Act, etc.)
- Sections and Articles (Section 438, Section 420, Article 21, etc.)
- Courts (Supreme Court, High Courts)
- Legal Issues and Core Doctrinal Concepts
"""

import re
from typing import List, Dict, Any, Set


class LegalEntityExtractor:
    """Extracts statutory references, sections, courts, and legal issues."""

    # Canonical Indian Acts mapping
    KNOWN_ACTS = {
        "crpc": "Code of Criminal Procedure, 1973",
        "code of criminal procedure": "Code of Criminal Procedure, 1973",
        "ipc": "Indian Penal Code, 1860",
        "indian penal code": "Indian Penal Code, 1860",
        "constitution": "Constitution of India, 1950",
        "constitution of india": "Constitution of India, 1950",
        "evidence act": "Indian Evidence Act, 1872",
        "indian evidence act": "Indian Evidence Act, 1872",
        "it act": "Information Technology Act, 2000",
        "information technology act": "Information Technology Act, 2000",
        "bnss": "Bharatiya Nagarik Suraksha Sanhita, 2023",
        "bharatiya nagarik suraksha sanhita": "Bharatiya Nagarik Suraksha Sanhita, 2023",
        "bns": "Bharatiya Nyaya Sanhita, 2023",
        "bharatiya nyaya sanhita": "Bharatiya Nyaya Sanhita, 2023",
        "bsa": "Bharatiya Sakshya Adhiniyam, 2023",
        "pocso": "Protection of Children from Sexual Offences Act, 2012",
        "ndps": "Narcotic Drugs and Psychotropic Substances Act, 1985",
        "pmla": "Prevention of Money Laundering Act, 2002",
        "ni act": "Negotiable Instruments Act, 1881",
    }

    # Section extraction patterns
    SECTION_PATTERN = re.compile(
        r"(?:Section|Sec\.|Sections|Secs\.)\s+(\d+[A-Z]?(?:\s*(?:and|,)\s*\d+[A-Z]?)*)",
        re.IGNORECASE,
    )
    ARTICLE_PATTERN = re.compile(
        r"(?:Article|Art\.|Articles|Arts\.)\s+(\d+[A-Z]?(?:\s*(?:and|,)\s*\d+[A-Z]?)*)",
        re.IGNORECASE,
    )

    # Core Indian Legal Issues & Taxonomy
    LEGAL_ISSUES_MAP = {
        "anticipatory bail": ["Section 438", "Personal Liberty", "Apprehension of Arrest", "Custodial Interrogation"],
        "regular bail": ["Section 437", "Section 439", "Post-arrest Bail", "Bail not Jail"],
        "default bail": ["Section 167(2)", "Statutory Bail", "Period of Remand"],
        "quashing of fir": ["Section 482", "Inherent Powers", "Abuse of Process of Court"],
        "cheating": ["Section 420", "Section 415", "Dishonest Inducement", "Fraudulent Intent"],
        "criminal breach of trust": ["Section 405", "Section 406", "Entrustment of Property", "Misappropriation"],
        "cybercrime": ["Information Technology Act", "Section 66", "Electronic Evidence", "Section 65B"],
    }

    def extract_acts(self, text: str) -> List[str]:
        """Identifies acts and statutory enactments referenced in text."""
        if not text:
            return []

        lower_text = text.lower()
        matched_acts: Set[str] = set()

        for key, canonical_name in self.KNOWN_ACTS.items():
            pattern = r"\b" + re.escape(key) + r"\b"
            if re.search(pattern, lower_text):
                matched_acts.add(canonical_name)

        return sorted(list(matched_acts))

    def extract_sections(self, text: str) -> List[str]:
        """Extracts unique statutory section numbers referenced in text."""
        if not text:
            return []

        sections: Set[str] = set()

        for match in self.SECTION_PATTERN.finditer(text):
            raw_nums = match.group(1)
            # Split numbers on comma or and
            split_nums = re.split(r"[,&]|\band\b", raw_nums)
            for num in split_nums:
                clean_num = num.strip()
                if clean_num:
                    sections.add(clean_num)

        return sorted(list(sections), key=lambda x: (int(re.sub(r"\D", "", x)) if re.sub(r"\D", "", x) else 0, x))

    def extract_articles(self, text: str) -> List[str]:
        """Extracts constitutional articles referenced in text."""
        if not text:
            return []

        articles: Set[str] = set()

        for match in self.ARTICLE_PATTERN.finditer(text):
            raw_nums = match.group(1)
            split_nums = re.split(r"[,&]|\band\b", raw_nums)
            for num in split_nums:
                clean_num = num.strip()
                if clean_num:
                    articles.add(clean_num)

        return sorted(list(articles), key=lambda x: (int(re.sub(r"\D", "", x)) if re.sub(r"\D", "", x) else 0, x))

    def infer_legal_issues(self, text: str) -> List[str]:
        """Identifies legal issues and domain categories discussed in the text."""
        if not text:
            return []

        lower_text = text.lower()
        issues: List[str] = []

        for issue_name, keywords in self.LEGAL_ISSUES_MAP.items():
            if issue_name in lower_text:
                issues.append(issue_name.title())
            elif any(kw.lower() in lower_text for kw in keywords):
                issues.append(issue_name.title())

        return list(set(issues))
