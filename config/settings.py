from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field  # noqa: F401

class Settings(BaseSettings):

    # Neo4j Database
    NEO4J_URI: str = "neo4j+s://bcb09060.databases.neo4j.io"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str | None = None

    # Langfuse Keys
    LANGFUSE_SECRET_KEY: str | None = None
    LANGFUSE_PUBLIC_KEY: str | None = None
    LANGFUSE_BASE_URL: str = "https://cloud.langfuse.com"
    LANGFUSE_HOST: str = "http://localhost:3000"

    # Redis Configs
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = "your_password_here"
    REDIS_SSL: bool = False
    REDIS_CERT: str | None = "/path/to/client.crt"
    REDIS_KEY: str | None = "/path/to/client.key"
    REDIS_CA: str | None = "/path/to/ca_bundle.crt"

    # LLM Configs
    LLM_PROVIDER: str = "openrouter"
    LLM_MODEL: str = "nvidia/nemotron-3-ultra-550b-a55b:free"
    FALLBACK_MODEL: str = "qwen/qwen3-7-plus"
    OPENROUTER_API_KEY: str | None = None
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    # Embedding Model
    EMBEDDING_MODEL: str = "BAAI/bge-large-en-v1.5"

    # Vector Database (Pymilvus)
    VECTOR_DB: str = "milvus"
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    MILVUS_USER: str | None = None
    MILVUS_PASSWORD: str | None = None

    #FastMCP Configuration metadata
    MCP_SERVER_NAME: str = "GraphRAG-Agent-Platform"
    MCP_SERVER_VERSION: str = "1.0.0"
    MCP_SERVER_DESCRIPTION: str = (
        "Production MCP Server for Multi-Agent GraphRAG Platform"
    )
    MCP_TRANSPORT: str = "stdio"
    MCP_HOST: str = "127.0.0.1"
    MCP_PORT: int = 8000
    MCP_LOG_LEVEL: str = "INFO"
    MCP_REQUEST_TIMEOUT: int = 60
    MCP_MAX_CONCURRENT_REQUESTS: int = 100
    MCP_ENABLE_TRACING: bool = True
    MCP_ENABLE_METRICS: bool = True

    #NAMS Graph Memory Layer
    NEO4J_AMS_URL: str = "https://memory.neo4jlabs.com"
    NAMS_MEMORY_API: str | None = None

    # Application Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # PYDANTIC SETTINGS CONFIG
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()