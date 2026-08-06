"""
============================================================================
Reflection Memory Module:
  - Maintains self-evaluation and execution reflections produced after task
completion. Reflection memory enables continuous improvement of future reasoning.

Responsibilities:
----------------
• Store reflections.
• Store execution feedback.
• Store reasoning improvements.
• Store failure analysis.
• Store optimization opportunities.
"""

"""Reflection Memory Module.

Maintains self-evaluation and execution reflections produced after task completion.
Reflection memory enables continuous improvement of future reasoning.

Responsibilities:
    - Store high-level reflections and abstract domain concepts.
    - Store execution feedback loop evaluations.
    - Store reasoning improvements and tactical logic patterns.
    - Store failure analysis profiles and mitigation parameters.
    - Store optimization opportunities for downstream orchestration engines.
"""

import logging
from typing import List, Dict, Any, Optional
import httpx
from .nams_client import NAMSClient

logger = logging.getLogger("GraphRAG.NAMSMemory.ReflectionMemory")


class ReflectionMemoryEngine:
    def __init__(self, app_settings: Any, nams_client: NAMSClient):
        """Initializes the reflection engine linking graph mutation pipelines with platform configurations."""
        self.settings = app_settings
        self.nams_client = nams_client

    async def store_reflection(
        self, 
        reflection_topic: str, 
        insight_summary: str, 
        associated_tags: List[str]
    ) -> None:
        """Stores a high-level cognitive reflection node inside the long-term knowledge graph."""
        cypher_mutation = """
        MERGE (r:Reflection {topic: $topic})
        ON CREATE SET 
            r.insight = $insight,
            r.tags = $tags,
            r.created_at = timestamp(),
            r.execution_count = 1
        ON MATCH SET 
            r.insight = $insight,
            r.tags = apoc.coll.toSet(r.tags + $tags),
            r.updated_at = timestamp(),
            r.execution_count = r.execution_count + 1
        """
        
        params = {
            "topic": reflection_topic.strip(),
            "insight": insight_summary.strip(),
            "tags": [tag.lower().strip() for tag in associated_tags]
        }
        try:
            await self.nams_client.execute_graph_mutation(cypher_mutation, params)
            logger.info(f"Successfully committed high-level self-reflection node: [{reflection_topic}]")
        except Exception as e:
            logger.error(f"Failed to record cognitive reflection node into graph cluster: {e}")

    async def store_execution_feedback(
        self, 
        session_id: str, 
        task_signature: str, 
        efficiency_rating: float, 
        feedback_notes: str
    ) -> None:
        """Logs architectural execution feedback metrics following a completed multi-agent task loop."""
        cypher_mutation = """
        MERGE (s:Session {id: $session_id})
        CREATE (f:ExecutionFeedback {
            timestamp: timestamp(),
            task: $task,
            efficiency: $efficiency,
            notes: $notes
        })
        MERGE (s)-[:PRODUCED_FEEDBACK]->(f)
        """
        
        params = {
            "session_id": session_id,
            "task": task_signature,
            "efficiency": efficiency_rating,
            "notes": feedback_notes
        }
        try:
            await self.nams_client.execute_graph_mutation(cypher_mutation, params)
        except Exception as e:
            logger.warning(f"Could not persist multi-agent operational execution metrics: {e}")

    async def store_reasoning_improvements(self, focus_area: str, recommended_logic_change: str) -> None:
        """Registers specific runtime strategy updates to help guide future multi-hop reasoning sweeps."""
        cypher_mutation = """
        MERGE (i:ReasoningImprovement {focus_area: $focus})
        ON CREATE SET i.remedy_pattern = $remedy, i.created_at = timestamp()
        ON MATCH SET i.remedy_pattern = $remedy, i.updated_at = timestamp()
        """
        try:
            await self.nams_client.execute_graph_mutation(cypher_mutation, {"focus": focus_area, "remedy": recommended_logic_change})
        except Exception as e:
            logger.error(f"Failed to record reasoning optimization logic bounds: {e}")

    async def store_failure_analysis(self, failing_step: str, error_signature: str, mitigation_strategy: str) -> None:
        """Saves error profiling diagnostics to prevent conversational loops or cascading tool crashes."""
        cypher_mutation = """
        CREATE (fa:FailureAnalysis {
            timestamp: timestamp(),
            failed_step: $step,
            error_msg: $error,
            mitigation: $mitigation
        })
        """
        params = {
            "step": failing_step,
            "error": error_signature,
            "mitigation": mitigation_strategy
        }
        try:
            await self.nams_client.execute_graph_mutation(cypher_mutation, params)
            logger.warning(f"Failure profile registered for trace checkpoint: {failing_step}")
        except Exception as e:
            logger.error(f"Failed to record automated diagnostics log package: {e}")

    async def store_optimization_opportunities(self, target_subsystem: str, detected_redundancy: str) -> None:
        """Logs detected bottlenecks to optimize future context processing frames."""
        cypher_mutation = """
        MERGE (o:OptimizationOpportunity {subsystem: $subsystem})
        SET o.detected_bottleneck = $redundancy, o.logged_at = timestamp()
        """
        try:
            await self.nams_client.execute_graph_mutation(cypher_mutation, {"subsystem": target_subsystem, "redundancy": detected_redundancy})
        except Exception as e:
            logger.debug(f"Muted optimization discovery registration exception: {e}")

    async def generate_and_store_reflections(self, session_id: str, history_payload: List[Dict[str, Any]]) -> None:
        """Processes historical transcripts using OpenRouter to generate long-term self-evaluations."""
        transcript_chunks = []
        for turn in history_payload:
            transcript_chunks.append(f"User Prompt: {turn.get('user')}\nAgent Execution: {turn.get('agent')}")
        
        full_transcript = "\n---\n".join(transcript_chunks)
        
        system_instruction = (
            "You are a meta-cognitive self-reflection engine working within a multi-agent framework.\n"
            "Analyze the provided dialogue history transcript. Extract high-level abstract reflections, "
            "noting execution feedback, potential reasoning failure modes, and logic optimizations.\n"
            "Format your response as a strict JSON block structure containing keys: 'topic', 'insight', and 'tags'."
        )
        
        headers = {
            "Authorization": f"Bearer {self.settings.OPENROUTER_API_KEY or 'anonymous'}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.settings.LLM_MODEL,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": f"Transcript Data:\n{full_transcript}"}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1
        }

        try:
            async with httpx.AsyncClient(timeout=25.0) as client:
                res = await client.post(f"{self.settings.OPENROUTER_BASE_URL}/chat/completions", json=payload, headers=headers)
                if res.status_code == 200:
                    import json
                    raw_content = res.json()["choices"]["message"]["content"]
                    parsed_insights = json.loads(raw_content)
                    
                    # 1. Commit the primary parsed abstraction node into the graph layout
                    await self.store_reflection(
                        reflection_topic=parsed_insights.get("topic", "General Behavior Patterns"),
                        insight_summary=parsed_insights.get("insight", "No anomalous behavior found."),
                        associated_tags=parsed_insights.get("tags", ["general"])
                    )
                    
                    # 2. Link the session to the new reflection node to capture data heritage
                    link_mutation = """
                    MATCH (s:Session {id: $session_id})
                    MATCH (r:Reflection {topic: $topic})
                    MERGE (s)-[:CONTRIBUTED_TO_REFLECTION]->(r)
                    """
                    await self.nams_client.execute_graph_mutation(
                        link_mutation, 
                        {"session_id": session_id, "topic": parsed_insights.get("topic")}
                    )
        except Exception as runtime_err:
            logger.error(f"Autonomous reflection evaluation thread collapsed: {runtime_err}")

    async def retrieve_reflections(self, query_keyword: str, limit: int = 3) -> List[str]:
        """Queries long-term reflection models using string-matching or tag intersections.
        
        Enriches the Context Engineering pipeline by appending historical self-corrections.
        """
        cypher_query = """
        MATCH (r:Reflection)
        WHERE r.topic CONTAINS $keyword OR any(tag IN r.tags WHERE tag = $keyword)
        RETURN r.topic AS topic, r.insight AS insight
        LIMIT $limit
        """
        try:
            records = await self.nams_client.execute_graph_query(
                cypher_query, 
                {"keyword": query_keyword.lower().strip(), "limit": limit}
            )
            return [f"Reflection on [{r['topic']}]: {r['insight']}" for r in records]
        except Exception as e:
            logger.error(f"Could not extract self-evaluation contexts from permanent database pools: {e}")
            return []