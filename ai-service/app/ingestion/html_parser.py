"""
NyayaAI — HTML Parser for Indian Legislative Documents & Judgments
Parses Acts and judgments from official portals such as India Code and eCourts.
"""

from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
import os
from loguru import logger

from app.ingestion.text_cleaner import LegalTextCleaner


class LegalHTMLParser:
    """Parses legal HTML documents into structured Act or Judgment records."""

    def __init__(self):
        self.cleaner = LegalTextCleaner()

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Parses an HTML file from disk."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"HTML file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        return self.parse_html_string(content, source_file=os.path.basename(file_path))

    def parse_html_string(self, html_content: str, source_file: str = "") -> Dict[str, Any]:
        """Parses raw HTML string into structured statutory or judgment representation."""
        soup = BeautifulSoup(html_content, "lxml")

        # Strip scripts, styles, forms, and navigation
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        # Extract title
        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        elif soup.find(["h1", "h2"]):
            heading = soup.find(["h1", "h2"])
            title = heading.get_text(strip=True)

        # Attempt to detect sections in statutory pages
        sections: List[Dict[str, Any]] = []
        section_elements = soup.find_all(
            lambda tag: tag.name in ["div", "section", "p"]
            and any("section" in cls.lower() for cls in tag.get("class", []))
        )

        for el in section_elements:
            sec_text = self.cleaner.clean_text(el.get_text())
            if sec_text:
                sections.append({
                    "raw_text": sec_text,
                    "html": str(el),
                })

        # Extract main text
        full_text = self.cleaner.clean_text(soup.get_text(separator="\n"))

        return {
            "title": title,
            "source_file": source_file,
            "full_text": full_text,
            "sections_extracted": sections,
            "char_count": len(full_text),
        }
