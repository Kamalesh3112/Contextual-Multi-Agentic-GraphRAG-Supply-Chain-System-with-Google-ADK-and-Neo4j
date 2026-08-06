"""
============================================================================
Central coordinator for all cognitive memory operations.
Acts as the unified entry point for storing, retrieving, updating and
maintaining multiple memory systems.

Contains
--------
• MemoryManager

Responsibilities
----------------
• Coordinate memory retrieval.
• Coordinate memory storage.
• Route memory requests.
• Manage memory lifecycle.
• Synchronize memory stores.
• Handle memory expiration.
• Coordinate context-aware recall.
• Support memory consolidation.
"""

"""Memory Manager Module.

Central coordinator for all cognitive memory operations. Acts as the unified entry 
point for storing, retrieving, updating, and maintaining multiple memory systems.

Responsibilities:
    - Coordinate memory retrieval across multi-source systems concurrently.
    - Coordinate atomic memory storage loops.
    - Route incoming requests to specialized short, long, or reasoning memory layers.
    - Manage complete memory lifecycles and cache expirations.
    - Synchronize data consistency between transient cache pools and permanent graphs.
    - Coordinate context-aware historical recall sequences.
    - Support asynchronous higher-order cognitive memory consolidation tasks.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
from .nams_client import NAMSClient
from .conversation_memory import ConversationMemoryStore
from .entity_memory import EntityMemoryGraph
from .reasoning_trace_memory import ReasoningTraceMemory
from .reflection_memory import ReflectionMemoryEngine

logger = logging.getLogger("GraphRAG.NAMSMemory.MemoryManager")


class NAMSMemoryManager:
    def __init__(self, app_settings: Any, nams_client: NAMSClient):
        """Initializes the top-level orchestration layer, binding all functional memory modules."""
        self.settings = app_settings
        self.nams_client = nams_client

        # Core Cognitive Submodule Initializations
        self.conversation = ConversationMemoryStore(app_settings, nams_client)
        self.entities = EntityMemoryGraph(app_settings, nams_client)
        self.traces = ReasoningTraceMemory(app_settings, nams_client)
        self.reflection = ReflectionMemoryEngine(app_settings, nams_client)

    async def ingest_interaction_lifecycle(
        self, 
        session_id: str, 
        user_query: str, 
        agent_response: str,
        extracted_entities: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """Coordinates multi-target async storage mutations following an interaction turn."""
        logger.info(f"Starting transaction ingestion sequence for session context: '{session_id}'")
        
        # Define asynchronous concurrent storage pipeline loops
        storage_tasks = [
            self.conversation.store_conversation_turn(session_id, user_query, agent_response),
            self.conversation.compress_historical_context(session_id)
        ]

        # Dynamically append entity processing chains if tracking outputs are intercepted
        if extracted_entities:
            for entity in extracted_entities:
                name = entity.get("name")
                etype = entity.get("type", "Generic")
                attrs = entity.get("attributes", {})
                if name:
                    storage_tasks.append(self.entities.store_entity(name, etype, attrs))

        # Run mutations concurrently across internal frameworks to eliminate sequential I/O blocks
        await asyncio.gather(*storage_tasks, return_exceptions=True)
        
        # Trigger periodic memory consolidation / observation evaluation asynchronously
        asyncio.create_task(self.consolidate_session_insights(session_id))

    async def fetch_contextual_recall(self, session_id: str, query_text: str) -> Dict[str, List[Any]]:
        """Coordinates concurrent high-throughput context-aware recall sweeps across cognitive tiers."""
        logger.info(f"Executing parallel memory recall routes for thread query optimization maps.")
        
        # Parallel read path triggers across short-term logs, reasoning footprints, and reflections
        conversation_task = self.conversation.retrieve_history(session_id, window_limit=10)
        trace_task = self.traces.retrieve_active_traces(session_id, limit=5)
        reflection_task = self.reflection.retrieve_reflections(query_text, limit=3)
        
        results = await asyncio.gather(conversation_task, trace_task, reflection_task, return_exceptions=True)
        
        # Graceful unpack with explicit data structural default safety mappings
        return {
            "conversation_history": results[0] if not isinstance(results[0], Exception) else [],
            "reasoning_footprints": results[1] if not isinstance(results[1], Exception) else [],
            "synthesized_reflections": results[2] if not isinstance(results[2], Exception) else []
        }

    async def consolidate_session_insights(self, session_id: str) -> None:
        """Supports memory consolidation by transforming episodic historical rows into high-order abstractions."""
        try:
            history = await self.conversation.retrieve_history(session_id, window_limit=15)
            # Evaluate threshold bounds to determine if a synthesis cycle is required
            if len(history) >= 10:
                logger.info("Session history token mass threshold reached. Spinning up background consolidation.")
                
                # 1. Summarize ongoing dialog parameters to streamline the context layer
                await self.conversation.summarize_long_conversations(session_id, history)
                
                # 2. Extract conceptual core insights into permanent reflection nodes
                await self.reflection.generate_and_store_reflections(session_id, history)
        except Exception as err:
            logger.error(f"Error encountered during background cognitive optimization loops: {err}")

    async def handle_session_expiration(self, session_id: str) -> None:
        """Manages memory life-cycle pruning by cleaning up session records when terms expire."""
        logger.warning(f"Evicting session memory layers from high-speed cache lines: '{session_id}'")
        
        # Run synchronous multi-source cleanups to flush short-term elements safely
        await self.conversation.clear_session(session_id)
        await self.traces.clear_session_traces(session_id)
        
        logger.info(f"Session layer lifecycle termination complete for target: {session_id}")