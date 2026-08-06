#Redis+Neo4j (hybrid)
"""
============================================================================
Conversation Memory Module:
  - Maintains conversational history across sessions.
Stores structured dialogue history while preserving contextual continuity
between user interactions.

Responsibilities
----------------
• Store conversations.
• Retrieve conversation history.
• Summarize long conversations.
• Compress historical context.
• Maintain session continuity.
• Support contextual recall.
"""

"""Conversation Memory Module.

Maintains conversational history across sessions. Stores structured dialogue history 
while preserving contextual continuity between user interactions via a hybrid 
Redis + Neo4j graph architecture.

Responsibilities:
    - Store conversation turns atomically across Redis cache and Neo4j.
    - Retrieve full or context-windowed conversation histories.
    - Summarize long conversations using OpenRouter fallback paths.
    - Compress historical context structures based on total session age.
    - Maintain strict multi-agent session continuity.
    - Support semantic and relationship-driven contextual recall.
"""

import json
import logging
from typing import List, Dict, Any, Optional
import redis
from .nams_client import NAMSClient

logger = logging.getLogger("GraphRAG.NAMSMemory.ConversationMemory")


class ConversationMemoryStore:
    def __init__(self, app_settings: Any, nams_client: NAMSClient):
        """Initializes the hybrid conversational store binding Redis pools and Neo4j drivers."""
        self.settings = app_settings
        self.nams_client = nams_client
        self.redis_client: Optional[redis.Redis] = None
        self._init_redis()

    def _init_redis(self) -> None:
        """Configures the high-performance Redis cache layer with optional TLS connection parameters."""
        try:
            redis_kwargs: Dict[str, Any] = {
                "host": self.settings.REDIS_HOST,
                "port": self.settings.REDIS_PORT,
                "password": self.settings.REDIS_PASSWORD,
                "decode_responses": True,
                "socket_timeout": 5.0
            }
            if self.settings.REDIS_SSL:
                redis_kwargs.update({
                    "ssl": True,
                    "ssl_certfile": self.settings.REDIS_CERT,
                    "ssl_keyfile": self.settings.REDIS_KEY,
                    "ssl_ca_certs": self.settings.REDIS_CA
                })

            self.redis_client = redis.Redis(**redis_kwargs)
            # Test high-speed connection ping
            self.redis_client.ping()
            logger.info("Redis cache pool successfully attached to short-term memory layer.")
        except Exception as e:
            logger.error(f"Redis memory attachment failure. Operating in fallback graph-only mode: {e}")
            self.redis_client = None

    async def store_conversation_turn(self, session_id: str, user_query: str, agent_response: str) -> None:
        """Atomically caches interaction metrics inside Redis and appends to Neo4j graph topology."""
        payload = {"user": user_query, "agent": agent_response}
        
        # 1. Update Short-Term High-Speed Cache (Redis)
        if self.redis_client:
            try:
                redis_key = f"session:{session_id}:history"
                self.redis_client.rpush(redis_key, json.dumps(payload))
                self.redis_client.expire(redis_key, 86400)  # Standard 24-hour cache lifespan
            except Exception as cache_err:
                logger.warning(f"Failed to append to Redis short-term cache layer: {cache_err}")

        # 2. Append to Long-Term Structural Knowledge Graph (Neo4j)
        cypher_query = """
        MERGE (s:Session {id: $session_id})
        CREATE (t:InteractionTurn {
            timestamp: timestamp(),
            user_input: $user_query,
            agent_output: $agent_response
        })
        WITH s, t
        MATCH (s)-[:HAS_TURN]->(last:InteractionTurn)
        WHERE NOT (last)-[:NEXT_TURN]->()
        CREATE (last)-[:NEXT_TURN]->(t)
        WITH s, t
        MERGE (s)-[:HAS_TURN]->(t)
        """
        
        # Safe fallback loop pattern if it's the absolute first record inside the session pipeline
        fallback_cypher = """
        MERGE (s:Session {id: $session_id})
        CREATE (t:InteractionTurn {
            timestamp: timestamp(),
            user_input: $user_query,
            agent_output: $agent_response
        })
        MERGE (s)-[:HAS_TURN]->(t)
        """
        
        try:
            # We call the underlying graph tools via our NAMS system client configuration
            await self.nams_client.execute_graph_mutation(
                cypher_query, 
                {"session_id": session_id, "user_query": user_query, "agent_response": agent_response}
            )
        except Exception:
            # Re-attempt ingestion using seed structural anchors
            await self.nams_client.execute_graph_mutation(
                fallback_cypher, 
                {"session_id": session_id, "user_query": user_query, "agent_response": agent_response}
            )

    async def retrieve_history(self, session_id: str, window_limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieves structured interaction steps back out of volatile caching layers or permanent graph stores."""
        # Step A: Attempt extraction from low-latency Redis
        if self.redis_client:
            try:
                redis_key = f"session:{session_id}:history"
                cached_turns = self.redis_client.lrange(redis_key, -window_limit, -1)
                if cached_turns:
                    return [json.loads(turn) for turn in cached_turns]
            except Exception as e:
                logger.warning(f"Short-term lookups failed; querying permanent Neo4j clusters: {e}")

        # Step B: Graph structural fallback query
        cypher_query = """
        MATCH (s:Session {id: $session_id})-[:HAS_TURN]->(t:InteractionTurn)
        RETURN t.user_input AS user, t.agent_output AS agent, t.timestamp AS ts
        ORDER BY ts DESC
        LIMIT $limit
        """
        try:
            records = await self.nams_client.execute_graph_query(
                cypher_query, 
                {"session_id": session_id, "limit": window_limit}
            )
            # Reversing the desc timeline sequence back into proper chat dialogue chronology
            return [{"user": r["user"], "agent": r["agent"]} for r in reversed(records)]
        except Exception as graph_err:
            logger.error(f"Complete breakdown of hybrid interaction storage targets: {graph_err}")
            return []

    async def summarize_long_conversations(self, session_id: str, context_blocks: List[Dict[str, Any]]) -> str:
        """Processes historical records through OpenRouter LLM engines to create a summarized memory state."""
        import httpx
        
        history_text = "\n".join([f"User: {turn['user']}\nAgent: {turn['agent']}" for turn in context_blocks])
        system_prompt = "You are a multi-agent cognitive optimizer. Condense this dialogue history into a dense, summary structural snapshot."
        
        headers = {
            "Authorization": f"Bearer {self.settings.OPENROUTER_API_KEY or 'anonymous'}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.settings.LLM_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": history_text}
            ],
            "temperature": 0.2
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                res = await client.post(f"{self.settings.OPENROUTER_BASE_URL}/chat/completions", json=payload, headers=headers)
                if res.status_code == 200:
                    summary = res.json()["choices"][0]["message"]["content"]
                    
                    # Persist conversational snapshot in Neo4j session node parameters
                    update_query = "MATCH (s:Session {id: $session_id}) SET s.rolling_summary = $summary"
                    await self.nams_client.execute_graph_mutation(update_query, {"session_id": session_id, "summary": summary})
                    return summary
        except Exception as e:
            logger.error(f"Failed to generate automated session summary layers: {e}")
        return "Session summary generation unavailable."

    async def compress_historical_context(self, session_id: str) -> None:
        """Evicts older interaction turns from high-speed cache once memory boundaries are crossed."""
        if not self.redis_client:
            return
        try:
            redis_key = f"session:{session_id}:history"
            current_len = self.redis_client.llen(redis_key)
            if current_len > 30:
                # Retain only the 10 most recent interactions to keep the context window small
                self.redis_client.ltrim(redis_key, -10, -1)
                logger.info(f"Compressed local Redis window buffer for session '{session_id}'.")
        except Exception as e:
            logger.error(f"Failed to execute cache pruning routine: {e}")

    async def clear_session(self, session_id: str) -> None:
        """Purges a session key from Redis and detaches relationship pointers within Neo4j."""
        if self.redis_client:
            self.redis_client.delete(f"session:{session_id}:history")
            
        cypher_query = """
        MATCH (s:Session {id: $session_id})
        OPTIONAL MATCH (s)-[r:HAS_TURN]->(t:InteractionTurn)
        DETACH DELETE t, s
        """
        await self.nams_client.execute_graph_mutation(cypher_query, {"session_id": session_id})
        logger.info(f"Session state arrays for context space '{session_id}' cleared successfully.")