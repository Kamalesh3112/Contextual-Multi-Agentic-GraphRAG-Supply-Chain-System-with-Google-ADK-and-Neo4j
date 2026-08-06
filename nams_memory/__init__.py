"""
#Neo4j's Agent Memory Service (NMS)
 AMS combines,
    - Long-term memory
    - Short-term memory
    - Reasoning memory

Cognitive Memory Layer for the Multi-Agent GraphRAG Platform.

This package provides persistent memory capabilities enabling reasoning
agents to recall previous interactions, execution history, entities,
reflections and reasoning traces.

Unlike traditional conversational memory, NAMS manages multiple forms of
long-term and short-term knowledge that collectively support Context
Engineering and GraphRAG.

Memory Types
------------
• Conversation Memory
• Entity Memory
• Reasoning Memory
• Reflection Memory
• Execution Memory (future)
• Tool Memory (future)
"""

"""Cognitive Memory Layer for the Multi-Agent GraphRAG Platform.

Neo4j's Agent Memory Service (AMS / NAMS) combines:
    - Long-term memory
    - Short-term memory
    - Reasoning memory

This package provides persistent memory capabilities enabling reasoning agents to 
recall previous interactions, execution history, entities, reflections, and reasoning traces.
Unlike traditional conversational memory, NAMS manages multiple forms of long-term and 
short-term knowledge that collectively support Context Engineering and GraphRAG.

Memory Types:
    - Conversation Memory: Short/Long-term episodic dialog structures.
    - Entity Memory: Knowledge graph-extracted domain entities and schemas.
    - Reasoning Memory: Dynamic step-by-step cognitive agent execution pathways.
    - Reflection Memory: Higher-order synthesized observations and abstractions.
    - Execution Memory: (Future) Task loop scheduling tracking systems.
    - Tool Memory: (Future) Execution analytics for external tool performance.
"""

import logging
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("GraphRAG.NAMSMemory")
logger.setLevel(logging.INFO)


__version__ = "1.0.0"
__author__ = "GraphRAG Core Architecture Team"

# -----------------------------------------------------------------------------
# Configuration Layer
# -----------------------------------------------------------------------------

class NAMSRuntimeConfig(BaseModel):
    """Configuration container for Neo4j's Agent Memory Service (AMS/NAMS)."""
    AMS_URL: str = "https://neo4jlabs.com"
    NAMS_MEMORY_API: Optional[str] = Field(default=None, repr=False)
    EMBEDDING_MODEL: str = "BAAI/bge-large-en-v1.5"
    DEBUG_MODE: bool = True

    class Config:
        frozen = True


# Initialize Global Memory Layer Runtime Configuration
nams_config = NAMSRuntimeConfig()

# -----------------------------------------------------------------------------
# Protected Module Component Registration & Verification
# -----------------------------------------------------------------------------

try:
    # Explicitly hooks into the underlying physical file-tree architecture
    from .nams_client import NAMSClient
    from .conversation_memory import ConversationMemoryStore
    from .entity_memory import EntityMemoryGraph
    from .reasoning_trace_memory import ReasoningTraceMemory
    from .reflection_memory import ReflectionMemoryEngine
    from .memory_manager import NAMSMemoryManager

except ImportError as err:
    logger.critical(
        f"Initialization Breakdown: Failed to securely load core cognitive submodules "
        f"inside the nams_memory namespace. Verify workspace path consistency. Error: {str(err)}"
    )

# -----------------------------------------------------------------------------
# Public API Surface Export Matrix
# -----------------------------------------------------------------------------

__all__ = [
    # Metadata & Base Configs
    "__version__",
    "nams_config",
    "logger",
    
    # Core Infrastructure Framework Transport
    "NAMSClient",
    "NAMSMemoryManager",
    
    # Core Cognitive Structural Components
    "ConversationMemoryStore",
    "EntityMemoryGraph",
    "ReasoningTraceMemory",
    "ReflectionMemoryEngine",
]