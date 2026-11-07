"""
NyayaAI — Multilingual Language Detector
=========================================
Detects query language across English (en), Telugu (te), and Hindi (hi).
Uses high-accuracy Unicode code-point range checking for Indic scripts with
fallback to the `langdetect` library.
"""

from dataclasses import dataclass
from typing import Optional
from loguru import logger

SUPPORTED_LANGUAGES = {
    "en": "English",
    "te": "Telugu",
    "hi": "Hindi"
}


@dataclass
class LanguageDetectionResult:
    language_code: str       # "en", "te", "hi", "unknown"
    language_name: str       # "English", "Telugu", "Hindi", "Unknown"
    confidence: float        # 0.0 - 1.0
    detection_method: str    # "unicode_range", "langdetect", "default"


class LanguageDetector:
    """Detects English, Telugu, and Hindi legal queries."""

    # Unicode ranges
    TELUGU_START = 0x0C00
    TELUGU_END = 0x0C7F

    DEVANAGARI_START = 0x0900
    DEVANAGARI_END = 0x097F

    def __init__(self):
        self._has_langdetect = False
        try:
            import langdetect
            self._has_langdetect = True
        except ImportError:
            self._has_langdetect = False

    def detect(self, text: str) -> LanguageDetectionResult:
        if not text or not text.strip():
            return LanguageDetectionResult("en", "English", 1.0, "default")

        # 1. Primary check: Unicode script density
        unicode_res = self._detect_by_unicode(text)
        if unicode_res:
            return unicode_res

        # 2. Secondary check: langdetect library
        if self._has_langdetect:
            try:
                import langdetect
                code = langdetect.detect(text)
                if code in SUPPORTED_LANGUAGES:
                    return LanguageDetectionResult(
                        language_code=code,
                        language_name=SUPPORTED_LANGUAGES[code],
                        confidence=0.85,
                        detection_method="langdetect",
                    )
            except Exception:
                pass

        # 3. Default to English
        return LanguageDetectionResult("en", "English", 0.90, "default")

    def _detect_by_unicode(self, text: str) -> Optional[LanguageDetectionResult]:
        total_chars = len(text)
        if total_chars == 0:
            return None

        telugu_count = sum(1 for c in text if self.TELUGU_START <= ord(c) <= self.TELUGU_END)
        devanagari_count = sum(1 for c in text if self.DEVANAGARI_START <= ord(c) <= self.DEVANAGARI_END)

        if telugu_count / total_chars > 0.15:
            conf = min(1.0, round(telugu_count / max(1, total_chars - text.count(' ')), 2))
            return LanguageDetectionResult("te", "Telugu", conf, "unicode_range")

        if devanagari_count / total_chars > 0.15:
            conf = min(1.0, round(devanagari_count / max(1, total_chars - text.count(' ')), 2))
            return LanguageDetectionResult("hi", "Hindi", conf, "unicode_range")

        return None

    def is_english(self, text: str) -> bool:
        return self.detect(text).language_code == "en"

    def is_telugu(self, text: str) -> bool:
        return self.detect(text).language_code == "te"

    def is_hindi(self, text: str) -> bool:
        return self.detect(text).language_code == "hi"

