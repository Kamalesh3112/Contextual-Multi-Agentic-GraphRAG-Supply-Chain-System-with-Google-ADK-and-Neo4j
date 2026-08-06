"""
============================================================================
AI Observability Layer

Provides end-to-end observability for the Multi-Agent GraphRAG Platform.

This package enables monitoring, tracing, evaluation and validation of
reasoning agents, orchestration workflows, GraphRAG retrieval, MCP tools,
memory operations and LLM interactions.

Unlike traditional application logging, AI observability captures the
complete reasoning lifecycle including planning, retrieval, execution,
reflection and response generation.

Modules
-------
• langfuse_tracer.py
• traces.py
• metrics.py
• validators.py

Observability Scope
-------------------
• Agent Execution
• Workflow Execution
• GraphRAG Retrieval
• Memory Operations
• MCP Tool Calls
• LLM Requests
• Context Engineering
• Loop Engineering
• Performance Metrics

Primary Backend
---------------
Langfuse

Future Integrations
-------------------
• OpenTelemetry
• Prometheus
• Grafana
• Phoenix
• Arize AI

Consumed By
-----------
• Google ADK Agents
• Orchestration Layer
• GraphRAG Layer
• Memory Layer
• MCP SDK

Design Goal
-----------
Provide enterprise-grade AI observability enabling explainability,
monitoring and continuous optimization of multi-agent systems.
============================================================================
"""

import logging
from typing import Optional, Any
from pydantic import BaseModel, Field

# 1. Setup Package-Level Production Logging Interface
logger = logging.getLogger("GraphRAG.Observability")
logger.setLevel(logging.INFO)

# 2. Define System Package Metadata
__version__ = "1.0.0"
__backend__ = "Langfuse"


# Observability Configuration Definition
class ObservabilityConfig(BaseModel):
    """System container storing feature flags and cluster keys for telemetry layers."""
    ENABLE_TRACING: bool = True
    ENABLE_METRICS: bool = True
    ENVIRONMENT: str = "development"
    DEBUG_MODE: bool = True
    
    # Cloud Telemetry Endpoints
    LANGFUSE_BASE_URL: str = "https://langfuse.com"
    LANGFUSE_HOST: str = "http://localhost:3000"

    class Config:
        frozen = True


# Initialize Global Package Validation Configuration Config
obs_config = ObservabilityConfig()

# Module Subcomponent Registration Matrix

# Pre-populate export interfaces cleanly matching the visual disk tree layout
try:
    from .langfuse_tracer import LangfuseTracer
    from .traces import ActiveTelemetryTracer
    from .metrics import PerformanceMetricsCollector
    from .validators import OutputSchemaValidator
    
except ImportError as err:
    logger.warning(
        f"Observability Submodule Initialization Warning: Some modular elements could not "
        f"be completely pre-loaded from root directory spaces: {str(err)}. "
        f"Verify implementation filenames ('langfuse_tracer.py', 'traces.py', 'metrics.py', 'validators.py')."
    )


# Package-level Export Interface Matrix
__all__ = [
    # Metadata & Base Engine Configs
    "__version__",
    "__backend__",
    "obs_config",
    "logger",
    
    # Exposed Telemetry & Auditing Classes
    "LangfuseTracer",
    "ActiveTelemetryTracer",
    "PerformanceMetricsCollector",
    "OutputSchemaValidator",
]