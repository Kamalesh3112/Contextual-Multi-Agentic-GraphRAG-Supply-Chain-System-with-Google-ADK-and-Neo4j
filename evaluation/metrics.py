"""
============================================================================
Evaluation Metrics Module

Defines quantitative and qualitative metrics used to evaluate the
performance of the Multi-Agent GraphRAG Platform.

Metrics measure not only response quality but also retrieval effectiveness,
reasoning quality, graph utilization and execution efficiency.

Responsibilities
----------------
• Define evaluation metrics.
• Compute retrieval accuracy.
• Measure reasoning quality.
• Evaluate GraphRAG effectiveness.
• Evaluate Context Engineering.
• Compare benchmark results.
• Generate evaluation reports.
"""

import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("GraphRAG.Evaluation.Metrics")


class EvaluationReport(BaseModel):
    """Encapsulates the consolidated metrics of an evaluation run sequence."""
    test_id: str
    faithfulness_score: float = Field(..., description="Measures if the answer is completely grounded in retrieved context.")
    answer_relevance_score: float = Field(..., description="Measures how well the generated statement matches the original query.")
    context_recall_score: float = Field(..., description="Measures if all golden target reference facts were successfully recovered.")
    graph_utilization_ratio: float = Field(..., description="Ratio of multi-hop graph nodes extracted versus total text context fragments.")
    execution_efficiency_seconds: float


class RAGQualityEvaluator:
    def __init__(self, openrouter_client: Optional[Any] = None):
        """Initializes the evaluator with optional LLM hooks for automated semantic scoring."""
        self.llm = openrouter_client

    def compute_retrieval_accuracy(
        self, 
        retrieved_ids: List[str], 
        golden_source_ids: List[str]
    ) -> Dict[str, float]:
        """Computes mathematical precision, recall, and F1 boundaries for context chunks."""
        retrieved_set = set(retrieved_ids)
        golden_set = set(golden_source_ids)
        
        if not retrieved_set or not golden_set:
            return {"precision": 0.0, "recall": 0.0, "f1_score": 0.0}
            
        intersection = retrieved_set.intersection(golden_set)
        precision = len(intersection) / len(retrieved_set)
        recall = len(intersection) / len(golden_set)
        
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4)
        }

    def measure_reasoning_quality(self, generated_steps: List[str], target_milestones: List[str]) -> float:
        """Measures agent reasoning quality by assessing token progress through target execution milestones."""
        if not target_milestones:
            return 1.0
            
        flat_steps = " ".join(generated_steps).lower()
        matched_milestones = sum(1 for milestone in target_milestones if milestone.lower() in flat_steps)
        
        score = matched_milestones / len(target_milestones)
        logger.debug(f"Reasoning path milestone score calculated: {score:.4f}")
        return round(score, 4)

    def evaluate_graph_effectiveness(self, retrieved_graph_edges: List[Dict[str, Any]], total_context_chunks: int) -> float:
        """Measures graph effectiveness by computing the graph-to-unstructured density ratio."""
        if total_context_chunks == 0:
            return 0.0
            
        # Higher density indicates highly interconnected knowledge structures
        edge_count = len(retrieved_graph_edges)
        ratio = edge_count / (edge_count + total_context_chunks)
        return round(ratio, 4)

    def evaluate_context_engineering(self, raw_retrieved_chars: int, post_compression_chars: int) -> Dict[str, Any]:
        """Evaluates Context Engineering efficiency by measuring prompt compaction ratios."""
        if raw_retrieved_chars == 0:
            return {"compression_ratio": 1.0, "savings_percentage": 0.0}
            
        ratio = post_compression_chars / raw_retrieved_chars
        savings = ((raw_retrieved_chars - post_compression_chars) / raw_retrieved_chars) * 100
        
        return {
            "compression_ratio": round(ratio, 4),
            "savings_percentage": round(savings, 2)
        }

    async def compute_rag_triad_scores(
        self, 
        query: str, 
        context_block: str, 
        response_text: str,
        golden_points: List[str]
    ) -> Tuple[float, float, float]:
        """Heuristically estimates the RAG Triad scores (Faithfulness, Relevance, Context Recall).
        
        In an automated environment, these metrics are extracted via structured LLM assessments.
        This framework provides a deterministic keyword and sentence intersection baseline.
        """
        # 1. Estimate Faithfulness: Verify if response statements are present within context
        response_sentences = [s.strip() for s in response_text.lower().split(".") if len(s.strip()) > 5]
        context_lower = context_block.lower()
        
        if not response_sentences:
            faithfulness = 0.0
        else:
            grounded_count = sum(1 for sentence in response_sentences if sentence[:20] in context_lower or any(word in context_lower for word in sentence.split()[:3]))
            faithfulness = grounded_count / len(response_sentences)

        # 2. Estimate Answer Relevance: Assess overlap between the generated text and the user query
        query_words = set(query.lower().split())
        response_words = set(response_text.lower().split())
        relevance = len(query_words.intersection(response_words)) / max(len(query_words), 1)

        # 3. Estimate Context Recall: Verify if target reference criteria points exist in the generated text
        if not golden_points:
            recall = 1.0
        else:
            recovered_points = sum(1 for pt in golden_points if pt.lower() in response_text.lower())
            recall = recovered_points / len(golden_points)

        return min(round(faithfulness, 2), 1.0), min(round(relevance, 2), 1.0), min(round(recall, 2), 1.0)

    async def generate_evaluation_report(
        self, 
        test_id: str, 
        query: str, 
        context_block: str, 
        response_text: str,
        retrieved_graph: List[Any],
        total_chunks: int,
        golden_points: List[str],
        duration: float
    ) -> EvaluationReport:
        """Assembles metrics into a structured, production-ready EvaluationReport."""
        faith, rel, rec = await self.compute_rag_triad_scores(
            query=query, 
            context_block=context_block, 
            response_text=response_text, 
            golden_points=golden_points
        )
        
        graph_ratio = self.evaluate_graph_effectiveness(retrieved_graph, total_chunks)
        
        report = EvaluationReport(
            test_id=test_id,
            faithfulness_score=faith,
            answer_relevance_score=rel,
            context_recall_score=rec,
            graph_utilization_ratio=graph_ratio,
            execution_efficiency_seconds=round(duration, 3)
        )
        
        logger.info(
            f"Evaluation Report Compiled [{test_id}]: Faithfulness={faith}, Relevance={rel}, Recall={rec}"
        )
        return report