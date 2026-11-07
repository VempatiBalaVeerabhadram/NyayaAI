# NyayaAI Retrieval-Augmented Generation (RAG) Specification

## 1. System Prompt & Groundedness Principles

The synthesis engine interfaces with Google Gemini. To eliminate hallucinations and prevent spurious legal opinions, the prompt architecture enforces strict constraints:

### Constraints:
1. **Zero External Fabrication:** The response must be derived strictly from the retrieved evidence chunks.
2. **Provenance Attribution:** Every legal assertion must link to `[Case Name, Page X, Para Y]` or `[Act Name, Section Z]`.
3. **Negative Constraint:** If the retrieved evidence does not answer the question, state:
   > *"Insufficient reliable evidence was retrieved from the authoritative legal sources to answer this question confidently."*
4. **Non-Advisory Mandate:** Every output includes the standard statutory disclaimer that NyayaAI does not provide legal advice.

---

## 2. Evidence Context Package Format

```json
{
  "query": "What are the essential grounds for granting anticipatory bail?",
  "mode": "researcher",
  "identified_legal_issues": ["Anticipatory Bail", "Personal Liberty", "Section 438 CrPC"],
  "statutory_context": [
    {
      "act": "Code of Criminal Procedure, 1973",
      "section": "438",
      "text": "Direction for grant of bail to person apprehending arrest..."
    }
  ],
  "retrieved_precedents": [
    {
      "case_id": "CASE_2020_SC_123",
      "case_name": "Sushila Aggarwal v. State (NCT of Delhi)",
      "court": "Supreme Court of India",
      "date": "2020-01-29",
      "page": 14,
      "para": "32",
      "text": "The protection granted under Section 438 CrPC is not invariably limited..."
    }
  ],
  "graph_precedent_lineage": [
    "Sushila Aggarwal (2020) CITES Gurbaksh Singh Sibbia (1980)",
    "Sushila Aggarwal (2020) DISCUSSES Section 438 CrPC"
  ]
}
```

---

## 3. Output Formats

### Simple User Mode:
- **Simple Explanation:** Plain-language summary free of legalistic jargon.
- **Relevant Law:** Applicable acts and sections.
- **Relevant Judgments:** Key case names and what they held.
- **Sources:** Exact verified citations.
- **Important Note:** Educational disclaimer.

### Legal Researcher Mode:
- **Legal Issue Formulation**
- **Applicable Acts & Sections**
- **Detailed Precedent Lineage & Holdings**
- **Knowledge Graph Discoveries**
- **Verbatim Evidence Extracts with Page Provenance**
- **Analytical Reasoning**
- **Sources & Limitations**
