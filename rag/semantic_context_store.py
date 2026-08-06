"""
Vector Store Module

Persistent semantic memory layer for GraphRAG.

Responsible for storing, indexing and retrieving vector embeddings used
during semantic retrieval.

Supports local Milvus deployments during development and cloud deployments
(Zilliz Cloud) in production without changing retrieval interfaces.

Responsibilities:
----------------
• Create vector collections.
• Store embeddings.
• Update embeddings.
• Delete embeddings.
• Batch insertion.
• Batch retrieval.
• Similarity search.
• Metadata filtering.
• Index management.
"""

"""Vector Store Module.

Persistent semantic memory layer for GraphRAG. Responsible for storing, indexing, 
and retrieving vector embeddings used during semantic retrieval. Supports local 
Milvus deployments during development and cloud deployments (Zilliz Cloud) 
in production without changing retrieval interfaces.

Responsibilities:
    - Create and initialize vector collections dynamically.
    - Store, update, and delete discrete vector records.
    - High-throughput batch insertion and retrieval arrays.
    - Top-K similarity searches with boolean metadata filtering.
    - Production index optimization and life-cycle management.
"""

import logging
from typing import List, Dict, Any, Optional
from pymilvus import connections, utility, Collection, FieldSchema, DataType, CollectionSchema

logger = logging.getLogger("GraphRAG.SemanticContextStore")


class SemanticContextStore:
    def __init__(
        self, 
        vector_db: str, 
        host: str, 
        port: int, 
        user: Optional[str] = None, 
        password: Optional[str] = None,
        secure: bool = False
    ):
        """Initializes connection credentials supporting local Milvus and Zilliz Cloud endpoints."""
        self.vector_db = vector_db.lower()
        self.host = host
        self.port = str(port)
        self.user = user
        self.password = password
        self.secure = secure
        self._connected = False
        self._alias = "default"

    def connect(self) -> None:
        """Establishes thread-safe global connection pools with the Milvus cluster."""
        if self._connected:
            return

        try:
            connect_kwargs: Dict[str, Any] = {
                "alias": self._alias,
                "host": self.host,
                "port": self.port
            }
            
            # Dynamically configure secure endpoints if connecting to production Zilliz Cloud instances
            if self.user and self.password:
                connect_kwargs["user"] = self.user
                connect_kwargs["password"] = self.password
                if self.secure or "zilliz" in self.host.lower():
                    connect_kwargs["secure"] = True

            logger.info(f"Establishing persistent connection to Milvus cluster target: {self.host}:{self.port}")
            connections.connect(**connect_kwargs)
            self._connected = True
        except Exception as e:
            logger.critical(f"Failed to securely establish Milvus cluster links: {str(e)}")
            self._connected = False
            raise e

    def create_collection(self, collection_name: str, dimension: int = 1024) -> None:
        """Creates a standardized structured vector schema with auto-id indices."""
        self.connect()
        try:
            if utility.has_collection(collection_name, using=self._alias):
                logger.info(f"Collection '{collection_name}' already registered in target database.")
                return

            # Construct standardized fields matching production schema blueprints
            fields = [
                FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=64, is_primary=True, auto_id=False),
                FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dimension),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=8192),
                FieldSchema(name="metadata", dtype=DataType.JSON)
            ]
            
            schema = CollectionSchema(fields, description="GraphRAG Production Semantic Space Context Records")
            collection = Collection(name=collection_name, schema=schema, using=self._alias)
            
            # Configure default HNSW high-speed retrieval metrics
            index_params = {
                "metric_type": "COSINE",
                "index_type": "HNSW",
                "params": {"M": 16, "efConstruction": 200}
            }
            collection.create_index(field_name="vector", index_params=index_params)
            logger.info(f"Successfully generated new Milvus collection registry: {collection_name}")
        except Exception as e:
            logger.error(f"Failed to cleanly initialize target schema configurations: {str(e)}")
            raise e

    async def query_vector_space(
        self, 
        embedding: List[float], 
        limit: int = 15, 
        collection_name: str = "kb_chunks",
        metadata_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Executes strict mathematical Top-K vector searches over target spaces.
        
        Args:
            embedding: Normalized multi-dimensional dense text array.
            limit: Quantization value regulating returned items buffer.
            collection_name: Name of the vector collection to scan.
            metadata_filter: Optional boolean expression string for metadata filtering (e.g. "metadata['entity_type'] == 'node'").
        """
        self.connect()
        try:
            if not utility.has_collection(collection_name, using=self._alias):
                logger.warning(f"Target memory schema '{collection_name}' not resolved. Returning empty candidates list.")
                return []

            collection = Collection(collection_name, using=self._alias)
            collection.load()  # Ensure records are actively swapped into RAM memory pools

            search_params = {"metric_type": "COSINE", "params": {"ef": 64}}
            
            # Run Milvus core vector-similarity scanner
            results = collection.search(
                data=[embedding],
                anns_field="vector",
                param=search_params,
                limit=limit,
                expr=metadata_filter,
                output_fields=["id", "text", "metadata"],
                using=self._alias
            )

            formatted_candidates = []
            if results:
                for hit in results[0]:
                    formatted_candidates.append({
                        "id": hit.id,
                        "text": hit.entity.get("text"),
                        "metadata": hit.entity.get("metadata"),
                        "score": round(hit.distance, 5)
                    })
                    
            return formatted_candidates
        except Exception as e:
            logger.error(f"Error querying Milvus vector space: {str(e)}")
            return []

    def store_embeddings(self, collection_name: str, id_key: str, embedding: List[float], text: str, metadata: Dict[str, Any]) -> None:
        """Stores a solitary context chunk directly inside active space partitions."""
        self.batch_insertion(collection_name, [id_key], [embedding], [text], [metadata])

    def batch_insertion(self, collection_name: str, ids: List[str], embeddings: List[List[float]], texts: List[str], metadatas: List[Dict[str, Any]]) -> None:
        """Executes scalable column-oriented batch payload transformations into storage layers."""
        self.connect()
        try:
            collection = Collection(collection_name, using=self._alias)
            data = [ids, embeddings, texts, metadatas]
            collection.insert(data)
            collection.flush()  # Guarantee transaction commit logs lock onto persistent disks
            logger.info(f"Successfully committed row batch array size ({len(ids)}) to {collection_name}.")
        except Exception as e:
            logger.error(f"High throughput serialization batch failure: {str(e)}")
            raise e

    def batch_retrieval(self, collection_name: str, ids: List[str]) -> List[Dict[str, Any]]:
        """Queries precise context arrays utilizing explicit identifier tracking keys."""
        self.connect()
        try:
            collection = Collection(collection_name, using=self._alias)
            id_expr = f"id in {str(ids)}"
            results = collection.query(expr=id_expr, output_fields=["id", "text", "metadata"], using=self._alias)
            return results
        except Exception as e:
            logger.error(f"Direct text chunk dictionary lookup validation failure: {str(e)}")
            return []

    def update_embeddings(self, collection_name: str, id_key: str, embedding: List[float], text: str, metadata: Dict[str, Any]) -> None:
        """Updates transactional parameters inside records by processing an overwrite cycle."""
        self.delete_embeddings(collection_name, [id_key])
        self.store_embeddings(collection_name, id_key, embedding, text, metadata)

    def delete_embeddings(self, collection_name: str, ids: List[str]) -> None:
        """Purges targeted vector blocks immediately using boolean term match indices."""
        self.connect()
        try:
            collection = Collection(collection_name, using=self._alias)
            expr = f"id in {str(ids)}"
            collection.delete(expr)
            logger.info(f"Purged target keys {ids} from vector schema records repository.")
        except Exception as e:
            logger.error(f"Failed to clear explicit elements from vector collection index parameters: {str(e)}")
            raise e

    def manage_index(self, collection_name: str, action: str = "create") -> None:
        """Manages collection indexes explicitly to free up RAM or apply updates."""
        self.connect()
        try:
            collection = Collection(collection_name, using=self._alias)
            if action.lower() == "drop":
                collection.drop_index()
                logger.info(f"Dropped all memory index spaces matching: {collection_name}")
            elif action.lower() == "release":
                collection.release()
                logger.info(f"Released collection target '{collection_name}' out of cluster RAM pools.")
        except Exception as e:
            logger.error(f"Index infrastructure state change operation failed: {str(e)}")