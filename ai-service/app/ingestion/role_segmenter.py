"""
NyayaAI — Rhetorical Role Segmenter for Indian Court Judgments
==============================================================
Segments legal judgments into distinct rhetorical roles:
- Facts: Factual background, incident, police investigation, FIR
- Issues: Legal questions framed for determination
- Arguments: Submissions of petitioner/respondent counsel
- Reasoning: Judicial analysis, doctrine, interpretation, ratio decidendi
- Decision: Operative order, holding, disposition (allowed/dismissed)
- Preamble: Case title, coram, date, parties
- Statute: Quoted statutory provisions

Uses rule-based heuristics and position priors tailored to Indian judicial styles.
Role weights for precedent similarity:
Facts: 0.35, Issues: 0.30, Reasoning: 0.20, Arguments: 0.10, Decision: 0.05
"""

import re
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger


class RhetoricalRole(str, Enum):
    PREAMBLE = "Preamble"
    FACTS = "Facts"
    ISSUES = "Issues"
    ARGUMENTS = "Arguments"
    REASONING = "Reasoning"
    DECISION = "Decision"
    STATUTE = "Statute"
    OTHER = "Other"


@dataclass
class SegmentedParagraph:
    paragraph_index: int
    text: str
    role: RhetoricalRole
    confidence: float
    signals: List[str]


@dataclass
class SegmentedJudgment:
    case_id: str
    segments: List[SegmentedParagraph]
    role_texts: Dict[str, str] = field(default_factory=dict)
    role_word_counts: Dict[str, int] = field(default_factory=dict)

    def get_role_text(self, role: RhetoricalRole) -> str:
        return self.role_texts.get(role.value, "")

    def has_role(self, role: RhetoricalRole) -> bool:
        return bool(self.role_texts.get(role.value, "").strip())


class JudgmentRoleSegmenter:
    """
    Rhetorical role segmenter for Indian judgments.
    Segments judgments by paragraph and assigns rhetorical roles.
    """

    ROLE_WEIGHTS: Dict[str, float] = {
        "Facts": 0.35,
        "Issues": 0.30,
        "Reasoning": 0.20,
        "Arguments": 0.10,
        "Decision": 0.05,
        "Statute": 0.00,
        "Preamble": 0.00,
        "Other": 0.00,
    }

    ROLE_SIGNALS: Dict[RhetoricalRole, List[str]] = {
        RhetoricalRole.PREAMBLE: [
            "in the supreme court of india", "in the high court of", "before the hon'ble",
            "criminal appeal no", "special leave petition", "writ petition", "slp (crl)",
            "appellant", "versus", "respondent", "petitioner", "bench:", "coram:",
            "date of judgment", "authored by"
        ],
        RhetoricalRole.FACTS: [
            "facts of the case", "brief facts", "factual background", "case of the prosecution",
            "prosecution case", "allegations are", "it is alleged", "the accused",
            "complainant", "fir was registered", "first information report", "police station",
            "incident took place", "arrested on", "charge sheet", "chargesheet",
            "trial court held", "sessions court convicted", "cognizance was taken"
        ],
        RhetoricalRole.ISSUES: [
            "question for consideration", "issues for determination", "the question is",
            "the short question", "the only question", "point for consideration",
            "reference to the", "substantial question of law", "the following questions",
            "issue before us", "whether the high court", "whether the court was justified"
        ],
        RhetoricalRole.ARGUMENTS: [
            "learned counsel", "learned senior counsel", "learned advocate",
            "it was argued", "it was submitted", "submission of", "contended that",
            "argued that", "urged that", "reliance was placed", "per contra",
            "on the other hand", "appearing on behalf of", "amicus curiae"
        ],
        RhetoricalRole.REASONING: [
            "we have considered", "in our considered view", "in our opinion",
            "we are of the view", "it is well settled", "it is settled law",
            "this court has held", "this court in", "ratio decidendi",
            "our analysis", "having regard to", "upon consideration", "we note that",
            "it is clear that", "we are satisfied", "the principle is", "the test is",
            "article 21", "due process", "statutory mandate"
        ],
        RhetoricalRole.DECISION: [
            "in the result", "for the foregoing reasons", "in view of the above",
            "accordingly", "the appeal is allowed", "the appeal is dismissed",
            "bail is granted", "bail is refused", "the order is set aside",
            "we hold that", "disposed of", "no order as to costs",
            "impugned order is set aside", "the conviction is upheld"
        ],
        RhetoricalRole.STATUTE: [
            "section", "sub-section", "clause", "schedule", "reads as follows",
            "is reproduced below", "as under:", "herein below", "proviso to"
        ],
    }

    def __init__(self):
        pass

    def segment(self, text: str, case_id: str = "") -> SegmentedJudgment:
        """Segments raw judgment text into typed rhetorical paragraphs."""
        raw_paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        total_paras = len(raw_paras)
        if total_paras == 0:
            return SegmentedJudgment(case_id=case_id, segments=[])

        segments: List[SegmentedParagraph] = []
        role_texts: Dict[str, List[str]] = {r.value: [] for r in RhetoricalRole}

        for idx, para in enumerate(raw_paras):
            pos_ratio = idx / max(1, total_paras - 1)
            role, conf, signals = self._score_paragraph(para, pos_ratio)

            seg = SegmentedParagraph(
                paragraph_index=idx,
                text=para,
                role=role,
                confidence=conf,
                signals=signals,
            )
            segments.append(seg)
            role_texts[role.value].append(para)

        merged_role_texts = {r: " ".join(texts) for r, texts in role_texts.items() if texts}
        word_counts = {r: len(t.split()) for r, t in merged_role_texts.items()}

        return SegmentedJudgment(
            case_id=case_id,
            segments=segments,
            role_texts=merged_role_texts,
            role_word_counts=word_counts,
        )

    def _score_paragraph(self, text: str, pos_ratio: float) -> Tuple[RhetoricalRole, float, List[str]]:
        """Scores a paragraph against keyword signals and position priors."""
        lower = text.lower()
        role_hits: Dict[RhetoricalRole, List[str]] = {}

        for role, signals in self.ROLE_SIGNALS.items():
            matched = [s for s in signals if s in lower]
            if matched:
                role_hits[role] = matched

        # Apply position prior boosts
        priors: Dict[RhetoricalRole, float] = {r: 0.0 for r in RhetoricalRole}
        if pos_ratio < 0.10:
            priors[RhetoricalRole.PREAMBLE] += 2.0
            priors[RhetoricalRole.FACTS] += 1.0
        elif pos_ratio < 0.35:
            priors[RhetoricalRole.FACTS] += 2.0
            priors[RhetoricalRole.ISSUES] += 1.0
        elif pos_ratio < 0.65:
            priors[RhetoricalRole.ARGUMENTS] += 1.5
            priors[RhetoricalRole.ISSUES] += 1.0
            priors[RhetoricalRole.REASONING] += 1.5
        elif pos_ratio < 0.88:
            priors[RhetoricalRole.REASONING] += 2.5
        else:
            priors[RhetoricalRole.DECISION] += 3.0

        best_role = RhetoricalRole.OTHER
        max_score = -1.0
        best_signals = []

        for role in RhetoricalRole:
            hits = role_hits.get(role, [])
            score = len(hits) * 1.5 + priors[role]
            if score > max_score and score > 0.5:
                max_score = score
                best_role = role
                best_signals = hits

        confidence = min(1.0, max(0.3, max_score / 5.0))
        return best_role, round(confidence, 2), best_signals

    def segment_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enriches standard chunk dictionaries with 'rhetorical_role' and 'role_weight'."""
        updated = []
        for c in chunks:
            text = c.get("text", "")
            section_hint = c.get("section", "").lower()

            if any(w in section_hint for w in ["fact", "allegation", "case of"]):
                role = RhetoricalRole.FACTS
            elif any(w in section_hint for w in ["issue", "question"]):
                role = RhetoricalRole.ISSUES
            elif any(w in section_hint for w in ["argument", "submission"]):
                role = RhetoricalRole.ARGUMENTS
            elif any(w in section_hint for w in ["reasoning", "considered view", "analysis"]):
                role = RhetoricalRole.REASONING
            elif any(w in section_hint for w in ["holding", "order", "operative", "decision"]):
                role = RhetoricalRole.DECISION
            else:
                role, _, _ = self._score_paragraph(text, 0.5)

            chunk_copy = dict(c)
            chunk_copy["rhetorical_role"] = role.value
            chunk_copy["role_weight"] = self.ROLE_WEIGHTS.get(role.value, 0.0)
            updated.append(chunk_copy)
        return updated


if __name__ == "__main__":
    segmenter = JudgmentRoleSegmenter()
    demo_judgment = """IN THE SUPREME COURT OF INDIA
Criminal Appeal No. 456 of 2021
State of Maharashtra v. ABC

The facts of the case are that on 12.01.2020, an FIR was registered under Section 420 IPC alleging cheating.
The accused was arrested by the police.

The question for consideration is whether anticipatory bail can be granted after filing of chargesheet.

Learned senior counsel for the appellant submitted that custodial interrogation is not required.

We have considered the submissions. In our considered view, personal liberty under Article 21 must be protected.
It is well settled that bail is the rule and jail is the exception.

In the result, the appeal is allowed. Bail is granted subject to conditions."""

    result = segmenter.segment(demo_judgment, case_id="DEMO_SC_2021")
    print(f"Segmented {len(result.segments)} paragraphs across roles:")
    for seg in result.segments:
        print(f"  [{seg.role.value}] (conf={seg.confidence}) {seg.text[:60]}...")

