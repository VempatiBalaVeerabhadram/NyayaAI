"""
NyayaAI Language Module
Includes language detection, bilingual legal glossary, and translation services.
"""
from app.language.detect import LanguageDetector, LanguageDetectionResult
from app.language.glossary import LegalGlossary, GlossaryEntry
from app.language.translate import LegalTranslator

__all__ = [
    "LanguageDetector",
    "LanguageDetectionResult",
    "LegalGlossary",
    "GlossaryEntry",
    "LegalTranslator",
]

