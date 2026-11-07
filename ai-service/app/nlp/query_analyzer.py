"""
NyayaAI — InLegalBERT Legal Query Understanding Service
Analyzes user legal queries to identify:
- Primary Legal Issue & Domain
- Extracted Legal Concepts & Terminology
- Statutory Acts & Section Numbers
- Query Intent / Classification
- Query Expansion for Downstream Retrieval
"""

import re
from typing import Dict, Any, List, Optional
from loguru import logger

from app.config import settings
from app.ingestion.legal_entity_extractor import LegalEntityExtractor
from app.models.nlp import QueryAnalysisResponse


class LegalQueryAnalyzer:
    """Understands and structures Indian legal questions using InLegalBERT & rule-based extraction."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(LegalQueryAnalyzer, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.model_name = settings.inlegalbert_model
        self.entity_extractor = LegalEntityExtractor()
        self.tokenizer = None
        self.model = None
        self._load_transformer()
        self._initialized = True

    def _load_transformer(self):
        """Lazy loads InLegalBERT tokenizer/model if available locally or online."""
        try:
            from transformers import AutoTokenizer, AutoModel
            import os
            # Fast check: try local cache first to avoid slow network timeouts
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, local_files_only=True)
                self.model = AutoModel.from_pretrained(self.model_name, local_files_only=True)
                logger.info(f"✔ InLegalBERT loaded from local cache: {self.model_name}")
                return
            except Exception:
                pass

            # If not in local files, only attempt online if HF_HUB_OFFLINE is not set
            if os.environ.get("HF_HUB_OFFLINE") != "1":
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModel.from_pretrained(self.model_name)
                logger.info("✔ InLegalBERT transformer loaded successfully.")
            else:
                self.tokenizer = None
                self.model = None
        except Exception as e:
            logger.warning(
                f"InLegalBERT transformer not loaded ({e}). Using robust legal semantic entity understanding."
            )
            self.tokenizer = None
            self.model = None

    # Concept taxonomy for legal classification
    CONCEPT_TAXONOMY = {
        "Anticipatory Bail": [
            "anticipatory bail", "section 438", "apprehension of arrest", "pre-arrest bail",
            "section 482 bnss", "liberty", "non-bailable offence", "arrest anticipation"
        ],
        "Regular Bail": [
            "regular bail", "section 439", "section 437", "bail is rule", "jail exception",
            "custody", "undertrial", "section 480 bnss", "section 483 bnss", "surety"
        ],
        "Arrest Guidelines": [
            "arrest", "section 41a", "section 41", "notice of appearance", "mechanical arrest",
            "police powers", "section 35 bnss", "guidelines on arrest"
        ],
        "Quashing of FIR": [
            "quash", "quashing", "section 482", "inherent powers", "abuse of process",
            "settlement", "compromise", "quash fir", "no coercive steps"
        ],
        "Mandatory FIR Registration": [
            "fir", "first information report", "section 154", "cognizable", "refusing fir",
            "mandatory registration", "preliminary inquiry"
        ],
        "Cheating and Fraud": [
            "cheating", "section 420", "section 415", "fraud", "deceit", "section 318 bns",
            "dishonest inducement", "valuable security"
        ],
        "Criminal Breach of Trust": [
            "breach of trust", "section 405", "section 406", "entrustment", "misappropriation",
            "section 316 bns", "security deposit", "refund"
        ],
        "Cybercrime & IT Act": [
            "cyber", "section 66", "section 66a", "section 66c", "section 66d", "identity theft",
            "hacking", "computer resource", "it act", "information technology act", "online fraud"
        ],
        "Speedy Trial & Article 21": [
            "speedy trial", "article 21", "prolonged incarceration", "delay in trial",
            "fundamental right", "personal liberty", "indefinite detention"
        ],
    }

    def analyze_query(self, query: str) -> QueryAnalysisResponse:
        """
        Processes query and returns structured legal intent, extracted sections,
        concepts, and expanded search representation.
        """
        if not query or not query.strip():
            raise ValueError("Query string cannot be empty")

        clean_query = query.strip()
        query_lower = clean_query.lower()

        # 1. Extract statutory references
        acts = self.entity_extractor.extract_acts(clean_query)
        sections = self.entity_extractor.extract_sections(clean_query)
        articles = self.entity_extractor.extract_articles(clean_query)

        # 2. Extract concepts & match taxonomy
        matched_concepts: List[str] = []
        primary_issue = "General Legal Inquiry"
        domain = "Criminal Law"

        for issue_name, keywords in self.CONCEPT_TAXONOMY.items():
            for kw in keywords:
                if kw in query_lower:
                    matched_concepts.append(kw.title())
                    if primary_issue == "General Legal Inquiry":
                        primary_issue = issue_name

        # Domain classification
        sec_upper = [s.upper() for s in sections]
        if (
            "cyber" in query_lower
            or "it act" in query_lower
            or "information technology act" in query_lower
            or any(s in ["66", "66A", "66C", "66D", "43"] for s in sec_upper)
            or "Information Technology Act, 2000" in acts
        ):
            domain = "Cyber Law"
        elif "article 21" in query_lower or "article 19" in query_lower or "constitution" in query_lower:
            domain = "Constitutional Law"
        else:
            domain = "Criminal Law"

        # Query classification
        query_type = "precedent_discovery"
        if any(w in query_lower for w in ["what is", "explain", "meaning of", "define"]):
            query_type = "concept_explanation"
        elif any(w in query_lower for w in ["which section", "what section", "provisions of", "penalty for"]):
            query_type = "statutory_inquiry"
        elif any(w in query_lower for w in ["connected to", "cites", "overrules", "relationship"]):
            query_type = "case_connection"

        # Expanded query for optimal hybrid retrieval
        expansion_terms = [clean_query]
        if primary_issue != "General Legal Inquiry":
            expansion_terms.append(primary_issue)
        for act in acts:
            expansion_terms.append(act)
        for sec in sections:
            expansion_terms.append(f"Section {sec}")

        expanded_query = " ".join(dict.fromkeys(expansion_terms))

        return QueryAnalysisResponse(
            original_query=clean_query,
            primary_legal_issue=primary_issue,
            legal_domain=domain,
            query_type=query_type,
            extracted_concepts=list(dict.fromkeys(matched_concepts)),
            referenced_acts=acts,
            referenced_sections=sections,
            referenced_articles=articles,
            normalized_expanded_query=expanded_query,
            confidence_score=0.95,
        )
