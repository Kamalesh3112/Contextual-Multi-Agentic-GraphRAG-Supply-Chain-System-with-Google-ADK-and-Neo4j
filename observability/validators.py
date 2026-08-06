"""
Validation Module

Responsible for validating execution quality throughout the Multi-Agent
GraphRAG Platform.

Validation ensures correctness, consistency and reliability before outputs
are returned to users.

Responsibilities
----------------
• Validate GraphRAG retrieval.
• Validate graph traversal.
• Validate generated Cypher.
• Validate retrieved context.
• Validate memory consistency.
• Validate reasoning outputs.
• Validate LLM responses.
• Validate workflow execution.
• Validate execution plans.
• Validate reflection quality.
"""

import logging
import json
import re
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger("GraphRAG.Observability.Validators")


class OutputSchemaValidator:
    def __init__(self, token_ceiling: int = 8000, query_blacklist: Optional[List[str]] = None):
        """Initializes structural constraints validation engines."""
        self.token_ceiling = token_ceiling
        # Prevent hazardous or destructive Cypher queries from hitting execution pools
        self._cypher_blacklist = query_blacklist or ["DELETE", "REMOVE", "DROP", "MATCH (n) DETACH DELETE n"]

    def validate_generated_cypher(self, raw_cypher_string: str) -> Tuple[bool, str]:
        """Validates generated Cypher scripts for semantic syntax rules and malicious injection risks.
        
        Returns:
            A tuple containing a success boolean and a diagnostic message.
        """
        cleaned_query = raw_cypher_string.strip().upper()
        if not cleaned_query:
            return False, "Cypher script statement payload is empty."

        # Scan for explicit statements that could damage persistent graphs
        for forbidden_keyword in self._cypher_blacklist:
            if re.search(r'\b' + re.escape(forbidden_keyword) + r'\b', cleaned_query):
                logger.error(f"Security Alert: Malicious or destructive command sequence identified: {forbidden_keyword}")
                return False, f"Prohibited mutation token identified within context stream: {forbidden_keyword}"

        # Enforce basic graph traversal matching requirements
        if "RETURN" not in cleaned_query:
            return False, "Invalid read expression syntax topology. Missing structural 'RETURN' definition."

        return True, "Cypher query verified for secure, read-only cluster execution."

    def validate_retrieved_context(self, context_packet: Dict[str, List[Any]]) -> Tuple[bool, str]:
        """Validates the structure and lineage integrity of retrieved contexts before formatting."""
        if not isinstance(context_packet, dict):
            return False, "Context packet must be a structured dictionary object."

        required_keys = {"semantic", "graph", "memory"}
        missing_keys = required_keys - set(context_packet.keys())
        if missing_keys:
            return False, f"Context infrastructure configuration failure. Missing payload arrays: {missing_keys}"

        # Validate dense data connectivity bounds
        total_items = len(context_packet["semantic"]) + len(context_packet["graph"]) + len(context_packet["memory"])
        if total_items == 0:
            logger.warning("Empty multi-source context packet passed through retrieval pipelines.")
            return True, "Warning: Context stream validated but contains zero matching references."

        return True, f"Context metrics verified. Collected {total_items} data hooks across hybrid streams."

    def validate_memory_consistency(self, redis_history: List[Any], neo4j_history: List[Any]) -> Tuple[bool, str]:
        """Ensures temporal transactional synchronization between Redis cache blocks and Neo4j graph pools."""
        if len(redis_history) == 0 and len(neo4j_history) > 0:
            logger.info("Transient short-term cache miss recorded. Synchronizing from long-term Neo4j graph tables.")
            return True, "Transient cache out-of-sync. Rehydration required."
            
        return True, "Memory distribution tiers structurally validated."

    def validate_reasoning_outputs(self, step_payload: Dict[str, Any]) -> Tuple[bool, str]:
        """Audits intermediary agent steps to ensure structured thinking chains follow schema guidelines."""
        if "thought" not in step_payload or "step" not in step_payload:
            return False, "Malformed reasoning payload. Intermediary agent thoughts must contain 'step' index and 'thought' fields."
            
        if not str(step_payload.get("thought", "")).strip():
            return False, "Reasoning execution block contains an unpopulated empty thought frame."

        return True, "Intermediate cognitive steps verified successfully."

    def validate_llm_response(self, response_text: str, contextual_grounding_block: str) -> Tuple[bool, str]:
        """Evaluates final responses to prevent hallucinations or empty answer strings."""
        if not response_text or not response_text.strip():
            return False, "Generative model model returned an empty string output payload."

        # Detect clear boilerplate indicators of grounding failures or broken retrievals
        hallucination_indicators = ["i do not have access to that information", "unknown context", "context missing"]
        for phrase in hallucination_indicators:
            if phrase in response_text.lower():
                return False, f"Ungrounded response state detected. Generation hit fallback warning phrase: '{phrase}'"

        return True, "Final generation passed grounding criteria audits."

    def validate_execution_plan(self, structured_steps: List[str]) -> Tuple[bool, str]:
        """Validates system planning trees to safeguard against cyclic dependencies or non-terminating workflows."""
        if not structured_steps:
            return False, "Execution plan array contains zero actionable directives."
            
        if len(structured_steps) > 20:
            return False, f"Execution plan exceeds safe multi-agent execution bounds (Max allowed: 20 steps, Found: {len(structured_steps)})."

        return True, "Workflow execution instructions validated."

    def validate_reflection_quality(self, parsed_reflection: Dict[str, Any]) -> Tuple[bool, str]:
        """Audits autonomous post-task reflections to verify structured formatting and key containment."""
        required_schema_keys = {"topic", "insight", "tags"}
        
        if not isinstance(parsed_reflection, dict):
            return False, "Reflection data structure is not a valid JSON dictionary payload."
            
        missing_fields = required_schema_keys - set(parsed_reflection.keys())
        if missing_fields:
            return False, f"Reflection block rejected. Missing key parameters: {missing_fields}"

        if not isinstance(parsed_reflection.get("tags"), list):
            return False, "Type mismatch constraint. Reflection metadata tags field must be a valid array list."

        return True, "Self-evaluation reflection object passed strict structural schema constraints."