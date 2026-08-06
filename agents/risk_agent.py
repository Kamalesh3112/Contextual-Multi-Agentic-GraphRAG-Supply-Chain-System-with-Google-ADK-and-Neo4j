"""
Responsibilities: Responsible for graph-aware risk reasoning and dependency analysis.
• Assess supply-chain risks.
• Analyze dependency propagation.
• Evaluate cascading failures.
• Compute risk scores.
• Explain risk factors.
• Generate structured risk insights.
• Coordinate graph-based risk reasoning.
• Convert graph knowledge into explainable risk intelligence.
"""

# agents/risk_agent.py
"""
===========================================================================
RiskAgent

Responsible for graph-aware risk reasoning and dependency analysis within 
the Multi-Agent GraphRAG platform.

Responsibilities
----------------
• Assess supply-chain risks.
• Analyze dependency propagation.
• Evaluate cascading failures.
• Compute risk scores.
• Explain risk factors.
• Generate structured risk insights.
• Coordinate graph-based risk reasoning.
• Convert graph knowledge into explainable risk intelligence.

Does NOT
---------
• Retrieve graph data directly from databases.
• Manage short-term conversation memory.
• Schedule multi-agent graph execution steps.
• Generate final user presentation responses.
• Execute framework-level orchestration logic.

Collaborates With
-----------------
• GraphAgent
• MemoryAgent
• SynthesisAgent

Design Goal
-----------
Convert granular graph node topologies into explainable, production-ready
risk intelligence utilizing structural analysis and deep model reasoning.
===========================================================================
"""

import json
import logging
from typing import Dict, Any, List, Optional
from google.adk.agents import Agent
from agents.registry import global_registry
from orchestration.llm_provider import OpenRouterADKAdapter, OpenRouterClient

logger = logging.getLogger("ADK.RiskAgent")


class RiskAgent(OpenRouterADKAdapter):
    """
    Graph Topology Risk Reasoning and Impact Assessment Agent.
    Subclasses OpenRouterADKAdapter to maintain complete type compliance with Google ADK.
    """

    AGENT_NAME = "RiskAgent"
    AGENT_VERSION = "1.0.0"
    AGENT_TYPE = "reasoning"
    AGENT_DOMAIN = "risk_analysis"

    def __init__(self) -> None:
        instruction_prompt = (
            "You are an expert Graph-Aware Security and Risk Intelligence Agent. "
            "Your objective is to evaluate network node topologies, dependency arcs, and supply-chain maps "
            "to discover hidden cascading failures, single points of failure (SPOF), and propagation risks. "
            "Analyze metrics such as connection centrality, node counts, and critical paths. "
            "You must respond with a raw, valid JSON object containing exactly these structural keys:\n"
            "{\n"
            "  \"risk_score\": 0.00,\n"
            "  \"level\": \"NOMINAL\" or \"CRITICAL\",\n"
            "  \"explainable_intelligence\": \"text reasoning analysis here\",\n"
            "  \"identified_vulnerabilities\": [\"list\", \"of\", \"issues\"]\n"
            "}"
        )
        
        runner_client = OpenRouterClient()
        
        super().__init__(
            name=self.AGENT_NAME, 
            instruction=instruction_prompt, 
            runner=runner_client
        )

    def assess_risk(self, graph_topology: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates propagation risks using programmatic graph characteristics 
        complemented by deep deep-parameter model reasoning.
        """
        logger.info(f"[{self.AGENT_NAME}] Initiating topology threat vector analysis.")
        
        nodes: List[Dict[str, Any]] = graph_topology.get("nodes", [])
        edges: List[Dict[str, Any]] = graph_topology.get("edges", [])
        
        # 1. Deterministic/Programmatic Feature Extraction Gate
        programmatic_warnings: List[str] = []
        base_calculated_score: float = 0.1
        
        if len(nodes) < 3:
            base_calculated_score = 0.5
            programmatic_warnings.append("Low operational redundancy detected in isolated subgraph topology boundary.")
            
        if len(nodes) > 0 and (len(edges) / len(nodes)) > 3.0:
            base_calculated_score = max(base_calculated_score, 0.6)
            programmatic_warnings.append("High relationship density arc matrix detected; potential for fast cascading blast radius values.")

        # 2. Deep Structural Model Reasoning Path (Nemotron 550B / Qwen Fallback)
        reasoning_prompt = (
            f"Evaluate this retrieved operational graph subgraph context for vulnerabilities:\n"
            f"Graph Node Count: {len(nodes)}\n"
            f"Graph Edge Relationship Count: {len(edges)}\n"
            f"Full JSON Structure Profile: {json.dumps(graph_topology)}\n"
            f"Local Rule Engine Warnings Found: {programmatic_warnings}\n"
            f"Generate structural impact risk insights following your strict JSON schema format guidelines."
        )
        
        try:
            # Execute inference loop through standard ADK object paths (.run)
            adk_output = self.run(user_prompt=reasoning_prompt)
            cleaned_text = adk_output.text.strip()
            
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
                
            parsed_analysis: Dict[str, Any] = json.loads(cleaned_text.strip())
            
            parsed_analysis["identified_vulnerabilities"] = list(
                set(parsed_analysis.get("identified_vulnerabilities", []) + programmatic_warnings)
            )
            parsed_analysis["compliance_checked"] = True
            
            return parsed_analysis

        except Exception as e:
            logger.error(f"[{self.AGENT_NAME}] Advanced reasoning exception: {e}. Falling back to clean deterministic parameters.")
            # Fail-safe operational compliance packet returned if api layer times out or drops frames
            return {
                "risk_score": base_calculated_score,
                "level": "CRITICAL" if base_calculated_score >= 0.6 else "NOMINAL",
                "explainable_intelligence": "Model reasoning layer unavailable. Fallback data calculated programmatically from topology metrics.",
                "identified_vulnerabilities": programmatic_warnings,
                "compliance_checked": True,
                "backup_mode_active": True
            }


risk_agent_instance = RiskAgent()

# Formally bind into our centralized thread-safe registration controller
global_registry.register_agent(
    name=RiskAgent.AGENT_NAME,
    capabilities={
        "risk_scoring", 
        "dependency_analysis", 
        "compliance", 
        "cascading_failure_evaluation"
    },
    instance=risk_agent_instance,
    metadata={
        "type": RiskAgent.AGENT_TYPE, 
        "domain": RiskAgent.AGENT_DOMAIN,
        "version": RiskAgent.AGENT_VERSION
    }
)