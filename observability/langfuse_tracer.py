#langfuse(LLMOps) + LlamaIndex
"""
============================================================================
Langfuse Tracer Module

Central tracing interface for the Multi-Agent GraphRAG Platform.

Responsible for recording the complete execution lifecycle into Langfuse,
including agent reasoning, retrieval operations, memory access, tool
invocations and LLM interactions.

Responsibilities
----------------
• Initialize Langfuse client.
• Create execution traces.
• Record agent spans.
• Record workflow spans.
• Record LLM interactions.
• Record retrieval operations.
• Record memory operations.
• Record MCP tool execution.
• Attach metadata.
• Record execution costs.
"""

import logging
from typing import Dict, Any, Optional, List
from langfuse import Langfuse
from langfuse.client import StatefulSpanClient, StatefulTraceClient

logger = logging.getLogger("GraphRAG.Observability.LangfuseTracer")


class LangfuseTracer:
    def __init__(self, app_settings: Any):
        """Initializes the Langfuse tracking core client utilizing system parameters."""
        self.settings = app_settings
        self.client: Optional[Langfuse] = None
        self._enabled = False
        self._bootstrap_langfuse()

    def _bootstrap_langfuse(self) -> None:
        """Securely mounts the Langfuse tracking engine, verifying operational environment flags."""
        if not self.settings.MCP_ENABLE_TRACING:
            logger.info("Langfuse observability layer deactivated via system-wide configuration flags.")
            return

        if not self.settings.LANGFUSE_SECRET_KEY or not self.settings.LANGFUSE_PUBLIC_KEY:
            logger.warning("Langfuse public/secret keys missing from active configuration. Bypassing tracking layers.")
            return

        try:
            logger.info(f"Connecting to Langfuse analytical cloud plane at: {self.settings.LANGFUSE_BASE_URL}")
            self.client = Langfuse(
                public_key=self.settings.LANGFUSE_PUBLIC_KEY,
                secret_key=self.settings.LANGFUSE_SECRET_KEY,
                host=self.settings.LANGFUSE_BASE_URL
            )
            self._enabled = True
        except Exception as bootstrap_err:
            logger.error(f"Failed to mount Langfuse operational telemetry context: {bootstrap_err}")
            self._enabled = False

    def create_root_trace(
        self, 
        trace_name: str, 
        session_id: str, 
        user_id: Optional[str] = None, 
        input_data: Optional[Any] = None
    ) -> Optional[StatefulTraceClient]:
        """Spins up a master trace tracking an independent multi-agent workflow runtime session."""
        if not self._enabled or not self.client:
            return None

        try:
            return self.client.trace(
                name=trace_name,
                session_id=session_id,
                user_id=user_id,
                input=input_data,
                environment=self.settings.ENVIRONMENT,
                metadata={
                    "platform_name": self.settings.MCP_SERVER_NAME,
                    "platform_version": self.settings.MCP_SERVER_VERSION,
                    "debug_mode": self.settings.DEBUG
                }
            )
        except Exception as e:
            logger.warning(f"Unable to spin up root trace container: {e}")
            return None

    def start_span(
        self, 
        parent_context: Any, 
        span_name: str, 
        category: str, 
        input_data: Optional[Any] = None
    ) -> Optional[StatefulSpanClient]:
        """Generates a tracking child span beneath a parent context (Trace or Span)."""
        if not self._enabled or not parent_context:
            return None

        try:
            # Polymorphic approach allows parent context to be either a Trace or another Span
            return parent_context.span(
                name=span_name,
                input=input_data,
                metadata={"span_category": category}
            )
        except Exception as e:
            logger.debug(f"Failed to cleanly start operational trace sub-span: {e}")
            return None

    def log_llm_generation(
        self, 
        parent_context: Any, 
        model_name: str, 
        prompt: Any, 
        completion: str, 
        usage_metadata: Dict[str, int]
    ) -> None:
        """Records an OpenAI/OpenRouter style generation block with token and model details."""
        if not self._enabled or not parent_context:
            return

        try:
            # Extract standard tracking parameter tokens
            prompt_tokens = usage_metadata.get("prompt_tokens", 0)
            completion_tokens = usage_metadata.get("completion_tokens", 0)
            total_tokens = usage_metadata.get("total_tokens", prompt_tokens + completion_tokens)

            parent_context.generation(
                name="llm_generation_block",
                model=model_name,
                input=prompt,
                output=completion,
                usage={
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens
                }
            )
        except Exception as e:
            logger.error(f"Error logging generation analytics payload onto Langfuse layer: {e}")

    def log_retrieval_operation(
        self, 
        parent_context: Any, 
        retrieval_type: str, 
        query: str, 
        results_summary: List[Dict[str, Any]]
    ) -> None:
        """Logs vector similarity matches or multi-hop graph neighborhood lookups."""
        if not self._enabled or not parent_context:
            return

        try:
            parent_context.event(
                name=f"retrieval_{retrieval_type.lower()}",
                input={"query": query},
                output={"candidates_count": len(results_summary), "matches": results_summary}
            )
        except Exception as e:
            logger.warning(f"Could not record retrieval trace checkpoint metrics: {e}")

    def log_memory_operation(
        self, 
        parent_context: Any, 
        operation_name: str, 
        memory_type: str, 
        key_or_query: str, 
        payload: Optional[Any] = None
    ) -> None:
        """Tracks conversational context transactions or self-reflection mutations."""
        if not self._enabled or not parent_context:
            return

        try:
            parent_context.event(
                name=f"memory_{operation_name.lower()}",
                input={"memory_type": memory_type, "target": key_or_query},
                output={"data_dump": payload}
            )
        except Exception as e:
            logger.debug(f"Muted memory auditing footprint log exception: {e}")

    def log_tool_invocation(
        self, 
        parent_context: Any, 
        tool_name: str, 
        arguments: Dict[str, Any], 
        output: Any, 
        is_success: bool = True
    ) -> None:
        """Audits internal algorithms or FastMCP external server tool executions."""
        if not self._enabled or not parent_context:
            return

        try:
            parent_context.event(
                name=f"tool_call_{tool_name}",
                input=arguments,
                output={"success": is_success, "payload": output},
                metadata={"engine": "FastMCP_Protocol_Layer"}
            )
        except Exception as e:
            logger.warning(f"Failed to commit tool invocation footprint telemetry: {e}")

    def end_span_or_trace(self, context_object: Any, output_data: Optional[Any] = None) -> None:
        """Gracefully closes an active span or trace object, finalizing latency and duration counters."""
        if not self._enabled or not context_object:
            return

        try:
            context_object.end(output=output_data)
        except Exception as e:
            logger.debug(f"Exception encountered during telemetry container termination: {e}")

    def flush_tracer(self) -> None:
        """Forces the underlying Langfuse network pipeline to flush queued events to the server."""
        if self._enabled and self.client:
            try:
                logger.info("Flushing operational telemetry queues to the Langfuse cloud plane.")
                self.client.flush()
            except Exception as e:
                logger.error(f"Error flushing analytical tracking events to endpoints: {e}")