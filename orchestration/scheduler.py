"""
Responsibilities: Execution engine responsible for coordinating reasoning agents and worker
agents.
The scheduler determines how execution should occur after planning has
completed.
----------------
• Agent scheduling.
• Workflow execution.
• Parallel execution.
• Sequential execution.
• Loop execution.
• Retry handling.
• Execution monitoring.
• Worker allocation.
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List
from agents.registry import global_registry

logger = logging.getLogger("ADK.Orchestration.Scheduler")


class SequentialExecutor:
    """Handles deep multi-stage dependent execution components in serial lock step."""
    @staticmethod
    def execute_chain(tasks: List[Dict[str, Any]], runtime_context: Any) -> None:
        for task in tasks:
            agent_name = task["agent"]
            method_target = task.get("method", "run")
            logger.info(f"[SequentialExecutor] Launching serial processing step: {agent_name}.{method_target}")
            
            agent_instance = global_registry.get_or_create_instance(agent_name)
            if not agent_instance:
                raise RuntimeError(f"Scheduling target agent runtime resource missing: '{agent_name}'")

            # Route context mappings dynamically based on structural agent footprints
            if agent_name == "MemoryAgent":
                res = agent_instance.retrieve_context(runtime_context.session_id)
                runtime_context.update_state("history", res)
            elif agent_name == "GraphAgent":
                res = agent_instance.retrieve(runtime_context.get_data("entities", []))
                runtime_context.update_state("graph_context", res)
            elif agent_name == "RiskAgent":
                res = agent_instance.assess_risk(runtime_context.get_data("graph_context", {}))
                runtime_context.update_state("risk_context", res)


class ParallelExecutor:
    """Executes detached, non-dependent task arrays concurrently using clean thread allocation blocks."""
    def __init__(self, max_workers: int = 4) -> None:
        self.pool = ThreadPoolExecutor(max_workers=max_workers)

    def execute_concurrently(self, tasks: List[Dict[str, Any]], runtime_context: Any) -> None:
        futures = {}
        for task in tasks:
            agent_name = task["agent"]
            agent_instance = global_registry.get_or_create_instance(agent_name)
            if agent_instance:
                logger.info(f"[ParallelExecutor] Enqueuing non-blocking worker thread resource: {agent_name}")
                # Mock execution proxy maps for asynchronous worker scaling
                if agent_name == "GraphAgent":
                    f = self.pool.submit(agent_instance.retrieve, runtime_context.get_data("entities", []))
                    futures[f] = ("graph_context", agent_name)

        for future in as_completed(futures):
            key, agent = futures[future]
            try:
                data = future.result()
                runtime_context.update_state(key, data)
            except Exception as e:
                logger.error(f"[ParallelExecutor] Asynchronous processing trace fault on agent '{agent}': {e}")


class LoopController:
    """Implements Loop Engineering bounds for iterative verification loops."""
    @staticmethod
    def evaluate_loop_criteria(context: Any, current_depth: int, max_loops: int = 2) -> bool:
        risk_data = context.get_data("risk_context", {})
        # If risk evaluation fails or remains critical, invoke a verification cycle loop
        if risk_data.get("status") == "CRITICAL" and current_depth < max_loops:
            logger.warning(f"[LoopController] Optimization loop criteria matched. Re-routing execution cycle. Step depth: {current_depth}")
            return True
        return False


class AgentScheduler:
    """
    The orchestrator that consumes workflow definitions and handles the execution strategy.
    """
    def __init__(self) -> None:
        self.sequential = SequentialExecutor()
        self.parallel = ParallelExecutor()
        self.loop_mgr = LoopController()

    def dispatch_workflow(self, dag: Dict[str, Any], runtime_context: Any) -> None:
        logger.info(f"[AgentScheduler] Dispatching workflow pipeline tasks. Execution strategy profile: {dag['estimated_complexity']}")
        
        tasks_map = dag["tasks"]
        path = dag["linear_execution_path"]
        
        # Hydrate execution task list
        ordered_tasks = [tasks_map[tid] for tid in path if tid in tasks_map]
        
        loop_depth = 0
        while True:
            # Segment into baseline execution chains
            self.sequential.execute_chain(ordered_tasks, runtime_context)
            
            if not self.loop_mgr.evaluate_loop_criteria(runtime_context, loop_depth):
                break
            loop_depth += 1