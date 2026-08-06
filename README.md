Domain: Multi-Agentic GraphRAG Supply chain Application using Google ADK and Neo4j
Models:  NVIDIA Nemotron 3 Nano Omni, NVIDIA nemotron-3-ultra-550b-a55b:free,  Gemma 4 - 12B, Saravam Vision or TTS or STT, Gemini 3.1 Flash TTS, GLM-5.2 (Ollama)
LLM Inference and Server: Open Router or Nvidia or Ollama
Plans: Fallback, Autonomous pipeline, self-healing and grounding, Multi-Hop Reasoning agent, Harness, Skills, Sub-graph retrieval connector and context engineering, Structured Memory layers, Recursive self-improvement traces (Anthropic), RL (Reward, Loop, ), Neo4j Agent Memory Service (AMS), Gemini Interactions skills API
Post testing of GraphRAG application: Front-end and Back-end using TypeScript

User
 │
 ▼
Google ADK Root Agent
 │
 ├───────────────┐
 │               │
 ▼               ▼
Query Agent    Memory Agent
 │               │
 │               ▼
 │        Neo4j AMS (NAMS)
 │
 ▼
Graph Agent
 │
 ├── Neo4j GraphRAG
 ├── Cypher Queries
 ├── Multi-Hop Traversal
 └── Milvus Vector Search
 │
 ▼
Risk Agent
 │
 ▼
Synthesis Agent
 │
 ▼
Gemini Interactions API
 │
 ▼
Nemotron Ultra 3
(Fallback → Qwen 3.7 Plus)
 │
 ▼
Final Response

Google ADK → Multi-agent orchestration
Gemini Interactions API → Agent runtime/orchestration layer
Neo4j GraphRAG → Knowledge graph reasoning
Neo4j Agent Memory Service (NAMS) → Memory layer
OpenRouter Nemotron Ultra 3 → Primary reasoning model
Qwen 3.7 Plus → Fallback model
Milvus → Vector retrieval
Langfuse → Observability