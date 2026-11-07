"""
NyayaAI — Gold Set Evaluation Loader
====================================
Loads, validates, and provides iteration interfaces over the ground-truth legal evaluation dataset.
"""

import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List, Set
from loguru import logger


@dataclass
class GoldQuery:
    query_id: str
    query_en: str
    query_te: Optional[str]
    query_hi: Optional[str]
    date: Optional[str]
    expected_law_version: Optional[str]
    expected_sections: List[str]
    expected_cases: List[str]
    expected_answer_contains: List[str]
    difficulty: str
    domain: str

    def get_query(self, language: str = "en") -> str:
        if language == "te" and self.query_te and "PLACEHOLDER" not in self.query_te:
            return self.query_te
        if language == "hi" and self.query_hi and "PLACEHOLDER" not in self.query_hi:
            return self.query_hi
        return self.query_en

    @property
    def relevant_ids(self) -> Set[str]:
        ids: Set[str] = set()
        for s in self.expected_sections:
            ids.add(s)
            ids.add(s.lower())
        for c in self.expected_cases:
            ids.add(c)
            ids.add(c.lower())
        return ids


class GoldSetLoader:
    """Manages the annotated evaluation queries for ablation tests."""

    def __init__(self, gold_set_path: Optional[str] = None):
        if gold_set_path:
            self.path = Path(gold_set_path)
        else:
            base = Path(__file__).resolve().parent.parent.parent.parent
            self.path = base / "data" / "gold_set" / "gold_queries.json"

        self.queries: List[GoldQuery] = []
        self._load()

    def _load(self):
        if not self.path.exists():
            logger.warning(f"Gold queries file not found at {self.path}")
            return

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
                entries = data.get("entries", [])
                for e in entries:
                    q = GoldQuery(
                        query_id=e.get("query_id", ""),
                        query_en=e.get("query_en", ""),
                        query_te=e.get("query_te"),
                        query_hi=e.get("query_hi"),
                        date=e.get("date"),
                        expected_law_version=e.get("expected_law_version"),
                        expected_sections=e.get("expected_sections", []),
                        expected_cases=e.get("expected_cases", []),
                        expected_answer_contains=e.get("expected_answer_contains", []),
                        difficulty=e.get("difficulty", "medium"),
                        domain=e.get("domain", "general"),
                    )
                    self.queries.append(q)
            logger.info(f"✔ Loaded {len(self.queries)} gold queries from {self.path.name}")
        except Exception as err:
            logger.error(f"Error loading gold queries: {err}")

    def get_by_domain(self, domain: str) -> List[GoldQuery]:
        return [q for q in self.queries if q.domain.lower() == domain.lower()]

    def get_by_difficulty(self, difficulty: str) -> List[GoldQuery]:
        return [q for q in self.queries if q.difficulty.lower() == difficulty.lower()]

    def __len__(self) -> int:
        return len(self.queries)

    def __iter__(self):
        return iter(self.queries)

