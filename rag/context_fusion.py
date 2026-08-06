"""
Hybrid Retriever Module

Central retrieval engine for GraphRAG.

Combines semantic retrieval, graph retrieval and reasoning memory into a
single unified retrieval pipeline.

Responsibilities:
----------------
• Coordinate GraphRAG retrieval.
• Merge graph and vector retrieval.
• Expand graph neighborhoods.
• Retrieve reasoning memory.
• Multi-hop graph traversal.
• Candidate fusion.
• Context aggregation.
"""

"""Hybrid Retriever & Fusion Module.

Central retrieval engine for GraphRAG. Combines semantic retrieval, graph retrieval, 
and reasoning memory into a single unified retrieval pipeline.

Responsibilities:
    - Coordinate GraphRAG retrieval layers.
    - Merge graph and vector similarity retrieval matrices.
    - Expand neighborhood nodes over cross-referenced topologies.
    - Retrieve reasoning history and active memory blocks.
    - Multi-hop graph traversal balancing patterns.
    - Candidate fusion (Reciprocal Rank Fusion - RRF).
    - Structured context aggregation for target agents.
"""

import logging
from typing import Dict, List, Any, Set, Tuple

logger = logging.getLogger("GraphRAG.ContextFusion")


class ContextFusionEngine:
    def __init__(self, rrf_constant: int = 60):
        """Initializes the fusion registry with configurable reciprocal scaling constants."""
        self.k = rrf_constant

    def reciprocal_rank_fusion(
        self, 
        semantic_candidates: List[Dict[str, Any]], 
        graph_candidates: List[Dict[str, Any]],
        top_n: int = 20
    ) -> List[Dict[str, Any]]:
        """Applies Reciprocal Rank Fusion (RRF) to merge and rank cross-platform results.
        
        This normalizes semantic similarity metrics with structural graph path connection scores
        without needing score calibration across disparate search spaces.
        """
        fused_scores: Dict[str, float] = {}
        candidate_registry: Dict[str, Dict[str, Any]] = {}

        # 1. Process Semantic Candidates
        for rank, item in enumerate(semantic_candidates):
            # Fallback identifier generation to guarantee matching footprint bounds
            item_id = str(item.get("id") or hash(item.get("text", "")))
            fused_scores[item_id] = fused_scores.get(item_id, 0.0) + (1.0 / (self.k + rank + 1))
            
            if item_id not in candidate_registry:
                candidate_registry[item_id] = {"source": "semantic", "data": item}

        # 2. Process Graph Topological Candidates
        for rank, node in enumerate(graph_candidates):
            node_id = str(node.get("id") or f"{node.get('source')}-{node.get('target')}")
            fused_scores[node_id] = fused_scores.get(node_id, 0.0) + (1.0 / (self.k + rank + 1))
            
            if node_id not in candidate_registry:
                candidate_registry[node_id] = {"source": "graph", "data": node}

        # 3. Sort, rank, and extract top-N candidate objects
        sorted_candidates = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
        
        fused_results: List[Dict[str, Any]] = []
        for entity_id, score in sorted_candidates[:top_n]:
            base_meta = candidate_registry[entity_id]["data"]
            base_meta["rrf_score"] = round(score, 5)
            fused_results.append(base_meta)

        logger.info(f"RRF Pipeline consolidated {len(fused_scores)} nodes down into top {len(fused_results)} unified items.")
        return fused_results

    def merge_graph_and_vector(
        self, 
        vector_nodes: List[Dict[str, Any]], 
        graph_nodes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Intersects overlapping vector indices and graph entities to resolve entity alignment."""
        aligned_nodes: List[Dict[str, Any]] = []
        graph_entities = {str(node.get("source")).lower() for node in graph_nodes}.union(
            {str(node.get("target")).lower() for node in graph_nodes}
        )

        for v_node in vector_nodes:
            text_content = str(v_node.get("text", "")).lower()
            # Explicitly elevate vector blocks that share terms with the structured graph topology
            matched_entities = [entity for entity in graph_entities if entity in text_content]
            
            if matched_entities:
                v_node["aligned_graph_entities"] = matched_entities
                v_node["score"] = v_node.get("score", 0.5) + 0.15  # Elevate alignment weight
            aligned_nodes.append(v_node)
            
        return sorted(aligned_nodes, key=lambda x: x.get("score", 0), reverse=True)

    def expand_graph_neighborhoods(self, core_subgraph: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Simulates hop neighbor expansions to prevent relational knowledge fragmentation."""
        expanded_subgraph = list(core_subgraph)
        visited_nodes = {str(edge.get("source")) for edge in core_subgraph}.union(
            {str(edge.get("target")) for edge in core_subgraph}
        )
        
        # Proactively map out inferred multi-hop bridge pathways for the context layer
        for node in visited_nodes:
            if "platform" in node.lower() and "mcp" not in visited_nodes:
                expanded_subgraph.append({
                    "source": node,
                    "relationship": "EXPOSES_VIA",
                    "target": "FastMCP_Protocol_Layer",
                    "inferred": True
                })
        return expanded_subgraph

    def synthesize_to_prompt_format(self, aggregated_packet: Dict[str, List[Any]]) -> str:
        """Aggregates multi-source payloads into clean, markdown-delimited prompt structures.
        
        Args:
            aggregated_packet: Dictionary containing lists of 'semantic', 'graph', and 'memory' objects.
            
        Returns:
            A clean, markdown-delimited context block ready for consumption by LLM agents.
        """
        manifest = []
        
        # 1. Unstructured High-Density Vector Blocks
        manifest.append("### Unstructured Semantic Documents")
        semantic_items = aggregated_packet.get("semantic", [])
        if semantic_items:
            for doc in semantic_items:
                score_str = f" [Score: {doc.get('score')}]" if "score" in doc else ""
                manifest.append(f"- ID: {doc.get('id', 'N/A')}{score_str} -> {doc.get('text')}")
        else:
            manifest.append("- No semantic vector documents retrieved.")

        # 2. Structured Graph Topology Connections
        manifest.append("\n### Structured Knowledge Graph Topology")
        graph_items = aggregated_packet.get("graph", [])
        if graph_items:
            for edge in graph_items:
                inf_tag = " [Inferred Hop]" if edge.get("inferred") else ""
                manifest.append(
                    f"- ({edge.get('source')}) --[{edge.get('relationship')}]--> ({edge.get('target')}){inf_tag}"
                )
        else:
            manifest.append("- No corresponding knowledge graph paths discovered.")

        # 3. Short/Long Term Agent Memory Systems & Reasoning History Traces
        manifest.append("\n### Active Reasoning Memories & Session Traces")
        memory_items = aggregated_packet.get("memory", [])
        if memory_items:
            for idx, trace in enumerate(memory_items):
                if isinstance(trace, dict):
                    manifest.append(f"- Trace {idx}: [{trace.get('type', 'Step')}] -> {trace.get('text')}")
                else:
                    manifest.append(f"- History {idx}: {trace}")
        else:
            manifest.append("- No preceding active execution traces found in session.")

        return "\n".join(manifest)