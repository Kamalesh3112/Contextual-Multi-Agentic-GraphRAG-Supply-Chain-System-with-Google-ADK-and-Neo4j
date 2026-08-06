"""
root_agent.py  (Orchestrator)
   - This is the only agent that receives the user's request.

Responsibilities: Primary Orchestrator of the Multi-Agent GraphRAG Platform.
• Entry point for every user request.
• Initializes execution context and session state.
• Invokes the Planning Agent through the orchestration layer.
• Coordinates specialized Google ADK agents.
• Delegates execution to orchestration components.
• Collects intermediate outputs from worker agents.
• Invokes the Synthesis Agent to generate the final response.
• Updates memory after successful execution.
• Returns the final response to the user.
"""

import logging
from typing import Dict, Any, Optional

# Enforce strict layout paths based on our internal workspace directory structure
from agents.registry import global_registry
from orchestration.llm_provider import OpenRouterADKAdapter
from orchestration.router import orchestration_router

logger = logging.getLogger("ADK.RootAgent")


class RootAgent:
    """
    The master entry-point supervisor gateway for the Multi-Agent system.
    Subclasses properties to fulfill google.adk structural identification patterns.
    """

    AGENT_NAME = "RootAgent"
    AGENT_VERSION = "1.0.0"
    AGENT_TYPE = "orchestrator"
    AGENT_DOMAIN = "workflow"

    def __init__(self) -> None:
        # Wrap the core ADK agent structure used to trace orchestration boundaries
        self._adk_agent = OpenRouterADKAdapter(
            name=self.AGENT_NAME, 
            instruction="You are the system ingress supervisor. Intercept requests and track execution topologies."
        )

    def execute(self, user_input: str, session_id: str, media_files: Optional[list] = None) -> Dict[str, Any]:
        """
        Primary system ingress interface. delegates incoming context tokens 
        directly through the centralized dynamic task routing DAG manager engine.
        """
        logger.info(f"[{self.AGENT_NAME}] Ingress interception completed. Processing transaction framework for session: {session_id}")
        
        try:
            router_output = orchestration_router.route_and_execute(
                user_query=user_input,
                session_id=session_id,
                media_assets=media_files
            )
            
            # Unpack payload structures from internal pipeline loops
            final_payload = router_output.get("payload", {})
            
            # Post-Execution: Update persistent trace context via MemoryAgent if completion reports success
            if router_output.get("status") == "COMPLETED":
                memory_agent = global_registry.get_or_create_instance("MemoryAgent")
                if memory_agent:
                    memory_agent.update_memory(session_id, user_input, final_payload)
            
            return final_payload
            
        except Exception as e:
            logger.critical(f"[{self.AGENT_NAME}] Gateway layer execution panic: {e}", exc_info=True)
            return {
                "content": "### System Process Failure\nA critical exception blocked compilation inside the platform orchestration routing layer.",
                "citations": [],
                "risk_level": "UNKNOWN",
                "synthesis_status": "FATAL_ORCHESTRATION_ERROR",
                "error_details": str(e)
            }


root_agent_instance = RootAgent()

global_registry.register_agent(
    name=RootAgent.AGENT_NAME,
    capabilities={"master_supervision", "entrypoint_routing", "unified_interface"},
    factory_or_instance=root_agent_instance._adk_agent,  # Pass the core Agent instance to satisfy type-check criteria
    is_singleton=True,
    version=RootAgent.AGENT_VERSION,
    metadata={
        "type": RootAgent.AGENT_TYPE,
        "domain": RootAgent.AGENT_DOMAIN
    }
)