"""
Application Configuration Module

Responsible for initializing and validating application-wide
configuration before the GraphRAG platform starts.

Unlike settings.py, which defines configuration values, this module
assembles, validates and prepares runtime configuration for the entire
application.

Responsibilities
----------------
• Load application configuration.
• Initialize runtime settings.
• Validate required environment variables.
• Configure infrastructure services.
• Configure dependency injection.
• Prepare application state.
• Initialize startup resources.
"""

import os
import logging
from typing import Dict, Any, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Setup Core Root Logging Configuration
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("GraphRAG.App.Config")


class Settings(BaseSettings):
    """Pydantic system validation layout tracking all environmental infrastructure properties."""
    
    # Neo4j Graph Cluster Settings
    NEO4J_URI: str = "neo4j+s://bcb09060.databases.neo4j.io"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: Optional[str] = None

    # Analytical Observability (Langfuse Engine)
    LANGFUSE_SECRET_KEY: Optional[str] = None
    LANGFUSE_PUBLIC_KEY: Optional[str] = None
    LANGFUSE_BASE_URL: str = "https://langfuse.com"
    LANGFUSE_HOST: str = "http://localhost:3000"

    # Fast Volatile Cache Layer (Redis Connection Pool)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = "your_password_here"
    REDIS_SSL: bool = False
    REDIS_CERT: Optional[str] = "/path/to/client.crt"
    REDIS_KEY: Optional[str] = "/path/to/client.key"
    REDIS_CA: Optional[str] = "/path/to/ca_bundle.crt"

    # Core LLM Providers & Falling Engines (OpenRouter Interface)
    LLM_PROVIDER: str = "openrouter"
    LLM_MODEL: str = "nvidia/nemotron-3-ultra-550b-a55b:free"
    FALLBACK_MODEL: str = "qwen/qwen3-7-plus"
    OPENROUTER_API_KEY: Optional[str] = Field(default=None, repr=False)
    OPENROUTER_BASE_URL: str = "https://openrouter.ai"

    # Dense Similarity Embedding Vector Base Widths
    EMBEDDING_MODEL: str = "BAAI/bge-large-en-v1.5"

    # High-Throughput Unstructured Shards Storage (PyMilvus Driver Contexts)
    VECTOR_DB: str = "milvus"
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    MILVUS_USER: Optional[str] = None
    MILVUS_PASSWORD: Optional[str] = None

    # Server Core Metadatas (FastMCP Protocol Configuration Matrix)
    MCP_SERVER_NAME: str = "GraphRAG-Agent-Platform"
    MCP_SERVER_VERSION: str = "1.0.0"
    MCP_SERVER_DESCRIPTION: str = "Production MCP Server for Multi-Agent GraphRAG Platform"
    MCP_TRANSPORT: str = "stdio"
    MCP_HOST: str = "127.0.0.1"
    MCP_PORT: int = 8000
    MCP_LOG_LEVEL: str = "INFO"
    MCP_REQUEST_TIMEOUT: int = 60
    MCP_MAX_CONCURRENT_REQUESTS: int = 100
    MCP_ENABLE_TRACING: bool = True
    MCP_ENABLE_METRICS: bool = True

    # Cloud Agent Memory Architecture Layer (Neo4j AMSREST Endpoint Platforms)
    NEO4J_AMS_URL: str = "https://neo4jlabs.com"
    NAMS_MEMORY_API: Optional[str] = Field(default=None, repr=False)

    # Runtime Execution Environments
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Pydantic Structural Parser Management Hooks
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


class ApplicationStateRegistry:
    """Manages the application state, acting as a global dependency injection container."""
    
    def __init__(self, validated_settings: Settings):
        """Initializes the runtime state container."""
        self.settings = validated_settings
        self.services: Dict[str, Any] = {}
        self._is_ready = False

    def verify_critical_variables(self) -> None:
        """Verifies that all required API credentials are present to prevent downstream crashes."""
        missing_credentials = []
        if not self.settings.NEO4J_PASSWORD:
            missing_credentials.append("NEO4J_PASSWORD")
        if not self.settings.OPENROUTER_API_KEY:
            missing_credentials.append("OPENROUTER_API_KEY")

        if missing_credentials:
            if self.settings.ENVIRONMENT == "production":
                logger.critical(f"Missing required production credentials: {missing_credentials}. Boot aborted.")
                raise ValueError(f"Missing deployment variables: {missing_credentials}")
            else:
                logger.warning(f"Development mode active. Missing configuration fields: {missing_credentials}")

    def inject_dependency(self, service_key: str, service_instance: Any) -> None:
        """Registers instantiated components into the global runtime container."""
        self.services[service_key] = service_instance
        logger.debug(f"Service entity registered under key: '{service_key}'")

    def get_service(self, service_key: str) -> Any:
        """Retrieves a registered system dependency."""
        if service_key not in self.services:
            raise KeyError(f"Requested resource dependency '{service_key}' is not registered in the system container.")
        return self.services[service_key]

    def prepare_startup_resources(self) -> None:
        """Prepares system resources, path buffers, and global logging parameters."""
        logger.info(f"Assembling system resources for environment profile: [{self.settings.ENVIRONMENT.upper()}]")
        
        # Sync system log levels with the server configuration
        log_level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR
        }
        target_level = log_level_map.get(self.settings.MCP_LOG_LEVEL.upper(), logging.INFO)
        logging.getLogger("GraphRAG").setLevel(target_level)
        
        self.verify_critical_variables()
        self._is_ready = True
        logger.info("Application runtime configuration and system state successfully initialized.")


# Initialize Configuration and Application State Singletons
settings = Settings()
app_state = ApplicationStateRegistry(validated_settings=settings)