"""
GraphRAG Knowledge Intelligence Layer

This package provides the complete Retrieval-Augmented Generation (RAG)
pipeline powering the Multi-Agent GraphRAG Platform.

Unlike traditional RAG systems, this package combines multiple retrieval
strategies including vector search, graph traversal, semantic reranking,
memory retrieval and context construction.

Responsibilities:
----------------
• Semantic retrieval.
• Graph-aware retrieval.
• Hybrid retrieval.
• Multi-hop knowledge expansion.
• Embedding generation.
• Context construction.
• Retrieval optimization.
• Retrieval ranking.
"""

"""
GraphRAG Knowledge Intelligence Layer

This package provides the complete Retrieval-Augmented Generation (RAG)
pipeline powering the Multi-Agent GraphRAG Platform.

Unlike traditional RAG systems, this package combines multiple retrieval
strategies including vector search, graph traversal, semantic reranking,
memory retrieval and context construction.

Responsibilities:
----------------
• Semantic retrieval.
• Graph-aware retrieval.
• Hybrid retrieval.
• Multi-hop knowledge expansion.
• Embedding generation.
• Context construction.
• Retrieval optimization.
• Retrieval ranking.
"""

import logging
import os
from typing import Any, Dict, List, Optional, Protocol

# Configure structured package logging
logger = logging.getLogger(__name__)

__version__ = "1.0.0"

# =====================================================================
# Configuration & Environment Assertions
# =====================================================================

DEFAULT_EMBEDDING_MODEL = "BAAI/bge-large-en-v1.5"
DEFAULT_LLM_PROVIDER = "openrouter"
DEFAULT_LLM_MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"
DEFAULT_FALLBACK_MODEL = "qwen/qwen3-7-plus"
DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"

EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", DEFAULT_LLM_PROVIDER)
LLM_MODEL: str = os.getenv("LLM_MODEL", DEFAULT_LLM_MODEL)
FALLBACK_MODEL: str = os.getenv("FALLBACK_MODEL", DEFAULT_FALLBACK_MODEL)
OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", DEFAULT_BASE_URL)
OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")

# Neo4j Agent Memory Service (AMS) & MCP Integration Settings
NEO4J_AMS_URL: str = os.getenv("NEO4J_AMS_URL", "https://memory.neo4jlabs.com")
NAMS_MEMORY_API: str = os.getenv("NAMS_MEMORY_API", "True").lower() == "true"


def validate_environment() -> None:
    """Validates required authentication tokens and endpoints."""
    if LLM_PROVIDER == "openrouter" and not OPENROUTER_API_KEY:
        logger.warning(
            "OPENROUTER_API_KEY is not set. API calls to OpenRouter providers will fail "
            "unless targeted strictly at explicit public endpoints."
        )
    logger.info(
        f"GraphRAG initialized with Embedding Model: {EMBEDDING_MODEL}. "
        f"Neo4j AMS Auto-Embedding: {NAMS_MEMORY_API}"
    )


# Execute package-level system validation
validate_environment()

# =====================================================================
# Core RAG Interfaces & Protocols
# =====================================================================

class RetrievalStrategy(Protocol):
    """Protocol defining the operational boundary of structural retrieval strategies."""
    async def retrieve(self, query: str, limit: int = 5, **kwargs: Any) -> List[Dict[str, Any]]:
        ...


class ContextBuilder(Protocol):
    """Protocol for structuring raw multi-modal and structural outputs into context blocks."""
    def construct_context(self, retrieved_data: List[Dict[str, Any]], max_tokens: int) -> str:
        ...

# =====================================================================
# Public Package Exports
# =====================================================================

# Expose clean interfaces from the sub-modules to abstract subsystem internal layout
# Note: Ensure these components are implemented inside their respective source files.
try:
    from .context_engineering_pipeline import ContextPipeline
    from .context_fusion import ContextFusionEngine
    from .context_optimizer import ContextOptimizer
    from .context_retreiver import ContextRetriever  # Fixed typo as seen in file explorer layout
    from .embedding_model import EmbeddingEngine
    from .semantic_context_store import SemanticContextStore
except ImportError as e:
    logger.error(f"Failed to bind GraphRAG subcomponents: {e}")
    # Fallbacks or structural stubs can be set here if resilient degradations are expected

__all__ = [
    # Top-Level Infrastructure Configurations
    "EMBEDDING_MODEL",
    "LLM_PROVIDER",
    "LLM_MODEL",
    "FALLBACK_MODEL",
    "OPENROUTER_BASE_URL",
    "OPENROUTER_API_KEY",
    "NEO4J_AMS_URL",
    "NAMS_MEMORY_API",
    
    # Structural System Components
    "ContextPipeline",
    "ContextFusionEngine",
    "ContextOptimizer",
    "ContextRetriever",
    "EmbeddingEngine",
    "SemanticContextStore",
    
    # Interface Specifications
    "RetrievalStrategy",
    "ContextBuilder",
]