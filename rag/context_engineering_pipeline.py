#Context Engineering Foundation for GraphRAG workflows and orchestration
"""
Context Builder Module

Final knowledge aggregation layer for GraphRAG.

Responsible for constructing a unified execution context from multiple
knowledge sources before passing information to the reasoning agents.

Responsibilities:
----------------
• Merge graph context.
• Merge semantic retrieval.
• Merge memory retrieval.
• Merge ontology enrichment.
• Remove duplicate information.
• Compress retrieval context.
• Prepare LLM-ready context.
"""

"""Context Engineering Foundation for GraphRAG workflows and orchestration.

Context Builder Module: The final knowledge aggregation layer for GraphRAG.
Responsible for constructing a unified execution context from multiple knowledge
sources before passing information to the reasoning agents.

Responsibilities:
    - Merge graph topological context structure.
    - Merge semantic vector similarity results.
    - Merge long-term agent memory retrieval streams.
    - Merge ontology enrichment and entity descriptions.
    - Remove duplicate information nodes across overlapping streams.
    - Compress retrieval context to fit target execution token frames.
    - Prepare LLM-ready structured prompt payloads.
"""

import logging
from typing import Dict, List, Any, Set, Optional
from .embedding_model import EmbeddingEngine
from .semantic_context_store import SemanticContextStore
from .context_retreiver import ContextRetriever
from .context_fusion import ContextFusionEngine
from .context_optimizer import ContextOptimizer

logger = logging.getLogger("GraphRAG.ContextEngineeringPipeline")


class ContextEngineeringPipeline:
    def __init__(self, app_settings: Any):
        """Initializes the final context orchestration foundation with all multi-source systems."""
        self.settings = app_settings
        
        # 1. Initialize Core Embedding Machinery
        self.embedding_engine = EmbeddingEngine(
            ams_url=self.settings.NEO4J_AMS_URL,
            embedding_model=self.settings.EMBEDDING_MODEL
        )
        
        # 2. Initialize Semantic Memory Storage Systems
        self.semantic_store = SemanticContextStore(
            vector_db=self.settings.VECTOR_DB,
            host=self.settings.MILVUS_HOST,
            port=self.settings.MILVUS_PORT,
            user=self.settings.MILVUS_USER,
            password=self.settings.MILVUS_PASSWORD
        )
        self.semantic_store.connect()
        
        # 3. Initialize High-Performance Multi-Source Retriever
        self.retriever = ContextRetriever(
            semantic_store=self.semantic_store,
            ams_url=self.settings.NEO4J_AMS_URL,
            neo4j_uri=self.settings.NEO4J_URI,
            auth=(self.settings.NEO4J_USER, self.settings.NEO4J_PASSWORD)
        )
        
        # 4. Core Synthesis, Fusion, and Optimization Foundations
        self.fusion_engine = ContextFusionEngine()
        self.optimizer = ContextOptimizer(
            provider=self.settings.LLM_PROVIDER,
            primary_model=self.settings.LLM_MODEL,
            fallback_model=self.settings.FALLBACK_MODEL,
            base_url=self.settings.OPENROUTER_BASE_URL,
            api_key=self.settings.OPENROUTER_API_KEY
        )

    def _deduplicate_knowledge_sources(self, raw_packet: Dict[str, List[Any]]) -> Dict[str, List[Any]]:
        """Removes overlapping or exact duplicate entity matches across disparate data streams."""
        seen_semantic_ids: Set[str] = set()
        unique_semantic: List[Dict[str, Any]] = []
        
        # Deduplicate semantic unstructured nodes
        for item in raw_packet.get("semantic", []):
            item_id = str(item.get("id", "")) or str(item.get("text", ""))
            if item_id not in seen_semantic_ids:
                seen_semantic_ids.add(item_id)
                unique_semantic.append(item)
                
        # Deduplicate Graph Topology Edges
        seen_edges: Set[str] = set()
        unique_graph: List[Dict[str, Any]] = []
        for rel in raw_packet.get("graph", []):
            edge_key = f"{rel.get('source')}-{rel.get('relationship')}-{rel.get('target')}"
            if edge_key not in seen_edges:
                seen_edges.add(edge_key)
                unique_graph.append(rel)
                
        # Deduplicate Memory streams
        seen_memories: Set[str] = set()
        unique_memory: List[Any] = []
        for mem in raw_packet.get("memory", []):
            mem_text = str(mem) if not isinstance(mem, dict) else str(mem.get("text", ""))
            if mem_text not in seen_memories:
                seen_memories.add(mem_text)
                unique_memory.append(mem)

        return {
            "semantic": unique_semantic,
            "graph": unique_graph,
            "memory": unique_memory
        }

    def _inject_ontology_enrichment(self, graph_context: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enriches raw graph edges with structural schema definitions and conceptual descriptions.
        
        Injecting the domain ontology empowers the downstream LLM agent to accurately reason across
        complex graph paths using explicit domain rule spaces.
        """
        enriched_graph = []
        for edge in graph_context:
            source = edge.get("source", "Unknown")
            rel = edge.get("relationship", "CONNECTED_TO")
            target = edge.get("target", "Unknown")
            
            # Simple functional ontology map parsing rules
            edge["source_definition"] = f"Domain class entity tracking instantiations of type {source}."
            edge["target_definition"] = f"Target operational component defining systemic {target} node space."
            edge["relationship_rule"] = f"Valid directional semantic association defined as: {rel}."
            
            enriched_graph.append(edge)
            
        logger.info(f"Enriched {len(enriched_graph)} graph network nodes with domain ontology guidelines.")
        return enriched_graph

    def _compress_context_payload(self, structured_text: str, max_chars: int = 24000) -> str:
        """Compresses context strings to protect execution window safety profiles."""
        if len(structured_text) <= max_chars:
            return structured_text
            
        logger.warning(f"Context payload size ({len(structured_text)} chars) exceeds maximum safety. Compressing runtime context.")
        # Production string slicing optimization structure
        lines = structured_text.split("\n")
        compressed_lines = []
        current_len = 0
        
        for line in lines:
            if current_len + len(line) + 1 > max_chars:
                compressed_lines.append("[... Context Trucation Rule Invoked: Remaining details omitted due to token boundaries ...]")
                break
            compressed_lines.append(line)
            current_len += len(line) + 1
            
        return "\n".join(compressed_lines)

    async def execute_pipeline(self, user_query: str, session_id: str) -> Dict[str, Any]:
        """Runs the context building execution workflow to construct an LLM-ready context layer.
        
        Args:
            user_query: Raw natural language prompt sent by the routing agent.
            session_id: Unique reference tracking ongoing multi-agent execution spaces.
            
        Returns:
            A unified payload dict containing the optimized system instructions and final response answers.
        """
        logger.info(f"Ingesting user query for GraphRAG context architecture building: '{user_query}'")
        
        # Step 1: Resolve vectors from the embedding model layer
        query_vectors = await self.embedding_engine.get_embeddings(user_query)
        target_vector = query_vectors[0] if query_vectors else [0.0] * 1024
        
        # Step 2: Retrieve multi-source knowledge vectors and subgraphs in parallel
        raw_retrieved_packet = await self.retriever.fetch_all_sources(
            text_query=user_query,
            vector_query=target_vector,
            session_id=session_id
        )
        
        # Step 3: Remove duplicate items crossing pipeline boundaries
        deduplicated_packet = self._deduplicate_knowledge_sources(raw_retrieved_packet)
        
        # Step 4: Inject ontology definition rules into graph arrays
        deduplicated_packet["graph"] = self._inject_ontology_enrichment(deduplicated_packet["graph"])
        
        # Step 5: Fuse multi-modal knowledge records into a unified representation
        unified_context_block = self.fusion_engine.synthesize_to_prompt_format(deduplicated_packet)
        
        # Step 6: Compress text down under safety constraints
        final_compressed_context = self._compress_context_payload(unified_context_block)
        
        # Step 7: Formulate systemic instructions anchoring reasoning pathways
        system_instructions = (
            "You are a context-grounded Knowledge Intelligence Engine running within a multi-agent framework.\n"
            "Analyze the provided merged context blocks carefully. Synthesis must rely exclusively on these inputs.\n"
            "Do not introduce external assumptions. Always cite sources back to their origin tokens."
        )
        
        user_payload = (
            f"=== AGGREGATED RETRIEVAL CONTEXT ===\n"
            f"{final_compressed_context}\n\n"
            f"=== TARGET PROMPT ===\n"
            f"Query: {user_query}"
        )
        
        # Step 8: Fire generation payload via OpenRouter with robust fallback orchestration
        final_answer = await self.optimizer.call_llm_with_fallback(
            system_prompt=system_instructions,
            user_content=user_payload
        )
        
        return {
            "query": user_query,
            "context_block": final_compressed_context,
            "response": final_answer,
            "pipeline_metadata": {
                "embedding_model": self.settings.EMBEDDING_MODEL,
                "primary_llm": self.settings.LLM_MODEL,
                "fallback_llm": self.settings.FALLBACK_MODEL,
                "vector_db_target": self.settings.VECTOR_DB
            }
        }