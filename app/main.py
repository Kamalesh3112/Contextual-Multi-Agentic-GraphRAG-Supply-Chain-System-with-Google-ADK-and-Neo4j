"""
============================================================================
Application Entry Point

Primary startup module for the Multi-Agent GraphRAG Platform.

Responsible for initializing all platform components and starting the
application runtime.

This module serves as the orchestration entry point for infrastructure,
AI services and application lifecycle management.

Startup Sequence
----------------
1. Load configuration.
2. Initialize logging.
3. Initialize Langfuse.
4. Connect Neo4j.
5. Connect Milvus.
6. Connect NAMS.
7. Initialize MCP SDK.
8. Register Google ADK agents.
9. Initialize GraphRAG.
10. Initialize orchestration layer.
11. Start API server.
12. Begin serving requests.

Responsibilities
----------------
• Bootstrap application.
• Configure infrastructure.
• Initialize AI platform.
• Register services.
• Configure dependency injection.
• Start API server.
• Handle graceful shutdown.
• Manage application lifecycle.
"""
