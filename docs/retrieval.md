# NyayaAI Multi-Stage Hybrid Retrieval Engine

## 1. Overview

NyayaAI implements a multi-stage retrieval architecture specifically tailored for Indian statutory codes and judicial precedents.

The system combines:
1. **Lexical Keyword Retrieval (BM25)**: Accurately matches explicit statutory section numbers (e.g. *Section 438 CrPC*, *Section 41A*, *Section 420 IPC*, *Section 66A IT Act*), legal terms of art, and case titles.
2. **Dense Semantic Vector Retrieval (Sentence Transformers + Qdrant/FAISS)**: Captures conceptual legal meaning, synonyms, and natural language fact scenarios.
3. **Convex Hybrid Fusion**: Merges lexical and dense scores using a configurable parameter $\alpha \in [0.0, 1.0]$.

---

## 2. Mathematical Scoring Model

For a user query $q$ and a candidate document chunk $c_i$, the final hybrid relevance score is defined as:

$$\text{Score}_{\text{hybrid}}(q, c_i) = \alpha \cdot \text{Norm}(\text{Score}_{\text{BM25}}(q, c_i)) + (1 - \alpha) \cdot \text{Norm}(\text{Score}_{\text{semantic}}(q, c_i))$$

Where:
- $\alpha \in [0.0, 1.0]$ is the weighting factor (Default: $\alpha = 0.5$).
- $\text{Norm}(S) = \frac{S - S_{\min}}{S_{\max} - S_{\min} + \epsilon} \in [0.0, 1.0]$ scales raw scores across heterogeneous scoring distributions.

---

## 3. Subsystem Architecture

```
User Query: "What judgments discuss anticipatory bail under Section 438?"
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
┌─────────────────────────┐           ┌─────────────────────────┐
│  Lexical Tokenizer      │           │  Sentence Transformer   │
│  (Custom Legal Tokenizer│           │  (all-MiniLM-L6-v2)     │
│  + Stopword Filtering)  │           │  (384-dimensional)      │
└───────────┬─────────────┘           └───────────┬─────────────┘
            ▼                                     ▼
┌─────────────────────────┐           ┌─────────────────────────┐
│      BM25 Engine        │           │ Vector Store Engine     │
│   (rank-bm25 BM25Okapi) │           │ (Qdrant / Local FAISS)  │
└───────────┬─────────────┘           └───────────┬─────────────┘
            ▼                                     ▼
     BM25 Candidates                       Dense Candidates
            │                                     │
            └──────────────────┬──────────────────┘
                               ▼
               ┌───────────────────────────────┐
               │    Hybrid Fusion & Ranking    │
               │   Score = α·BM25 + (1-α)·Dense│
               └───────────────┬───────────────┘
                               ▼
                   Deduplicated Top-K Chunks
```

---

## 4. Vector Store & Failover Strategy

- **Primary Backend**: **Qdrant Vector Database** via REST/gRPC on port `6333`.
- **Local Fallback**: High-performance **FAISS (`IndexFlatIP`)** persisted to `data/vector_store/faiss_index.bin`.
- The system automatically detects Qdrant availability at startup. If Qdrant is offline, it seamlessly activates the local FAISS engine with zero downtime and exact metadata mapping.

---

## 5. REST API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/ai/search/bm25` | `POST` | Keyword lexical retrieval |
| `/ai/search/semantic` | `POST` | Dense vector semantic search |
| `/ai/search/hybrid` | `POST` | Convex linear combination fusion |
| `/ai/search/rebuild-index`| `POST` | Re-indexes all chunks in BM25 and vector stores |
