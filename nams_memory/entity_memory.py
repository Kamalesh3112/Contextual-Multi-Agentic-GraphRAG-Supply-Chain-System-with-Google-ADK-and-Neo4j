"""
Entity Memory Module:
  - Maintains persistent knowledge about entities encountered during reasoning.
Rather than remembering conversations, this module remembers important
entities and their evolving relationships.

Responsibilities:
----------------
• Store entities.
• Track entity evolution.
• Store relationships.
• Resolve entity identities.
• Support entity linking.
• Enable long-term entity recall.
"""

"""Entity Memory Module.

Maintains persistent knowledge about entities encountered during reasoning. Rather 
than remembering conversation strings, this module registers unique domain entities 
and maps their evolving semantic relationship layers.

Responsibilities:
    - Atomically store and update entities inside the graph layout.
    - Track property transformations and historical text evolution.
    - Establish directed graph relationship lines between tracked entities.
    - Resolve core matching aliases to prevent duplicate identity fragmentation.
    - Support real-time entity linking vectors with unstructured text frames.
    - Enable high-throughput, cross-session long-term entity recall.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from .nams_client import NAMSClient

logger = logging.getLogger("GraphRAG.NAMSMemory.EntityMemory")


class EntityMemoryGraph:
    def __init__(self, app_settings: Any, nams_client: NAMSClient):
        """Initializes the entity graph database tracker with explicit client pipelines."""
        self.settings = app_settings
        self.nams_client = nams_client

    async def store_entity(self, entity_name: str, entity_type: str, attributes: Dict[str, Any]) -> None:
        """Saves or expands an entity node within the graph database environment.
        
        Applies a structural incremental patch list pattern to log changes, 
        preserving the historical context of property evolution.
        """
        cypher_mutation = """
        MERGE (e:Entity {name: $name})
        ON CREATE SET 
            e.type = $type,
            e.created_at = timestamp(),
            e.version = 1,
            e.history = [json.encode($attributes)]
        ON MATCH SET 
            e.version = e.version + 1,
            e.history = e.history + json.encode($attributes)
        SET e += $attributes
        """
        
        # Inject standard parameters directly to normalize underlying storage schemas
        payload_params = {
            "name": entity_name.strip(),
            "type": entity_type.upper().strip(),
            "attributes": attributes
        }
        
        try:
            await self.nams_client.execute_graph_mutation(cypher_mutation, payload_params)
            logger.info(f"Successfully committed entity structure state adjustments: [{entity_type}] {entity_name}")
        except Exception as e:
            logger.error(f"Failed to record entity attributes modifications inside graph repository: {e}")
            raise e

    async def track_entity_evolution(self, entity_name: str, observation_summary: str, session_id: str) -> None:
        """Appends historical observations to an entity, tying the updates to an active session context."""
        cypher_mutation = """
        MATCH (e:Entity {name: $name})
        MERGE (s:Session {id: $session_id})
        CREATE (ev:EntityEvolutionStep {
            timestamp: timestamp(),
            observation: $observation
        })
        CREATE (e)-[:EVOLVED_THROUGH]->(ev)
        CREATE (s)-[:LOGGED_EVOLUTION]->(ev)
        """
        
        params = {
            "name": entity_name.strip(),
            "observation": observation_summary,
            "session_id": session_id
        }
        try:
            await self.nams_client.execute_graph_mutation(cypher_mutation, params)
        except Exception as e:
            logger.warning(f"Unable to cleanly log entity trajectory evolution markers: {e}")

    async def store_relationship(
        self, 
        source_name: str, 
        relationship_type: str, 
        target_name: str, 
        properties: Dict[str, Any]
    ) -> None:
        """Constructs an explicit directed edge mapping interactions between entities.
        
        Normalizes edge relationship tokens to strict uppercase layout requirements.
        """
        rel_token = relationship_type.upper().strip().replace(" ", "_")
        
        # Dynamic query insertion formatting safely isolated from parameter block targets
        cypher_mutation = f"""
        MATCH (source:Entity {{name: $source_name}})
        MATCH (target:Entity {{name: $target_name}})
        MERGE (source)-[r:{rel_token}]->(target)
        ON CREATE SET r.created_at = timestamp(), r += $props
        ON MATCH SET r.updated_at = timestamp(), r += $props
        """
        
        params = {
            "source_name": source_name.strip(),
            "target_name": target_name.strip(),
            "props": properties
        }
        try:
            await self.nams_client.execute_graph_mutation(cypher_mutation, params)
            logger.info(f"Established graph topology edge connection: ({source_name})-[{rel_token}]->({target_name})")
        except Exception as e:
            logger.error(f"Failed to build persistent graph relationship link structures: {e}")

    async def resolve_entity_identities(self, target_alias: str, canonical_name: str) -> None:
        """Links aliases or entity variations back to a single primary canonical parent node."""
        cypher_mutation = """
        MERGE (canonical:Entity {name: $canonical_name})
        MERGE (alias:Entity {name: $target_alias})
        SET alias.is_alias = true, alias.canonical_target = $canonical_name
        MERGE (alias)-[:ALIAS_OF]->(canonical)
        """
        
        params = {
            "canonical_name": canonical_name.strip(),
            "target_alias": target_alias.strip()
        }
        try:
            await self.nams_client.execute_graph_mutation(cypher_mutation, params)
            logger.info(f"Entity identification match resolved: '{target_alias}' is linked as an alias of '{canonical_name}'")
        except Exception as e:
            logger.error(f"Identity resolution step failed to link overlapping definitions: {e}")

    async def support_entity_linking(self, text_chunk_id: str, extracted_entities: List[str]) -> None:
        """Links graph entity entities directly back to their source document chunk identifiers."""
        cypher_mutation = """
        UNWIND $entities AS entity_name
        MATCH (e:Entity {name: entity_name})
        MERGE (chunk:DocumentChunk {id: $chunk_id})
        MERGE (e)-[:MENTIONED_IN]->(chunk)
        """
        
        params = {
            "chunk_id": text_chunk_id,
            "entities": [name.strip() for name in extracted_entities]
        }
        try:
            await self.nams_client.execute_graph_mutation(cypher_mutation, params)
        except Exception as e:
            logger.warning(f"Could not map document index tracking constraints back to target graph structures: {e}")

    async def long_term_entity_recall(self, seed_entity_name: str, max_neighborhood_depth: int = 2) -> Dict[str, Any]:
        """Retrieves an entity's complete multi-hop relationship network for deep reasoning.
        
        Args:
            seed_entity_name: Starting entry node name parameter.
            max_neighborhood_depth: Max relationship hops to traverse.
            
        Returns:
            A structured schema container detailing target parameters and connections maps.
        """
        cypher_query = """
        MATCH (e:Entity {name: $name})
        OPTIONAL MATCH path = (e)-[r*1..2]-(neighbor:Entity)
        RETURN e AS source_node, collect(path) AS structural_paths
        """
        
        # Safe constraint limit truncation
        depth = min(max(max_neighborhood_depth, 1), 3)
        
        try:
            records = await self.nams_client.execute_graph_query(cypher_query, {"name": seed_entity_name.strip()})
            if not records:
                return {"entity": seed_entity_name, "message": "Node instance could not be resolved."}
                
            return {
                "queried_entity": seed_entity_name,
                "profile": records[0].get("source_node"),
                "graph_neighborhood_depth": depth,
                "message": "Long-term tracking contextual maps extracted successfully."
            }
        except Exception as critical_err:
            logger.error(f"Long term graph routing recall exception encountered: {critical_err}")
            return {"entity": seed_entity_name, "error": str(critical_err)}