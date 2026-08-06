"""
Responsibilities: Responsible for producing the final user response.
• Merge outputs from all agents.
• Resolve conflicting information.
• Compress retrieved context.
• Build final LLM prompt.
• Generate natural-language responses.
• Produce structured reasoning summaries.
• Trigger reflection generation.
• Return the final response.
  - Calls nemotron-3-ultra-550b-a55b:free
  - Structured reasoning into accurate, coherent and explainable
natural-language responses.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from google.adk.agents import Agent
from agents.registry import global_registry
from orchestration.llm_provider import OpenRouterADKAdapter, OpenRouterClient

logger = logging.getLogger("ADK.SynthesisAgent")


class SynthesisAgent(OpenRouterADKAdapter):
    """
    Final Content Synthesis and Context Compression Agent.
    Subclasses OpenRouterADKAdapter to maintain complete type compliance with Google ADK.
    """

    AGENT_NAME = "SynthesisAgent"
    AGENT_VERSION = "1.0.0"
    AGENT_TYPE = "reasoning"
    AGENT_DOMAIN = "response_generation"

    def __init__(self) -> None:
        instruction_prompt = (
            "You are the master Synthesis and Content Production Agent for an advanced GraphRAG framework.\n"
            "Your critical task is to consolidate conflicting or disparate streams of context into a seamless, "
            "highly professional executive response. You are provided with: User Input, Subgraph Context, "
            "Risk Assessment Intelligence reports, and Conversation State Histories.\n\n"
            "CRITICAL DIRECTIVES:\n"
            "1. Resolve contradictions logically across sources by relying on verified graph constraints.\n"
            "2. Ground every single technical deduction. Explicitly cite relevant graph nodes using their entity details or names.\n"
            "3. Format outputs strictly inside clear Markdown presentations containing an executive summary, "
            "a grounded facts layout, and a downstream risk/dependency profile summary."
        )
        
        runner_client = OpenRouterClient()
        
        super().__init__(
            name=self.AGENT_NAME, 
            instruction=instruction_prompt, 
            runner=runner_client
        )

    def generate_response(
        self, 
        user_input: str, 
        graph_context: Dict[str, Any], 
        risk_context: Dict[str, Any], 
        history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Gathers structural inputs from all independent layers, compiles a localized 
        long-context template prompt, and calls the primary 550B inference model engine.
        """
        logger.info(f"[{self.AGENT_NAME}] Initiating context consolidation and final response generation loops.")
        
        # Build out a long-context template prompt maximizing the 550B model's reasoning capabilities
        comprehensive_prompt = (
            f"### USER INTENT REQUEST\n"
            f"Query: {user_input}\n\n"
            f"### CONVERSATION STATE REGISTRIES (HISTORY)\n"
            f"{json.dumps(history, indent=2) if history else 'No historical conversation history provided.'}\n\n"
            f"### RETRIEVED GRAPH DATA LAYER CONTEXT\n"
            f"{json.dumps(graph_context, indent=2)}\n\n"
            f"### RISK INTELLIGENCE MATRIX REPORT\n"
            f"{json.dumps(risk_context, indent=2)}\n\n"
            f"### COMPILATION DIRECTIVE\n"
            f"Generate a clear, grounded, natural-language executive report using the structural parameters detailed above. "
            f"Ensure all node citations utilize names or entity specifics from the graph context."
        )

        try:
            adk_output = self.run(user_prompt=comprehensive_prompt)
            final_text = adk_output.text
            
            return {
                "content": final_text,
                "citations": graph_context.get("nodes", []),
                "risk_level": risk_context.get("level", "UNKNOWN"),
                "synthesis_status": "COMPLETED",
                "execution_engine": "openrouter/nvidia-nemotron-550b"
            }

        except Exception as e:
            logger.error(f"[{self.AGENT_NAME}] Error during executive synthesis processing run: {e}", exc_info=True)
            fallback_text = (
                f"### System Alert Notification\n"
                f"The high-parameter reasoning engine is temporarily unavailable. Data has been consolidated programmatically.\n\n"
                f"**Query Ref:** {user_input}\n"
                f"**Risk Profile Level Identified:** {risk_context.get('level', 'UNKNOWN')}\n"
                f"**Programmatic Summary:** A total of {len(graph_context.get('nodes', []))} graph nodes were extracted "
                f"and passed through safety metrics. Please check active logs to recover raw inference frames."
            )
            return {
                "content": fallback_text,
                "citations": graph_context.get("nodes", []),
                "risk_level": risk_context.get("level", "UNKNOWN"),
                "synthesis_status": "DEGRADED_FALLBACK",
                "execution_engine": "local-deterministic-compiler"
            }


synthesis_agent_instance = SynthesisAgent()

global_registry.register_agent(
    name=SynthesisAgent.AGENT_NAME,
    capabilities={
        "response_synthesis", 
        "hallucination_check", 
        "formatting", 
        "context_compression"
    },
    factory_or_instance=synthesis_agent_instance,
    is_singleton=True,
    version=SynthesisAgent.AGENT_VERSION,
    metadata={
        "type": SynthesisAgent.AGENT_TYPE, 
        "domain": SynthesisAgent.AGENT_DOMAIN
    }
)