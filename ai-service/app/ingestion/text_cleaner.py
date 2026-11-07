"""
NyayaAI — Text Cleaner for Indian Legal Documents
Cleans raw text extracted from Indian court judgments and legislative documents.
Preserves legal structure, section notations, and case references while removing
header/footer noise, page stamps, watermarks, and irregular typography.
"""

import re
import unicodedata
from typing import List, Optional


class LegalTextCleaner:
    """Normalizes and cleans Indian legal documents."""

    # Patterns for court header/footer noise
    HEADER_FOOTER_PATTERNS = [
        r"(?i)^\s*(?:in\s+the\s+supreme\s+court\s+of\s+india|supreme\s+court\s+of\s+india)\s*$",
        r"(?i)^\s*(?:in\s+the\s+high\s+court\s+of\s+[a-z\s]+)\s*$",
        r"(?i)^\s*(?:appellate\s+jurisdiction|criminal\s+appellate\s+jurisdiction|civil\s+appellate\s+jurisdiction)\s*$",
        r"(?i)^\s*page\s+\d+\s+of\s+\d+\s*$",
        r"(?i)^\s*judgment\s+dated\s*:\s*\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\s*$",
        r"(?i)^\s*digitally\s+signed\s+by\s+[^\n]+\s*$",
        r"(?i)^\s*signature\s+not\s+verified\s*$",
        r"(?i)^\s*www\.\w+\.gov\.in[^\n]*\s*$",
        r"(?i)^\s*scc\s+online\s+web\s+edition[^\n]*\s*$",
        r"(?i)^\s*true\s+copy\s*$",
    ]

    def __init__(self):
        self._header_footer_regexes = [
            re.compile(pattern, re.MULTILINE) for pattern in self.HEADER_FOOTER_PATTERNS
        ]

    def normalize_unicode(self, text: str) -> str:
        """Converts ligatures, smart quotes, em-dashes, and irregular unicode characters to standard ASCII/UTF-8."""
        if not text:
            return ""
        # NFKC normalizes special ligatures and forms
        text = unicodedata.normalize("NFKC", text)

        # Replace non-standard legal typographical quotes and dashes
        replacements = {
            "\u2018": "'",  # Left single quotation mark
            "\u2019": "'",  # Right single quotation mark
            "\u201c": '"',  # Left double quotation mark
            "\u201d": '"',  # Right double quotation mark
            "\u2013": "-",  # En dash
            "\u2014": " - ",  # Em dash
            "\u2026": "...",  # Ellipsis
            "\u00a0": " ",  # Non-breaking space
            "\t": " ",  # Tab
        }
        for orig, rep in replacements.items():
            text = text.replace(orig, rep)

        return text

    def clean_court_noise(self, text: str) -> str:
        """Removes common digital signature stamps, watermark indicators, and header/footer boilerplate."""
        if not text:
            return ""

        cleaned = text
        for regex in self._header_footer_regexes:
            cleaned = regex.sub("", cleaned)

        return cleaned

    def fix_hyphenated_linebreaks(self, text: str) -> str:
        """
        Rejoins words split by hyphens across line breaks in legal text:
        e.g., 'jurisdic-\\ntion' -> 'jurisdiction'.
        """
        if not text:
            return ""
        return re.sub(r"(\b\w+)-\s*\n\s*(\w+\b)", r"\1\2", text)

    def normalize_whitespace(self, text: str) -> str:
        """
        Normalizes multiple spaces while maintaining meaningful paragraph breaks (double newlines).
        """
        if not text:
            return ""

        # Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Replace multiple spaces with a single space
        text = re.sub(r"[ ]{2,}", " ", text)

        # Clean leading/trailing spaces per line
        lines = [line.strip() for line in text.split("\n")]

        # Collapse more than two consecutive empty lines into a double newline (paragraph boundary)
        collapsed_lines: List[str] = []
        consecutive_empty = 0

        for line in lines:
            if not line:
                consecutive_empty += 1
                if consecutive_empty <= 1:
                    collapsed_lines.append("")
            else:
                consecutive_empty = 0
                collapsed_lines.append(line)

        return "\n".join(collapsed_lines).strip()

    def clean_text(self, text: str) -> str:
        """
        Full cleaning pipeline:
        1. Unicode normalization
        2. Court header/footer noise removal
        3. Hyphenated line-break repair
        4. Whitespace and paragraph boundary normalization
        """
        if not text:
            return ""

        text = self.normalize_unicode(text)
        text = self.clean_court_noise(text)
        text = self.fix_hyphenated_linebreaks(text)
        text = self.normalize_whitespace(text)
        return text
