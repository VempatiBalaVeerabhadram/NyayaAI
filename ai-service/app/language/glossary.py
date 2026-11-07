"""
NyayaAI — Bilingual Legal Glossary Manager
==========================================
Loads the curated English-Telugu-Hindi legal dictionary for prompt injection
and bilingual term alignment.
"""

import csv
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List, Dict
from loguru import logger


@dataclass
class GlossaryEntry:
    english: str
    telugu: str
    hindi: str
    domain: str
    reviewed_by: str


class LegalGlossary:
    """Provides access to curated legal term translations in Telugu and Hindi."""

    def __init__(self, glossary_path: Optional[str] = None):
        self.entries: List[GlossaryEntry] = []
        self._by_english: Dict[str, GlossaryEntry] = {}

        if glossary_path:
            self.glossary_path = Path(glossary_path)
        else:
            # Locate relative to app directory or workspace data
            base = Path(__file__).resolve().parent.parent.parent.parent
            self.glossary_path = base / "data" / "glossary" / "legal_glossary.csv"

        self._load()

    def _load(self):
        if not self.glossary_path.exists():
            logger.warning(f"Glossary file not found at {self.glossary_path}")
            return

        try:
            with open(self.glossary_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    eng = row.get("english", "").strip().lower()
                    if not eng:
                        continue
                    entry = GlossaryEntry(
                        english=row.get("english", "").strip(),
                        telugu=row.get("telugu", "").strip(),
                        hindi=row.get("hindi", "").strip(),
                        domain=row.get("domain", "general").strip(),
                        reviewed_by=row.get("reviewed_by", "PLACEHOLDER").strip(),
                    )
                    self.entries.append(entry)
                    self._by_english[eng] = entry
            logger.info(f"✔ Loaded {len(self.entries)} legal glossary entries from {self.glossary_path.name}")
        except Exception as e:
            logger.error(f"Error loading legal glossary: {e}")

    def lookup(self, english_term: str) -> Optional[GlossaryEntry]:
        return self._by_english.get(english_term.strip().lower())

    def get_translation_context(self, language_code: str, domain: Optional[str] = None, max_terms: int = 30) -> str:
        """Formats glossary lines for LLM system prompt injection."""
        lines = []
        for entry in self.entries:
            if domain and entry.domain.lower() != domain.lower() and entry.domain != "general":
                continue

            if language_code == "te":
                lines.append(f"• {entry.english} -> {entry.telugu}")
            elif language_code == "hi":
                lines.append(f"• {entry.english} -> {entry.hindi}")
            else:
                lines.append(f"• {entry.english}: Telugu={entry.telugu}, Hindi={entry.hindi}")

            if len(lines) >= max_terms:
                break

        return "\n".join(lines)

    def find_terms_in_text(self, text: str) -> List[GlossaryEntry]:
        lower = text.lower()
        matches = []
        for eng, entry in self._by_english.items():
            if eng in lower:
                matches.append(entry)
        return matches

