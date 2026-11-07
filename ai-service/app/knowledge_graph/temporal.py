"""
NyayaAI — Temporal Statute Index
=================================
Manages SectionVersion objects across the IPC→BNS, CrPC→BNSS, IEA→BSA transitions
(all effective 1 July 2024).

Key concepts
------------
* SectionVersion  — a section's text as it existed during a time range
  [valid_from, valid_to].  valid_to=None means "still in force".
* TemporalStatuteIndex — builds an in-memory index from the Act JSON files
  in ``data/raw/acts/`` and an optional IPC→BNS mapping CSV, then answers
  temporal queries: "which version of section X was in force on date Y?"

IPC/CrPC/IEA sunset date : 2024-06-30
BNS/BNSS/BSA commencement: 2024-07-01
"""

from __future__ import annotations

import csv
import json
import os
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from loguru import logger

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Official commencement / sunset dates
_IPC_VALID_FROM  = date(1860, 10,  6)
_CRPC_VALID_FROM = date(1973,  1, 25)
_IEA_VALID_FROM  = date(1872,  3, 15)
_OLD_REGIME_SUNSET = date(2024,  6, 30)   # IPC / CrPC / IEA last effective day
_NEW_REGIME_START  = date(2024,  7,  1)   # BNS / BNSS / BSA effective date

# Map short_title / file-prefix → commencement date & sunset (None = still active)
_ACT_DATES: Dict[str, Tuple[date, Optional[date]]] = {
    "IPC":  (_IPC_VALID_FROM,   _OLD_REGIME_SUNSET),
    "CrPC": (_CRPC_VALID_FROM,  _OLD_REGIME_SUNSET),
    "IEA":  (_IEA_VALID_FROM,   _OLD_REGIME_SUNSET),
    "BNS":  (_NEW_REGIME_START, None),
    "BNSS": (_NEW_REGIME_START, None),
    "BSA":  (_NEW_REGIME_START, None),
    "IT":   (date(2000, 10, 17), None),   # IT Act 2000 — still active
}

# Old-regime acts paired with their replacement
_SUCCESSOR: Dict[str, str] = {
    "IPC":  "BNS",
    "CrPC": "BNSS",
    "IEA":  "BSA",
}


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class SectionVersion:
    """Represents a statutory section as it stood during [valid_from, valid_to]."""

    section_id: str            # e.g. "IPC_378" or "BNS_303"
    act: str                   # "IPC", "BNS", "CrPC", "BNSS", "IEA", "BSA"
    section_number: str        # "378"
    title: str
    text: str
    valid_from: date
    valid_to: Optional[date]   # None = currently in force
    source_act: str            # original act name (long title)
    superseded_by: Optional[str] = None  # section_id of replacement section

    @property
    def is_current(self) -> bool:
        """True if this version is still in force (no sunset date)."""
        return self.valid_to is None

    def was_in_force_on(self, query_date: date) -> bool:
        """Return True if this version was in force on *query_date*."""
        if query_date < self.valid_from:
            return False
        if self.valid_to is not None and query_date > self.valid_to:
            return False
        return True

    def __repr__(self) -> str:
        end = self.valid_to.isoformat() if self.valid_to else "present"
        return (
            f"<SectionVersion {self.section_id!r} "
            f"[{self.valid_from.isoformat()} → {end}]>"
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _infer_act_key(filename: str) -> Optional[str]:
    """
    Guess the short act name (IPC, BNS, CrPC, BNSS, IEA, BSA, IT) from a
    JSON filename.  Returns None if the act is unknown / should be skipped.
    """
    fn = filename.lower()
    if "ipc"  in fn: return "IPC"
    if "bns"  in fn and "bnss" not in fn: return "BNS"
    if "bnss" in fn: return "BNSS"
    if "crpc" in fn: return "CrPC"
    if "iea"  in fn: return "IEA"
    if "bsa"  in fn: return "BSA"
    if "it_act" in fn or "it-act" in fn: return "IT"
    return None


def _build_section_id(act: str, section_number: str) -> str:
    """Return canonical section ID like 'IPC_378'."""
    return f"{act}_{section_number}"


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------

class TemporalStatuteIndex:
    """
    In-memory temporal index of statutory sections loaded from Act JSON files.

    Usage
    -----
    >>> idx = TemporalStatuteIndex("/path/to/data/raw/acts")
    >>> sv = idx.get_section_as_of("IPC_420", date(2020, 1, 1))
    >>> sv.title
    'Cheating and dishonestly inducing delivery of property'
    """

    def __init__(self, acts_dir: str) -> None:
        """
        Load all Act JSON files found in *acts_dir* and build the temporal index.

        Also attempts to load the IPC→BNS mapping CSV from the same directory
        (``ipc_bns_mapping.csv``) if it exists.

        Parameters
        ----------
        acts_dir:
            Path to the directory containing ``*_property.json`` and
            ``*_bail.json`` Act files.
        """
        # section_id → list of SectionVersion (usually 1, may be more)
        self._index: Dict[str, List[SectionVersion]] = {}

        # (act, section_number) → section_id — fast lookup by act+number
        self._by_act_num: Dict[Tuple[str, str], str] = {}

        # section_number → list[section_id] — lookup when act is unknown
        self._by_number: Dict[str, List[str]] = {}

        self.load_acts(acts_dir)

        mapping_csv = os.path.join(acts_dir, "ipc_bns_mapping.csv")
        self.load_mapping(mapping_csv)

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def load_acts(self, acts_dir: str) -> None:
        """
        Read all JSON files in *acts_dir* and create ``SectionVersion`` objects.

        Date assignments
        ~~~~~~~~~~~~~~~~
        * IPC  → valid_from=1860-10-06, valid_to=2024-06-30
        * CrPC → valid_from=1973-01-25, valid_to=2024-06-30
        * IEA  → valid_from=1872-03-15, valid_to=2024-06-30
        * BNS  → valid_from=2024-07-01, valid_to=None
        * BNSS → valid_from=2024-07-01, valid_to=None
        * BSA  → valid_from=2024-07-01, valid_to=None
        * IT   → valid_from=2000-10-17, valid_to=None
        """
        acts_path = Path(acts_dir)
        if not acts_path.exists():
            logger.warning(f"Acts directory not found: {acts_dir}")
            return

        json_files = sorted(acts_path.glob("*.json"))
        if not json_files:
            logger.warning(f"No JSON files found in {acts_dir}")
            return

        loaded_sections = 0
        for json_file in json_files:
            act_key = _infer_act_key(json_file.name)
            if act_key is None:
                logger.debug(f"Skipping unrecognised Act file: {json_file.name}")
                continue

            try:
                with open(json_file, encoding="utf-8") as fh:
                    data = json.load(fh)
            except (json.JSONDecodeError, OSError) as exc:
                logger.error(f"Failed to load {json_file}: {exc}")
                continue

            # Support two JSON shapes:
            #   shape A: {"act_name": ..., "sections": [...]}  (IPC)
            #   shape B: {"act_name": ..., "sections": [...]}  (BNS — same keys)
            #   shape C: {"document_id": ..., "sections": [...]}  (also BNS)
            act_name: str = data.get("act_name") or data.get("short_title", act_key)
            sections: list = data.get("sections", [])

            if not sections:
                logger.warning(f"No 'sections' array in {json_file.name}")
                continue

            valid_from, valid_to = _ACT_DATES.get(act_key, (date(1900, 1, 1), None))

            for sec in sections:
                sec_num   = str(sec.get("section_number", "")).strip()
                sec_title = sec.get("section_title", sec.get("title", "")).strip()
                sec_text  = sec.get("section_text", sec.get("text", "")).strip()

                if not sec_num:
                    continue  # skip malformed entries

                section_id = _build_section_id(act_key, sec_num)
                sv = SectionVersion(
                    section_id     = section_id,
                    act            = act_key,
                    section_number = sec_num,
                    title          = sec_title,
                    text           = sec_text,
                    valid_from     = valid_from,
                    valid_to       = valid_to,
                    source_act     = act_name,
                )

                # Store in index
                self._index.setdefault(section_id, []).append(sv)
                self._by_act_num[(act_key, sec_num)] = section_id
                self._by_number.setdefault(sec_num, []).append(section_id)
                loaded_sections += 1

            logger.debug(
                f"Loaded {len(sections)} sections from {json_file.name} "
                f"(act={act_key}, {valid_from}→{valid_to or 'present'})"
            )

        logger.info(
            f"TemporalStatuteIndex: loaded {loaded_sections} section versions "
            f"from {len(json_files)} files in {acts_dir}"
        )

    def load_mapping(self, mapping_csv_path: str) -> None:
        """
        Load an IPC→BNS mapping CSV and set ``superseded_by`` links.

        Expected CSV columns (order-independent, header row required):
            ipc_section, bns_section

        Any missing or malformed file is handled gracefully (warning only).
        """
        csv_path = Path(mapping_csv_path)
        if not csv_path.exists():
            logger.debug(
                f"IPC→BNS mapping CSV not found at {mapping_csv_path}; "
                "superseded_by links will not be set."
            )
            return

        try:
            with open(csv_path, encoding="utf-8", newline="") as fh:
                reader = csv.DictReader(fh)
                # Accept flexible header names
                fieldnames = {f.strip().lower() for f in (reader.fieldnames or [])}
                if not {"ipc_section", "bns_section"}.issubset(fieldnames):
                    logger.warning(
                        f"Mapping CSV {mapping_csv_path} must have columns "
                        "'ipc_section' and 'bns_section'.  Skipping."
                    )
                    return

                linked = 0
                for row in reader:
                    ipc_num = str(row.get("ipc_section", "")).strip()
                    bns_num = str(row.get("bns_section", "")).strip()
                    if not ipc_num or not bns_num:
                        continue

                    ipc_id = _build_section_id("IPC", ipc_num)
                    bns_id = _build_section_id("BNS", bns_num)

                    for sv in self._index.get(ipc_id, []):
                        sv.superseded_by = bns_id
                        linked += 1

                logger.info(
                    f"Loaded {linked} IPC→BNS superseded_by links from {csv_path.name}"
                )
        except (OSError, csv.Error) as exc:
            logger.error(f"Failed to load mapping CSV {mapping_csv_path}: {exc}")

    # ------------------------------------------------------------------
    # Core temporal query
    # ------------------------------------------------------------------

    def get_section_as_of(
        self, section_ref: str, query_date: date
    ) -> Optional[SectionVersion]:
        """
        Return the ``SectionVersion`` that was in force on *query_date*.

        Parameters
        ----------
        section_ref:
            Section identifier in one of these forms:

            * ``"IPC_378"``  — explicit act + number
            * ``"BNS_303"``  — explicit act + number
            * ``"CrPC_438"`` — explicit act + number
            * ``"378"``      — bare number; act inferred from *query_date*

        query_date:
            The date for which we want the in-force version.

        Returns
        -------
        SectionVersion or None
            The matching version, or None if not found.  Advisory log messages
            are emitted when a section has expired or its successor is known.
        """
        section_ref = section_ref.strip()

        # ---- 1. Parse the ref into (act, number) -------------------------
        act: Optional[str] = None
        number: Optional[str] = None

        if "_" in section_ref:
            parts = section_ref.split("_", 1)
            act, number = parts[0].upper(), parts[1]
        else:
            # Bare number — infer act from query_date
            number = section_ref
            if query_date < _NEW_REGIME_START:
                act = "IPC"
            else:
                act = "BNS"
            logger.debug(
                f"Bare section ref '{section_ref}' on {query_date}: "
                f"inferring act='{act}'"
            )

        # ---- 2. Build the canonical section_id and look it up ------------
        section_id = _build_section_id(act, number)
        candidates = self._index.get(section_id, [])

        if not candidates:
            # Try a case-insensitive / alternate act spelling search
            candidates = self._fallback_lookup(act, number)

        # ---- 3. Find the version valid on query_date ---------------------
        for sv in candidates:
            if sv.was_in_force_on(query_date):
                return sv

        # ---- 4. Not found — emit helpful advisory log --------------------
        if candidates:
            # We know the section, but it wasn't active on query_date
            sv_ref = candidates[0]
            if sv_ref.valid_to is not None and query_date > sv_ref.valid_to:
                successor_id = sv_ref.superseded_by
                if successor_id:
                    logger.warning(
                        f"{section_id} expired on {sv_ref.valid_to.isoformat()}. "
                        f"Use {successor_id} for dates on/after {_NEW_REGIME_START}."
                    )
                else:
                    # Try to auto-suggest successor act
                    succ_act = _SUCCESSOR.get(act)
                    if succ_act:
                        succ_candidates = self._index.get(
                            _build_section_id(succ_act, number), []
                        )
                        if succ_candidates:
                            succ_id = succ_candidates[0].section_id
                            logger.warning(
                                f"{section_id} expired on {sv_ref.valid_to.isoformat()}. "
                                f"Possible successor: {succ_id}."
                            )
                        else:
                            logger.warning(
                                f"{section_id} expired on {sv_ref.valid_to.isoformat()}. "
                                f"No known successor in {succ_act}."
                            )
            elif query_date < sv_ref.valid_from:
                logger.warning(
                    f"{section_id} did not commence until {sv_ref.valid_from.isoformat()}."
                )
        else:
            logger.debug(f"Section '{section_ref}' not found in the index.")

        return None

    # ------------------------------------------------------------------
    # Convenience query methods
    # ------------------------------------------------------------------

    def get_law_version_label(self, query_date: date) -> str:
        """
        Return a human-readable label for the legal regime active on *query_date*.

        >>> idx.get_law_version_label(date(2023, 1, 1))
        'IPC/CrPC/IEA (pre-BNS regime)'
        >>> idx.get_law_version_label(date(2024, 7, 1))
        'BNS/BNSS/BSA (effective 1 July 2024)'
        """
        if query_date < _NEW_REGIME_START:
            return "IPC/CrPC/IEA (pre-BNS regime)"
        return "BNS/BNSS/BSA (effective 1 July 2024)"

    def get_applicable_acts(self, query_date: date) -> List[str]:
        """
        Return the list of act short-titles that were in force on *query_date*.

        >>> idx.get_applicable_acts(date(2023, 6, 1))
        ['IPC', 'CrPC', 'IEA']
        >>> idx.get_applicable_acts(date(2024, 8, 1))
        ['BNS', 'BNSS', 'BSA', 'IT']
        """
        active: List[str] = []
        for act_key, (vf, vt) in _ACT_DATES.items():
            if query_date < vf:
                continue
            if vt is not None and query_date > vt:
                continue
            active.append(act_key)
        return sorted(active)

    def find_equivalent(
        self, section_ref: str, target_date: date
    ) -> Optional[SectionVersion]:
        """
        Given a section from one legal regime, find its equivalent version
        that was in force on *target_date*.

        This is especially useful for translating old IPC sections to BNS
        (and vice-versa) when the user asks about a case in a different era.

        Examples
        --------
        >>> idx.find_equivalent("IPC_420", date(2025, 1, 1))
        <SectionVersion 'BNS_318' [2024-07-01 → present]>

        >>> idx.find_equivalent("BNS_303", date(2020, 6, 1))
        None  # BNS did not exist yet; logs advisory
        """
        # First, resolve the given ref to its SectionVersion
        src_sv = self._resolve_to_any_version(section_ref)

        if src_sv is None:
            logger.warning(f"find_equivalent: '{section_ref}' not found in index.")
            return None

        # Check if the src is already valid on target_date
        if src_sv.was_in_force_on(target_date):
            return src_sv

        # Try superseded_by pointer
        if src_sv.superseded_by:
            succ_sv = self.get_section_as_of(src_sv.superseded_by, target_date)
            if succ_sv:
                return succ_sv

        # Try matching section number in the successor / predecessor act
        src_act = src_sv.act
        target_regime_acts = self.get_applicable_acts(target_date)

        # Look for the same number in a related act
        related_acts: List[str] = []
        if src_act in _SUCCESSOR:
            # old → new
            related_acts = [_SUCCESSOR[src_act]]
        else:
            # new → old: reverse the successor map
            reverse = {v: k for k, v in _SUCCESSOR.items()}
            if src_act in reverse:
                related_acts = [reverse[src_act]]

        for candidate_act in related_acts:
            if candidate_act in target_regime_acts:
                equiv = self.get_section_as_of(
                    _build_section_id(candidate_act, src_sv.section_number),
                    target_date,
                )
                if equiv:
                    return equiv

        logger.debug(
            f"No equivalent found for '{section_ref}' on {target_date}."
        )
        return None

    def all_versions(self, section_number: str) -> List[SectionVersion]:
        """
        Return all versions of a section across all acts (e.g., IPC + BNS).

        Parameters
        ----------
        section_number:
            Bare section number, e.g. ``"420"``.

        Returns
        -------
        list[SectionVersion]
            All known versions, ordered by valid_from ascending.
        """
        section_ids = self._by_number.get(section_number, [])
        all_sv: List[SectionVersion] = []
        for sid in section_ids:
            all_sv.extend(self._index.get(sid, []))
        return sorted(all_sv, key=lambda sv: sv.valid_from)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _resolve_to_any_version(self, section_ref: str) -> Optional[SectionVersion]:
        """
        Resolve *section_ref* to *any* SectionVersion (regardless of date).
        Used when we need metadata about a section independent of time.
        """
        if "_" in section_ref:
            parts = section_ref.split("_", 1)
            act, num = parts[0].upper(), parts[1]
        else:
            # Try IPC first, then BNS
            for act in ("IPC", "BNS", "CrPC", "BNSS", "IEA", "BSA"):
                candidates = self._index.get(_build_section_id(act, section_ref), [])
                if candidates:
                    return candidates[0]
            return None

        candidates = self._index.get(_build_section_id(act, num), [])
        return candidates[0] if candidates else None

    def _fallback_lookup(
        self, act: str, number: str
    ) -> List[SectionVersion]:
        """
        Case-insensitive fallback lookup when the primary index miss occurs.
        """
        for (a, n), sid in self._by_act_num.items():
            if a.upper() == act.upper() and n == number:
                return self._index.get(sid, [])
        return []


# ---------------------------------------------------------------------------
# Module-level convenience singleton factory
# ---------------------------------------------------------------------------

def build_temporal_index(acts_dir: Optional[str] = None) -> TemporalStatuteIndex:
    """
    Build and return a ``TemporalStatuteIndex`` for the given (or default) acts dir.

    The default acts directory is resolved relative to this file's location:
    ``<project_root>/data/raw/acts``.
    """
    if acts_dir is None:
        # Navigate from ai-service/app/knowledge_graph/ to data/raw/acts/
        this_dir = Path(__file__).resolve().parent
        acts_dir = str(this_dir.parents[3] / "data" / "raw" / "acts")
    return TemporalStatuteIndex(acts_dir)


# ---------------------------------------------------------------------------
# Quick smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from datetime import date

    idx = build_temporal_index()

    tests = [
        ("IPC_420",  date(2020, 1,  1)),
        ("IPC_420",  date(2025, 1,  1)),
        ("420",      date(2025, 1,  1)),
        ("BNS_318",  date(2024, 8,  1)),
        ("CrPC_438", date(2024, 8,  1)),
    ]

    print("\n=== Temporal Query Smoke Tests ===")
    for ref, qdate in tests:
        sv = idx.get_section_as_of(ref, qdate)
        print(f"  get_section_as_of({ref!r}, {qdate}) → {sv}")

    print("\n=== Regime Labels ===")
    for d in [date(2023, 6, 1), date(2024, 7, 1), date(2025, 1, 1)]:
        print(f"  {d}: {idx.get_law_version_label(d)} | acts={idx.get_applicable_acts(d)}")

    print("\n=== find_equivalent ===")
    eq = idx.find_equivalent("IPC_420", date(2025, 1, 1))
    print(f"  IPC_420 → (2025) → {eq}")
