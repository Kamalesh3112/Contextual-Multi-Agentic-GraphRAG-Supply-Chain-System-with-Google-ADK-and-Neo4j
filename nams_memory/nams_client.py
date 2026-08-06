"""
============================================================================
Neo4j Agent Memory Service Client

Low-level client responsible for communicating with Neo4j Agent Memory
Service (NAMS).

Provides an abstraction layer between memory modules and the underlying
Neo4j storage.

Responsibilities
----------------
• Establish Neo4j connections.
• Execute memory queries.
• Store memory objects.
• Retrieve memory objects.
• Update memory records.
• Delete obsolete memories.
• Manage transactions.
• Handle connection lifecycle.
"""

"""Neo4j Agent Memory Service Client.

Low-level client responsible for communicating with Neo4j Agent Memory Service (NAMS).
Provides an abstraction layer between high-level cognitive memory modules and the 
underlying Neo4j graph storage and cloud REST endpoints.

Responsibilities:
    - Establish thread-safe Neo4j driver connection pools.
    - Execute transactional graph mutation and query scripts via Cypher.
    - Store memory objects dynamically into relational nodes.
    - Retrieve historical session memory entities.
    - Update transactional memory records via atomic patch sets.
    - Delete obsolete or expired contextual frames.
    - Manage native ACID database transactions with automatic retry blocks.
    - Handle client connection lifecycles and connection teardown.
"""

import logging
from typing import List, Dict, Any, Optional
import httpx
from neo4j import AsyncGraphDatabase, AsyncDriver

logger = logging.getLogger("GraphRAG.NAMSMemory.NAMSClient")


class NAMSClient:
    def __init__(self, app_settings: Any):
        """Initializes endpoints, keys, and driver structures for both local drivers and AMS cloud APIs."""
        self.settings = app_settings
        self.uri = self.settings.NEO4J_URI
        self.user = self.settings.NEO4J_USER
        self.password = self.settings.NEO4J_PASSWORD
        self.ams_url = self.settings.NEO4J_AMS_URL.rstrip("/")
        
        # Internal client session placeholders
        self._driver: Optional[AsyncDriver] = None
        self._http_client: Optional[httpx.AsyncClient] = None

    async def initialize_client(self) -> None:
        """Establishes persistent, high-performance connection pools for Graph drivers and HTTP channels."""
        if not self._driver:
            try:
                logger.info(f"Connecting to underlying Neo4j Database cluster at: {self.uri}")
                # Leverage internal driver configuration mechanics for robust connection lifecycles
                auth_token = (self.user, self.password) if self.password else None
                self._driver = AsyncGraphDatabase.driver(
                    self.uri, 
                    auth=auth_token,
                    max_connection_lifetime=3600,
                    max_connection_pool_size=100
                )
                # Verify backend connection integrity
                await self._driver.verify_connectivity()
            except Exception as conn_err:
                logger.critical(f"Fatal connection exception while mounting Neo4j driver pools: {conn_err}")
                raise conn_err

        if not self._http_client:
            # Mount a persistent connection-reusing client pool targeting AMS API gateways
            headers = {"Content-Type": "application/json"}
            if hasattr(self.settings, "NAMS_MEMORY_API") and self.settings.NAMS_MEMORY_API:
                headers["Authorization"] = f"Bearer {self.settings.NAMS_MEMORY_API}"
            self._http_client = httpx.AsyncClient(timeout=15.0, headers=headers)

    async def execute_graph_query(self, cypher: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Executes an isolated, read-only Cypher query transaction against the graph cluster database."""
        await self.initialize_client()
        params = parameters or {}
        
        try:
            # Run queries inside managed transaction blocks for thread safety
            async with self._driver.session() as session:
                result = await session.run(cypher, parameters_=params)
                records = await result.data()
                return records
        except Exception as query_err:
            logger.error(f"Cypher execution read pathway failure: {query_err} | Target Query: {cypher}")
            return []

    async def execute_graph_mutation(self, cypher: str, parameters: Optional[Dict[str, Any]] = None) -> None:
        """Executes a database write transaction to modify, create, update, or clear graph data layers."""
        await self.initialize_client()
        params = parameters or {}
        
        try:
            async with self._driver.session() as session:
                # Execute mutation atomically as a write transaction block
                await session.execute_write(lambda tx: tx.run(cypher, parameters_=params))
        except Exception as mutation_err:
            logger.error(f"ACID Graph modification mutation transaction rejected by cluster: {mutation_err}")
            raise mutation_err

    async def store_memory_object(self, session_id: str, payload_type: str, memory_body: Dict[str, Any]) -> bool:
        """Invokes the remote Neo4j AMS cloud REST endpoint to store a structured memory object."""
        await self.initialize_client()
        url = f"{self.ams_url}/v1/memory/store"
        
        payload = {
            "session_id": session_id,
            "type": payload_type.lower(),
            "content": memory_body,
            "auto_embed": True  # Instructs AMS to automatically run BAAI/bge-large-en-v1.5 embedding workflows
        }
        
        try:
            response = await self._http_client.post(url, json=payload)
            if response.status_code in (200, 201):
                return True
            logger.error(f"AMS memory storage request rejected by server ({response.status_code}): {response.text}")
        except Exception as net_err:
            logger.error(f"Network transport infrastructure failure on remote AMS storage path: {net_err}")
        return False

    async def retrieve_memory_objects(self, session_id: str, search_query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Queries the Neo4j AMS service layer using semantic vector similarity filters over stored elements."""
        await self.initialize_client()
        url = f"{self.ams_url}/v1/memory/search"
        
        payload = {
            "session_id": session_id,
            "text": search_query,
            "limit": limit
        }
        
        try:
            response = await self._http_client.post(url, json=payload)
            if response.status_code == 200:
                return response.json().get("memories", [])
            logger.error(f"AMS cloud vector search lookup error ({response.status_code}): {response.text}")
        except Exception as search_err:
            logger.error(f"AMS query gateway exception encountered: {search_err}")
        return []

    async def update_memory_record(self, memory_id: str, updated_fields: Dict[str, Any]) -> bool:
        """Updates specific fields of an existing memory object via the AMS cloud interface patch workflow."""
        await self.initialize_client()
        url = f"{self.ams_url}/v1/memory/update/{memory_id}"
        
        try:
            response = await self._http_client.put(url, json={"updates": updated_fields})
            return response.status_code == 200
        except Exception as update_err:
            logger.error(f"Failed to transmit transaction patch set adjustments to target memory item: {update_err}")
            return False

    async def delete_obsolete_memory(self, memory_id: str) -> bool:
        """Purges obsolete or expired memory items permanently from the AMS cloud storage layers."""
        await self.initialize_client()
        url = f"{self.ams_url}/v1/memory/delete/{memory_id}"
        
        try:
            response = await self._http_client.delete(url)
            return response.status_code == 200
        except Exception as delete_err:
            logger.error(f"Failed to securely execute deletion lifecycle payload: {delete_err}")
            return False

    async def close_connections(self) -> None:
        """Gracefully tears down persistent transport pools and flushes open drivers."""
        if self._driver:
            logger.info("Closing active Neo4j driver connection pools.")
            await self._driver.close()
            self._driver = None
            
        if self._http_client:
            logger.info("Terminating open httpx transport clients.")
            await self._http_client.aclose()
            self._http_client = None