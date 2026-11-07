"""
NyayaAI — Retrieval Intent Classifier
======================================
Detects the semantic intent of a legal query and recommends an optimal alpha
weight for the hybrid BM25 + semantic retrieval engine.

Intent types
------------
- ``statute_lookup``:  User references a specific statutory section or act.
                       Alpha = 0.70  (BM25-heavy — exact term matching matters)
- ``case_narrative`` : User describes a fact pattern or references a case.
                       Alpha = 0.30  (Semantic-heavy — contextual understanding matters)
- ``mixed``          : Both types of signals detected.
                       Alpha = 0.50  (Balanced fusion)

No external LLM or ML model is required — purely rule-based via regex patterns.
"""

from __future__ import annotations

import re
from typing import NamedTuple

from loguru import logger


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Alpha weight when query is a direct statute / section lookup
ALPHA_STATUTE_LOOKUP: float = 0.70

#: Alpha weight when query describes a case fact pattern
ALPHA_CASE_NARRATIVE: float = 0.30

#: Alpha weight when both statute and narrative signals are present
ALPHA_MIXED: float = 0.50

# ---------------------------------------------------------------------------
# Signal patterns — Statute Lookup
# ---------------------------------------------------------------------------

#: Explicit "section N" or "s. N" references (handles multi-word like "section 41A")
_RE_SECTION_REF = re.compile(
    r"\b(?:section|sec\.?|s\.)\s*\d+[a-zA-Z]?\b",
    re.IGNORECASE,
)

#: "under section …" prepositional phrases
_RE_UNDER_SECTION = re.compile(
    r"\bunder\s+(?:section|sec\.?|s\.)\s*\d+",
    re.IGNORECASE,
)

#: Standalone act name acronyms (word-boundary anchored to avoid false hits)
_RE_ACT_ACRONYMS = re.compile(
    r"\b(?:IPC|BNS|CrPC|BNSS|IEA|BSA|CPC|IT\s?Act|POCSO|NDPS|PMLA|UAPA)\b",
    re.IGNORECASE,
)

#: "provision", "penalty for", "punishment under", "what does section …"
_RE_PROVISION_PHRASES = re.compile(
    r"\b(?:provision|provisions|penalty\s+for|punishment\s+under|what\s+does\s+section|"
    r"offence\s+under|defined\s+under|covered\s+under)\b",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Signal patterns — Case Narrative
# ---------------------------------------------------------------------------

#: Case citation format e.g. "(2023) 5 SCC 123" or "2021 AIR SC 456"
_RE_CASE_CITATION = re.compile(
    r"\(\d{4}\)\s*\d+\s+(?:SCC|SCR|AIR|HC|CriLJ|DLT|BLR|KLT|ILR)\s*\d+|"
    r"\d{4}\s+(?:AIR|SCC|SCR|CriLJ)\s+(?:SC|HC)?\s*\d+",
    re.IGNORECASE,
)

#: Versus patterns indicating case reference
_RE_VERSUS = re.compile(
    r"\b(?:vs?\.?|versus)\b",
    re.IGNORECASE,
)

#: Descriptive verbs typical of fact-pattern queries
_RE_NARRATIVE_VERBS = re.compile(
    r"\b(?:accused|arrested|charged|convicted|acquitted|granted\s+bail|denied\s+bail|"
    r"remanded|sentenced|absconding|absconded|escaped|confessed|"
    r"complained|alleged|filed\s+an?\s+FIR|lodged\s+a\s+complaint|"
    r"assaulted|murdered|cheated|defrauded|stolen|misappropriated|"
    r"apprehended|detained|released|discharged)\b",
    re.IGNORECASE,
)

#: Conditional / hypothetical fact-pattern phrases
_RE_FACT_PATTERN = re.compile(
    r"\b(?:person\s+who|if\s+someone|can\s+(?:the\s+)?police|what\s+happens\s+when|"
    r"what\s+if|suppose|suppose\s+that|in\s+a\s+case\s+where|when\s+a\s+person|"
    r"how\s+to\s+get\s+bail|is\s+it\s+legal|can\s+(?:an?|the)\s+accused)\b",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _collect_statute_signals(query: str) -> list[str]:
    """Return a deduplicated list of statute-lookup signal strings found in *query*."""
    signals: list[str] = []

    for m in _RE_SECTION_REF.finditer(query):
        signals.append(m.group().strip())

    for m in _RE_UNDER_SECTION.finditer(query):
        # Avoid duplicating what _RE_SECTION_REF already captured
        signal = m.group().strip()
        if signal not in signals:
            signals.append(signal)

    for m in _RE_ACT_ACRONYMS.finditer(query):
        signal = m.group().strip().upper()
        if signal not in signals:
            signals.append(signal)

    for m in _RE_PROVISION_PHRASES.finditer(query):
        signal = m.group().strip()
        if signal not in signals:
            signals.append(signal)

    return signals


def _collect_narrative_signals(query: str) -> list[str]:
    """Return a deduplicated list of case-narrative signal strings found in *query*."""
    signals: list[str] = []

    for m in _RE_CASE_CITATION.finditer(query):
        signals.append(m.group().strip())

    for m in _RE_VERSUS.finditer(query):
        signal = m.group().strip()
        if signal not in signals:
            signals.append(signal)

    for m in _RE_NARRATIVE_VERBS.finditer(query):
        signal = m.group().strip()
        if signal not in signals:
            signals.append(signal)

    for m in _RE_FACT_PATTERN.finditer(query):
        signal = m.group().strip()
        if signal not in signals:
            signals.append(signal)

    return signals


def _compute_confidence(signals: list[str], total_signals: int) -> float:
    """
    Heuristic confidence score [0.0, 1.0].

    More unique signals → higher confidence, saturating at ~5 signals.
    """
    n = len(signals)
    if n == 0:
        return 0.0
    # Logarithmic saturation: conf = n / (n + 2)  → reaches 0.9 at n≈18, 0.6 at n=3
    return round(min(1.0, n / (n + 2.0)), 4)


# ---------------------------------------------------------------------------
# Public API — functional interface
# ---------------------------------------------------------------------------


def classify_intent(query: str) -> tuple[str, float]:
    """
    Classify the retrieval intent of a legal query and return the recommended
    hybrid-retrieval alpha weight.

    Parameters
    ----------
    query:
        The raw user query string.

    Returns
    -------
    tuple[str, float]
        A 2-tuple ``(intent_label, recommended_alpha)`` where *intent_label*
        is one of ``"statute_lookup"``, ``"case_narrative"``, or ``"mixed"``,
        and *recommended_alpha* is a float in ``[0.0, 1.0]``.

    Examples
    --------
    >>> classify_intent("What is punishment under section 420 IPC?")
    ('statute_lookup', 0.7)
    >>> classify_intent("The accused was arrested and denied bail by the sessions court.")
    ('case_narrative', 0.3)
    >>> classify_intent("Section 438 CrPC — accused was arrested. Can he get anticipatory bail?")
    ('mixed', 0.5)
    """
    if not query or not query.strip():
        logger.debug("Empty query supplied to classify_intent; defaulting to 'mixed'")
        return ("mixed", ALPHA_MIXED)

    statute_signals = _collect_statute_signals(query)
    narrative_signals = _collect_narrative_signals(query)

    has_statute = len(statute_signals) > 0
    has_narrative = len(narrative_signals) > 0

    if has_statute and has_narrative:
        intent = "mixed"
        alpha = ALPHA_MIXED
    elif has_statute:
        intent = "statute_lookup"
        alpha = ALPHA_STATUTE_LOOKUP
    elif has_narrative:
        intent = "case_narrative"
        alpha = ALPHA_CASE_NARRATIVE
    else:
        # No strong signals — fall back to balanced fusion
        intent = "mixed"
        alpha = ALPHA_MIXED

    logger.debug(
        "classify_intent | query={!r:.80} | intent={} | alpha={} | "
        "statute_signals={} | narrative_signals={}",
        query,
        intent,
        alpha,
        statute_signals,
        narrative_signals,
    )
    return (intent, alpha)


# ---------------------------------------------------------------------------
# Public API — class interface
# ---------------------------------------------------------------------------


class IntentClassifier:
    """
    Rule-based legal query intent classifier.

    Wraps :func:`classify_intent` with a richer dict output including
    all matched signals and a heuristic confidence score.

    Usage
    -----
    ::

        classifier = IntentClassifier()
        result = classifier.classify("What is section 302 IPC?")
        # {'intent': 'statute_lookup', 'alpha': 0.7, 'signals': ['section 302', 'IPC'], 'confidence': 0.5}
    """

    def classify(self, query: str) -> dict:
        """
        Classify the intent of *query* and return a detailed result dict.

        Parameters
        ----------
        query:
            The raw user legal query string.

        Returns
        -------
        dict
            Keys:

            - ``intent``     – ``str``: one of ``"statute_lookup"``,
              ``"case_narrative"``, ``"mixed"``
            - ``alpha``      – ``float``: recommended hybrid-retrieval weight
              for BM25 component
            - ``signals``    – ``list[str]``: matched signal strings that drove
              the classification
            - ``confidence`` – ``float``: heuristic confidence in ``[0.0, 1.0]``
        """
        statute_signals = _collect_statute_signals(query)
        narrative_signals = _collect_narrative_signals(query)

        has_statute = len(statute_signals) > 0
        has_narrative = len(narrative_signals) > 0

        if has_statute and has_narrative:
            intent = "mixed"
            alpha = ALPHA_MIXED
            all_signals = list(dict.fromkeys(statute_signals + narrative_signals))
        elif has_statute:
            intent = "statute_lookup"
            alpha = ALPHA_STATUTE_LOOKUP
            all_signals = statute_signals
        elif has_narrative:
            intent = "case_narrative"
            alpha = ALPHA_CASE_NARRATIVE
            all_signals = narrative_signals
        else:
            intent = "mixed"
            alpha = ALPHA_MIXED
            all_signals = []

        confidence = _compute_confidence(all_signals, len(all_signals))

        result: dict = {
            "intent": intent,
            "alpha": alpha,
            "signals": all_signals,
            "confidence": confidence,
        }

        logger.debug(
            "IntentClassifier.classify | intent={} | alpha={} | confidence={} | signals={}",
            intent,
            alpha,
            confidence,
            all_signals,
        )
        return result


# ---------------------------------------------------------------------------
# CLI demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    _DEMO_QUERIES = [
        # Statute lookups
        "What is the punishment under section 420 IPC?",
        "Explain section 438 CrPC anticipatory bail",
        "What does section 303 BNS say about theft?",
        "Provision under BNSS 482 for inherent powers",
        "Define criminal breach of trust under s. 316 BNS",
        # Case narratives
        "The accused was arrested and denied bail by the sessions court",
        "(2023) 5 SCC 123 — accused acquitted on lack of evidence",
        "State of Maharashtra vs. Ram Lal — convicted for cheating",
        "If someone is arrested without a warrant can police detain them?",
        "Person who was charged with murder and later granted bail",
        # Mixed
        "Section 438 CrPC — the accused was arrested and wants anticipatory bail",
        "In (2021) 3 SCC 450 what did the court say about section 302 IPC punishment?",
        "Can police arrest without warrant under section 41 CrPC if accused absconded?",
        # Edge cases
        "",
        "bail",
        "What is legal?",
    ]

    classifier = IntentClassifier()
    print("\n" + "=" * 72)
    print("NyayaAI — Intent Classifier Demo")
    print("=" * 72)
    for q in _DEMO_QUERIES:
        label, alpha = classify_intent(q)
        detail = classifier.classify(q)
        display_q = (q[:60] + "…") if len(q) > 63 else q
        print(f"\nQuery  : {display_q!r}")
        print(f"Intent : {label:<18}  Alpha: {alpha}")
        print(f"Signals: {detail['signals']}")
        print(f"Conf   : {detail['confidence']}")
    print("\n" + "=" * 72)
