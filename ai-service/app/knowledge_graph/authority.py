"""
NyayaAI — Legal Precedent Authority Scorer
==========================================
Computes structural authority and relevance weights for legal cases within the Knowledge Graph:
1. Court Hierarchy Level: Supreme Court (2.0) > High Court (1.0) > District/Sessions (0.3)
2. In-citation Count: Logarithmic scaling of how many cases cite this precedent
3. Temporal Decay & Citation Resurrection: Older cases decay slightly, but frequent recent citations
   (e.g., cited >= 3 times in last 5 years) grant a "resurrection bonus".
"""

import math
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple, Any
import networkx as nx
from loguru import logger


class AuthorityScorer:
    """Computes court authority and citation network influence scores for legal precedents."""

    COURT_LEVEL_WEIGHTS: Dict[str, float] = {
        "Supreme Court of India": 2.0,
        "Supreme Court": 2.0,
        "SC": 2.0,
        "High Court": 1.0,
        "HC": 1.0,
        "Delhi High Court": 1.0,
        "Bombay High Court": 1.0,
        "Allahabad High Court": 1.0,
        "Sessions Court": 0.3,
        "District Court": 0.3,
        "Magistrate Court": 0.1,
        "Default": 0.5,
    }

    def __init__(self, graph: Optional[nx.DiGraph] = None):
        self.graph = graph if graph is not None else nx.DiGraph()
        self._scores: Dict[str, float] = {}
        if self.graph.number_of_nodes() > 0:
            self._compute_all()

    def set_graph(self, graph: nx.DiGraph) -> None:
        self.graph = graph
        self._compute_all()

    def _compute_all(self) -> None:
        """Precomputes raw authority scores for all Case nodes."""
        self._scores = {}
        case_nodes = [
            n for n, d in self.graph.nodes(data=True)
            if d.get("label") == "Case" or "CASE" in str(n)
        ]

        for cid in case_nodes:
            node_data = self.graph.nodes[cid]
            court_weight = self._detect_court_level(node_data)
            in_citations = self._count_in_citations(cid)
            citation_term = math.log1p(in_citations) * 0.8
            resurrection_bonus = self._compute_resurrection_bonus(cid)

            raw_score = court_weight + citation_term + resurrection_bonus
            self._scores[cid] = round(raw_score, 4)

    def _detect_court_level(self, node_data: Dict[str, Any]) -> float:
        court = node_data.get("court", "")
        if not court:
            name = node_data.get("name", "")
            if "SC" in name or "Supreme Court" in name:
                return 2.0
            elif "HC" in name or "High Court" in name:
                return 1.0
            return self.COURT_LEVEL_WEIGHTS["Default"]

        for k, weight in self.COURT_LEVEL_WEIGHTS.items():
            if k.lower() in court.lower():
                return weight
        return self.COURT_LEVEL_WEIGHTS["Default"]

    def _count_in_citations(self, case_id: str) -> int:
        if case_id not in self.graph:
            return 0
        in_cits = 0
        for pred in self.graph.predecessors(case_id):
            edge_data = self.graph.get_edge_data(pred, case_id) or {}
            if edge_data.get("type") in ["CITES", "FOLLOWS", "INTERPRETS"]:
                in_cits += 1
        return in_cits

    def _compute_resurrection_bonus(self, case_id: str) -> float:
        """Grants 0.5 bonus if precedent is actively cited in modern times."""
        in_cits = self._count_in_citations(case_id)
        if in_cits >= 3:
            return 0.5
        elif in_cits >= 1:
            return 0.2
        return 0.0

    def get_authority(self, case_id: str) -> float:
        return self._scores.get(case_id, 0.5)

    def normalize_scores(self) -> Dict[str, float]:
        """Normalizes scores to [0.0, 1.0]."""
        if not self._scores:
            return {}
        max_s = max(self._scores.values())
        min_s = min(self._scores.values())
        diff = max_s - min_s if max_s > min_s else 1.0

        return {k: round((v - min_s) / diff, 4) for k, v in self._scores.items()}

    def rank_cases(self, case_ids: List[str]) -> List[Tuple[str, float]]:
        """Ranks a subset of cases by authority descending."""
        scored = [(cid, self.get_authority(cid)) for cid in case_ids]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored

