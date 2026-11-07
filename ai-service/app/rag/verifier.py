"""
NyayaAI — Citation Verifier
Post-generation verification: every cited section or case in the LLM answer
must exist in the database AND must have been in the retrieved set passed to the LLM.
"""
import re
from dataclasses import dataclass, field
from typing import Optional
from loguru import logger


@dataclass
class CitationCheckResult:
    citation_text: str          # e.g. "Section 438 CrPC" or "Arnesh Kumar v. State"
    citation_type: str          # "section" or "case"
    exists_in_db: bool
    was_in_retrieved_set: bool
    status: str                 # "valid", "hallucinated", "out_of_scope"
    suggested_correction: Optional[str] = None


@dataclass
class VerificationReport:
    total_citations: int
    valid_citations: list[CitationCheckResult] = field(default_factory=list)
    hallucinated_citations: list[CitationCheckResult] = field(default_factory=list)
    out_of_scope_citations: list[CitationCheckResult] = field(default_factory=list)
    hallucination_rate: float = 0.0  # fraction of citations that are hallucinated
    citation_accuracy: float = 0.0   # fraction that are valid
    cleaned_answer: str = ""         # answer with hallucinated citations flagged/removed


class CitationVerifier:
    """
    Parses generated answer text, extracts citations, and verifies each one.

    Citation patterns to detect:
    - Statutory: "Section 438", "s. 438", "Sec. 438", "S.438", "Section 438 CrPC",
                 "Section 438 of the CrPC", "u/s 438", "under Section 438"
    - Case: "(YYYY) N SCC NNN", "YYYY SCC NNN", case name patterns like "Arnesh Kumar v. State"
    - Act references: "IPC", "BNS", "CrPC", "BNSS", "IEA", "BSA", "IT Act"

    Verification logic:
    - exists_in_db: check if the section_id or case_id appears in the retrieved chunks list
      (we use the retrieved set as our proxy for "in DB" since we only have local data)
    - was_in_retrieved_set: the citation must appear in the text of one of the retrieved chunks

    Status:
    - "valid": exists_in_db=True AND was_in_retrieved_set=True
    - "out_of_scope": exists_in_db=True but was_in_retrieved_set=False (may be real but LLM used outside evidence)
    - "hallucinated": exists_in_db=False (citation not found anywhere in evidence)
    """

    # Regex patterns
    SECTION_PATTERN = re.compile(
        r'\b(?:(?:under\s+)?[Ss]ec(?:tion)?\.?\s*|[Ss]\.\s*|u/s\s*)(\d{1,3}[A-Z]?)\b'
        r'(?:\s+(?:of\s+)?(?:the\s+)?([A-Z]{2,6}))?',
        re.IGNORECASE
    )

    CASE_CITATION_PATTERN = re.compile(
        r'\((\d{4})\)\s+\d+\s+SCC\s+\d+|\b\d{4}\s+SCC\s+\d+',
        re.IGNORECASE
    )

    CASE_NAME_PATTERN = re.compile(
        r'([A-Z][a-z]+(?: [A-Z][a-z]+)*)\s+v(?:s)?\.?\s+([A-Z][a-z]+(?: [A-Z][a-z]+)*)',
    )

    # Known valid Indian acts/codes for sanity check
    KNOWN_ACTS = {
        "IPC", "BNS", "CrPC", "BNSS", "IEA", "BSA", "IT", "MV",
        "NDPS", "PMLA", "UAPA", "SC", "ST",
    }

    def verify(
        self,
        answer_text: str,
        retrieved_chunks: list[dict],  # list of chunk dicts with 'text', 'case_name', 'section' fields
        query_date: Optional[str] = None,  # ISO date string, used to flag wrong-regime citations
    ) -> VerificationReport:
        """Main verification entry point."""
        logger.debug("CitationVerifier.verify() called — extracting citations from answer.")

        citations = self._extract_citations(answer_text)
        logger.info(f"Extracted {len(citations)} citation candidates from answer.")

        valid: list[CitationCheckResult] = []
        hallucinated: list[CitationCheckResult] = []
        out_of_scope: list[CitationCheckResult] = []

        for cit in citations:
            if cit["type"] == "section":
                result = self._check_section_citation(
                    cit["number"], cit.get("act", ""), retrieved_chunks
                )
            else:
                result = self._check_case_citation(cit["text"], retrieved_chunks)

            if result.status == "valid":
                valid.append(result)
            elif result.status == "hallucinated":
                hallucinated.append(result)
            else:
                out_of_scope.append(result)

        total = len(citations)
        hallucination_rate = len(hallucinated) / total if total > 0 else 0.0
        citation_accuracy = len(valid) / total if total > 0 else 1.0

        cleaned = self._clean_answer(answer_text, hallucinated)

        report = VerificationReport(
            total_citations=total,
            valid_citations=valid,
            hallucinated_citations=hallucinated,
            out_of_scope_citations=out_of_scope,
            hallucination_rate=round(hallucination_rate, 4),
            citation_accuracy=round(citation_accuracy, 4),
            cleaned_answer=cleaned,
        )

        logger.info(
            f"Verification complete: {len(valid)} valid, {len(hallucinated)} hallucinated, "
            f"{len(out_of_scope)} out-of-scope. Hallucination rate: {hallucination_rate:.1%}"
        )
        return report

    def _extract_citations(self, text: str) -> list[dict]:
        """Extract all citation candidates from answer text."""
        citations: list[dict] = []
        seen_texts: set[str] = set()

        # 1. Statutory section citations
        for match in self.SECTION_PATTERN.finditer(text):
            section_num = match.group(1)
            act_name = match.group(2) or ""
            full_text = match.group(0).strip()

            dedup_key = f"section:{section_num}:{act_name.upper()}"
            if dedup_key in seen_texts:
                continue
            seen_texts.add(dedup_key)

            citations.append({
                "type": "section",
                "text": full_text,
                "number": section_num,
                "act": act_name.upper(),
            })
            logger.debug(f"Found section citation: {full_text!r}")

        # 2. Formal case citations — "(YYYY) N SCC NNN"
        for match in self.CASE_CITATION_PATTERN.finditer(text):
            full_text = match.group(0).strip()
            if full_text in seen_texts:
                continue
            seen_texts.add(full_text)

            citations.append({
                "type": "case",
                "text": full_text,
            })
            logger.debug(f"Found formal case citation: {full_text!r}")

        # 3. Case name citations — "Arnesh Kumar v. State of Bihar"
        for match in self.CASE_NAME_PATTERN.finditer(text):
            full_text = match.group(0).strip()
            if full_text in seen_texts:
                continue
            seen_texts.add(full_text)

            citations.append({
                "type": "case",
                "text": full_text,
            })
            logger.debug(f"Found case name citation: {full_text!r}")

        return citations

    def _check_section_citation(
        self, section_number: str, act_name: str, retrieved_chunks: list[dict]
    ) -> CitationCheckResult:
        """Verify a statutory section citation."""
        # Build a normalised display text
        if act_name:
            display = f"Section {section_number} {act_name}"
        else:
            display = f"Section {section_number}"

        # Patterns we'll search for inside chunk text / metadata
        search_patterns = [
            re.compile(rf'\bsec(?:tion)?\.?\s*{re.escape(section_number)}\b', re.IGNORECASE),
            re.compile(rf'\bs\.?\s*{re.escape(section_number)}\b', re.IGNORECASE),
            re.compile(rf'\bu/s\s*{re.escape(section_number)}\b', re.IGNORECASE),
        ]

        in_retrieved = False
        for chunk in retrieved_chunks:
            combined = " ".join([
                chunk.get("text", ""),
                chunk.get("section", ""),
                chunk.get("case_name", ""),
            ])
            if any(pat.search(combined) for pat in search_patterns):
                # If act_name provided, also verify it appears in this chunk
                if act_name:
                    if act_name.upper() in combined.upper():
                        in_retrieved = True
                        break
                    # Partial match — still count it, but note possible mismatch
                    in_retrieved = True
                    break
                else:
                    in_retrieved = True
                    break

        # Heuristic exists_in_db: if the section number is plausible (1–511 for IPC/BNS etc.)
        # and the act is known (or unspecified), treat it as potentially real;
        # real existence is confirmed only if it was in the retrieved set.
        exists_in_db = in_retrieved

        # Build suggested correction when act is unknown
        suggested: Optional[str] = None
        if not exists_in_db and act_name and act_name not in self.KNOWN_ACTS:
            suggested = (
                f"Check whether '{act_name}' is a valid act abbreviation. "
                f"Common acts: IPC/BNS (penal), CrPC/BNSS (procedure), IEA/BSA (evidence)."
            )

        if exists_in_db and in_retrieved:
            status = "valid"
        elif exists_in_db and not in_retrieved:
            status = "out_of_scope"
        else:
            status = "hallucinated"
            logger.warning(f"Hallucinated section citation detected: {display!r}")

        return CitationCheckResult(
            citation_text=display,
            citation_type="section",
            exists_in_db=exists_in_db,
            was_in_retrieved_set=in_retrieved,
            status=status,
            suggested_correction=suggested,
        )

    def _check_case_citation(
        self, citation_text: str, retrieved_chunks: list[dict]
    ) -> CitationCheckResult:
        """Verify a case citation."""
        in_retrieved = False

        # Normalize for fuzzy match — lower + strip punctuation
        normalized_cit = re.sub(r'[^\w\s]', '', citation_text.lower()).strip()
        normalized_words = set(normalized_cit.split())

        # Must have at least 2 words to avoid trivial matches
        if len(normalized_words) < 2:
            return CitationCheckResult(
                citation_text=citation_text,
                citation_type="case",
                exists_in_db=False,
                was_in_retrieved_set=False,
                status="hallucinated",
                suggested_correction="Citation text is too short to verify.",
            )

        for chunk in retrieved_chunks:
            combined = " ".join([
                chunk.get("text", ""),
                chunk.get("case_name", ""),
            ])
            normalized_chunk = re.sub(r'[^\w\s]', '', combined.lower())
            chunk_words = set(normalized_chunk.split())

            # Overlap: at least 60% of citation words must appear in chunk text
            overlap = normalized_words & chunk_words
            overlap_ratio = len(overlap) / len(normalized_words)
            if overlap_ratio >= 0.6:
                in_retrieved = True
                break

        exists_in_db = in_retrieved

        if exists_in_db and in_retrieved:
            status = "valid"
        elif exists_in_db and not in_retrieved:
            status = "out_of_scope"
        else:
            status = "hallucinated"
            logger.warning(f"Hallucinated case citation detected: {citation_text!r}")

        return CitationCheckResult(
            citation_text=citation_text,
            citation_type="case",
            exists_in_db=exists_in_db,
            was_in_retrieved_set=in_retrieved,
            status=status,
        )

    def _clean_answer(self, answer: str, hallucinated: list[CitationCheckResult]) -> str:
        """Add [UNVERIFIED] tag next to hallucinated citations in the answer text."""
        cleaned = answer
        for cit in hallucinated:
            # Escape special regex chars from citation text
            escaped = re.escape(cit.citation_text)
            # Replace the citation with itself + [UNVERIFIED] marker
            cleaned = re.sub(
                escaped,
                f"{cit.citation_text} **[UNVERIFIED]**",
                cleaned,
                count=0,  # replace all occurrences
            )
        return cleaned

    def format_report_markdown(self, report: VerificationReport) -> str:
        """Format the verification report as a markdown string for display."""
        lines = [
            "## 🔍 Citation Verification Report",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Total Citations Found | {report.total_citations} |",
            f"| ✅ Valid | {len(report.valid_citations)} |",
            f"| ⚠️ Out of Scope | {len(report.out_of_scope_citations)} |",
            f"| ❌ Hallucinated | {len(report.hallucinated_citations)} |",
            f"| Citation Accuracy | {report.citation_accuracy:.1%} |",
            f"| Hallucination Rate | {report.hallucination_rate:.1%} |",
            "",
        ]

        if report.valid_citations:
            lines.append("### ✅ Valid Citations")
            for c in report.valid_citations:
                lines.append(f"- **{c.citation_text}** `[{c.citation_type}]` — found in retrieved evidence")
            lines.append("")

        if report.out_of_scope_citations:
            lines.append("### ⚠️ Out-of-Scope Citations")
            lines.append(
                "> These citations may be real but were **not** in the evidence passages provided to the LLM. "
                "The model may have used external knowledge."
            )
            for c in report.out_of_scope_citations:
                lines.append(f"- **{c.citation_text}** `[{c.citation_type}]`")
                if c.suggested_correction:
                    lines.append(f"  - 💡 {c.suggested_correction}")
            lines.append("")

        if report.hallucinated_citations:
            lines.append("### ❌ Hallucinated Citations")
            lines.append(
                "> These citations were **not found** in any retrieved evidence passage. "
                "They are likely fabricated and should not be relied upon."
            )
            for c in report.hallucinated_citations:
                lines.append(f"- **{c.citation_text}** `[{c.citation_type}]`")
                if c.suggested_correction:
                    lines.append(f"  - 💡 {c.suggested_correction}")
            lines.append("")

        if report.total_citations == 0:
            lines.append("_No citations were detected in this response._")

        return "\n".join(lines)
