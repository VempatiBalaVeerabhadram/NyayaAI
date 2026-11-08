"""
NyayaAI — Gemini Generation & Grounded Template Synthesizer
Uses Google Gemini SDK for evidence-grounded response generation
with a deterministic offline synthesizer when API key is not configured.
Supports full native-language output for Telugu (te) and Hindi (hi) queries.
"""

import os
from typing import List, Dict, Any, Optional
from loguru import logger

from app.config import settings
from app.rag.prompt_templates import (
    SYSTEM_PROMPT_RESEARCHER,
    SYSTEM_PROMPT_USER,
    LEGAL_DISCLAIMER,
    build_rag_context,
)
from app.models.retrieval import RetrievedChunkItem
from app.models.graph_retrieval import GraphRelationshipTriple

# ──────────────────────────────────────────────────────────────────────────────
# Full bilingual template dictionaries
# Every string emitted by _synthesize_grounded_response is covered here.
# Section numbers, case names, and law names are NEVER translated.
# ──────────────────────────────────────────────────────────────────────────────

TEMPLATES: Dict[str, Dict[str, str]] = {
    # ── Telugu (te) ──────────────────────────────────────────────────────────
    "te": {
        # Section headers
        "h_legal_issue":        "### 1. చట్టపరమైన అంశం & ప్రాథమిక సూత్రాలు",
        "h_statutory":          "### 2. వర్తించే చట్టబద్ధమైన నిబంధనలు",
        "h_judgments":          "### 3. సుప్రీంకోర్టు మైలురాయి తీర్పులు & న్యాయ సూత్రాలు (Ratio Decidendi)",
        "h_kg":                 "### 4. న్యాయపరమైన సంబంధాలు (Knowledge Graph)",
        "h_evidence":           "### 5. వివరణాత్మక న్యాయ విశ్లేషణ & ధృవీకరించబడిన సాక్ష్యాలు",
        "h_sources":            "### 6. అధికారిక న్యాయ మూలాలు",
        "h_caveats":            "### 7. చట్టపరమైన పరిమితులు & హెచ్చరికలు",
        # Simple-mode headers
        "h_simple":             "### 📌 సులభమైన వివరణ",
        "h_provisions":         "### ⚖️ సంబంధిత చట్టబద్ధమైన నిబంధనలు",
        "h_landmark":           "### 🏛️ ముఖ్యమైన న్యాయస్థాన తీర్పులు",
        "h_sources_say":        "### 📖 మూలాలు ఏమి చెప్తున్నాయి",
        "h_official":           "### 🔗 అధికారిక మూలాలు",
        "h_note":               "### ⚠️ ముఖ్యమైన గమనిక",
        "h_insufficient":       "### ⚠️ సరిపోయే సాక్ష్యాలు లేవు",
        # Body sentences
        "question_pertains":    "ఈ ప్రశ్న",
        "within_domain":        "యొక్క చట్ట పరిధికి సంబంధించినది",
        "governing_framework":  "వర్తించే ప్రాథమిక చట్టబద్ధమైన నిబంధనలు:",
        "jurisprudence_body":   (
            "భారత రాజ్యాంగంలోని Article 21 ప్రకారం వ్యక్తిగత స్వేచ్ఛ, "
            "న్యాయ ప్రక్రియ మరియు చట్టబద్ధమైన నిర్దేశాలకు ఖచ్చితమైన "
            "అనుసరణను న్యాయశాస్త్రం స్పష్టపరుస్తోంది."
        ),
        "simple_body": (
            "యొక్క ప్రాథమిక అంశానికి సంబంధించి, {act_str} ప్రకారం "
            "న్యాయ చట్టం వ్యక్తిగత స్వేచ్ఛను రక్షిస్తుంది మరియు "
            "అధికారులు తప్పనిసరిగా అనుసరించవలసిన ప్రక్రియాగత మార్గదర్శకాలను "
            "నిర్ణయిస్తుంది."
        ),
        "section_lays_down":    "నిర్దిష్ట చట్టబద్ధమైన అవసరాలు, విధానాలు మరియు షరతులను నిర్ణయిస్తుంది.",
        "landmark_ruling":      "ఈ అంశంపై ముఖ్యమైన సుప్రీంకోర్టు తీర్పు.",
        "holding_label":        "తీర్పు సారాంశం (Holding):",
        "extract_label":        "న్యాయ సారాంశం",
        "page_label":           "పేజీ",
        "para_label":           "పేరా",
        "source_label":         "మూలం:",
        "official_record":      "అధికారిక సుప్రీం కోర్టు రికార్డు",
        "verified_judgments":   "ధృవీకరించబడిన తీర్పులు:",
        "statutory_acts":       "చట్టబద్ధమైన చట్టాలు:",
        "analysis_derived":     (
            "ఈ విశ్లేషణ అధికారిక భారతీయ చట్ట నిబంధనలు మరియు "
            "సుప్రీంకోర్టు తీర్పుల ఆధారంగా మాత్రమే రూపొందించబడింది."
        ),
        "disclaimer":           (
            "న్యాయAI ప్రాథమిక న్యాయ సమాచారం మరియు పరిశోధన సహాయాన్ని "
            "అందిస్తుంది. ఇది న్యాయవాద సలహా కాదు. నిర్దిష్ట కేసులపై "
            "చట్టబద్ధమైన చర్యల కోసం నమోదు చేసుకున్న న్యాయవాదిని సంప్రదించండి."
        ),
        "insufficient_body":    (
            "ఈ ప్రశ్నకు నమ్మదగిన విధంగా సమాధానం ఇవ్వడానికి "
            "డేటాబేస్ నుండి తగినంత సాక్ష్యాలు లభ్యం కాలేదు.\n\n"
            "దయచేసి నిర్దిష్ట చట్టబద్ధమైన నిబంధనలతో మళ్ళీ శోధించండి "
            "(ఉదా., Section 438 CrPC, Section 420 IPC)."
        ),
        "criminal_law":         "క్రిమినల్ చట్టం",
        "general_inquiry":      "సాధారణ న్యాయ విచారణ",
        "judicial_discussion":  "న్యాయపరమైన చర్చ",
        "general_provisions":   "సాధారణ చట్టబద్ధమైన నిబంధనలు",
        "indian_law":           "భారతీయ చట్టం",
        # Evidence block context
        "evidence_intro":       "ఈ తీర్పు ప్రకారం న్యాయస్థానం ఇలా పేర్కొంది (అధికారిక ఆంగ్ల న్యాయ సాక్ష్యం):",
        "case_from":            "కేసు మూలం:",
        "judgment_note":        "📋 *న్యాయ సాక్ష్యాలు అధికారిక న్యాయస్థాన రికార్డుల నుండి నేరుగా ఉటంకించబడ్డాయి. చట్టపరమైన ప్రామాణికత కోసం అసలు ఆంగ్ల వచనం సంరక్షించబడింది.*",
        "case_discusses":       "ఈ కేసు చర్చిస్తోంది:",
        "section_ref":          "సంబంధిత నిబంధన:",
        "court_held":           "న్యాయస్థానం తీర్పు:",
        "simple_evidence_intro": "న్యాయ మూలం ఏమి చెప్తోందంటే (అధికారిక ఆంగ్ల న్యాయ సాక్ష్యం):",
    },

    # ── Hindi (hi) ────────────────────────────────────────────────────────────
    "hi": {
        # Section headers
        "h_legal_issue":        "### 1. कानूनी मुद्दा और मुख्य सिद्धांत",
        "h_statutory":          "### 2. लागू वैधानिक प्रावधान",
        "h_judgments":          "### 3. सर्वोच्च न्यायालय के ऐतिहासिक निर्णय और कानूनी सिद्धांत (Ratio Decidendi)",
        "h_kg":                 "### 4. न्यायिक संबंध (Knowledge Graph)",
        "h_evidence":           "### 5. विस्तृत न्यायिक तर्क और प्रमाणित साक्ष्य",
        "h_sources":            "### 6. आधिकारिक स्रोत और प्रमाणिकता",
        "h_caveats":            "### 7. कानूनी सीमाएं और सावधानियां",
        # Simple-mode headers
        "h_simple":             "### 📌 सरल स्पष्टीकरण",
        "h_provisions":         "### ⚖️ संबंधित कानूनी प्रावधान",
        "h_landmark":           "### 🏛️ महत्वपूर्ण न्यायालय निर्णय",
        "h_sources_say":        "### 📖 स्रोत क्या कहते हैं",
        "h_official":           "### 🔗 आधिकारिक स्रोत",
        "h_note":               "### ⚠️ महत्वपूर्ण सूचना",
        "h_insufficient":       "### ⚠️ पर्याप्त साक्ष्य उपलब्ध नहीं",
        # Body sentences
        "question_pertains":    "यह प्रश्न",
        "within_domain":        "के कानूनी दायरे से संबंधित है",
        "governing_framework":  "लागू मुख्य वैधानिक ढांचा:",
        "jurisprudence_body":   (
            "संविधान के अनुच्छेद 21 के अंतर्गत व्यक्तिगत स्वतंत्रता, "
            "उचित कानूनी प्रक्रिया और वैधानिक आदेशों के सख्त अनुपालन "
            "पर न्यायशास्त्र बल देता है।"
        ),
        "simple_body": (
            "के प्राथमिक मुद्दे के संबंध में, {act_str} के तहत "
            "कानूनी ढांचा व्यक्तिगत स्वतंत्रता की रक्षा करता है और "
            "उन प्रक्रियागत दिशानिर्देशों को निर्धारित करता है जिनका "
            "अधिकारियों और न्यायालयों को पालन करना आवश्यक है।"
        ),
        "section_lays_down":    "विशिष्ट वैधानिक आवश्यकताएं, प्रक्रियाएं और शर्तें निर्धारित करता है।",
        "landmark_ruling":      "इस विषय पर महत्वपूर्ण सर्वोच्च न्यायालय का निर्णय।",
        "holding_label":        "निर्णय का निष्कर्ष (Holding):",
        "extract_label":        "न्यायिक उद्धरण",
        "page_label":           "पृष्ठ",
        "para_label":           "पैरा",
        "source_label":         "स्रोत:",
        "official_record":      "आधिकारिक शीर्ष अदालत रिकॉर्ड",
        "verified_judgments":   "सत्यापित निर्णय:",
        "statutory_acts":       "वैधानिक अधिनियम:",
        "analysis_derived":     (
            "यह विश्लेषण आधिकारिक वैधानिक धाराओं और "
            "शीर्ष न्यायालय के निर्णयों से लिया गया है।"
        ),
        "disclaimer":           (
            "न्यायAI केवल कानूनी जानकारी और अनुसंधान सहायता प्रदान करता है। "
            "यह पेशेवर कानूनी सलाह नहीं है। विशिष्ट मामलों के लिए "
            "योग्य अधिवक्ता से परामर्श लें।"
        ),
        "insufficient_body":    (
            "इस प्रश्न का विश्वसनीय उत्तर देने के लिए डेटाबेस से "
            "पर्याप्त साक्ष्य प्राप्त नहीं हुए।\n\n"
            "कृपया विशिष्ट वैधानिक प्रावधानों के साथ पुनः खोजें "
            "(जैसे, Section 438 CrPC, Section 420 IPC)।"
        ),
        "criminal_law":         "आपराधिक कानून",
        "general_inquiry":      "सामान्य कानूनी पूछताछ",
        "judicial_discussion":  "न्यायिक चर्चा",
        "general_provisions":   "सामान्य वैधानिक प्रावधान",
        "indian_law":           "भारतीय कानून",
        # Evidence block context
        "evidence_intro":       "इस निर्णय में न्यायालय ने इस प्रकार कहा (आधिकारिक अंग्रेजी कानूनी साक्ष्य):",
        "case_from":            "मामले का स्रोत:",
        "judgment_note":        "📋 *कानूनी साक्ष्य आधिकारिक न्यायालय अभिलेखों से सीधे उद्धृत किए गए हैं। कानूनी प्रामाणिकता के लिए मूल अंग्रेजी पाठ संरक्षित है।*",
        "case_discusses":       "यह मामला चर्चा करता है:",
        "section_ref":          "संबंधित प्रावधान:",
        "court_held":           "न्यायालय का निर्णय:",
        "simple_evidence_intro": "कानूनी स्रोत के अनुसार (आधिकारिक अंग्रेजी कानूनी साक्ष्य):",
    },
}


def _t(lang: str, key: str) -> str:
    """Return template string for lang/key, falling back to English key name."""
    return TEMPLATES.get(lang, {}).get(key, key)


class GeminiGenerator:
    """Generates evidence-grounded legal responses using Gemini or deterministic fallback."""

    def __init__(self):
        self.api_key = settings.gemini_api_key or os.environ.get("GEMINI_API_KEY")
        self.model_name = settings.gemini_model
        self.client = None
        self._init_gemini()

    def _init_gemini(self):
        """Initializes Google Generative AI client if API key is present."""
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel(
                    model_name=self.model_name,
                    generation_config={
                        "temperature": 0.1,
                        "top_p": 0.95,
                        "max_output_tokens": 2048,
                    },
                )
                logger.info(f"✔ Gemini model initialized successfully: {self.model_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini client ({e}). Using deterministic evidence synthesizer.")
                self.client = None
        else:
            logger.info("Gemini API key not configured. Using deterministic grounded evidence synthesizer.")
            self.client = None

    def generate_response(
        self,
        query: str,
        mode: str,
        legal_issue: str,
        legal_domain: str,
        applicable_sections: List[str],
        applicable_acts: List[str],
        evidence_chunks: List[RetrievedChunkItem],
        graph_relationships: List[GraphRelationshipTriple],
        target_language: str = "en",
    ) -> str:
        """
        Generates structured legal answer grounded in retrieved chunks and graph triples.
        When target_language is 'te' or 'hi', the entire structured answer is built
        natively in that language — section numbers and case names are NEVER translated.
        """
        if not evidence_chunks:
            lang = target_language if target_language in TEMPLATES else "en"
            if lang == "en":
                return (
                    "### ⚠️ Insufficient Evidence\n\n"
                    "Insufficient reliable evidence was retrieved from the database to answer this question confidently.\n\n"
                    "Please verify the legal terms or try searching with specific statutory provisions (e.g., Section 438 CrPC, Section 420 IPC)."
                )
            return f"{_t(lang, 'h_insufficient')}\n\n{_t(lang, 'insufficient_body')}"

        # Build comprehensive context (always in English for Gemini prompt)
        context_str = build_rag_context(
            query=query,
            legal_issue=legal_issue,
            legal_domain=legal_domain,
            applicable_sections=applicable_sections,
            applicable_acts=applicable_acts,
            evidence_chunks=evidence_chunks,
            graph_relationships=graph_relationships,
        )

        system_instruction = SYSTEM_PROMPT_RESEARCHER if mode == "researcher" else SYSTEM_PROMPT_USER

        # 1. If Gemini API is available, generate via LLM
        if self.client:
            try:
                lang_instruction = ""
                if target_language in TEMPLATES:
                    lang_name = "Telugu (తెలుగు)" if target_language == "te" else "Hindi (हिन्दी)"
                    lang_instruction = (
                        f"\n\nIMPORTANT: Write your ENTIRE response in {lang_name}. "
                        "Do NOT translate statutory section numbers (e.g. Section 378 IPC, "
                        "Section 438 CrPC, Section 303 BNS), case names, or Latin maxims. "
                        "Keep those exactly as-is."
                    )
                prompt = (
                    f"{system_instruction}{lang_instruction}\n\n"
                    f"{context_str}\n\n"
                    "Please provide your detailed evidence-grounded response below:"
                )
                response = self.client.generate_content(prompt)
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                logger.error(f"Gemini generation call failed: {e}. Falling back to deterministic synthesizer.")

        # 2. Deterministic Grounded Evidence Synthesizer (Fallback / Offline)
        return self._synthesize_grounded_response(
            query=query,
            mode=mode,
            legal_issue=legal_issue,
            legal_domain=legal_domain,
            applicable_sections=applicable_sections,
            applicable_acts=applicable_acts,
            evidence_chunks=evidence_chunks,
            graph_relationships=graph_relationships,
            lang=target_language if target_language in TEMPLATES else "en",
        )

    def _synthesize_grounded_response(
        self,
        query: str,
        mode: str,
        legal_issue: str,
        legal_domain: str,
        applicable_sections: List[str],
        applicable_acts: List[str],
        evidence_chunks: List[RetrievedChunkItem],
        graph_relationships: List[GraphRelationshipTriple],
        lang: str = "en",
    ) -> str:
        """
        Builds a fully bilingual structured legal response.
        When lang='te' or 'hi', ALL prose is in Telugu/Hindi;
        section numbers, case names, and law abbreviations stay in English.
        """
        unique_cases = list(dict.fromkeys([c.case_name for c in evidence_chunks if c.case_name]))
        is_native = lang in TEMPLATES  # True for 'te' and 'hi'

        # ── Helpers ───────────────────────────────────────────────────────────
        def L(key: str) -> str:
            return _t(lang, key) if is_native else key

        sec_str = (
            ", ".join(f"Section {s}" for s in applicable_sections)
            if applicable_sections
            else (L("general_provisions") if is_native else "General Legal Provisions")
        )
        act_str = (
            ", ".join(applicable_acts)
            if applicable_acts
            else (L("indian_law") if is_native else "Indian Law")
        )
        act_str_cpc = (
            ", ".join(applicable_acts)
            if applicable_acts
            else ("Code of Criminal Procedure / Indian Statutes" if lang == "en" else
                  "Code of Criminal Procedure / " + L("indian_law"))
        )

        # ── USER mode ─────────────────────────────────────────────────────────
        if mode == "user":
            if is_native:
                body = [
                    L("h_simple"),
                    (
                        f"**{legal_issue}** {L('within_domain')} **{legal_domain}**. "
                        f"{act_str} " + L("simple_body").format(act_str=act_str) +
                        f" ({sec_str})."
                    ),
                    "",
                    L("h_provisions"),
                ]
                for sec in applicable_sections:
                    body.append(f"• **Section {sec}**: {L('section_lays_down')}")
                body.extend(["", L("h_landmark")])
                for case in unique_cases[:3]:
                    body.append(f"• **{case}**: {L('landmark_ruling')}")
                body.extend(["", L("h_sources_say")])
                for chunk in evidence_chunks[:2]:
                    body.append(f"*{L('simple_evidence_intro')}*")
                    body.append(
                        f"> \"{chunk.text[:220]}...\" "
                        f"— *({chunk.case_name}, {L('page_label')} {chunk.page})*"
                    )
                    body.append("")
                body.extend([
                    L("h_official"),
                    f"• {L('verified_judgments')} {', '.join(unique_cases)}",
                    f"• {L('statutory_acts')} {act_str}",
                    "",
                    L("h_note"),
                    L("disclaimer"),
                ])
            else:
                body = [
                    "### 📌 Simple Explanation",
                    f"Under {act_str}, the primary issue concerning **{legal_issue}** is governed by {sec_str}. "
                    "The legal framework protects individual personal liberty and outlines the exact procedural guidelines "
                    "that authorities and courts must follow.",
                    "",
                    "### ⚖️ Relevant Legal Provisions",
                ]
                for sec in applicable_sections:
                    body.append(f"• **Section {sec}**: Lays down specific statutory requirements, procedures, and conditions.")
                body.extend(["", "### 🏛️ Landmark Court Judgments"])
                for case in unique_cases[:3]:
                    body.append(f"• **{case}**: Landmark Supreme Court ruling addressing core principles on this matter.")
                body.extend(["", "### 📖 What the Sources Say"])
                for chunk in evidence_chunks[:2]:
                    body.append(f"> \"{chunk.text[:220]}...\" — *({chunk.case_name}, Page {chunk.page})*")
                    body.append("")
                body.extend([
                    "### 🔗 Official Sources",
                    f"• Verified Judgments: {', '.join(unique_cases)}",
                    f"• Statutory Enactments: {act_str}",
                    "",
                    "### ⚠️ Important Note",
                    LEGAL_DISCLAIMER,
                ])
            return "\n".join(body)

        # ── RESEARCHER mode ───────────────────────────────────────────────────
        if is_native:
            body = [
                L("h_legal_issue"),
                (
                    f"{L('question_pertains')} **{legal_issue}** {L('within_domain')} "
                    f"**{legal_domain}**. {L('governing_framework')} {act_str_cpc}, "
                    f"విశేషంగా {sec_str}. {L('jurisprudence_body')}"
                    if lang == "te" else
                    f"{L('question_pertains')} **{legal_issue}** {L('within_domain')} "
                    f"**{legal_domain}**। {L('governing_framework')} {act_str_cpc}, "
                    f"विशेष रूप से {sec_str}। {L('jurisprudence_body')}"
                ),
                "",
                L("h_statutory"),
            ]
            for act in applicable_acts:
                body.append(f"• **{act}**")
            for sec in applicable_sections:
                body.append(f"  - **Section {sec}**")

            body.extend(["", L("h_judgments")])
            for chunk in evidence_chunks[:3]:
                body.append(f"• **{chunk.case_name}** (*{chunk.section}*):")
                body.append(
                    f"  - *{L('holding_label')}* \"{chunk.text[:200]}...\" "
                    f"`[{L('page_label')} {chunk.page}, {L('para_label')} {chunk.paragraph_number}]`"
                )

            if graph_relationships:
                body.extend(["", L("h_kg")])
                for rel in graph_relationships[:5]:
                    target_type_label = L("judicial_discussion") if "DISCUSSES" in rel.relationship else rel.target_type
                    body.append(
                        f"• `{rel.source}` **--[{rel.relationship}]--> ** `{rel.target}` (*{target_type_label}*)"
                    )

            body.extend(["", L("h_evidence")])
            for idx, chunk in enumerate(evidence_chunks, start=1):
                # Native-language header + context sentence before English verbatim quote
                body.append(
                    f"**{L('extract_label')} {idx} — {chunk.case_name}** "
                    f"({L('section_ref')} {chunk.section} | "
                    f"{L('page_label')} {chunk.page}, {L('para_label')} {chunk.paragraph_number})"
                )
                body.append(f"*{L('case_discusses')} **{chunk.case_name}** — {chunk.section}*")
                body.append(f"*{L('evidence_intro')}*")
                body.append(f"> {chunk.text.strip()}")
                body.append("")

            # Note about verbatim English citations
            body.append(f"---\n{L('judgment_note')}\n")

            body.append(L("h_sources"))
            for case in unique_cases:
                matching_chunk = next((c for c in evidence_chunks if c.case_name == case), None)
                url = matching_chunk.source_url if matching_chunk else ""
                body.append(
                    f"• **{case}** — {L('source_label')} `{url or L('official_record')}`"
                )

            body.extend([
                "",
                L("h_caveats"),
                f"• {L('analysis_derived')}",
                f"• {L('disclaimer')}",
            ])

        else:
            # English researcher mode (original)
            body = [
                "### 1. Legal Issue & Core Principles",
                f"The question pertains to **{legal_issue}** within the domain of **{legal_domain}**. "
                f"The governing statutory framework comprises {act_str_cpc}, specifically {sec_str}. "
                "The jurisprudence emphasizes adherence to due process, constitutional guarantees under Article 21, "
                "and strict compliance with statutory mandates.",
                "",
                "### 2. Applicable Statutory Provisions",
            ]
            for act in applicable_acts:
                body.append(f"• **{act}**")
            for sec in applicable_sections:
                body.append(f"  - **Section {sec}**")

            body.extend(["", "### 3. Landmark Judgments & Ratio Decidendi"])
            for chunk in evidence_chunks[:3]:
                body.append(f"• **{chunk.case_name}** (*{chunk.section}*):")
                body.append(f"  - *Holding*: \"{chunk.text[:200]}...\" `[Page {chunk.page}, Para {chunk.paragraph_number}]`")

            if graph_relationships:
                body.extend(["", "### 4. Knowledge Graph Precedent Relationships"])
                for rel in graph_relationships[:5]:
                    body.append(f"• `{rel.source}` **--[{rel.relationship}]--> ** `{rel.target}` (*{rel.target_type}*)")

            body.extend(["", "### 5. Detailed Judicial Reasoning & Evidence"])
            for idx, chunk in enumerate(evidence_chunks, start=1):
                body.append(f"**Extract {idx} [{chunk.case_name} — Page {chunk.page}, Para {chunk.paragraph_number}]**:")
                body.append(f"> {chunk.text.strip()}")
                body.append("")

            body.append("### 6. Sources & Provenance")
            for case in unique_cases:
                matching_chunk = next((c for c in evidence_chunks if c.case_name == case), None)
                url = matching_chunk.source_url if matching_chunk else ""
                body.append(f"• **{case}** — Source: `{url or 'Official Court Record'}`")

            body.extend([
                "",
                "### 7. Limitations & Caveats",
                "• The analysis is derived strictly from the ingested statutory sections and apex court judgments.",
                f"• {LEGAL_DISCLAIMER}",
            ])

        return "\n".join(body)
