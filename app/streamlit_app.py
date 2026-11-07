"""
NyayaAI — Hybrid Legal Intelligence Platform for Indian Law
============================================================
Streamlit Interactive Research & Demonstration UI
Features:
- Multilingual Querying (English, Telugu, Hindi)
- Temporal Statute Modeling (IPC->BNS transition on 1 July 2024)
- Hybrid BM25 + SBERT Retrieval with Dynamic Intent Weighting
- Knowledge Graph Precedent Authority & Role Segmentation
- Citation Verification & Evidence Grounding
- Side-by-side Answer & Original Source Passages
- Mandatory Legal Disclaimer
"""

import sys
import os
from pathlib import Path
from datetime import date, datetime

# Ensure ai-service modules are resolvable
APP_ROOT = Path(__file__).resolve().parent.parent
AI_SERVICE_DIR = APP_ROOT / "ai-service"
sys.path.insert(0, str(AI_SERVICE_DIR))

import streamlit as st

# Configure Page
st.set_page_config(
    page_title="NyayaAI — Indian Legal Intelligence",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0.2rem; }
    .sub-header { font-size: 1.1rem; color: #475569; margin-bottom: 1.5rem; }
    .badge-bns { background-color: #DC2626; color: white; padding: 3px 8px; border-radius: 4px; font-weight: 600; font-size: 0.85rem; }
    .badge-ipc { background-color: #2563EB; color: white; padding: 3px 8px; border-radius: 4px; font-weight: 600; font-size: 0.85rem; }
    .disclaimer-box { background-color: #FEF3C7; border-left: 4px solid #F59E0B; padding: 12px; border-radius: 4px; margin-top: 20px; font-size: 0.9rem; }
    .score-card { background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 12px; border-radius: 6px; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Lazy Load Core Engines (Cached)
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner="Initializing Legal Search Engines...")
def load_engines():
    os.environ["HF_HUB_OFFLINE"] = "1"
    from app.retrieval.hybrid_retriever import LegalHybridRetriever
    from app.retrieval.intent import IntentClassifier
    from app.knowledge_graph.temporal import TemporalStatuteIndex
    from app.knowledge_graph.authority import AuthorityScorer
    from app.knowledge_graph.graph_builder import LegalGraphManager
    from app.language.detect import LanguageDetector
    from app.language.glossary import LegalGlossary
    from app.language.translate import LegalTranslator
    from app.rag.verifier import CitationVerifier
    from app.rag.prompt_templates import build_grounded_prompt

    acts_dir = APP_ROOT / "data" / "raw" / "acts"
    temporal_idx = TemporalStatuteIndex(acts_dir=str(acts_dir))
    hybrid_retriever = LegalHybridRetriever()
    intent_clf = IntentClassifier()
    graph_mgr = LegalGraphManager()
    authority_scorer = AuthorityScorer(graph_mgr.graph)
    detector = LanguageDetector()
    glossary = LegalGlossary()
    translator = LegalTranslator()
    verifier = CitationVerifier()

    return {
        "temporal": temporal_idx,
        "retriever": hybrid_retriever,
        "intent": intent_clf,
        "graph": graph_mgr,
        "authority": authority_scorer,
        "detector": detector,
        "glossary": glossary,
        "translator": translator,
        "verifier": verifier,
        "build_grounded_prompt": build_grounded_prompt,
    }

try:
    engines = load_engines()
except Exception as e:
    st.error(f"Error loading AI service engines: {e}")
    st.stop()

# ---------------------------------------------------------------------------
# Sidebar Settings
# ---------------------------------------------------------------------------
st.sidebar.title("⚖️ NyayaAI Controls")
st.sidebar.markdown("Configure query parameters and jurisdiction:")

selected_date = st.sidebar.date_input(
    "📅 Date of Alleged Incident / Legal Inquiry",
    value=date(2024, 8, 15),
    min_value=date(1860, 10, 6),
    max_value=date(2030, 12, 31),
    help="Select the date of the offence to automatically apply the law in force on that date.",
)

# Regime computation
law_version_label = engines["temporal"].get_law_version_label(selected_date)
is_post_bns = selected_date >= date(2024, 7, 1)

if is_post_bns:
    st.sidebar.markdown(f'<span class="badge-bns">NEW REGIME: {law_version_label}</span>', unsafe_allow_html=True)
else:
    st.sidebar.markdown(f'<span class="badge-ipc">HISTORICAL REGIME: {law_version_label}</span>', unsafe_allow_html=True)

st.sidebar.markdown("---")

language = st.sidebar.selectbox(
    "🌐 Query & Output Language",
    options=["Auto-detect", "English", "Telugu (తెలుగు)", "Hindi (हिन्दी)"],
    index=0,
)

st.sidebar.markdown("---")
st.sidebar.subheader("🔬 Retrieval Configuration")
auto_intent = st.sidebar.checkbox("Intent-Adaptive Alpha Weighting", value=True)
manual_alpha = st.sidebar.slider("Manual Alpha (BM25 vs SBERT weight)", 0.0, 1.0, 0.5, 0.05, disabled=auto_intent)
top_k = st.sidebar.slider("Top Documents to Retrieve", 3, 15, 5)

# ---------------------------------------------------------------------------
# Main UI Header
# ---------------------------------------------------------------------------
st.markdown('<div class="main-header">⚖️ NyayaAI: Indian Legal Intelligence System</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Evidence-grounded hybrid retrieval with temporal statute versioning '
    '(IPC ↔ BNS transition), knowledge graph precedent authority, and bilingual verification.</div>',
    unsafe_allow_html=True
)

# Sample Queries Quick-Picks
sample_queries = [
    "— Select a sample query —",
    "What are the mandatory conditions and grounds for anticipatory bail under Section 438?",
    "Can the police arrest an accused person without warrant for petty theft under Section 379?",
    "When does an offence of cheating under Section 420 IPC also constitute criminal breach of trust?",
    "What guidelines did the Supreme Court lay down in Arnesh Kumar regarding arrest under Section 41A?",
    "దొంగతనానికి శిక్ష ఏమిటి మరియు బెయిల్ లభిస్తుందా? (Telugu: Theft punishment & bail)",
    "अग्रिम जमानत के लिए अदालत की क्या शर्तें हैं? (Hindi: Anticipatory bail conditions)",
]

selected_sample = st.selectbox("💡 Try a sample legal query:", sample_queries)
default_query = selected_sample if selected_sample != sample_queries[0] else ""

user_query = st.text_area(
    "📝 Enter your legal question (in English, Telugu, or Hindi):",
    value=default_query,
    height=90,
    placeholder="e.g. What are the principles governing grant of anticipatory bail in criminal breach of trust?",
)

btn_search = st.button("🔍 Search & Analyze", type="primary", use_container_width=True)

if btn_search and user_query.strip():
    with st.spinner("Analyzing query, performing multilingual translation, and executing hybrid retrieval..."):
        # 1. Language Detection
        detected = engines["detector"].detect(user_query)
        detected_lang = detected.language_name
        lang_code = detected.language_code

        # 2. Translation to English if non-English
        tr_info = engines["translator"].translate_to_english(user_query, source_language=lang_code)
        search_query_en = tr_info["translated"]

        # 3. Intent Classification
        intent_info = engines["intent"].classify(search_query_en)
        effective_alpha = intent_info["alpha"] if auto_intent else manual_alpha

        # 4. Hybrid Retrieval
        retrieved_chunks = engines["retriever"].search(
            query=search_query_en,
            top_k=top_k,
            alpha=effective_alpha,
            auto_intent=auto_intent,
        )

        # 5. Temporal Mapping & Equivalent Provisions
        applicable_acts = engines["temporal"].get_applicable_acts(selected_date)

        # 6. Format Grounded Answer
        from app.rag.generator import GeminiGenerator
        gen = GeminiGenerator()
        unique_sections = list(dict.fromkeys([c.section for c in retrieved_chunks if c.section]))
        unique_cases = list(dict.fromkeys([c.case_name for c in retrieved_chunks if c.case_name]))

        synthesized_answer = gen._synthesize_grounded_response(
            query=search_query_en,
            mode="researcher",
            legal_issue=intent_info.get("intent", "Criminal Law Inquiry"),
            legal_domain="Criminal Law",
            applicable_sections=unique_sections[:3],
            applicable_acts=applicable_acts[:2],
            evidence_chunks=retrieved_chunks,
            graph_relationships=[],
        )

        # 7. Citation Verification
        chunk_dicts = [
            {"text": c.text, "case_name": c.case_name, "section": c.section}
            for c in retrieved_chunks
        ]
        verification_report = engines["verifier"].verify(synthesized_answer, chunk_dicts, query_date=str(selected_date))

    # -----------------------------------------------------------------------
    # Display Results Tabs
    # -----------------------------------------------------------------------
    tab_answer, tab_evidence, tab_explain, tab_temporal, tab_graph = st.tabs([
        "📄 Grounded Legal Analysis",
        "📖 Retrieved Evidence Passages",
        "🔬 Explainability & Verification",
        "⏳ Temporal Law Regime",
        "🕸️ Precedent Graph",
    ])

    with tab_answer:
        col_ans, col_meta = st.columns([2, 1])

        with col_ans:
            st.subheader("🏛️ Synthesized Answer (Grounded in Verified Court Records)")
            st.markdown(synthesized_answer)

        with col_meta:
            st.subheader("📋 Query Provenance")
            st.markdown(f"**Query Date:** `{selected_date.strftime('%d %B %Y')}`")
            st.markdown(f"**Applicable Law Regime:** `{law_version_label}`")
            st.markdown(f"**Detected Query Language:** `{detected_lang}` ({detected.detection_method})")
            if lang_code != "en":
                st.markdown(f"**English Translation for Retrieval:** *\"{search_query_en}\"*")
            st.markdown(f"**Detected Intent:** `{intent_info['intent']}`")
            st.markdown(f"**Hybrid Alpha:** `{effective_alpha:.2f}` (BM25: {effective_alpha*100:.0f}%, Dense: {(1-effective_alpha)*100:.0f}%)")
            st.markdown(f"**Verified Citations:** `{len(verification_report.valid_citations)}`")
            if verification_report.hallucinated_citations:
                st.error(f"⚠️ {len(verification_report.hallucinated_citations)} unverified citations flagged")
            else:
                st.success("✔ 0 hallucinated citations detected")

    with tab_evidence:
        st.subheader("📚 Top Retrieved Evidence Chunks")
        for idx, chunk in enumerate(retrieved_chunks, start=1):
            auth_score = engines["authority"].get_authority(chunk.case_id)
            with st.expander(f"Passage #{idx}: {chunk.case_name} | {chunk.section} (Hybrid Score: {chunk.hybrid_score:.4f})", expanded=(idx==1)):
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("BM25 Score", f"{chunk.bm25_score:.4f}")
                col2.metric("SBERT Dense Score", f"{chunk.semantic_score:.4f}")
                col3.metric("Hybrid Combined", f"{chunk.hybrid_score:.4f}")
                col4.metric("Court Authority Weight", f"{auth_score:.2f}")

                st.markdown(f"**Source Text (Page {chunk.page}, Para {chunk.paragraph_number}):**")
                st.info(chunk.text)
                if chunk.source_url:
                    st.caption(f"Source URL: {chunk.source_url}")

    with tab_explain:
        st.subheader("🔬 Transparency & Verification Breakdown")
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            st.markdown("#### Citation Verification Summary")
            st.markdown(f"• **Total Citations Identified:** {verification_report.total_citations}")
            st.markdown(f"• **Valid Grounded Citations:** {len(verification_report.valid_citations)}")
            st.markdown(f"• **Hallucination Rate:** {verification_report.hallucination_rate * 100:.1f}%")
            st.markdown(f"• **Citation Accuracy:** {verification_report.citation_accuracy * 100:.1f}%")

            if verification_report.valid_citations:
                st.markdown("**Valid Citations Found in Records:**")
                for vc in verification_report.valid_citations:
                    st.markdown(f"- ✅ `{vc.citation_text}` (*{vc.citation_type}*)")

        with col_v2:
            st.markdown("#### Retrieval Intent Signals")
            st.markdown(f"• **Identified Intent Category:** `{intent_info.get('intent', 'N/A')}`")
            st.markdown(f"• **Classifier Confidence:** `{intent_info.get('confidence', 0.9):.2f}`")
            signals = intent_info.get("signals", [])
            st.markdown(f"• **Trigger Signals:** {', '.join(f'`{s}`' for s in signals) if signals else 'General narrative'}")

    with tab_temporal:
        st.subheader("⏳ Temporal Statute Mapping (IPC ↔ BNS & CrPC ↔ BNSS)")
        st.markdown(f"For the selected date **{selected_date.strftime('%d %b %Y')}**, the applicable laws are:")
        for act in applicable_acts:
            st.markdown(f"• **{act}**")

        st.markdown("#### Key Provision Equivalents")
        mapping_table = [
            {"Subject": "Theft (Substantive)", "IPC (Pre-July 2024)": "Section 378", "BNS (Effective 1 July 2024)": "Section 303"},
            {"Subject": "Theft Punishment", "IPC (Pre-July 2024)": "Section 379", "BNS (Effective 1 July 2024)": "Section 304"},
            {"Subject": "Criminal Breach of Trust", "IPC (Pre-July 2024)": "Section 405 / 406", "BNS (Effective 1 July 2024)": "Section 316 / 317"},
            {"Subject": "Cheating", "IPC (Pre-July 2024)": "Section 415 / 420", "BNS (Effective 1 July 2024)": "Section 318 / 323"},
            {"Subject": "Anticipatory Bail", "IPC (Pre-July 2024)": "CrPC Section 438", "BNS (Effective 1 July 2024)": "BNSS Section 482"},
            {"Subject": "Regular Bail (HC/Sessions)", "IPC (Pre-July 2024)": "CrPC Section 439", "BNS (Effective 1 July 2024)": "BNSS Section 483"},
            {"Subject": "Police Arrest Without Warrant", "IPC (Pre-July 2024)": "CrPC Section 41 / 41A", "BNS (Effective 1 July 2024)": "BNSS Section 35"},
        ]
        st.table(mapping_table)

    with tab_graph:
        st.subheader("🕸️ Precedent & Citation Knowledge Graph")
        overview = engines["graph"].get_overview()
        g_c1, g_c2, g_c3 = st.columns(3)
        g_c1.metric("Total Graph Nodes", overview.total_nodes)
        g_c2.metric("Total Graph Relationships", overview.total_relationships)
        g_c3.metric("Graph Backend", overview.active_backend.upper())

        st.markdown("#### Key Connected Precedents:")
        for case in unique_cases[:6]:
            cid = f"CASE_{case.upper().replace(' ', '_')}"
            auth = engines["authority"].get_authority(cid)
            st.markdown(f"• 🏛️ **{case}** — Authority Weight: `{auth:.2f}` (Supreme Court of India)")

# ---------------------------------------------------------------------------
# Persistent Legal Disclaimer
# ---------------------------------------------------------------------------
st.markdown("""
<div class="disclaimer-box">
    <strong>⚠️ LEGAL DISCLAIMER & DECISION-SUPPORT NOTICE:</strong><br>
    NyayaAI is an academic research and decision-support prototype developed for final-year major engineering project evaluation.
    It does NOT provide legal advice and does not establish an advocate-client relationship. All legal outputs are grounded
    in retrieved judicial records and statutory gazettes. Consult an enrolled Advocate under the Advocates Act, 1961 for any formal legal representation.
</div>
""", unsafe_allow_html=True)

