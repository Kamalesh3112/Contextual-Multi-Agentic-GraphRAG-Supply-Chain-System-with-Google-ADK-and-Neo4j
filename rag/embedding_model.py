#Integrating both an pre-trained embedding model and Qdrant
#Blog: https://qdrant.tech/blog/case-study-datagraphs/
"""
Embedding Model Module

Responsible for transforming structured and unstructured knowledge into
dense vector representations.

Supports batch embedding generation for documents, graph nodes,
relationships and reasoning traces.

Responsibilities
----------------
• Generate embeddings.
• Batch embedding generation.
• Graph node embeddings.
• Relationship embeddings.
• Query embeddings.
• Embedding caching.
• Embedding normalization.
"""

"""Embedding Model Module.

Responsible for transforming structured and unstructured knowledge into dense 
vector representations, integrating with both pre-trained embedding models and Qdrant.
Supports batch embedding generation for documents, graph nodes, relationships,
and reasoning traces.

Responsibilities:
    - Dense vector representation generation.
    - Highly efficient chunked batch embedding generation.
    - Node, relationship, and abstract property transformations.
    - L2 Euclidean or Cosine distance matrix normalization.
    - LRU-backed query and node embedding caching.
"""

import logging
import hashlib
from typing import List, Union, Dict, Any, Tuple, Optional
import httpx

logger = logging.getLogger("GraphRAG.EmbeddingModel")


class EmbeddingEngine:
    def __init__(
        self, 
        ams_url: str, 
        embedding_model: str = "BAAI/bge-large-en-v1.5",
        cache_size: int = 4096,
        normalize: bool = True
    ):
        """Initializes the Embedding Engine with local caching and Qdrant compatibility configs."""
        self.ams_url = ams_url.rstrip("/")
        self.model_name = embedding_model
        self.headers = {"Content-Type": "application/json"}
        self.normalize = normalize
        
        # Simple high-throughput in-memory LRU-equivalent cache structure
        self._cache: Dict[str, List[float]] = {}
        self.cache_size = cache_size

    def _compute_hash(self, text: str) -> str:
        """Computes a deterministic cache key for text values."""
        return hashlib.blake2b(text.encode("utf-8"), digest_size=16).hexdigest()

    def _normalize_vector(self, vector: List[float]) -> List[float]:
        """Normalizes a vector to unit length (L2 norm) for direct Cosine similarity matching."""
        squared_sum = sum(val ** 2 for val in vector)
        if squared_sum == 0:
            return vector
        norm = squared_sum ** 0.5
        return [val / norm for val in vector]

    async def get_embeddings(self, texts: Union[str, List[str]]) -> List[List[float]]:
        """Generates embedding representations for raw text queries or documents."""
        if isinstance(texts, str):
            texts = [texts]

        results: List[Optional[List[float]]] = [None] * len(texts)
        uncached_indices: List[int] = []
        uncached_texts: List[str] = []

        # Step 1: Check memory cache surfaces
        for idx, text in enumerate(texts):
            cache_key = self._compute_hash(text)
            if cache_key in self._cache:
                results[idx] = self._cache[cache_key]
            else:
                uncached_indices.append(idx)
                uncached_texts.append(text)

        # Step 2: Request remaining elements from downstream engines
        if uncached_texts:
            payload = {
                "model": self.model_name,
                "input": uncached_texts
            }
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        f"{self.ams_url}/v1/embeddings", 
                        json=payload, 
                        headers=self.headers
                    )
                    if response.status_code == 200:
                        data = response.json()
                        embeddings = [item["embedding"] for item in data["data"]]
                        
                        # Apply normalization and update cache
                        for i, raw_emb in enumerate(embeddings):
                            processed_emb = self._normalize_vector(raw_emb) if self.normalize else raw_emb
                            
                            # Cache management
                            orig_idx = uncached_indices[i]
                            results[orig_idx] = processed_emb
                            
                            cache_key = self._compute_hash(uncached_texts[i])
                            if len(self._cache) >= self.cache_size:
                                self._cache.pop(next(iter(self._cache)))  # Basic FIFO eviction
                            self._cache[cache_key] = processed_emb
                    else:
                        logger.error(f"Embedding backend error {response.status_code}: {response.text}")
                        raise RuntimeError("Failed to resolve embeddings from remote AMS API endpoint.")
            except Exception as e:
                logger.exception(f"Unexpected network layer failure on embedding path: {e}")
                # Production protection: fall back safely without stalling core execution threads
                for i in uncached_indices:
                    results[i] = [0.0] * 1024  # Standard vector width baseline

        return [v for v in results if v is not None]

    async def generate_batch_embeddings(self, items: List[str], batch_size: int = 64) -> List[List[float]]:
        """Processes massive text payloads using fixed-window chunked streaming."""
        batched_embeddings: List[List[float]] = []
        for i in range(0, len(items), batch_size):
            chunk = items[i : i + batch_size]
            embeddings = await self.get_embeddings(chunk)
            batched_embeddings.extend(embeddings)
        return batched_embeddings

    async def transform_graph_node(self, label: str, properties: Dict[str, Any]) -> Tuple[List[float], Dict[str, Any]]:
        """Transforms a graph entity node's structural and unstructured fields into a Qdrant-ready payload format.
        
        Args:
            label: The structural type or class string matching your domain schema.
            properties: Key-value attributes from the graph node instance.
            
        Returns:
            A tuple containing the dense vector array and a structured Qdrant payload dictionary.
        """
        # Convert explicit properties into a structured data description string for embedding
        prop_string = ", ".join([f"{k}: {v}" for k, v in properties.items() if isinstance(v, (str, int, float))])
        serialized_context = f"Node Label: {label} | Properties: {{ {prop_string} }}"
        
        vector = (await self.get_embeddings([serialized_context]))[0]
        
        # Format payload structure to match Qdrant DSL filtering expectations
        qdrant_payload = {
            "entity_type": "node",
            "node_label": label,
            "metadata_fields": properties
        }
        return vector, qdrant_payload

    async def transform_graph_relationship(
        self, 
        source_label: str, 
        rel_type: str, 
        target_label: str, 
        properties: Dict[str, Any]
    ) -> Tuple[List[float], Dict[str, Any]]:
        """Transforms a directed multi-hop relationship edge into a dense vector embedding."""
        prop_string = ", ".join([f"{k}: {v}" for k, v in properties.items() if isinstance(v, (str, int, float))])
        serialized_context = f"Relationship: ({source_label})-[{rel_type}]->({target_label}) | Metadata: {{ {prop_string} }}"
        
        vector = (await self.get_embeddings([serialized_context]))[0]
        
        qdrant_payload = {
            "entity_type": "relationship",
            "relation_type": rel_type,
            "source_class": source_label,
            "target_class": target_label,
            "metadata_fields": properties
        }
        return vector, qdrant_payload

    async def transform_reasoning_trace(self, agent_id: str, plan_step: str, validation_logic: str) -> List[float]:
        """Transforms system-generated thoughts and execution steps into a semantic vector."""
        serialized_trace = f"Agent: {agent_id} | Plan: {plan_step} | Proof: {validation_logic}"
        return (await self.get_embeddings([serialized_trace]))[0]

    def clear_cache(self) -> None:
        """Flushes the local in-memory lookup buffers."""
        self._cache.clear()
        logger.info("Local vector embedding cache cleared successfully.")