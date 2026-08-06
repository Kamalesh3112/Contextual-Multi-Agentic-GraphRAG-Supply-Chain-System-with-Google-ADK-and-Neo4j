"""
Responsibilities: Defines reusable execution workflows for the Multi-Agent GraphRAG Platform.
----------------
• Define execution workflows.
• Generate execution DAGs.
• Represent execution DAGs.
• Configure agent collaboration.
• Support sequential, parallel and hybrid workflows.
• Enable reusable execution pipelines.
"""

from typing import List, Dict, Any
from orchestration.router import orchestration_router

class WorkflowTemplate:
    """
    Blueprint structure definition wrapper used to load predefined configurations.
    """
    def __init__(self, template_name: str, sequence_steps: List[str]) -> None:
        self.template_name = template_name
        self.sequence_steps = sequence_steps


class StandardGraphRAGPipeline(WorkflowTemplate):
    """
    Standard corporate template pattern configuration enforcing clear data processing topologies.
    """
    def __init__(self) -> None:
        super().__init__(
            template_name="Standard_GraphRAG_Compliance_Pipeline",
            sequence_steps=["MemoryRetrieval", "GraphExtraction", "RiskAuditAssessment", "ExecutiveSynthesis"]
        )

    def run_pipeline(self, query: str, session_id: str) -> Dict[str, Any]:
        """
        Executes an incoming query directly against the pre-configured router.
        """
        return orchestration_router.route_and_execute(user_query=query, session_id=session_id)