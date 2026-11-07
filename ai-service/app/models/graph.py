"""
NyayaAI — Pydantic Schemas for Knowledge Graph
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class GraphNodeItem(BaseModel):
    id: str
    label: str  # "Case", "Act", "Section", "Court", "Judge", "LegalIssue", "Document"
    properties: Dict[str, Any] = Field(default_factory=dict)


class GraphRelationshipItem(BaseModel):
    id: str
    source_id: str
    target_id: str
    type: str  # "CITES", "DISCUSSES", "PART_OF", "DECIDED_BY", "JUDGED_BY", "INVOLVES", "HAS_DOCUMENT"
    properties: Dict[str, Any] = Field(default_factory=dict)


class SubgraphResponse(BaseModel):
    root_node_id: str
    depth: int
    nodes: List[GraphNodeItem]
    relationships: List[GraphRelationshipItem]
    total_nodes: int
    total_relationships: int


class GraphOverviewResponse(BaseModel):
    total_nodes: int
    total_relationships: int
    node_counts_by_label: Dict[str, int]
    relationship_counts_by_type: Dict[str, int]
    active_backend: str = "neo4j"  # or "networkx_local"
    nodes: List[GraphNodeItem] = Field(default_factory=list)
    relationships: List[GraphRelationshipItem] = Field(default_factory=list)


class GraphExpansionRequest(BaseModel):
    case_ids: List[str] = Field(..., description="List of case IDs or names to expand")
    depth: int = Field(1, ge=1, le=2, description="Expansion depth (1 or 2)")
    include_sections: bool = True
    include_cited_cases: bool = True
    include_judges: bool = False


class ExpandedEntityItem(BaseModel):
    node_id: str
    label: str
    name: str
    relationship: str
    connected_to: str
    relevance_score: float = 1.0


class GraphExpansionResponse(BaseModel):
    seed_case_ids: List[str]
    expanded_entities: List[ExpandedEntityItem]
    connected_cases: List[str]
    applicable_sections: List[str]
    applicable_acts: List[str]
    legal_issues: List[str]
