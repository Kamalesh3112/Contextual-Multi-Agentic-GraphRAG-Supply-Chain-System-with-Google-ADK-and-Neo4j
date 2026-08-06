"""
Responsibilities: (Abstract Base Class)
   - Common logger of along with other registered MCP tools
   - Access to settings
   - Standard response formatting
   - Error handling
   - Timing/metrics hooks
   - Validation helpers
Dependency injection for:
   - Neo4jClient
   - MemoryManager
   - Langfuse tracer
   - VectorStore
   - SparQL
"""

from __future__ import annotations
import logging
import time
from abc import ABC
from typing import Any, Dict, Optional

from config.settings import settings

from graph.neo4j_client import Neo4jClient
from nams_memory.memory_manager import MemoryManager
from observability.langfuse_tracer import LangfuseTracer
from rag.semantic_context_store import VectorStore

logger = logging.getlogger(__name__)

class BaseTool(ABC):
     def __init__(self,
                 neo4j_client: Optional[Neo4jClient] = None,
                 memory_manager: Optional[MemoryManager] = None,
                 vector_store: Optional[VectorStore] = None,
                 tracer: Optional[LangfuseTracer] = None,
                 ) -> None:
        self.settings = settings
        self.logger = logging.getlogging(__class__.__name__)
        self.neo4j_client = neo4j_client or Neo4jClient()
        self.memory_manager = memory_manager or MemoryManager()
        self.vector_store = vector_store or VectorStore()
        self.tracer = tracer or LangfuseTracer()

     @staticmethod
     def success(data: Any, message: str = "Success", ) -> Dict[str, Any]:
         return {
             "status": "success",
             "message": message,
             "data": data
         }

     @staticmethod
     def failure(data: Any, message: str, error: Optional[str] = None) -> Dict[str, Any]:
         return {
             "status": "error",
             "message": message,
             "error": error
         }

     def start_timer(self) -> float:
         return time.perf_counter()

     def stop_timer(self, start_time: float) -> float:
         return round(
             time.perf_counter() - start_time,
             4
         )

     def log_start(self, operation: str) -> None:
         self.logger.info("Starting %s", operation)

     def log_success(self, operation: str, duration: float,) -> None:
         self.logger.info("%s completed in %.4f seconds", operation, duration)

     def log_error(self, operation:str, exception = Exception) -> None:
         self.logger.exception("%s failed in %s", operation, exception)

     @staticmethod
     def require(value: Any, field: str) -> None:
         if value is None:
             raise ValueError("f{field} cannot be None.")

     @staticmethod
     def require_not_empty(value: str, field: str) -> None:
         if not value.strip():
             raise ValueError(
                 f"{field} cannot be empty"
             )

    
     async def health(self) -> Dict[str, Any]:
         return {
             "tool": self.__class__.__name__,
             "neo4j": await self.neo4j is not None,
             "memory": await self.memory is not None,
             "vector_store": await self.vector_store is not None,
             "tracer": await self.tracer is not None
         }


     @property
     def tool_name(self) -> str:
         return self.__class_.__name__

     @property
     def version(self) -> str:
         return "1.0.0"

     @property
     def description(self) -> str:
         return self.__doc__ or ""

     async def __aenter__(self):
         return self

     async def __aexit__(self: Any, exc_type: Any, exc: Any, tb: Any) -> None:
         # Cleanup resources on context manager exit. Override in subclasses if cleanup is needed.
         return None