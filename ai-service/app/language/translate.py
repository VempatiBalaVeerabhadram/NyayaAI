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

    def translate_to_target_language(self, text: str, target_language: str) -> str:
        """
        Translates English legal text to Telugu or Hindi while shielding citations,
        case names, and section numbers.
        """
        if not text or target_language in ["en", "English", "unknown"]:
            return text

        lang_code = "te" if target_language in ["te", "telugu", "Telugu"] else "hi" if target_language in ["hi", "hindi", "Hindi"] else "en"
        if lang_code == "en":
            return text

        # 1. Mask citations, section numbers, and case tokens
        masked_text, token_map = self._extract_preserve_tokens(text)

        # 2. If Gemini is available, use Gemini with glossary context
        if self.client:
            try:
                glossary_context = self.glossary.get_translation_context(lang_code, max_terms=40)
                lang_name = "Telugu (తెలుగు)" if lang_code == "te" else "Hindi (हिन्दी)"
                prompt = (
                    f"You are an expert Indian Supreme Court translator. Translate the following legal response into fluent {lang_name}.\n\n"
                    f"CRITICAL RULES:\n"
                    f"1. Never translate or modify tokens like __PRESERVED_N__.\n"
                    f"2. Keep statutory section numbers (e.g. Section 378 IPC, Section 438 CrPC, Section 303 BNS) and Latin maxims (e.g. mens rea, ratio decidendi) exact and untranslated.\n"
                    f"3. Use standard formal legal vocabulary from this glossary:\n{glossary_context}\n"
                    f"4. Maintain markdown headers, bullet points, and structure exactly.\n\n"
                    f"Text:\n{masked_text}"
                )
                resp = self.client.generate_content(prompt)
                if resp and resp.text:
                    translated = resp.text.strip()
                    return self._restore_preserve_tokens(translated, token_map)
            except Exception as e:
                logger.warning(f"Gemini target translation failed ({e}). Reverting to rule-based legal translator.")

        # 3. Rule-based legal translation fallback
        return self._rule_based_legal_translate(text, lang_code)

    def _rule_based_legal_translate(self, text: str, lang_code: str) -> str:
        """High-precision legal domain translation preserving structure and section citations."""
        masked_text, token_map = self._extract_preserve_tokens(text)

        phrases_te = {
            "### 1. Legal Issue & Core Principles": "### 1. చట్టపరమైన అంశం & ప్రాథమిక సూత్రాలు",
            "### 2. Applicable Statutory Provisions": "### 2. వర్తించే చట్టబద్ధమైన నిబంధనలు (Statutory Provisions)",
            "### 3. Landmark Judgments & Ratio Decidendi": "### 3. సుప్రీంకోర్టు మైలురాయి తీర్పులు & న్యాయ సూత్రాలు (Ratio Decidendi)",
            "### 4. Detailed Judicial Reasoning & Evidence": "### 4. వివరణాత్మక న్యాయ విశ్లేషణ & ధృవీకరించబడిన సాక్ష్యాలు",
            "### 5. Detailed Judicial Reasoning & Evidence": "### 5. వివరణాత్మక న్యాయ విశ్లేషణ & ధృవీకరించబడిన సాక్ష్యాలు",
            "### 6. Sources & Provenance": "### 6. అధికారిక న్యాయ మూలాలు (Sources & Provenance)",
            "### 7. Limitations & Caveats": "### 7. చట్టపరమైన పరిమితులు & హెచ్చరికలు",
            "The question pertains to": "ఈ ప్రశ్న",
            "within the domain of": "చట్ట పరిధిలోని",
            "The governing statutory framework comprises": "వర్తించే ప్రధాన చట్టబద్ధమైన నిబంధనలు:",
            "The jurisprudence emphasizes adherence to due process, constitutional guarantees under Article 21, and strict compliance with statutory mandates.": "భారత రాజ్యాంగంలోని ఆర్టికల్ 21 ప్రకారం వ్యక్తిగత స్వేచ్ఛ, చట్టబద్ధమైన ప్రక్రియ మరియు న్యాయ సూత్రాల ఖచ్చితమైన అమలును న్యాయశాస్త్రం స్పష్టం చేస్తోంది.",
            "The analysis is derived strictly from the ingested statutory sections and apex court judgments.": "ఈ విశ్లేషణ అధికారిక భారతీయ చట్ట నిబంధనలు మరియు సుప్రీంకోర్టు తీర్పుల ఆధారంగా మాత్రమే రూపొందించబడింది.",
            "NyayaAI provides legal information and research assistance based on retrieved sources. It does not provide professional legal advice or establish an attorney-client relationship. Users should verify the original legal sources and consult a qualified legal professional for case-specific advice.": "న్యాయAI ప్రాథమిక న్యాయ సమాచారం మరియు పరిశోధనా సహాయాన్ని అందిస్తుంది. ఇది న్యాయవాద సలహా కాదు. నిర్దిష్ట కేసులపై చట్టబద్ధమైన చర్యల కోసం నమోదు చేసుకున్న న్యాయవాదిని సంప్రదించండి.",
            "Criminal Law": "క్రిమినల్ చట్టం",
            "General Legal Inquiry": "సాధారణ న్యాయ విచారణ",
            "Holding:": "తీర్పు సారాంశం (Holding):",
            "Extract": "న్యాయ సారాంశం",
            "Source:": "మూలం:",
            "Official Court Record": "అధికారిక సుప్రీం కోర్టు రికార్డు",
            "Judicial Discussion": "న్యాయపరమైన చర్చ",
            "Page": "పేజీ",
            "Para": "పేరా",
        }

        phrases_hi = {
            "### 1. Legal Issue & Core Principles": "### 1. कानूनी मुद्दा और मुख्य सिद्धांत",
            "### 2. Applicable Statutory Provisions": "### 2. लागू वैधानिक प्रावधान (Statutory Provisions)",
            "### 3. Landmark Judgments & Ratio Decidendi": "### 3. सर्वोच्च न्यायालय के ऐतिहासिक निर्णय और कानूनी सिद्धांत (Ratio Decidendi)",
            "### 4. Detailed Judicial Reasoning & Evidence": "### 4. विस्तृत न्यायिक तर्क और प्रमाणित साक्ष्य",
            "### 5. Detailed Judicial Reasoning & Evidence": "### 5. विस्तृत न्यायिक तर्क और प्रमाणित साक्ष्य",
            "### 6. Sources & Provenance": "### 6. आधिकारिक स्रोत और प्रमाणिकता (Sources & Provenance)",
            "### 7. Limitations & Caveats": "### 7. कानूनी सीमाएं और सावधानियां",
            "The question pertains to": "यह प्रश्न",
            "within the domain of": "के अधिकार क्षेत्र से संबंधित है",
            "The governing statutory framework comprises": "लागू मुख्य वैधानिक ढांचा:",
            "The jurisprudence emphasizes adherence to due process, constitutional guarantees under Article 21, and strict compliance with statutory mandates.": "संविधान के अनुच्छेद 21 के तहत व्यक्तिगत स्वतंत्रता, कानून की उचित प्रक्रिया और वैधानिक निर्देशों के सख्त अनुपालन पर सर्वोच्च न्यायालय ने बल दिया है।",
            "The analysis is derived strictly from the ingested statutory sections and apex court judgments.": "यह विश्लेषण आधिकारिक वैधानिक धाराओं और शीर्ष अदालत के निर्णयों से लिया गया है।",
            "NyayaAI provides legal information and research assistance based on retrieved sources. It does not provide professional legal advice or establish an attorney-client relationship. Users should verify the original legal sources and consult a qualified legal professional for case-specific advice.": "न्यायAI केवल कानूनी जानकारी और अनुसंधान सहायता प्रदान करता है। यह पेशेवर कानूनी सलाह नहीं है। विशिष्ट मामलों के लिए योग्य अधिवक्ता से परामर्श लें।",
            "Criminal Law": "आपराधिक कानून",
            "General Legal Inquiry": "सामान्य कानूनी पूछताछ",
            "Holding:": "निर्णय का निष्कर्ष (Holding):",
            "Extract": "न्यायिक उद्धरण",
            "Source:": "स्रोत:",
            "Official Court Record": "आधिकारिक शीर्ष अदालत रिकॉर्ड",
            "Judicial Discussion": "न्यायिक चर्चा",
            "Page": "पृष्ठ",
            "Para": "पैरा",
        }

        phrase_map = phrases_te if lang_code == "te" else phrases_hi

        translated = masked_text
        for eng, localized in phrase_map.items():
            translated = translated.replace(eng, localized)

        # Apply glossary terms
        for entry in self.glossary.entries:
            loc = entry.telugu if lang_code == "te" else entry.hindi
            if loc and entry.english and len(entry.english) > 3:
                pattern = re.compile(rf'\b{re.escape(entry.english)}\b', re.IGNORECASE)
                translated = pattern.sub(loc, translated)

        return self._restore_preserve_tokens(translated, token_map)

