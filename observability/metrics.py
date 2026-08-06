"""Metrics Module.

Responsible for collecting quantitative performance metrics across the Multi-Agent
GraphRAG Platform. Metrics enable continuous optimization of reasoning quality,
retrieval accuracy, and execution efficiency.

Responsibilities:
    - Collect runtime execution metrics for system validation.
    - Track vector similarity and graph lookup precision performance.
    - Measure component latencies using monotonic precision timers.
    - Measure overall transactional prompt throughput rates.
    - Monitor prompt, completion, and cumulative token usage structures.
    - Track financial token execution costs based on vendor profiles.
    - Measure GraphRAG context density quality.
    - Monitor short-term Redis cache and internal pooling utilization rates.
    - Record performance baselines for individual multi-agent scripts.
"""

import time
import logging
from typing import Dict, List, Any, Optional
from threading import Lock

logger = logging.getLogger("GraphRAG.Observability.Metrics")


class PerformanceMetricsCollector:
    def __init__(self):
        """Initializes the multi-tier quantitative metrics dashboard with thread-safe hooks."""
        self._lock: Lock = Lock()
        
        # Financial pricing tiers matching current OpenRouter standard baselines (Cost per 1M tokens)
        self._cost_profiles: Dict[str, Dict[str, float]] = {
            "nvidia/nemotron-3-ultra-550b-a55b:free": {"input": 0.0, "output": 0.0},
            "qwen/qwen3-7-plus": {"input": 0.20, "output": 0.60},
            "default": {"input": 0.15, "output": 0.50}
        }
        
        # Core Platform Aggregations
        self._execution_counts: Dict[str, int] = {}
        self._latencies: Dict[str, List[float]] = {}
        self._token_counters: Dict[str, int] = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        self._cumulative_cost: float = 0.0
        self._quality_scores: Dict[str, List[float]] = {"retrieval_precision": [], "graph_connectivity_ratio": []}

    def record_execution(self, component_name: str, execution_time: float) -> None:
        """Increments invocation counts and appends precise processing times."""
        with self._lock:
            self._execution_counts[component_name] = self._execution_counts.get(component_name, 0) + 1
            if component_name not in self._latencies:
                self._latencies[component_name] = []
            self._latencies[component_name].append(execution_time)
            
        logger.debug(f"Metrics Logged: Component '{component_name}' completed in {execution_time:.4f}s.")

    def track_token_consumption(self, model_name: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculates precise API usage footprints and logs cumulative token costs.
        
        Returns:
            The calculated dollar cost float value for the individual generation turn.
        """
        profile = self._cost_profiles.get(model_name, self._cost_profiles["default"])
        turn_cost = (
            (prompt_tokens / 1_000_000) * profile["input"]
        ) + (
            (completion_tokens / 1_000_000) * profile["output"]
        )
        
        with self._lock:
            self._token_counters["prompt_tokens"] += prompt_tokens
            self._token_counters["completion_tokens"] += completion_tokens
            self._token_counters["total_tokens"] += (prompt_tokens + completion_tokens)
            self._cumulative_cost += turn_cost
            
        logger.info(
            f"Token Update [{model_name}]: +{prompt_tokens + completion_tokens} tokens. "
            f"Current Cumulative Cost: ${self._cumulative_cost:.6f}"
        )
        return round(turn_cost, 6)

    def log_graphrag_quality_metrics(self, precision_score: float, context_overlap_ratio: float) -> None:
        """Registers performance quality metrics regarding semantic context boundaries."""
        with self._lock:
            self._quality_scores["retrieval_precision"].append(precision_score)
            self._quality_scores["graph_connectivity_ratio"].append(context_overlap_ratio)

    def compute_average_latency(self, component_name: str) -> float:
        """Computes the arithmetic mean processing duration for a selected component module."""
        with self._lock:
            durations = self._latencies.get(component_name, [])
            if not durations:
                return 0.0
            return round(sum(durations) / len(durations), 4)

    def generate_diagnostics_snapshot(self) -> Dict[str, Any]:
        """Compiles analytical platform metrics into a structured summary report payload."""
        with self._lock:
            averages = {comp: round(sum(t) / len(t), 4) for comp, t in self._latencies.items() if t}
            
            avg_precision = (
                sum(self._quality_scores["retrieval_precision"]) / len(self._quality_scores["retrieval_precision"])
                if self._quality_scores["retrieval_precision"] else 1.0
            )
            
            return {
                "system_throughput": {
                    "total_invocations": dict(self._execution_counts),
                    "average_latencies_seconds": averages
                },
                "resource_utilization": {
                    "token_metrics": dict(self._token_counters),
                    "total_financial_burn_usd": round(self._cumulative_cost, 6)
                },
                "graphrag_intelligence_index": {
                    "mean_retrieval_precision": round(avg_precision, 4),
                    "historical_samples_count": len(self._quality_scores["retrieval_precision"])
                }
            }

    def clear_metrics_registry(self) -> None:
        """Resets metric indexes back to factory baseline states to begin new analytics tracking runs."""
        with self._lock:
            self._execution_counts.clear()
            self._latencies.clear()
            self._token_counters = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            self._cumulative_cost = 0.0
            self._quality_scores = {"retrieval_precision": [], "graph_connectivity_ratio": []}
        logger.info("Local multi-agent quantitative analytics telemetry registers successfully cleared.")