"""
NyayaAI — Legal Knowledge Graph Builder & Manager
Builds, queries, and expands the legal relationship network across:
Nodes: Case, Act, Section, Court, Judge, LegalIssue, Document
Edges: CITES, DISCUSSES, PART_OF, DECIDED_BY, JUDGED_BY, INVOLVES, HAS_DOCUMENT
Operates on Neo4j with a zero-downtime NetworkX + JSON local engine fallback.
"""

import os
import json
import networkx as nx
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from loguru import logger

from app.config import settings
from app.models.graph import (
    GraphNodeItem,
    GraphRelationshipItem,
    SubgraphResponse,
    GraphOverviewResponse,
    GraphExpansionResponse,
    ExpandedEntityItem,
)


class LegalGraphManager:
    """Manages the Indian Legal Knowledge Graph across Neo4j and Local NetworkX engines."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(LegalGraphManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.use_neo4j = False
        self.neo4j_driver = None
        self.graph = nx.DiGraph()
        self.graph_dir = Path(settings.data_processed_dir).parent / "knowledge_graph"
        self.graph_dir.mkdir(parents=True, exist_ok=True)

        self._init_neo4j()
        self.load_or_rebuild()
        self._initialized = True

    def _init_neo4j(self):
        """Attempts connection to Neo4j graph database."""
        try:
            from neo4j import GraphDatabase
            driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_username, settings.neo4j_password),
                connection_timeout=2.0,
            )
            # Test connectivity
            with driver.session() as session:
                session.run("RETURN 1 AS test")
            self.neo4j_driver = driver
            self.use_neo4j = True
            logger.info(f"✔ Successfully connected to Neo4j at {settings.neo4j_uri}")
        except Exception as e:
            logger.warning(
                f"Neo4j unavailable at {settings.neo4j_uri} ({e}). Using NetworkX graph fallback."
            )
            self.use_neo4j = False
            self.neo4j_driver = None

    def load_or_rebuild(self):
        """Loads graph from local JSON cache or builds from data directory."""
        nodes_file = self.graph_dir / "graph_nodes.json"
        edges_file = self.graph_dir / "graph_edges.json"

        if nodes_file.exists() and edges_file.exists():
            try:
                with open(nodes_file, "r", encoding="utf-8") as nf:
                    nodes_data = json.load(nf)
                with open(edges_file, "r", encoding="utf-8") as ef:
                    edges_data = json.load(ef)

                self.graph = nx.DiGraph()
                for n in nodes_data:
                    self.graph.add_node(n["id"], label=n["label"], **n.get("properties", {}))
                for e in edges_data:
                    self.graph.add_edge(
                        e["source_id"],
                        e["target_id"],
                        id=e.get("id", f"{e['source_id']}_{e['type']}_{e['target_id']}"),
                        type=e["type"],
                        **e.get("properties", {}),
                    )
                logger.info(
                    f"✔ Loaded local Knowledge Graph: {self.graph.number_of_nodes()} nodes, "
                    f"{self.graph.number_of_edges()} relationships."
                )
                return
            except Exception as e:
                logger.warning(f"Error loading graph cache: {e}. Rebuilding...")

        self.build_graph_from_metadata()

    def build_graph_from_metadata(self) -> Tuple[int, int]:
        """
        Scans data/metadata/ and data/raw/acts/ to construct the complete legal knowledge graph.
        """
        self.graph = nx.DiGraph()
        metadata_dir = Path(settings.data_metadata_dir)
        acts_raw_dir = Path(settings.data_raw_dir) / "acts"

        # 1. Ingest Statutory Acts and Sections
        if acts_raw_dir.exists():
            for act_file in acts_raw_dir.glob("*.json"):
                try:
                    with open(act_file, "r", encoding="utf-8") as af:
                        act_data = json.load(af)

                    act_id = act_data.get("act_id") or f"ACT_{act_data.get('document_id', '')}"
                    act_name = act_data.get("act_name", act_file.stem)
                    year = act_data.get("year", 2023)
                    domain = act_data.get("legal_domain", "General Law")

                    self.graph.add_node(
                        act_id,
                        label="Act",
                        name=act_name,
                        year=year,
                        legal_domain=domain,
                        source_url=act_data.get("source_url", ""),
                    )

                    for sec in act_data.get("sections", []):
                        sec_num = str(sec.get("section_number", "")).strip()
                        if not sec_num:
                            continue
                        sec_id = f"{act_id}_SEC_{sec_num}"
                        self.graph.add_node(
                            sec_id,
                            label="Section",
                            section_number=sec_num,
                            title=sec.get("section_title", ""),
                            text=sec.get("section_text", ""),
                            act_name=act_name,
                        )
                        self.graph.add_edge(sec_id, act_id, type="PART_OF")

                except Exception as e:
                    logger.error(f"Error reading Act file {act_file.name}: {e}")

        # 2. Ingest Cases and Judicial Metadata
        if metadata_dir.exists():
            for meta_file in metadata_dir.glob("*_metadata.json"):
                try:
                    with open(meta_file, "r", encoding="utf-8") as mf:
                        meta = json.load(mf)

                    doc_type = meta.get("document_type", "judgment")
                    if doc_type == "act":
                        continue

                    case_id = meta.get("case_id", meta.get("document_id", ""))
                    case_name = meta.get("case_name", "Unknown Case")
                    court_name = meta.get("court", "Supreme Court of India")
                    domain = meta.get("legal_domain", "Criminal Law")

                    # Add Case Node
                    self.graph.add_node(
                        case_id,
                        label="Case",
                        name=case_name,
                        court=court_name,
                        judgment_date=meta.get("judgment_date", ""),
                        case_number=meta.get("case_number", ""),
                        legal_domain=domain,
                        source_url=meta.get("source_url", ""),
                    )

                    # Add Document Node
                    doc_id = meta.get("document_id", "")
                    if doc_id:
                        self.graph.add_node(
                            doc_id,
                            label="Document",
                            name=f"Document {doc_id}",
                            sha256=meta.get("sha256", ""),
                            total_pages=meta.get("total_pages", 1),
                        )
                        self.graph.add_edge(case_id, doc_id, type="HAS_DOCUMENT")

                    # Add Court Node & Edge
                    court_id = f"COURT_{court_name.upper().replace(' ', '_')}"
                    self.graph.add_node(court_id, label="Court", name=court_name)
                    self.graph.add_edge(case_id, court_id, type="DECIDED_BY")

                    # Add Judge Nodes & Edges
                    for judge_name in meta.get("judges", []):
                        judge_id = f"JUDGE_{judge_name.upper().replace(' ', '_')}"
                        self.graph.add_node(judge_id, label="Judge", name=judge_name)
                        self.graph.add_edge(case_id, judge_id, type="JUDGED_BY")

                    # Add Legal Issue Nodes & Edges
                    for issue in meta.get("legal_issues", []):
                        issue_id = f"ISSUE_{issue.upper().replace(' ', '_')}"
                        self.graph.add_node(issue_id, label="LegalIssue", name=issue)
                        self.graph.add_edge(case_id, issue_id, type="INVOLVES")

                    # Add Discussed Sections Edges
                    for sec_num in meta.get("sections", []):
                        # Link to matching section nodes if present, else create generic Section node
                        matched_sec_nodes = [
                            n for n, d in self.graph.nodes(data=True)
                            if d.get("label") == "Section" and d.get("section_number") == sec_num
                        ]
                        if matched_sec_nodes:
                            for target_sec in matched_sec_nodes:
                                self.graph.add_edge(case_id, target_sec, type="DISCUSSES", section_number=sec_num)
                        else:
                            sec_node_id = f"SEC_{sec_num}"
                            if sec_node_id not in self.graph:
                                self.graph.add_node(sec_node_id, label="Section", section_number=sec_num, title=f"Section {sec_num}")
                            self.graph.add_edge(case_id, sec_node_id, type="DISCUSSES", section_number=sec_num)

                    # Add Citations (Case -[:CITES]-> Target Case)
                    for cit in meta.get("citations", []):
                        raw_cit = cit.get("normalized_citation", cit.get("raw_citation", ""))
                        if raw_cit:
                            # Create placeholder case/citation node if target is outside corpus
                            target_id = f"CASE_CIT_{raw_cit.upper().replace(' ', '_')}"
                            if target_id not in self.graph:
                                self.graph.add_node(
                                    target_id,
                                    label="Case",
                                    name=raw_cit,
                                    citation=raw_cit,
                                    is_external=True,
                                )
                            self.graph.add_edge(
                                case_id,
                                target_id,
                                type="CITES",
                                citation_text=raw_cit,
                                page=cit.get("page_number", 1),
                            )

                except Exception as e:
                    logger.error(f"Error processing {meta_file.name} for graph: {e}")

        # Save to local JSON cache
        self._save_to_json_cache()

        # If Neo4j is active, sync to Neo4j
        if self.use_neo4j and self.neo4j_driver:
            self._sync_to_neo4j()

        logger.info(
            f"✔ Knowledge Graph built: {self.graph.number_of_nodes()} nodes, "
            f"{self.graph.number_of_edges()} relationships."
        )
        return self.graph.number_of_nodes(), self.graph.number_of_edges()

    def _save_to_json_cache(self):
        """Serializes current NetworkX graph into json artifacts."""
        nodes_out = []
        for n, d in self.graph.nodes(data=True):
            label = d.get("label", "Entity")
            props = {k: v for k, v in d.items() if k != "label"}
            nodes_out.append({"id": n, "label": label, "properties": props})

        edges_out = []
        for u, v, d in self.graph.edges(data=True):
            edge_type = d.get("type", "RELATED_TO")
            props = {k: v for k, v in d.items() if k not in ["type", "id"]}
            edges_out.append({
                "id": d.get("id", f"{u}_{edge_type}_{v}"),
                "source_id": u,
                "target_id": v,
                "type": edge_type,
                "properties": props,
            })

        with open(self.graph_dir / "graph_nodes.json", "w", encoding="utf-8") as nf:
            json.dump(nodes_out, nf, indent=2, ensure_ascii=False)
        with open(self.graph_dir / "graph_edges.json", "w", encoding="utf-8") as ef:
            json.dump(edges_out, ef, indent=2, ensure_ascii=False)

    def _sync_to_neo4j(self):
        """Syncs NetworkX nodes and edges to Neo4j instance."""
        try:
            with self.neo4j_driver.session() as session:
                # Clear existing
                session.run("MATCH (n) DETACH DELETE n")
                # Create constraints
                session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (c:Case) REQUIRE c.id IS UNIQUE")
                session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (a:Act) REQUIRE a.id IS UNIQUE")
                session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (s:Section) REQUIRE s.id IS UNIQUE")

                # Upsert nodes
                for n, d in self.graph.nodes(data=True):
                    label = d.get("label", "Entity")
                    props = {k: v for k, v in d.items() if k != "label"}
                    props["id"] = n
                    query = f"MERGE (node:{label} {{id: $id}}) SET node += $props"
                    session.run(query, id=n, props=props)

                # Upsert edges
                for u, v, d in self.graph.edges(data=True):
                    rel_type = d.get("type", "RELATED_TO")
                    props = {k: v for k, v in d.items() if k not in ["type", "id"]}
                    query = (
                        f"MATCH (a {{id: $u}}), (b {{id: $v}}) "
                        f"MERGE (a)-[r:{rel_type}]->(b) "
                        f"SET r += $props"
                    )
                    session.run(query, u=u, v=v, props=props)
            logger.info("✔ Synced Knowledge Graph to Neo4j.")
        except Exception as e:
            logger.error(f"Failed to sync to Neo4j: {e}")

    def get_case_subgraph(self, case_id: str, depth: int = 1) -> SubgraphResponse:
        """Extracts the neighborhood subgraph for a given Case up to depth 2."""
        # Find matching node (either exact ID or fuzzy matching name)
        target_node = None
        if case_id in self.graph:
            target_node = case_id
        else:
            case_id_lower = case_id.lower()
            for n, d in self.graph.nodes(data=True):
                if d.get("name", "").lower() == case_id_lower or case_id_lower in n.lower():
                    target_node = n
                    break

        if not target_node:
            return SubgraphResponse(
                root_node_id=case_id,
                depth=depth,
                nodes=[],
                relationships=[],
                total_nodes=0,
                total_relationships=0,
            )

        # BFS neighborhood traversal
        visited_nodes: Set[str] = {target_node}
        current_frontier = {target_node}

        for _ in range(depth):
            next_frontier = set()
            for node in current_frontier:
                neighbors = set(self.graph.successors(node)) | set(self.graph.predecessors(node))
                for nbr in neighbors:
                    if nbr not in visited_nodes:
                        visited_nodes.add(nbr)
                        next_frontier.add(nbr)
            current_frontier = next_frontier

        subgraph_nodes = []
        for n in visited_nodes:
            d = self.graph.nodes[n]
            subgraph_nodes.append(
                GraphNodeItem(
                    id=n,
                    label=d.get("label", "Entity"),
                    properties={k: v for k, v in d.items() if k != "label"},
                )
            )

        subgraph_edges = []
        for u in visited_nodes:
            for v in visited_nodes:
                if self.graph.has_edge(u, v):
                    d = self.graph.get_edge_data(u, v)
                    subgraph_edges.append(
                        GraphRelationshipItem(
                            id=d.get("id", f"{u}_{d.get('type')}_{v}"),
                            source_id=u,
                            target_id=v,
                            type=d.get("type", "RELATED_TO"),
                            properties={k: v for k, v in d.items() if k not in ["type", "id"]},
                        )
                    )

        return SubgraphResponse(
            root_node_id=target_node,
            depth=depth,
            nodes=subgraph_nodes,
            relationships=subgraph_edges,
            total_nodes=len(subgraph_nodes),
            total_relationships=len(subgraph_edges),
        )

    def expand_candidates(self, seed_case_ids: List[str], depth: int = 1) -> GraphExpansionResponse:
        """
        Expands a set of seed case IDs to discover connected precedents,
        statutory sections, acts, and shared legal issues.
        """
        connected_cases: Set[str] = set()
        applicable_sections: Set[str] = set()
        applicable_acts: Set[str] = set()
        legal_issues: Set[str] = set()
        expanded_entities: List[ExpandedEntityItem] = []

        for cid in seed_case_ids:
            subgraph = self.get_case_subgraph(cid, depth=depth)
            for node in subgraph.nodes:
                if node.id == cid:
                    continue
                node_name = node.properties.get("name", node.id)

                if node.label == "Case":
                    connected_cases.add(node_name)
                elif node.label == "Section":
                    sec_num = node.properties.get("section_number", node_name)
                    applicable_sections.add(str(sec_num))
                elif node.label == "Act":
                    applicable_acts.add(node_name)
                elif node.label == "LegalIssue":
                    legal_issues.add(node_name)

                expanded_entities.append(
                    ExpandedEntityItem(
                        node_id=node.id,
                        label=node.label,
                        name=node_name,
                        relationship="CONNECTED_TO",
                        connected_to=cid,
                        relevance_score=1.0 if depth == 1 else 0.7,
                    )
                )

        return GraphExpansionResponse(
            seed_case_ids=seed_case_ids,
            expanded_entities=expanded_entities,
            connected_cases=list(connected_cases),
            applicable_sections=list(applicable_sections),
            applicable_acts=list(applicable_acts),
            legal_issues=list(legal_issues),
        )

    def get_overview(self) -> GraphOverviewResponse:
        """Returns high-level graph node and relationship statistics."""
        node_counts: Dict[str, int] = {}
        for _, d in self.graph.nodes(data=True):
            lbl = d.get("label", "Unknown")
            node_counts[lbl] = node_counts.get(lbl, 0) + 1

        rel_counts: Dict[str, int] = {}
        for _, _, d in self.graph.edges(data=True):
            rel_type = d.get("type", "UNKNOWN")
            rel_counts[rel_type] = rel_counts.get(rel_type, 0) + 1

        backend = "neo4j" if self.use_neo4j else "networkx_local"

        nodes_list = []
        for n, d in list(self.graph.nodes(data=True))[:120]:
            nodes_list.append(
                GraphNodeItem(
                    id=n,
                    label=d.get("label", "Entity"),
                    properties={k: v for k, v in d.items() if k != "label"},
                )
            )

        visible_ids = {item.id for item in nodes_list}
        edges_list = []
        for u, v, d in self.graph.edges(data=True):
            if u in visible_ids and v in visible_ids:
                edges_list.append(
                    GraphRelationshipItem(
                        id=d.get("id", f"{u}_{d.get('type', 'REL')}_{v}"),
                        source_id=u,
                        target_id=v,
                        type=d.get("type", "RELATED_TO"),
                        properties={k: v_val for k, v_val in d.items() if k not in ("type", "id")},
                    )
                )

        return GraphOverviewResponse(
            total_nodes=self.graph.number_of_nodes(),
            total_relationships=self.graph.number_of_edges(),
            node_counts_by_label=node_counts,
            relationship_counts_by_type=rel_counts,
            active_backend=backend,
            nodes=nodes_list,
            relationships=edges_list,
        )
