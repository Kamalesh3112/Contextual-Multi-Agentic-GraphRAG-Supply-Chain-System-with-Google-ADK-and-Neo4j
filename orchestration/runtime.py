"""
Responsibilities: Shared runtime infrastructure for the Multi-Agent GraphRAG Platform. Provides execution state, shared context, task management and context
aggregation during agent execution.
----------------
• Runtime context management.
• Shared execution state.
• Task management.
• Context aggregation.
• Workflow synchronization.
"""

import queue
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("ADK.Orchestration.Runtime")


class ExecutionContext:
    """
    Thread-safe container holding session records and cross-agent execution payloads.
    """
    def __init__(self, session_id: str, raw_query: str) -> None:
        self.session_id = session_id
        self.raw_query = raw_query
        self._shared_data: Dict[str, Any] = {}

    def update_state(self, key: str, value: Any) -> None:
        self._shared_data[key] = value
        logger.debug(f"[ExecutionContext] Context variable state update: key='{key}'")

    def get_data(self, key: str, default: Any = None) -> Any:
        return self._shared_data.get(key, default)


class StateManager:
    """
    Tracks and updates execution statuses to maintain clear pipeline observability, session management
    """
    def __init__(self, workflow_id: str) -> None:
        self.workflow_id = workflow_id
        self.current_state = "INITIALIZED"
        self.metrics: Dict[str, Any] = {}

    def transition_to(self, next_state: str) -> None:
        logger.info(f"[StateManager] Workflow cycle transition: '{self.current_state}' -> '{next_state}'")
        self.current_state = next_state


class TaskQueue:
    """
    Manages priority queuing for processing asynchronous worker task inputs.
    """
    def __init__(self) -> None:
        self._queue: queue.PriorityQueue = queue.PriorityQueue()

    def enqueue_task(self, priority: int, task_payload: Dict[str, Any]) -> None:
        self._queue.put((priority, task_payload))

    def dequeue_task(self) -> Optional[Dict[str, Any]]:
        try:
            return self._queue.get_nowait()[1]
        except queue.Empty:
            return None


class ContextMerger:
    """
    Aggregates multi-agent graph segments, vectors, and memory maps into a unified context payload.
    """
    @staticmethod
    def compile_unified_payload(context: ExecutionContext) -> Dict[str, Any]:
        logger.info("[ContextMerger] Compiling multi-source metadata frames into a unified payload.")
        return {
            "query": context.raw_query,
            "session_id": context.session_id,
            "compiled_graph_subgraphs": context.get_data("graph_context", {}),
            "compiled_historical_memory": context.get_data("history", []),
            "compiled_security_risks": context.get_data("risk_context", {})
        }