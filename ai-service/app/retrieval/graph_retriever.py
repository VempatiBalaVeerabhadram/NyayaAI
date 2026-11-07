"""
NyayaAI — Graph-Enhanced Hybrid Retrieval Engine
Unifies:
1. InLegalBERT Query Understanding
2. BM25 Lexical Keyword Search
3. Dense Semantic Vector Search
4. Neo4j / NetworkX Knowledge Graph Expansion
To produce high-precision, precedent-connected evidence packages.
"""

import time
from typing import List, Dict, Any, Optional, Set
from loguru import logger

from app.nlp.query_analyzer import LegalQueryAnalyzer
from app.retrieval.hybrid_retriever import LegalHybridRetriever
from app.knowledge_graph.graph_builder import LegalGraphManager
from app.models.retrieval import RetrievedChunkItem
from app.models.graph_retrieval import (
    GraphEnhancedSearchRequest,
    GraphRelationshipTriple,
    GraphEnhancedSearchResponse,
)


class LegalGraphEnhancedRetriever:
    """Multi-modal legal retriever combining Lexical, Semantic, and Knowledge Graph signals."""

    def __init__(self):
        self.analyzer = LegalQueryAnalyzer()
        self.hybrid = LegalHybridRetriever()
        self.graph = LegalGraphManager()

    def search(
        self,
        query: str,
        top_k: int = 10,
        alpha: float = 0.5,
        depth: int = 1,
        domain_filter: Optional[str] = None,
        document_type_filter: Optional[str] = None,
    ) -> GraphEnhancedSearchResponse:
        """
        Executes graph-enhanced hybrid retrieval:
        1. Analyzes legal query using InLegalBERT
        2. Retrieves candidate chunks using Hybrid Fusion (BM25 + Dense)
        3. Traverses Knowledge Graph from top candidates (depth 1–2)
        4. Boosts and re-ranks candidates with graph connectedness
        5. Returns structured evidence + relational graph triples
        """
        start_time = time.perf_counter()

        # Step 1: Legal Query Understanding
        analysis = self.analyzer.analyze_query(query)
        effective_domain = domain_filter or (analysis.legal_domain if analysis.legal_domain != "Criminal Law" else None)

        # Step 2: Hybrid Retrieval with Query Expansion
        hybrid_candidates = self.hybrid.search(
            query=analysis.normalized_expanded_query,
            top_k=max(top_k * 2, 20),
            alpha=alpha,
            domain_filter=effective_domain,
            document_type_filter=document_type_filter,
        )

        # Step 3: Graph Expansion on Top Seeds
        seed_cases = list(dict.fromkeys([c.case_id for c in hybrid_candidates[:5] if c.case_id]))
        graph_expansion = self.graph.expand_candidates(seed_cases, depth=depth)

        # Step 4: Extract Graph Triples for Evidence Package
        graph_triples: List[GraphRelationshipTriple] = []
        for seed_id in seed_cases:
            subgraph = self.graph.get_case_subgraph(seed_id, depth=depth)
            seed_name = next(
                (n.properties.get("name", seed_id) for n in subgraph.nodes if n.id == seed_id),
                seed_id,
            )
            for rel in subgraph.relationships:
                source_node = next((n for n in subgraph.nodes if n.id == rel.source_id), None)
                target_node = next((n for n in subgraph.nodes if n.id == rel.target_id), None)
                if source_node and target_node:
                    s_name = source_node.properties.get("name", source_node.id)
                    t_name = target_node.properties.get("name", target_node.id)
                    graph_triples.append(
                        GraphRelationshipTriple(
                            source=s_name,
                            relationship=rel.type,
                            target=t_name,
                            source_type=source_node.label,
                            target_type=target_node.label,
                        )
                    )

        # Deduplicate triples
        unique_triples: List[GraphRelationshipTriple] = []
        seen_triples = set()
        for gt in graph_triples:
            key = (gt.source, gt.relationship, gt.target)
            if key not in seen_triples:
                seen_triples.add(key)
                unique_triples.append(gt)

        # Step 5: Graph Boost & Re-Ranking
        # Boost chunks that belong to cases/sections discovered in the graph expansion
        boosted_candidates: List[RetrievedChunkItem] = []
        connected_case_names_lower = {c.lower() for c in graph_expansion.connected_cases}
        applicable_sec_set = set(graph_expansion.applicable_sections) | set(analysis.referenced_sections)

        for item in hybrid_candidates:
            graph_boost = 0.0
            # Citation / Precedent match boost
            if item.case_name.lower() in connected_case_names_lower:
                graph_boost += 0.15
            # Statutory section match boost
            for sec in applicable_sec_set:
                if sec and sec in item.text:
                    graph_boost += 0.10
                    break

            adjusted_hybrid_score = round(min(1.0, item.hybrid_score + graph_boost), 4)

            boosted_candidates.append(
                RetrievedChunkItem(
                    chunk_id=item.chunk_id,
                    case_id=item.case_id,
                    case_name=item.case_name,
                    document_id=item.document_id,
                    page=item.page,
                    paragraph_number=item.paragraph_number,
                    text=item.text,
                    section=item.section,
                    legal_domain=item.legal_domain,
                    source_url=item.source_url,
                    bm25_score=item.bm25_score,
                    semantic_score=item.semantic_score,
                    hybrid_score=adjusted_hybrid_score,
                    rank=item.rank,
                )
            )

        # Sort descending by adjusted hybrid score
        boosted_candidates.sort(key=lambda x: x.hybrid_score, reverse=True)

        # Re-assign ranks
        final_results = []
        for rank, item in enumerate(boosted_candidates[:top_k], start=1):
            item.rank = rank
            final_results.append(item)

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        # Combine discovered applicable sections & acts
        all_sections = sorted(list(dict.fromkeys(analysis.referenced_sections + graph_expansion.applicable_sections)))
        all_acts = sorted(list(dict.fromkeys(analysis.referenced_acts + graph_expansion.applicable_acts)))

        return GraphEnhancedSearchResponse(
            query=query,
            primary_legal_issue=analysis.primary_legal_issue,
            legal_domain=analysis.legal_domain,
            total_results=len(final_results),
            results=final_results,
            connected_precedents=graph_expansion.connected_cases[:10],
            applicable_sections=all_sections,
            applicable_acts=all_acts,
            graph_relationships=unique_triples[:15],
            execution_time_ms=round(elapsed_ms, 2),
        )
