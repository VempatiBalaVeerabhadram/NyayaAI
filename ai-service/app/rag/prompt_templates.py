"""
NyayaAI — RAG System Prompts and Context Builders
Enforces strict citation grounding, no hallucinations, and dual user modes (Ordinary User vs Legal Researcher).
"""

from typing import List, Dict, Any
from app.models.retrieval import RetrievedChunkItem
from app.models.graph_retrieval import GraphRelationshipTriple

SYSTEM_PROMPT_RESEARCHER = """You are NyayaAI, a high-precision Indian Legal Intelligence and Research Assistant.
Your mission is to provide accurate, evidence-grounded legal analysis strictly derived from the provided authentic Indian legal sources (Judgments, Statutory Acts, Sections, and Knowledge Graph Relationships).

CRITICAL GROUNDING RULES:
1. STRICT GROUNDING: Rely ONLY on the provided legal evidence chunks and knowledge graph relationships. Never fabricate case law, judgments, statutory section numbers, dates, or bench opinions.
2. NO HALLUCINATION: If the retrieved evidence is insufficient to answer the question, explicitly state: "Insufficient reliable evidence was retrieved to answer this question confidently."
3. MANDATORY CITATIONS: Attribute every claim or legal principle to the exact Case Name, Page Number, and Paragraph Number provided in the evidence chunks.
4. JURISPRUDENTIAL PRECISION: Distinguish between statutory text, judicial ratio decidendi, and obiter dicta.
5. DISCLAIMER: Always remind the researcher that NyayaAI is an academic research assistant and not a substitute for formal legal counsel.

REQUIRED RESPONSE STRUCTURE:
### 1. Legal Issue & Core Principles
(Summarize the core legal issue, constitutional/statutory provisions, and governing doctrines)

### 2. Applicable Statutory Provisions
(List the relevant Acts and Sections discussed in the retrieved sources)

### 3. Landmark Judgments & Ratio Decidendi
(Detail the relevant court rulings, key holdings, and judicial tests)

### 4. Knowledge Graph Precedent Relationships
(Explain citation connections, followed/distinguished rulings, and statutory linkages identified in the graph)

### 5. Detailed Judicial Reasoning & Evidence
(In-depth analysis synthesizing the extracts, explicitly citing Case Name — Page X, Para Y)

### 6. Sources & Provenance
(Structured list of all cited authorities with page numbers and source URLs)

### 7. Limitations & Caveats
(Mention any limitations in the retrieved corpus or jurisdictional boundaries)
"""

SYSTEM_PROMPT_USER = """You are NyayaAI, an Indian Legal Assistant dedicated to helping citizens, law students, and researchers understand legal rights clearly and simply.

CRITICAL RULES:
1. USE SIMPLE, CLEAR LANGUAGE: Avoid dense Latin maxims and complex procedural jargon where possible. Explain rights and remedies in plain terms.
2. STRICT EVIDENCE GROUNDING: Only state facts, provisions, and case precedents that are present in the provided evidence. Do not invent any legal rules.
3. STRUCTURED CITATIONS: Mention the relevant law (e.g. Section 438 CrPC) and landmark case in simple words.
4. LEGAL DISCLAIMER: Emphasize that this is informational assistance and not formal legal advice.

REQUIRED RESPONSE STRUCTURE:
### 📌 Simple Explanation
(Plain-language explanation of the legal concept or rights)

### ⚖️ Relevant Legal Provisions
(The specific Sections and Acts that apply, explained simply)

### 🏛️ Landmark Court Judgments
(What the Supreme Court or High Courts have ruled on this matter)

### 📖 What the Sources Say
(Key practical takeaways from the retrieved legal evidence)

### 🔗 Official Sources
(List of judgment names, sections, and source documents)

### ⚠️ Important Note
(Clear statement that users should consult a qualified legal practitioner for case-specific representation)
"""

LEGAL_DISCLAIMER = (
    "NyayaAI provides legal information and research assistance based on retrieved sources. "
    "It does not provide professional legal advice or establish an attorney-client relationship. "
    "Users should verify the original legal sources and consult a qualified legal professional for case-specific advice."
)


def build_rag_context(
    query: str,
    legal_issue: str,
    legal_domain: str,
    applicable_sections: List[str],
    applicable_acts: List[str],
    evidence_chunks: List[RetrievedChunkItem],
    graph_relationships: List[GraphRelationshipTriple],
) -> str:
    """Formats retrieved evidence chunks and graph relationships into a unified prompt context."""
    lines = [
        f"USER QUERY: {query}",
        f"IDENTIFIED LEGAL ISSUE: {legal_issue}",
        f"LEGAL DOMAIN: {legal_domain}",
        f"APPLICABLE ACTS: {', '.join(applicable_acts) if applicable_acts else 'General Law'}",
        f"APPLICABLE SECTIONS: {', '.join(applicable_sections) if applicable_sections else 'Not specified'}",
        "",
        "=" * 60,
        "RETRIEVED LEGAL EVIDENCE CHUNKS (VERIFIED PROVENANCE):",
        "=" * 60,
    ]

    for idx, chunk in enumerate(evidence_chunks, start=1):
        lines.append(f"\n[EVIDENCE #{idx}]")
        lines.append(f"Case/Document: {chunk.case_name}")
        lines.append(f"Court: {chunk.section}")
        lines.append(f"Page Number: {chunk.page} | Paragraph Number: {chunk.paragraph_number}")
        lines.append(f"Source URL: {chunk.source_url}")
        lines.append(f"Text:\n\"\"\"{chunk.text.strip()}\"\"\"")

    if graph_relationships:
        lines.append("\n" + "=" * 60)
        lines.append("KNOWLEDGE GRAPH RELATIONSHIPS (VERIFIED PRECEDENT NETWORK):")
        lines.append("=" * 60)
        for rel in graph_relationships:
            lines.append(f"• {rel.source} --[{rel.relationship}]--> {rel.target} ({rel.target_type})")

    return "\n".join(lines)


# ===========================================================================
# Evidence-Grounded Citation Prompts (Phase 5)
# ===========================================================================

GROUNDED_CITATION_SYSTEM_PROMPT = """You are NyayaAI, an evidence-grounded legal research assistant specializing in Indian criminal law.

STRICT GROUNDING RULES:
1. Answer ONLY using the EVIDENCE PASSAGES provided below. Do not use external legal knowledge.
2. Cite EVERY legal proposition explicitly as [Section X, Act] or [Case Name, Citation].
3. If the evidence passages do not contain sufficient information, state clearly:
   "INSUFFICIENT_EVIDENCE: The retrieved records do not contain adequate legal grounds to answer [specific aspect]."
4. Never invent, extrapolate, or hallucinate section numbers or case precedents.
5. Keep statutory section numbers and case names identical to the provided evidence.
6. Language: Provide your answer in {language}. Keep citations and section numbers in standard English/Latin script.
7. Legal regime applicable on query date ({query_date}): {law_version}.

EVIDENCE PASSAGES:
{evidence_passages}

LEGAL GLOSSARY (Use standard translations when responding in Indian regional languages):
{glossary_terms}

USER QUERY:
{query}
"""


def build_grounded_prompt(
    query: str,
    evidence_chunks: List[Any],
    language: str = "English",
    query_date: str = "current",
    law_version: str = "BNS/BNSS/BSA (effective 1 July 2024)",
    glossary_terms: str = "",
) -> str:
    """Builds a strictly grounded prompt for Gemini requiring evidence citations."""
    passages = []
    for idx, c in enumerate(evidence_chunks, start=1):
        if hasattr(c, "case_name"):
            name = c.case_name
            sec = c.section
            text = c.text
            page = getattr(c, "page", 1)
        elif isinstance(c, dict):
            name = c.get("case_name", "Unknown Case")
            sec = c.get("section", "General")
            text = c.get("text", "")
            page = c.get("page", 1)
        else:
            name, sec, text, page = "Source", "Section", str(c), 1

        passages.append(f"--- [PASSAGE {idx}] {name} (Page {page}, {sec}) ---\n{text}")

    evidence_text = "\n\n".join(passages) if passages else "No evidence passages retrieved."

    return GROUNDED_CITATION_SYSTEM_PROMPT.format(
        language=language,
        query_date=query_date,
        law_version=law_version,
        evidence_passages=evidence_text,
        glossary_terms=glossary_terms or "(Standard legal terms apply)",
        query=query,
    )

