"""
============================================================================
Application Bootstrap Layer

Provides the application entry point for the Multi-Agent GraphRAG Platform.

This package initializes the complete runtime environment required by the
platform including configuration, infrastructure services, AI components
and application lifecycle management.

Modules
-------
• config.py
• main.py

Initializes
-----------
• Configuration
• Logging
• Langfuse
• Neo4j
• Milvus
• NAMS
• MCP SDK
• Google ADK Agents
• Orchestration Layer

Design Goal
-----------
Provide a clean application bootstrap process while keeping business
logic separated from infrastructure initialization.
============================================================================
"""

import logging
from typing import Optional, Any

# 1. Setup Root Platform Logging Environment Trace Footprints
logger = logging.getLogger("GraphRAG.App")
logger.setLevel(logging.INFO)

# 2. Package Level Global Manifest Properties
__version__ = "1.0.0"
__runtime_status__ = "uninitialized"

# Module Subcomponent Registration & Verification
try:
    # Explicitly links the core pipeline blocks matching the physical disk tree layout
    from .config import Settings, settings
    from .main import run_application_bootstrap
    
except ImportError as err:
    logger.critical(
        f"Critical Infrastructure Fault: Failed to initialize application bootstrap submodules "
        f"within the app namespace. Verify workspace path consistency. Error: {str(err)}"
    )

# -----------------------------------------------------------------------------
# Public API Surface Export Matrix
# -----------------------------------------------------------------------------

__all__ = [
    # Metadata & Base Engine Configs
    "__version__",
    "__runtime_status__",
    "logger",
    
    # Configuration Singletons
    "Settings",
    "settings",
    
    # Core Entry Executables
    "run_application_bootstrap",
]