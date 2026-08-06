"""
Trace Management Module

Responsible for creating structured execution traces across the entire
GraphRAG platform.

Unlike conventional logging, traces preserve execution hierarchy,
dependencies and reasoning flow.

Responsibilities
----------------
• Create execution traces.
• Build span hierarchies.
• Record execution timing.
• Track workflow dependencies.
• Correlate agent interactions.
• Capture retrieval pipelines.
• Record context engineering stages.
"""

import time
import uuid
import logging
from typing import Dict, List, Any, Optional
from threading import Lock

logger = logging.getLogger("GraphRAG.Observability.Traces")


class LocalSpan:
    def __init__(self, name: str, category: str, parent_id: Optional[str] = None):
        """Initializes an atomic execution span container."""
        self.span_id: str = str(uuid.uuid4())
        self.name: str = name
        self.category: str = category
        self.parent_id: Optional[str] = parent_id
        self.start_time: float = time.monotonic()
        self.end_time: Optional[float] = None
        self.duration: Optional[float] = None
        self.input: Optional[Any] = None
        self.output: Optional[Any] = None
        self.metadata: Dict[str, Any] = {}
        self.children_ids: List[str] = []

    def finalize(self, output: Optional[Any] = None) -> None:
        """Closes the current operational frame, calculating execution latencies."""
        self.end_time = time.monotonic()
        self.duration = round(self.end_time - self.start_time, 4)
        self.output = output


class ActiveTelemetryTracer:
    def __init__(self):
        """Initializes the thread-safe local trace management module registry."""
        self._spans: Dict[str, LocalSpan] = {}
        self._lock: Lock = Lock()

    def start_trace(
        self, 
        name: str, 
        category: str, 
        parent_span_id: Optional[str] = None,
        input_data: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Spins up a new localized execution span inside the tracking map.
        
        Args:
            name: Label identifying the operational step (e.g., 'subgraph_expansion').
            category: Classification bucket ('agent', 'retrieval', 'context_engineering').
            parent_span_id: Target ID of the preceding step if creating a child node.
            input_data: Prompt text, vector, or properties ingested by this node.
            metadata: Custom dictionary tags for extra system details.
            
        Returns:
            The string trace identifier (span_id) acting as the lineage handle.
        """
        span = LocalSpan(name=name, category=category, parent_id=parent_span_id)
        span.input = input_data
        if metadata:
            span.metadata = dict(metadata)

        with self._lock:
            self._spans[span.span_id] = span
            
            # Map structural parent-child links if tracing within an existing execution chain
            if parent_span_id and parent_span_id in self._spans:
                self._spans[parent_span_id].children_ids.append(span.span_id)

        logger.debug(f"Local span started: [{category.upper()}] {name} (ID: {span.span_id})")
        return span.span_id

    def end_trace(self, span_id: str, output_data: Optional[Any] = None) -> Optional[Dict[str, Any]]:
        """Finalizes an active span by mapping execution statistics into a clean dictionary.
        
        Args:
            span_id: Target ID matching the opened span block.
            output_data: Finalized answer string, graph payload, or dictionary response.
            
        Returns:
            A dictionary detailing span diagnostics, or None if the ID is missing.
        """
        with self._lock:
            if span_id not in self._spans:
                logger.warning(f"Attempted to end a trace with an untracked span identifier: {span_id}")
                return None
                
            span = self._spans[span_id]
            span.finalize(output=output_data)
            
            # Extract a shallow log representation before clearing out old keys
            serialized_report = {
                "span_id": span.span_id,
                "parent_id": span.parent_id,
                "name": span.name,
                "category": span.category,
                "latency_seconds": span.duration,
                "input": span.input,
                "output": span.output,
                "metadata": span.metadata
            }

        logger.info(
            f"Local span finished: {span.name} completed in {span.duration}s "
            f"under category: {span.category.upper()}"
        )
        return serialized_report

    def fetch_execution_tree(self, root_span_id: str) -> Dict[str, Any]:
        """Recursively builds an execution graph dependency tree starting from a parent ID."""
        with self._lock:
            if root_span_id not in self._spans:
                return {}
                
            span = self._spans[root_span_id]
            
            tree_node = {
                "name": span.name,
                "category": span.category,
                "span_id": span.span_id,
                "latency": span.duration,
                "metadata": span.metadata,
                "children": [self._fetch_execution_tree_unlocked(child_id) for child_id in span.children_ids]
            }
            return tree_node

    def _fetch_execution_tree_unlocked(self, span_id: str) -> Dict[str, Any]:
        """Internal recursive walker method running safely within locked database lines."""
        if span_id not in self._spans:
            return {}
        span = self._spans[span_id]
        return {
            "name": span.name,
            "category": span.category,
            "span_id": span.span_id,
            "latency": span.duration,
            "metadata": span.metadata,
            "children": [self._fetch_execution_tree_unlocked(child_id) for child_id in span.children_ids]
        }

    def purge_trace_tree(self, root_span_id: str) -> None:
        """Recursively deletes finished span chains from memory to prevent leaks."""
        with self._lock:
            self._purge_span_recursive(root_span_id)
        logger.debug(f"Successfully purged trace data tree matching root ID: {root_span_id}")

    def _purge_span_recursive(self, span_id: str) -> None:
        """Internal helper handling clear sweeps across nested lists."""
        if span_id in self._spans:
            span = self._spans[span_id]
            for child_id in span.children_ids:
                self._purge_span_recursive(child_id)
            del self._spans[span_id]