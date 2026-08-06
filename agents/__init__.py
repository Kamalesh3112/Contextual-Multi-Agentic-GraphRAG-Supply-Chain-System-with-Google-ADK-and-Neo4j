"""
Package initialization
"""
import logging
from google.adk.agents import Agent
from .registry import ADKAgentRegistry

logger = logging.getLogger("google.adk.agents.init")

try:
    import agents.root_agent
    import agents.risk_agent
    import agents.query_agent
    import agents.graph_agent
    import agents.memory_agent
    import agents.synthesis_agent

    __all__ = ["root_agent", "ADKAgentRegistry"]
    logger.info("Successfully initialized the ADK Multi-Agent GraphRAG Package.")

except ImportError as e:
    logger.error(f"Failed to bootstrap ADK package components: {e}")
    raise e