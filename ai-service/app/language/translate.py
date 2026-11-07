"""
NyayaAI — Multilingual Legal Translation Service
================================================
Translates queries from Telugu/Hindi to English for BM25 retrieval while
preserving section numbers, acts, and case citations unchanged.
"""

import re
import os
from typing import Optional, Dict, Any, List, Tuple
from loguru import logger

from app.config import settings
from app.language.glossary import LegalGlossary
from app.language.detect import LanguageDetector, LanguageDetectionResult


class LegalTranslator:
    """Translates Indian regional legal queries to English with token preservation."""

    PRESERVE_PATTERNS = [
        re.compile(r'\b(?:section|sec\.?|s\.)\s*\d+[a-zA-Z]?\b', re.IGNORECASE),
        re.compile(r'\b(?:IPC|BNS|CrPC|BNSS|IEA|BSA|IT\s+Act)\b', re.IGNORECASE),
        re.compile(r'\b(?:article|art\.)\s*\d+[a-zA-Z]?\b', re.IGNORECASE),
        re.compile(r'\(\d{4}\)\s+\d+\s+SCC\s+\d+', re.IGNORECASE),
    ]

    def __init__(self, gemini_api_key: Optional[str] = None):
        self.glossary = LegalGlossary()
        self.detector = LanguageDetector()
        self.api_key = gemini_api_key or settings.gemini_api_key or os.environ.get("GEMINI_API_KEY")
        self.client = None
        self._init_gemini()

    def _init_gemini(self):
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel("gemini-1.5-flash")
            except Exception as e:
                logger.warning(f"Could not initialize Gemini for translation ({e}). Using passthrough.")
                self.client = None

    def translate_to_english(self, query: str, source_language: str = "auto") -> Dict[str, Any]:
        """
        Translates a query to English while keeping legal citations intact.
        Returns translation payload with provenance details.
        """
        if not query or not query.strip():
            return {
                "original": query,
                "translated": query,
                "source_language": "en",
                "preserved_tokens": [],
                "method": "passthrough",
                "glossary_matches": [],
            }

        # 1. Detect language if auto
        if source_language == "auto":
            det = self.detector.detect(query)
            lang_code = det.language_code
        else:
            lang_code = source_language

        if lang_code == "en":
            return {
                "original": query,
                "translated": query,
                "source_language": "en",
                "preserved_tokens": [],
                "method": "identity",
                "glossary_matches": [e.english for e in self.glossary.find_terms_in_text(query)],
            }

        # 2. Extract and preserve statutory numbers & case citations
        masked_text, token_map = self._extract_preserve_tokens(query)

        # 3. Find matching glossary terms
        matched_entries = self.glossary.find_terms_in_text(query)
        glossary_context = self.glossary.get_translation_context(lang_code, max_terms=20)

        # 4. Perform translation via Gemini or rule-based fallback
        translated_masked = query
        method = "passthrough"

        if self.client:
            try:
                prompt = (
                    f"Translate the following Indian legal query from {lang_code} to English.\n"
                    f"Rules:\n"
                    f"1. Keep tokens like __PRESERVED_N__ untouched.\n"
                    f"2. Use these legal translations:\n{glossary_context}\n"
                    f"3. Return ONLY the English translation without preamble.\n\n"
                    f"Query: {masked_text}"
                )
                resp = self.client.generate_content(prompt)
                if resp and resp.text:
                    translated_masked = resp.text.strip()
                    method = "gemini"
            except Exception as e:
                logger.warning(f"Translation call failed ({e}). Reverting to fallback.")
                translated_masked = masked_text
        else:
            # Fallback: simple token replacement using glossary
            translated_masked = masked_text
            for entry in self.glossary.entries:
                target_word = entry.telugu if lang_code == "te" else entry.hindi
                if target_word and target_word in translated_masked:
                    translated_masked = translated_masked.replace(target_word, entry.english)
            method = "rule_based_fallback"

        # 5. Restore preserved tokens
        final_translation = self._restore_preserve_tokens(translated_masked, token_map)

        return {
            "original": query,
            "translated": final_translation,
            "source_language": lang_code,
            "preserved_tokens": list(token_map.values()),
            "method": method,
            "glossary_matches": [e.english for e in matched_entries],
        }

    def _extract_preserve_tokens(self, text: str) -> Tuple[str, Dict[str, str]]:
        token_map = {}
        counter = 1
        masked = text

        for pattern in self.PRESERVE_PATTERNS:
            for match in pattern.finditer(text):
                matched_str = match.group(0)
                placeholder = f"__PRESERVED_{counter}__"
                token_map[placeholder] = matched_str
                masked = masked.replace(matched_str, placeholder)
                counter += 1

        return masked, token_map

    def _restore_preserve_tokens(self, text: str, token_map: Dict[str, str]) -> str:
        restored = text
        for placeholder, original in token_map.items():
            restored = restored.replace(placeholder, original)
        return restored

