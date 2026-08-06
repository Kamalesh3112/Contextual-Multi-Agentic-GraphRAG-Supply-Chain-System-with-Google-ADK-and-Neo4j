"""
Reranker Module

Responsible for improving retrieval quality by ranking candidate contexts
according to relevance.

Rather than relying solely on vector similarity, reranking evaluates the
semantic importance of retrieved graph and document contexts.

Responsibilities
----------------
• Cross-encoder reranking.
• Candidate ranking.
• Relevance scoring.
• Duplicate removal.
• Context prioritization.
"""

"""Context Optimizer Module.

Responsible for maximizing context density, optimizing token consumption window 
budgets, and orchestrating failover LLM routing execution across OpenRouter providers.

Responsibilities:
    - Token ceiling tracking and verification.
    - Context compression and structural pruning.
    - Prompt-density stabilization.
    - Resilient primary-to-fallback LLM API request routing.
"""

import logging
from typing import List, Dict, Any, Optional
import httpx

logger = logging.getLogger("GraphRAG.ContextOptimizer")


class ContextOptimizer:
    def __init__(
        self, 
        provider: str, 
        primary_model: str, 
        fallback_model: str, 
        base_url: str, 
        api_key: Optional[str],
        max_context_tokens: int = 6000
    ):
        """Initializes the Optimizer engine with explicit token window and failover configs."""
        self.provider = provider
        self.primary_model = primary_model
        self.fallback_model = fallback_model
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.max_context_tokens = max_context_tokens

    def estimate_token_count(self, text: str) -> int:
        """Estimates token footprint safely in production using standard word-metric multipliers.
        
        Rule: 1 word approximately maps to 1.3 tokens.
        """
        return int(len(text.split()) * 1.3) + 12

    def compress_context_block(self, raw_context_str: str) -> str:
        """Prunes the combined context string down systematically to fit within the designated token budget ceiling."""
        estimated_tokens = self.estimate_token_count(raw_context_str)
        if estimated_tokens <= self.max_context_tokens:
            return raw_context_str

        logger.warning(
            f"Context size ({estimated_tokens} tokens) exceeds target budget of {self.max_context_tokens}. "
            "Executing structural payload truncation rules."
        )

        lines = raw_context_str.split("\n")
        compressed_lines: List[str] = []
        accumulated_tokens = 50  # Operational padding budget

        for line in lines:
            line_tokens = self.estimate_token_count(line)
            if accumulated_tokens + line_tokens > self.max_context_tokens:
                compressed_lines.append(
                    "\n[... Context Budget Threshold Reached: Remaining multi-hop graph/semantic paths truncated for token compliance ...]"
                )
                break
            compressed_lines.append(line)
            accumulated_tokens += line_tokens

        return "\n".join(compressed_lines)

    async def call_llm_with_fallback(self, system_prompt: str, user_content: str) -> str:
        """Routes execution to OpenRouter. 
        
        Fails over gracefully from Nemotron to Qwen if timeouts, rate limits, or 5xx exceptions occur.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key or 'anonymous'}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://neo4jlabs.com",
            "X-Title": "Multi-Agent GraphRAG Platform"
        }
        
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "temperature": 0.1
        }

        # 1. Attempt Primary Request: nvidia/nemotron-3-ultra-550b-a55b:free
        payload["model"] = self.primary_model
        try:
            logger.info(f"Dispatching context to primary engine: {self.primary_model}")
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions", 
                    json=payload, 
                    headers=headers
                )
                if response.status_code == 200:
                    return response.json()["choices"]["message"]["content"]
                
                logger.warning(f"Primary engine rejected request with status code: {response.status_code}")
        except Exception as e:
            logger.error(f"Network transport fault encountered on primary route: {str(e)}")

        # 2. Resilient Failover Request: qwen/qwen3-7-plus
        logger.warning(f"Initiating secondary failover routing to fallback model target: {self.fallback_model}")
        payload["model"] = self.fallback_model
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions", 
                    json=payload, 
                    headers=headers
                )
                if response.status_code == 200:
                    return response.json()["choices"]["message"]["content"]
                
                raise RuntimeError(f"Fallback endpoint rejected response with status code: {response.status_code}")
        except Exception as critical_err:
            logger.critical(f"All structural generation pathways exhausted. Pipeline runtime failure: {critical_err}")
            raise critical_err