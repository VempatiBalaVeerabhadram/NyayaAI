"""
NyayaAI — Unit Tests for Modular Architecture (Phases 1 - 8)
============================================================
Tests each newly implemented component:
- Intent Classifier (rule-based intent & dynamic alpha weighting)
- Temporal Statute Index & Transition Modelling (IPC -> BNS)
- Rhetorical Role Segmenter
- Precedent Authority Scorer
- Citation Verifier (hallucination & grounding check)
- Multilingual Language Detector & Glossary
- Information Retrieval & Legal Evaluation Metrics
- Gold Set Evaluation Loader
"""

import os
import sys
import pytest
from datetime import date
from pathlib import Path

# Add ai-service to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# ===========================================================================
# 1. Intent Classifier Tests
# ===========================================================================
class TestIntentClassifier:
    def setup_method(self):
        from app.retrieval.intent import IntentClassifier
        self.clf = IntentClassifier()

    def test_statute_lookup_intent(self):
        q = "What does Section 438 CrPC say about anticipatory bail?"
        result = self.clf.classify(q)
        assert result["intent"] == "statute_lookup"
        assert result["alpha"] == 0.70
        assert result["confidence"] > 0.5

    def test_case_narrative_intent(self):
        q = "A person was arrested without a warrant by police. Can they get bail?"
        result = self.clf.classify(q)
        assert result["intent"] == "case_narrative"
        assert result["alpha"] == 0.30

    def test_mixed_intent(self):
        q = "Under Section 437 IPC, when an accused is arrested without warrant as in Arnesh Kumar v. State?"
        result = self.clf.classify(q)
        assert result["intent"] == "mixed"
        assert result["alpha"] == 0.50

    def test_classify_intent_function(self):
        from app.retrieval.intent import classify_intent
        label, alpha = classify_intent("punishment for theft under IPC section 379")
        assert label == "statute_lookup"
        assert alpha == 0.70


# ===========================================================================
# 2. Temporal Statute Index Tests
# ===========================================================================
class TestTemporalStatuteIndex:
    def setup_method(self):
        from app.knowledge_graph.temporal import TemporalStatuteIndex
        acts_dir = Path(__file__).resolve().parent.parent.parent / "data" / "raw" / "acts"
        self.index = TemporalStatuteIndex(acts_dir=str(acts_dir))

    def test_law_version_label_pre_bns(self):
        label = self.index.get_law_version_label(date(2023, 6, 30))
        assert "IPC" in label or "pre" in label.lower()

    def test_law_version_label_post_bns(self):
        label = self.index.get_law_version_label(date(2024, 7, 1))
        assert "BNS" in label or "2024" in label

    def test_applicable_acts_post_transition(self):
        acts = self.index.get_applicable_acts(date(2025, 1, 1))
        assert any("BNS" in a or "Bharatiya" in a for a in acts)

    def test_applicable_acts_pre_transition(self):
        acts = self.index.get_applicable_acts(date(2023, 1, 1))
        assert any("IPC" in a or "Indian Penal Code" in a for a in acts)


# ===========================================================================
# 3. Rhetorical Role Segmenter Tests
# ===========================================================================
class TestRoleSegmenter:
    def setup_method(self):
        from app.ingestion.role_segmenter import JudgmentRoleSegmenter, RhetoricalRole
        self.seg = JudgmentRoleSegmenter()
        self.Role = RhetoricalRole

    def test_facts_detection(self):
        para = "The facts of the case are as follows. The accused was arrested on 15 March 2023. An FIR was registered at the police station under Section 420 IPC."
        result = self.seg.segment(para, case_id="TEST_001")
        assert any(s.role == self.Role.FACTS for s in result.segments)

    def test_decision_detection(self):
        para = "In the result, for the foregoing reasons, the appeal is allowed. Bail is granted to the appellant."
        result = self.seg.segment(para, case_id="TEST_002")
        assert any(s.role == self.Role.DECISION for s in result.segments)

    def test_role_weights(self):
        from app.ingestion.role_segmenter import JudgmentRoleSegmenter
        weights = JudgmentRoleSegmenter.ROLE_WEIGHTS
        assert weights["Facts"] == 0.35
        assert weights["Issues"] == 0.30
        assert weights["Reasoning"] == 0.20
        assert weights["Arguments"] == 0.10
        assert weights["Decision"] == 0.05

    def test_segment_chunks(self):
        sample_chunks = [
            {"text": "The facts are that the accused took money.", "section": "Facts of the Case"},
            {"text": "Learned counsel submitted that custodial arrest is unwarranted.", "section": "Arguments"},
        ]
        enriched = self.seg.segment_chunks(sample_chunks)
        assert len(enriched) == 2
        assert enriched[0]["rhetorical_role"] == "Facts"
        assert enriched[0]["role_weight"] == 0.35


# ===========================================================================
# 4. Precedent Authority Scorer Tests
# ===========================================================================
class TestAuthorityScorer:
    def setup_method(self):
        import networkx as nx
        from app.knowledge_graph.authority import AuthorityScorer

        g = nx.DiGraph()
        # Supreme court case
        g.add_node("CASE_SC_01", label="Case", name="Apex Landmark", court="Supreme Court of India")
        # High court case
        g.add_node("CASE_HC_01", label="Case", name="HC Ruling", court="High Court of Delhi")
        # District court case
        g.add_node("CASE_DC_01", label="Case", name="Trial Ruling", court="Sessions Court")

        # CITES edges to apex landmark
        g.add_edge("CASE_HC_01", "CASE_SC_01", type="CITES")
        g.add_edge("CASE_DC_01", "CASE_SC_01", type="CITES")

        self.scorer = AuthorityScorer(g)

    def test_supreme_court_authority_higher(self):
        sc_score = self.scorer.get_authority("CASE_SC_01")
        hc_score = self.scorer.get_authority("CASE_HC_01")
        dc_score = self.scorer.get_authority("CASE_DC_01")

        assert sc_score > hc_score
        assert hc_score > dc_score

    def test_rank_cases(self):
        ranked = self.scorer.rank_cases(["CASE_DC_01", "CASE_SC_01", "CASE_HC_01"])
        assert ranked[0][0] == "CASE_SC_01"


# ===========================================================================
# 5. Citation Verifier Tests
# ===========================================================================
class TestCitationVerifier:
    def setup_method(self):
        from app.rag.verifier import CitationVerifier
        self.verifier = CitationVerifier()

    def test_valid_citation_detected(self):
        answer = "Under Section 438 of the CrPC, anticipatory bail may be granted."
        chunks = [{"text": "Section 438 CrPC provides for direction for grant of bail.", "case_name": "Sibbia", "section": "Court Reasoning"}]
        report = self.verifier.verify(answer, chunks)
        assert report.total_citations >= 1
        assert len(report.valid_citations) >= 1

    def test_hallucinated_citation_detected(self):
        answer = "Under Section 999 of the Fantasy Act, mandatory release applies."
        chunks = [{"text": "Bail is the rule, jail is exception.", "case_name": "Antil", "section": "Holding"}]
        report = self.verifier.verify(answer, chunks)
        assert report.hallucination_rate > 0.0 or len(report.hallucinated_citations) > 0


# ===========================================================================
# 6. Multilingual Language Layer Tests
# ===========================================================================
class TestLanguageLayer:
    def setup_method(self):
        from app.language.detect import LanguageDetector
        from app.language.glossary import LegalGlossary
        from app.language.translate import LegalTranslator

        self.detector = LanguageDetector()
        self.glossary = LegalGlossary()
        self.translator = LegalTranslator()

    def test_english_detection(self):
        res = self.detector.detect("What is the punishment for theft under Section 379 IPC?")
        assert res.language_code == "en"

    def test_telugu_detection(self):
        res = self.detector.detect("దొంగతనానికి శిక్ష ఏమిటి?")
        assert res.language_code == "te"

    def test_hindi_detection(self):
        res = self.detector.detect("चोरी की सज़ा क्या है?")
        assert res.language_code == "hi"

    def test_glossary_lookup(self):
        entry = self.glossary.lookup("anticipatory bail")
        assert entry is not None
        assert "ముందస్తు" in entry.telugu or "జామీను" in entry.telugu
        assert "अग्रिम" in entry.hindi

    def test_preserve_tokens_in_translation(self):
        text = "Under Section 438 CrPC, please clarify."
        masked, token_map = self.translator._extract_preserve_tokens(text)
        assert len(token_map) >= 1
        restored = self.translator._restore_preserve_tokens(masked, token_map)
        assert restored == text


# ===========================================================================
# 7. Evaluation Metrics Tests
# ===========================================================================
class TestEvaluationMetrics:
    def setup_method(self):
        from app.evaluation.metrics import EvaluationMetrics
        self.metrics = EvaluationMetrics()

    def test_precision_at_k(self):
        retrieved = ["A", "B", "C", "D", "E"]
        relevant = {"A", "B", "C"}
        p5 = self.metrics.compute_precision_at_k(retrieved, relevant, 5)
        assert abs(p5 - 0.60) < 0.001

    def test_recall_at_k(self):
        retrieved = ["A", "B", "X", "Y"]
        relevant = {"A", "B", "C", "D"}
        r4 = self.metrics.compute_recall_at_k(retrieved, relevant, 4)
        assert abs(r4 - 0.50) < 0.001

    def test_mrr_first_rank(self):
        retrieved = ["TARGET", "B", "C"]
        relevant = {"TARGET"}
        assert self.metrics.compute_mrr(retrieved, relevant) == 1.0

    def test_mrr_second_rank(self):
        retrieved = ["A", "TARGET", "C"]
        relevant = {"TARGET"}
        assert abs(self.metrics.compute_mrr(retrieved, relevant) - 0.5) < 0.001

    def test_temporal_correctness_ipc(self):
        val = self.metrics.compute_temporal_correctness("IPC/CrPC/IEA", "IPC/CrPC regime (pre-BNS)")
        assert val == 1.0

    def test_temporal_correctness_mismatch(self):
        val = self.metrics.compute_temporal_correctness("BNS/BNSS/BSA", "IPC/CrPC regime")
        assert val == 0.0


# ===========================================================================
# 8. Gold Set Loader Tests
# ===========================================================================
class TestGoldSetLoader:
    def setup_method(self):
        from app.evaluation.gold_loader import GoldSetLoader
        self.loader = GoldSetLoader()

    def test_gold_queries_loaded(self):
        assert len(self.loader) >= 5

    def test_relevant_ids_populated(self):
        for q in self.loader:
            if q.expected_sections or q.expected_cases:
                assert len(q.relevant_ids) > 0
