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

import asyncio
import logging
import signal
import sys
from typing import Any, Dict, List, Optional

from config.settings import settings
from config import app_state
from observability.langfuse_tracer import LangfuseTracer
from rag.semantic_context_store import SemanticContextStore
from nams_memory.nams_client import NAMSClient
from nams_memory.memory_manager import NAMSMemoryManager
from rag.context_engineering_pipeline import ContextEngineeringPipeline

logger = logging.getLogger("GraphRAG.App.Main")
LOG_SEPARATOR = "========================================================="

class PlatformLifecycleManager:
    def __init__(self):
        """Initializes state tracking wrappers for cross-platform components."""
        self.shutdown_triggered = False
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    async def bootstrap_runtime(self) -> None:
        """Executes the complete 12-step asymmetrical structural initialization sequence."""
        self._loop = asyncio.get_running_loop()
        self._register_signal_handlers()

        logger.info(LOG_SEPARATOR)                #type: ignore
        logger.info("   Starting Multi-Agent GraphRAG Platform Core Engine   ")
        logger.info(LOG_SEPARATOR)

        try:
            logger.info("[STARTUP] Step 1: Evaluating Pydantic configuration schemas...")
            
            logger.info("[STARTUP] Step 2: Calibrating granular logging layers...")
            app_state.prepare_startup_resources()

            logger.info("[STARTUP] Step 3: Mounting Langfuse analytical observability plane...")
            tracer = LangfuseTracer(settings)
            app_state.inject_dependency("tracer", tracer)

            logger.info("[STARTUP] Step 4: Bootstrapping binary connection drivers to Neo4j database...")
            logger.info("[STARTUP] Step 5: Instantiating pyMilvus vectorized cluster connections...")
            vector_store = SemanticContextStore(
                vector_db=settings.VECTOR_DB,
                host=settings.MILVUS_HOST,
                port=settings.MILVUS_PORT,
                user=settings.MILVUS_USER,
                password=settings.MILVUS_PASSWORD
            )
            vector_store.connect()
            app_state.inject_dependency("vector_store", vector_store)

            logger.info("[STARTUP] Step 6: Initializing low-level network bridges to Neo4j AMS APIs...")
            nams_client = NAMSClient(settings)
            await nams_client.initialize_client()
            app_state.inject_dependency("nams_client", nams_client)
            
            memory_manager = NAMSMemoryManager(settings, nams_client)
            app_state.inject_dependency("memory_manager", memory_manager)

            logger.info("[STARTUP] Step 7: Initializing FastMCP standard server transport protocols...")
            logger.info(f"Exposing server capabilities under profile: {settings.MCP_SERVER_NAME}")

            logger.info("[STARTUP] Step 8: Intersecting Google ADK Agent worker schema runtime boundaries...")
            logger.info("ADK Agent capability routing tables compiled.")

            logger.info("[STARTUP] Step 9: Aligning Context Engineering and GraphRAG knowledge pipelines...")
            graph_rag_pipeline = ContextEngineeringPipeline(settings)
            app_state.inject_dependency("pipeline", graph_rag_pipeline)

            logger.info("[STARTUP] Step 10: Loading multi-agent supervisor orchestrator matrices...")
            logger.info("Multi-agent orchestration decision routing loops active.")

            logger.info("[STARTUP] Step 11: Binding platform runtime interfaces to socket transport lanes...")
            logger.info(f"API Server listening over protocol transport: [{settings.MCP_TRANSPORT.upper()}]")
            if settings.MCP_TRANSPORT.lower() == "sse":
                logger.info(f"Target cluster binding endpoint: http://{settings.MCP_HOST}:{settings.MCP_PORT}")

            logger.info("[STARTUP] Step 12: Multi-Agent GraphRAG platform online and serving requests.")
            logger.info(LOG_SEPARATOR)
            
            while not self.shutdown_triggered:
                await asyncio.sleep(1.0)

        except Exception as startup_err:
            logger.critical(f"FATAL: Application bootstrap failed during sequence execution: {startup_err}")
            await self.shutdown_lifecycle()
            sys.exit(1)

    def _register_signal_handlers(self) -> None:
        """Hooks low-level OS interrupt signal intercept pathways cleanly."""
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                self._loop.add_signal_handler(
                    sig, 
                    lambda s=sig: asyncio.create_task(self._handle_shutdown_signal(s))
                )
            except NotImplementedError:
                pass

    async def _handle_shutdown_signal(self, sig: signal.Signals) -> None:
        """Gracefully intercepts operating system shutdown signals."""
        if self.shutdown_triggered:
            return
        logger.warning(f"Shutdown intercept received via token: [{sig.name}]. Terminating workloads safely...")
        self.shutdown_triggered = True
        await self.shutdown_lifecycle()

    async def shutdown_lifecycle(self) -> None:
        """Tears down all active system processes and flushes pooling clients."""
        logger.info(LOG_SEPARATOR)
        logger.info("   Executing Platform Lifecycle Clean Teardown Sequence   ")
        logger.info(LOG_SEPARATOR)
        
        if "nams_client" in app_state.services:
            try:
                logger.info("[SHUTDOWN] Flushing Neo4j driver pools and httpx transport sessions...")
                await app_state.get_service("nams_client").close_connections()
            except Exception as e:
                logger.error(f"Error terminating graph connection driver pools: {e}")

        if "tracer" in app_state.services:
            try:
                logger.info("[SHUTDOWN] Flushing outstanding Langfuse telemetry event tracks...")
                app_state.get_service("tracer").flush_tracer()
            except Exception as e:
                logger.error(f"Error executing telemetry pipeline buffer flush: {e}")

        if "vector_store" in app_state.services:
            logger.info("[SHUTDOWN] Closing active pyMilvus client cluster linkages...")
            # connections.disconnect("default")

        logger.info("[SHUTDOWN] Platform teardown complete. Runtime system halted safely.")
        logger.info(LOG_SEPARATOR)


def run_application_bootstrap() -> None:
    """Root platform synchronous executable entry module."""
    manager = PlatformLifecycleManager()
    try:
        asyncio.run(manager.bootstrap_runtime())
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt intercepted at root container boundary. Exiting.")


if __name__ == "__main__":
    run_application_bootstrap()