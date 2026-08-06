"""
Responsibilities: Responsible for understanding user intent and preparing structured
execution requirements.
• Analyze user intent.
• Extract entities and relationships.
• Classify query type.
• Determine required capabilities.
• Estimate query complexity.
• Produce structured query metadata.
• Provide execution hints to the Planning Agent.

"""

# agents/query_agent.py
import logging
import json
from typing import Dict, Any, List, Optional
from agents.registry import global_registry
from orchestration.llm_provider import OpenRouterADKAdapter
from google.adk.tools import GoogleSearch

logger = logging.getLogger("ADK.QueryAgent")

class QueryAgent:
    AGENT_NAME = "QueryAgent"
    AGENT_VERSION = "1.0.0"
    AGENT_TYPE = "reasoning"
    AGENT_DOMAIN = "query_understanding"

    def __init__(self) -> None:
        self._adk_agent = OpenRouterADKAdapter(
            name=self.AGENT_NAME, 
            instruction="""
You are a highly analytical Retrieval and Query Agent.
Your primary role is to extract factual data from GraphRAG, provided inputs, data stores, or files.
You have access to Google Search for grounding. You must prioritize verifiable information.
If text, images, or documents are passed to you, analyze them thoroughly using your multimodal eyes.
Output your findings in structured JSON format contained within clear codeblocks.
""",
            tools=[GoogleSearch()],
            temperature=0.1
        )

    def register_agent(
        self,
        name: str = "query_agent",
        capabilities: Optional[set] = None,
        factory_or_instance: Any = None,
        version: str = "1.0.0",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        if capabilities is None:
            capabilities = {"data_retrieval", "web_grounding", "multimodal_analysis", "document_extraction"}
        if factory_or_instance is None:
            factory_or_instance = QueryAgent
        if metadata is None:
            metadata = {"tier": "data_layer"}

        global_registry.register_agent(name, capabilities, factory_or_instance, {"version": version, **metadata})

    def analyze(self, text_query: str, media_files: Optional[List[Any]] = None) -> Dict[str, Any]:
        logger.info(f"[{self.AGENT_NAME}] Performing intent mapping analysis.")
        response = self._adk_agent.run(f"Input query parameter target: {text_query}", files=media_files)
        try:
            return json.loads(response.text)
        except Exception:
            return {"entities": ["DefaultAsset"], "requires_graph": True, "requires_risk_check": True}

query_agent = QueryAgent()
global_registry.register_agent(QueryAgent.AGENT_NAME, {"intent_classification", "multimodal_extraction"}, query_agent, {"type": QueryAgent.AGENT_TYPE, "domain": QueryAgent.AGENT_DOMAIN})
