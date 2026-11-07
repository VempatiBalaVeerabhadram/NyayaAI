"""
NyayaAI — Knowledge Graph & Graph-Enhanced Retrieval Endpoints
"""

from fastapi import APIRouter, HTTPException, Query, status
from loguru import logger

from app.models.graph import (
    GraphOverviewResponse,
    SubgraphResponse,
    GraphExpansionRequest,
    GraphExpansionResponse,
)
from app.models.graph_retrieval import (
    GraphEnhancedSearchRequest,
    GraphEnhancedSearchResponse,
)
from app.knowledge_graph.graph_builder import LegalGraphManager
from app.retrieval.graph_retriever import LegalGraphEnhancedRetriever

router = APIRouter(prefix="/ai/graph", tags=["Knowledge Graph"])

graph_manager = LegalGraphManager()
graph_retriever = LegalGraphEnhancedRetriever()


@router.get("/overview", response_model=GraphOverviewResponse, summary="Get Knowledge Graph Overview & Metrics")
async def get_graph_overview():
    """Returns node and relationship counts across Case, Act, Section, Judge, Court, and LegalIssue."""
    return graph_manager.get_overview()


@router.get("/case/{case_id}", response_model=SubgraphResponse, summary="Get Subgraph for a Specific Case")
async def get_case_subgraph(
    case_id: str,
    depth: int = Query(1, ge=1, le=2, description="Neighborhood depth (1 or 2)"),
):
    """Retrieves neighborhood subgraph for visualization (cited precedents, judges, sections, court)."""
    subgraph = graph_manager.get_case_subgraph(case_id, depth=depth)
    if subgraph.total_nodes == 0:
        raise HTTPException(status_code=404, detail=f"Case or node not found in Knowledge Graph: {case_id}")
    return subgraph


@router.post("/expand", response_model=GraphExpansionResponse, summary="Expand Seed Case Nodes")
async def expand_cases(request: GraphExpansionRequest):
    """Discovers connected precedents, sections, acts, and legal issues for given seed cases."""
    return graph_manager.expand_candidates(request.case_ids, depth=request.depth)


@router.get("/search", response_model=SubgraphResponse, summary="Search Knowledge Graph Nodes")
async def search_graph_nodes(q: str = Query(..., description="Node name or keyword to search")):
    """Searches for a matching node in the graph and returns its neighborhood subgraph."""
    subgraph = graph_manager.get_case_subgraph(q, depth=1)
    return subgraph


@router.post("/search", response_model=GraphEnhancedSearchResponse, summary="Graph-Enhanced Hybrid Search")
async def graph_enhanced_search(request: GraphEnhancedSearchRequest):
    """
    Executes multi-stage retrieval:
    InLegalBERT Query Understanding + Hybrid Fusion (BM25 + Dense) + Knowledge Graph Expansion.
    """
    try:
        return graph_retriever.search(
            query=request.query,
            top_k=request.top_k,
            alpha=request.alpha,
            depth=request.graph_expansion_depth,
            domain_filter=request.legal_domain,
            document_type_filter=request.document_type,
        )
    except Exception as e:
        logger.error(f"Graph-enhanced retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Graph-enhanced search failed: {str(e)}")


@router.post("/rebuild", summary="Rebuild Knowledge Graph from Metadata")
async def rebuild_graph():
    """Rebuilds the complete Knowledge Graph and syncs to local storage / Neo4j."""
    num_nodes, num_edges = graph_manager.build_graph_from_metadata()
    overview = graph_manager.get_overview()
    return {
        "status": "SUCCESS",
        "total_nodes": num_nodes,
        "total_relationships": num_edges,
        "active_backend": overview.active_backend,
    }
