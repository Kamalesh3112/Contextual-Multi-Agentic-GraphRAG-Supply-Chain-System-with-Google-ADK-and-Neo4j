#Agent state tracking
"""
============================================================================
Reasoning Trace Memory Module:
 - Stores the reasoning process used by agents while solving previous tasks.
  - Rather than remembering only answers, this module remembers HOW decisions
were reached.

Responsibilities:
----------------
• Store reasoning chains.
• Store execution traces.
• Store planning decisions.
• Store retrieval history.
• Store intermediate reasoning.
• Enable reasoning replay.
"""

"""Reasoning Trace Memory Module.

Stores the reasoning process used by agents while solving previous tasks. Rather 
than remembering only raw answers, this module logs HOW decisions were reached, 
enabling cognitive replays and execution trail debugging.

Responsibilities:
    - Store reasoning chains and multi-hop node trails.
    - Store agent execution traces and tool performance telemetry.
    - Store high-level planning decisions and mid-course corrections.
    - Store historical retrieval footprints used during context synthesis.
    - Store intermediate reasoning thoughts and reflection states.
    - Enable chronological reasoning tree replay operations.
"""

import logging
from typing import Dict, List, Any, Optional
from .nams_client import NAMSClient

logger = logging.getLogger("GraphRAG.NAMSMemory.ReasoningTraceMemory")


class ReasoningTraceMemory:
    def __init__(self, app_settings: Any, nams_client: NAMSClient):
        """Initializes the agent state tracking store linked to core Neo4j operations."""
        self.settings = app_settings
        self.nams_client = nams_client

    async def store_reasoning_chain(
        self, 
        session_id: str, 
        agent_id: str, 
        thought_process: str, 
        step_index: int
    ) -> None:
        """Logs a specific thought process block inside a directed agent execution tree graph."""
        cypher_mutation = """
        MERGE (s:Session {id: $session_id})
        MERGE (a:Agent {id: $agent_id})
        CREATE (tc:ReasoningChain {
            timestamp: timestamp(),
            thought: $thought,
            step: $step_index
        })
        MERGE (s)-[:TRACKS_AGENT]->(a)
        MERGE (a)-[:GENERATED_THOUGHT]->(tc)
        """
        
        params = {
            "session_id": session_id,
            "agent_id": agent_id,
            "thought": thought_process,
            "step_index": step_index
        }
        try:
            await self.nams_client.execute_graph_mutation(cypher_mutation, params)
            logger.info(f"Recorded step {step_index} reasoning block for agent '{agent_id}'.")
        except Exception as e:
            logger.error(f"Failed to append reasoning chain chunk onto graph network structures: {e}")

    async def store_execution_trace(
        self, 
        session_id: str, 
        task_id: str, 
        action_taken: str, 
        result_payload: Dict[str, Any]
    ) -> None:
        """Stores a hard tool or algorithmic execution record, mapping results back to parent tasks."""
        import json
        
        cypher_mutation = """
        MERGE (s:Session {id: $session_id})
        MERGE (t:Task {id: $task_id})
        CREATE (ex:ExecutionTrace {
            timestamp: timestamp(),
            action: $action,
            output_dump: $output
        })
        MERGE (s)-[:HAS_TASK]->(t)
        MERGE (t)-[:PRODUCED_TRACE]->(ex)
        """
        
        params = {
            "session_id": session_id,
            "task_id": task_id,
            "action": action_taken,
            "output": json.dumps(result_payload)
        }
        try:
            await self.nams_client.execute_graph_mutation(cypher_mutation, params)
        except Exception as e:
            logger.warning(f"Could not persist operational execution trace metric fields: {e}")

    async def store_planning_decision(
        self, 
        session_id: str, 
        objective: str, 
        strategy_steps: List[str]
    ) -> None:
        """Registers a dynamic plan optimization map detailing target strategic actions."""
        cypher_mutation = """
        MERGE (s:Session {id: $session_id})
        CREATE (p:PlanningDecision {
            timestamp: timestamp(),
            goal: $objective,
            steps: $strategy
        })
        MERGE (s)-[:ADOPTED_PLAN]->(p)
        """
        
        params = {
            "session_id": session_id,
            "objective": objective,
            "strategy": strategy_steps
        }
        try:
            await self.nams_client.execute_graph_mutation(cypher_mutation, params)
            logger.info(f"Committed new strategic planning boundary for target context session: {session_id}")
        except Exception as e:
            logger.error(f"Planning record storage rejected by graph server layer: {e}")

    async def store_retrieval_history(
        self, 
        session_id: str, 
        query_used: str, 
        source_identifiers: List[str]
    ) -> None:
        """Tracks exactly what data hooks or vector shards were utilized to formulate response parameters."""
        cypher_mutation = """
        MERGE (s:Session {id: $session_id})
        CREATE (rh:RetrievalFootprint {
            timestamp: timestamp(),
            query: $query,
            sources: $sources
        })
        MERGE (s)-[:CONSUMED_RETRIEVAL]->(rh)
        """
        
        params = {
            "session_id": session_id,
            "query": query_used,
            "sources": source_identifiers
        }
        try:
            await self.nams_client.execute_graph_mutation(cypher_mutation, params)
        except Exception as e:
            logger.warning(f"Failed to cache underlying source retrieval logs: {e}")

    async def store_intermediate_reasoning(self, session_id: str, temporary_thought: str) -> None:
        """Stores non-final candidate sub-thoughts to evaluate agent doubt or execution dead-ends."""
        cypher_mutation = """
        MERGE (s:Session {id: $session_id})
        CREATE (ir:IntermediateReasoning {
            timestamp: timestamp(),
            context: $thought
        })
        MERGE (s)-[:HEURISTIC_TEMPORARY_PATH]->(ir)
        """
        try:
            await self.nams_client.execute_graph_mutation(cypher_mutation, {"session_id": session_id, "thought": temporary_thought})
        except Exception as e:
            logger.debug(f"Transient observation tracking failure safely skipped: {e}")

    async def retrieve_active_traces(self, session_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieves the most recent reasoning actions to keep the agent execution context aligned."""
        cypher_query = """
        MATCH (s:Session {id: $session_id})-[:TRACKS_AGENT]->(a:Agent)-[:GENERATED_THOUGHT]->(tc:ReasoningChain)
        RETURN a.id AS agent, tc.thought AS thought_step, tc.step AS idx, tc.timestamp AS ts
        ORDER BY ts DESC
        LIMIT $limit
        """
        try:
            records = await self.nams_client.execute_graph_query(cypher_query, {"session_id": session_id, "limit": limit})
            return [
                {"type": "ReasoningChain", "agent": r["agent"], "text": f"Step {r['idx']}: {r['thought_step']}"} 
                for r in reversed(records)
            ]
        except Exception as e:
            logger.error(f"Error extracting active thinking traces out of memory space: {e}")
            return []

    async def compile_reasoning_replay(self, session_id: str) -> Dict[str, Any]:
        """Compiles a complete chronological log of thoughts, actions, and plans to evaluate system decisions."""
        cypher_query = """
        MATCH (s:Session {id: $session_id})
        OPTIONAL MATCH (s)-[:ADOPTED_PLAN]->(p:PlanningDecision)
        OPTIONAL MATCH (s)-[:TRACKS_AGENT]->(a:Agent)-[:GENERATED_THOUGHT]->(tc:ReasoningChain)
        OPTIONAL MATCH (s)-[:HAS_TASK]->(t:Task)-[:PRODUCED_TRACE]->(ex:ExecutionTrace)
        RETURN p, tc, ex
        """
        try:
            records = await self.nams_client.execute_graph_query(cypher_query, {"session_id": session_id})
            return {
                "session_id": session_id,
                "raw_timeline_records": records,
                "status": "Chronological trace mapping aggregated successfully."
            }
        except Exception as err:
            logger.error(f"Failed to generate structured system replay audit trail: {err}")
            return {"session_id": session_id, "error": str(err)}

    async def clear_session_traces(self, session_id: str) -> None:
        """Purges transactional history items when task windows close."""
        cypher_mutation = """
        MATCH (s:Session {id: $session_id})
        OPTIONAL MATCH (s)-[:ADOPTED_PLAN]->(p:PlanningDecision)
        OPTIONAL MATCH (s)-[:TRACKS_AGENT]->(a:Agent)-[:GENERATED_THOUGHT]->(tc:ReasoningChain)
        OPTIONAL MATCH (s)-[:HAS_TASK]->(t:Task)-[:PRODUCED_TRACE]->(ex:ExecutionTrace)
        OPTIONAL MATCH (s)-[:CONSUMED_RETRIEVAL]->(rh:RetrievalFootprint)
        OPTIONAL MATCH (s)-[:HEURISTIC_TEMPORARY_PATH]->(ir:IntermediateReasoning)
        DETACH DELETE p, tc, ex, rh, ir
        """
        try:
            await self.nams_client.execute_graph_mutation(cypher_mutation, {"session_id": session_id})
            logger.info(f"State tracking parameters for session '{session_id}' safely purged.")
        except Exception as e:
            logger.error(f"Failed to run structural wipe operations over tracing layers: {e}")