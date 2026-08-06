"""Bootstrap layer for MCP server.

Purpose:
   1. Registers all valid MCP tools with the server.
   2. Registers all valid MCP resources
   3. Validates the bootstrap configuration for the server.
   4. Centralizes the server and startup configuration for the MCP server
"""

from __future__ import annotations
from asyncio.log import logger
import logging

from typing import TYPE_CHECKING, Iterable

from config.settings import settings

from mcp_sdk.tools.base_tool import register_base_tools
from mcp_sdk.tools.memory_tool import register_memory_tools
from mcp_sdk.tools.neo4j_tool import register_neo4j_tools
from mcp_sdk.tools.risk_tool import register_risk_tools
from mcp_sdk.tools.sparql_tool import register_sparql_tools
from mcp_sdk.tools.traversal_tool import register_traversal_tools

from mcp_sdk.resources.graph_resources import register_graph_resources

noot_logger = logging.getLogger(__name__)

class BootstrapError(RuntimeError):
    """Exception Handling for Bootstrap errors..."""
    try:
        if settings.MCP_BOOTSTRAP:
            noot_logger.info("Bootstrapping MCP server...")
            register_base_tools()
            register_memory_tools()
            register_neo4j_tools()
            register_risk_tools()
            register_sparql_tools()
            register_traversal_tools()
            register_graph_resources()
            noot_logger.info("MCP server bootstrapped successfully.")
        else:
            noot_logger.info("MCP_BOOTSTRAP is set to False. Skipping bootstrap.")

    except Exception as e:
        noot_logger.error(f"Error while trying bootstrapping the MCP Server: {e}")
        noot_logger.backtrace(
            exc_info=True, message = "Error while trying bootstrapping the MCP Server", traceback_limit = 5
        )

class MCPBootstrapServer:
    """Bootstrap class for MCP server. """
    def __init__(self, server) -> None:
        self.server = server

    def initialize(self) -> None:
        """Initiates the bootstrap logic for registeration of tools and resources. """
        noot_logger.info("Initializing the bootstrap process for MCP tools...")
        self._validate_configuration()
        self.__register_tools()
        self.__register_resources()
        noot_logger.info("MCP Bootstrap process authorized and initialized successfully.")

    def _validate_configuration(self) -> None:
        """Validates mandatory configuration required before server startup"""
        required = {
            "OPENROUTER_API_KEY": settings.OPENROUTER_API_KEY,
            "Neo4j_URI": settings.Neo4j_URI,
            "NEO4J_USERNAME": settings.NEO4J_USERNAME,
            "Neo4j_PASSWORD": settings.Neo4j_PASSWORD,
            "LANGFUSE_SECRET_KEY": settings.LANGFUSE_SECRET_KEY,
            "LANGFUSE_PUBLIC_KEY": settings.LANGFUSE_PUBLIC_KEY,
            "OPENROUTER_BASE_URL": settings.OPENROUTER_BASE_URL,
            "REDIS_HOST": settings.REDIS_HOST,
        }

        missing = [key for key,value in required.items() if not value]

        if missing:
            raise BootstrapError(f"Missing required configuration: {', '.join(missing)}")

        noot_logger.info("Configuration validation check for MCP tools has passed")

    def _register_tools(self) -> None:
        """
        Registers every tools of MCP defined in the bootstrap configuration after passed validation checks."""

        noot_logger.info("Proceeding to register MCP tools since validation checks has passed")

        registrars: Iterable[callable] = [
            register_base_tools,
            register_memory_tools,
            register_neo4j_tools,
            register_risk_tools,
            register_sparql_tools,
            register_traversal_tools
        ]

        for register in registrars:
            register(self.server)

        logger.info(
            "Registered %s tools with the MCP server successfully.", len(registrars), register.__name__
        )

    def _register_resources(self) -> None:
        logger.info("Proceeding to register MCP resources since validation checks has passed")
        register_graph_resources(self.server)
        logger.info("Resources for GraphRAG-MCP server registered successfully.")


    def bootstrap(self: MCPBootstrapServer) -> None:
        """Bootstraps the MCP server with tools and resources."""
        self.initialize()
        return self.server