"""
MCP Server Configurations

via: FastMCP SDK
Server + Context + OpenTelemetry + ((FastAPI + FastMCP))

 - Bootstrap Fast API
 - Register MCP Tool Registry
 - Registry API Routes
 - Configure lifespan
 - Configure logging
 - Configure observability
 - Concurrent initailization and shutdown of server and tools
 - Integrate Bootstrap class for MCP tools registeration under defined server class
 - Expose health endpoints
 - Start the MCP Server
 
Fast MCP implementation that will call bootstrap class for requesting for regitered and authenticated MCP tools
"""

from __future__ import annotations
import logging
import uvicorn
import asyncio
from contextlib import asynccontextmanager
from config.settings import settings
from config.redis_config import redis_config
from nams_memory.memory_manager import memory_manager
from graph.neo4j_client import neo4j_client
from observability.langfuse_tracer import langfuse_tracer
from rag.semantic_context_store import vector_store

from fastapi import FastAPI
from fastmcp import FastMCP
from mcp_sdk.bootstrap import BootstrapError, MCPBootstrapServer

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastMCP):
    """Lifespan context manager for FastMCP application.
    """

    logger = logging.info("Starting and initializing the GraphRAG MCP Server")
    try:
        await asyncio.gather(
            neo4j_client.connect(),
            vector_store.connect(),
            redis_config.connect(),
            memory_manager.connect(),
            vector_store.connect(),
            langfuse_tracer.connect(),
            return_exceptions = False
        )
        logger.info("Context Infrastructure initialized successfully.")
        yield

    finally:
        logger.info("Stopping the GraphRAG MCP Server and cleaning up resources")

        await asyncio.gather(
            neo4j_client.close(),
            vector_store.close(),
            redis_config.close(),
            memory_manager.shutdown(),
            vector_store.close(),
            langfuse_tracer.shutdown(),
            return_exceptions = True
        )

def create_server() -> FastMCP:
    """Creates and configures the FastMCP backend server"""
    logger.info("Creating the GraphRAG FastMCP server instance...")

    app = FastAPI(title = "GraphRAG MCP Server", version = "1.0.0")
 
    server = FastMCP(
        app = app,
        name = settings.MCP_SERVER_NAME,
        version = settings.MCP_SERVER_VERSION,
        lifespan = lifespan
    )

    bootsrap_server = MCPBootstrapServer(server)
    bootsrap_server.initialize()

    logger.info("GraphRAG FastMCP server instance created successfully.")

    return server

server = create_server()

if __name__ == "__main__":
    logger.info("Launching GraphRAG MCP Server...Please wait while the server is starting up...")
    uvicorn.run(server.app, host = "0.0.0.0", port = 8000)