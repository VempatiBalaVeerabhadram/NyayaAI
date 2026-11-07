# NyayaAI Empirical Evaluation Framework

## 1. Research Hypothesis

> **Hypothesis:** A unified retrieval framework combining sparse lexical indexing (BM25), dense representation learning (InLegalBERT / Sentence-Transformers), and topological knowledge-graph traversal (Neo4j) outperforms single-modality retrievers in discovering authoritative precedents and statutory provisions within Indian legal queries.

---

## 2. Quantitative Retrieval Metrics

We evaluate retrieval across a curated benchmark of approximately 100 Indian legal queries with ground-truth judgment references:

1. **Precision@K ($K \in \{5, 10\}$):**
   $$\text{Precision@K} = \frac{|\text{Retrieved}_K \cap \text{Relevant}|}{K}$$

2. **Recall@K ($K \in \{5, 10\}$):**
   $$\text{Recall@K} = \frac{|\text{Retrieved}_K \cap \text{Relevant}|}{|\text{Relevant}|}$$

3. **Mean Reciprocal Rank (MRR):**
   $$\text{MRR} = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{\text{rank}_i}$$

4. **Normalized Discounted Cumulative Gain (NDCG@K):**
   Evaluates graded relevance of precedents.

---

## 3. RAG Grounding & Hallucination Metrics

| Metric | Target | Evaluation Method |
|---|---|---|
| **Faithfulness / Groundedness** | > 95% | Fraction of statements supported by retrieved chunks |
| **Citation Correctness** | 100% | Every cited case/section exists in official dataset |
| **Hallucination Rate** | 0.0% | Zero invented case names or non-existent section numbers |
| **Refusal Accuracy** | > 90% | Returns explicit uncertainty when evidence is insufficient |
