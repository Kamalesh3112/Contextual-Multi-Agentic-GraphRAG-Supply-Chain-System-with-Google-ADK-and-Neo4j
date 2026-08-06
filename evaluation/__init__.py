"""
============================================================================
AI Evaluation & Benchmarking Layer

Provides systematic evaluation, benchmarking and validation for the
Multi-Agent GraphRAG Platform.

This package measures the quality of GraphRAG retrieval, agent reasoning,
workflow execution and response generation across standardized evaluation
datasets.

Unlike traditional software testing, AI evaluation focuses on retrieval
quality, reasoning accuracy, context engineering effectiveness and
response reliability.

Modules
-------
• benchmark_queries.py
• test_queries.py
• metrics.py

Evaluation Scope
----------------
• Query Understanding
• GraphRAG Retrieval
• Context Engineering
• Multi-Agent Reasoning
• Graph Traversal
• Risk Analysis
• Response Generation
• Workflow Execution

Evaluated Components
--------------------
• Google ADK Agents
• Orchestration Layer
• Graph Layer
• RAG Layer
• NAMS Memory
• MCP SDK

Design Goal
-----------
Provide repeatable, measurable and explainable evaluation for enterprise
GraphRAG systems while enabling continuous optimization of retrieval,
reasoning and response quality.
============================================================================
"""

import logging
from typing import Optional, Any, List
from pydantic import BaseModel, Field

# 1. Setup Package-Level Production Logging
logger = logging.getLogger("GraphRAG.Evaluation")
logger.setLevel(logging.INFO)

# 2. Package Metadata
__version__ = "1.0.0"
__framework__ = "GraphRAG_Benchmarking_Suite"

# -----------------------------------------------------------------------------
# Evaluation Configuration Schema
# -----------------------------------------------------------------------------

class EvaluationConfig(BaseModel):
    """Configuration container for defining evaluation metrics and criteria."""
    RUN_BENCHMARKS_ON_BOOT: bool = False
    SAMPLE_RATE: float = 1.0
    MIN_ACCEPTABLE_FAITHFULNESS: float = 0.85
    MIN_ACCEPTABLE_RELEVANCE: float = 0.80
    EVAL_ENVIRONMENT: str = "testing"

    class Config:
        frozen = True


# Initialize Global Runtime Configurations
eval_config = EvaluationConfig()

# -----------------------------------------------------------------------------
# Protected Module Component Registration & Verification
# -----------------------------------------------------------------------------

try:
    # Explicitly hooks into the underlying physical file-tree architecture
    from .benchmark_queries import BenchmarkQueryRegistry
    from .test_queries import TestQueryRunner
    from .metrics import RAGQualityEvaluator
    
except ImportError as err:
    logger.warning(
        f"Evaluation Layer Lazy-Load Warning: Some submodules could not be fully pre-loaded "
        f"from root directories: {str(err)}. Ensure 'benchmark_queries.py', 'test_queries.py', "
        f"and 'metrics.py' exist within your file tree."
    )

# -----------------------------------------------------------------------------
# Public API Surface Export Matrix
# -----------------------------------------------------------------------------

__all__ = [
    # Metadata & Base Configs
    "__version__",
    "__framework__",
    "eval_config",
    "logger",
    
    # Core Evaluation Engine Blocks
    "BenchmarkQueryRegistry",
    "TestQueryRunner",
    "RAGQualityEvaluator",
]