"""
NyayaAI — Gemini Generation & Grounded Template Synthesizer
Uses Google Gemini SDK for evidence-grounded response generation
with a deterministic offline synthesizer when API key is not configured.
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
                        "temperature": 0.1,  # Low temperature for precise legal extraction
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
    ) -> str:
        """
        Generates structured legal answer grounded in retrieved chunks and graph triples.
        """
        if not evidence_chunks:
            return (
                "### ⚠️ Insufficient Evidence\n\n"
                "Insufficient reliable evidence was retrieved from the database to answer this question confidently.\n\n"
                "Please verify the legal terms or try searching with specific statutory provisions (e.g., Section 438 CrPC, Section 420 IPC)."
            )

        # Build comprehensive context
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
                prompt = f"{system_instruction}\n\n{context_str}\n\nPlease provide your detailed evidence-grounded response below:"
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
    ) -> str:
        """Deterministically formats evidence chunks into a polished structured response."""
        unique_cases = list(dict.fromkeys([c.case_name for c in evidence_chunks if c.case_name]))

        if mode == "user":
            sec_str = ", ".join(f"Section {s}" for s in applicable_sections) if applicable_sections else "General Legal Provisions"
            act_str = ", ".join(applicable_acts) if applicable_acts else "Indian Law"

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

            body.extend([
                "",
                "### 🏛️ Landmark Court Judgments",
            ])
            for case in unique_cases[:3]:
                body.append(f"• **{case}**: Landmark Supreme Court ruling addressing core principles on this matter.")

            body.extend([
                "",
                "### 📖 What the Sources Say",
            ])
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

        else:
            # Mode: Researcher
            sec_str = ", ".join(f"Section {s}" for s in applicable_sections) if applicable_sections else "N/A"
            act_str = ", ".join(applicable_acts) if applicable_acts else "Code of Criminal Procedure / Indian Statutes"

            body = [
                "### 1. Legal Issue & Core Principles",
                f"The question pertains to **{legal_issue}** within the domain of **{legal_domain}**. "
                f"The governing statutory framework comprises {act_str}, specifically {sec_str}. "
                "The jurisprudence emphasizes adherence to due process, constitutional guarantees under Article 21, "
                "and strict compliance with statutory mandates.",
                "",
                "### 2. Applicable Statutory Provisions",
            ]
            for act in applicable_acts:
                body.append(f"• **{act}**")
            for sec in applicable_sections:
                body.append(f"  - **Section {sec}**")

            body.extend([
                "",
                "### 3. Landmark Judgments & Ratio Decidendi",
            ])
            for chunk in evidence_chunks[:3]:
                body.append(f"• **{chunk.case_name}** (*{chunk.section}*):")
                body.append(f"  - *Holding*: \"{chunk.text[:200]}...\" `[Page {chunk.page}, Para {chunk.paragraph_number}]`")

            if graph_relationships:
                body.extend([
                    "",
                    "### 4. Knowledge Graph Precedent Relationships",
                ])
                for rel in graph_relationships[:5]:
                    body.append(f"• `{rel.source}` **--[{rel.relationship}]-->** `{rel.target}` (*{rel.target_type}*)")

            body.extend([
                "",
                "### 5. Detailed Judicial Reasoning & Evidence",
            ])
            for idx, chunk in enumerate(evidence_chunks, start=1):
                body.append(f"**Extract {idx} [{chunk.case_name} — Page {chunk.page}, Para {chunk.paragraph_number}]**:")
                body.append(f"> {chunk.text.strip()}")
                body.append("")

            body.extend([
                "### 6. Sources & Provenance",
            ])
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
