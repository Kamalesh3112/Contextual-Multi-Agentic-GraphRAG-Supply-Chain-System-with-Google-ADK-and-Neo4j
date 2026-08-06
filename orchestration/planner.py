"""
Responsibilities: Responsible for planning, decomposition and dependency analysis for the
multi-agent execution pipeline.
----------------
• Analyze execution requirements.
• Decompose complex tasks into smaller subtasks.
• Build execution plans.
• Create dependency graphs.
• Estimate execution complexity.
• Determine execution strategies.
• Provide execution metadata for scheduling.
"""

import json
import logging
from typing import List, Dict, Any, Set
from orchestration.llm_provider import OpenRouterADKAdapter, OpenRouterClient

logger = logging.getLogger("ADK.Orchestration.Planner")


class PlanningAgent(OpenRouterADKAdapter):
    """
    Decomposes user objectives into atomic tasks using high-parameter reasoning models.
    """
    def __init__(self) -> None:
        instruction = (
            "You are an expert Multi-Agent Task Decomposer. Break down user goals into distinct operational tasks. "
            "Identify required specialist capabilities: data_retrieval, risk_scoring, response_synthesis, context_retrieval. "
            "Output your analysis strictly in a JSON array of task objects."
        )
        super().__init__(name="PlanningAgent", instruction=instruction, runner=OpenRouterClient())

    def decompose(self, query: str, intent_meta: Dict[str, Any]) -> List[Dict[str, Any]]:
        logger.info("[PlanningAgent] Decomposing goal state into atomic tasks.")
        prompt = f"Decompose this user query: '{query}' with metadata parameters: {json.dumps(intent_meta)}"
        try:
            res = self.run(user_prompt=prompt)
            cleaned = res.text.strip().removeprefix("```json").removesuffix("```").strip()
            return json.loads(cleaned)
        except Exception as e:
            logger.error(f"[PlanningAgent] Planning failure: {e}. Executing default baseline plan.")
            return [
                {"task_id": "t1", "agent": "MemoryAgent", "capability": "context_retrieval", "depends_on": []},
                {"task_id": "t2", "agent": "GraphAgent", "capability": "graph_retrieval", "depends_on": ["t1"]},
                {"task_id": "t3", "agent": "RiskAgent", "capability": "risk_scoring", "depends_on": ["t2"]},
                {"task_id": "t4", "agent": "SynthesisAgent", "capability": "response_synthesis", "depends_on": ["t3"]}
            ]


class DependencyGraph:
    """
    Constructs, validates, and sorts directed acyclic dependencies between system tasks.
    """
    def __init__(self) -> None:
        self.nodes: Set[str] = set()
        self.adj: Dict[str, List[str]] = {}
        self.in_degree: Dict[str, int] = {}

    def build_graph(self, tasks: List[Dict[str, Any]]) -> None:
        for t in tasks:
            tid = t["task_id"]
            self.nodes.add(tid)
            if tid not in self.adj:
                self.adj[tid] = []
            if tid not in self.in_degree:
                self.in_degree[tid] = 0

            for dep in t.get("depends_on", []):
                self.nodes.add(dep)
                if dep not in self.adj:
                    self.adj[dep] = []
                self.adj[dep].append(tid)
                self.in_degree[tid] = self.in_degree.get(tid, 0) + 1

    def compute_topological_sort(self) -> List[str]:
        """
        Kahn's algorithm implementation to prevent circular loops and compute execution path vectors.
        """
        in_deg = {n: self.in_degree.get(n, 0) for n in self.nodes}
        queue = [n for n in self.nodes if in_deg[n] == 0]
        order = []

        while queue:
            curr = queue.pop(0)
            order.append(curr)
            for neighbor in self.adj.get(curr, []):
                in_deg[neighbor] -= 1
                if in_deg[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(self.nodes):
            raise ValueError("Circular dependency detected within execution plan graph nodes.")
        return order


class ExecutionPlanner:
    """
    Transforms raw task breakdowns into validated execution DAGs ready for the scheduler.
    """
    def __init__(self) -> None:
        self.agent = PlanningAgent()

    def generate_workflow_dag(self, raw_query: str, query_metadata: Dict[str, Any]) -> Dict[str, Any]:
        tasks = self.agent.decompose(raw_query, query_metadata)
        graph = DependencyGraph()
        graph.build_graph(tasks)
        sorted_steps = graph.compute_topological_sort()

        return {
            "workflow_id": f"wf_{hash(raw_query) & 0xffffffff}",
            "tasks": {t["task_id"]: t for t in tasks},
            "linear_execution_path": sorted_steps,
            "estimated_complexity": "HIGH" if len(tasks) > 4 else "MEDIUM"
        }