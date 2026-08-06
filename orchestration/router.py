"""
Responsibilities: Responsible for selecting the most appropriate execution workflow based on
the user's intent, execution requirements and planning results.
----------------
• Route execution requests.
• Select workflows.
• Delegate execution.
• Coordinate planner and scheduler interaction.
"""

import logging
from typing import Dict, Any, Optional
from orchestration.planner import ExecutionPlanner
from orchestration.scheduler import AgentScheduler
from orchestration.runtime import ExecutionContext, StateManager, ContextMerger
from agents.registry import global_registry

logger = logging.getLogger("ADK.Orchestration.Router")


class OrchestrationRouter:
    """
    Central router that receives the user input, generates the task execution plan, 
    and drives the components through the multi-agent graph safely.
    """
    def __init__(self) -> None:
        self.planner = ExecutionPlanner()
        self.scheduler = AgentScheduler()

    def route_and_execute(self, user_query: str, session_id: str, media_assets: Optional[list] = None) -> Dict[str, Any]:
        logger.info(f"[OrchestrationRouter] Incoming transaction routing interception request for user payload session: {session_id}")
        
        # 1. Instantiate stateful tracking contexts
        context = ExecutionContext(session_id, user_query)
        
        # 2. Extract initial intent parameters via QueryAgent capability discovery
        query_agent_meta = global_registry.discover_by_capability("intent_classification")
        if not query_agent_meta:
            raise RuntimeError("Pipeline fault: Active QueryAgent resource module missing in registry catalog.")
        
        query_agent_instance = global_registry.get_or_create_instance(query_agent_meta[0]["name"])
        intent_analysis = query_agent_instance.analyze(user_query, media_assets)
        context.update_state("entities", intent_analysis.get("entities", []))

        # 3. Compute execution paths (DAGs) using the Planner
        workflow_dag = self.planner.generate_workflow_dag(user_query, intent_analysis)
        state_tracker = StateManager(workflow_dag["workflow_id"])
        
        state_tracker.transition_to("RUNNING")
        self.scheduler.dispatch_workflow(workflow_dag, context)
        
        state_tracker.transition_to("COMPILING")
        compiled_meta_frame = ContextMerger.compile_unified_payload(context)
        
        synthesis_node = global_registry.get_or_create_instance("SynthesisAgent")
        if not synthesis_node:
            raise RuntimeError("Pipeline fault: SynthesisAgent reference unavailable at final step.")
            
        final_executive_summary = synthesis_node.generate_response(
            user_input=user_query,
            graph_context=compiled_meta_frame["compiled_graph_subgraphs"],
            risk_context=compiled_meta_frame["compiled_security_risks"],
            history=compiled_meta_frame["compiled_historical_memory"]
        )
        
        state_tracker.transition_to("COMPLETED")
        return {
            "workflow_id": workflow_dag["workflow_id"],
            "status": state_tracker.current_state,
            "payload": final_executive_summary
        }

orchestration_router = OrchestrationRouter()