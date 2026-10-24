# Contextual Multi-Agentic GraphRAG Supply Chain Intelligence System

An enterprise-grade **Context Engineering** and **GraphRAG** platform built using **Google ADK**, **Neo4j**, **Milvus**, **MCP**, and **NAMS (Neo4j Agent Memory Service)** for intelligent supply chain risk analysis and explainable multi-agent reasoning.

---

## Overview

This project combines:

- 🧠 Google ADK Multi-Agent System
- 🌐 GraphRAG with Neo4j Knowledge Graph
- 📚 Context Engineering Pipeline
- 🧩 Model Context Protocol (MCP)
- 🗄️ Milvus Vector Database
- 💾 Neo4j Agent Memory Service (NAMS)
- 📊 Langfuse Observability
- ⚡ Hybrid Retrieval (Graph + Vector + Memory)

The platform enables agents to retrieve, reason, plan, collaborate and generate explainable responses using structured knowledge and long-term memory.

---

## Architecture

```
User
   │
   ▼
Root Agent
   │
   ▼
Orchestration Layer
   │
   ▼
Google ADK Agents
   │
   ▼
Context Engineering
   │
   ▼
GraphRAG
   │
 ┌─┴──────────────┐
 ▼                ▼
Neo4j          Milvus
(Graph)       (Vectors)
   │                │
   └──────┬─────────┘
          ▼
     NAMS Memory
          │
          ▼
    Final Response
```

---

## Features

- Multi-Agent Architecture
- Context Engineering Pipeline
- GraphRAG Retrieval
- Hybrid Graph + Vector Search
- Multi-hop Graph Traversal
- Neo4j Knowledge Graph
- Milvus Vector Search
- NAMS Long-Term Memory
- MCP Tool Integration
- Langfuse Observability
- Risk Intelligence Engine
- Explainable AI Reasoning

---

## Technology Stack

| Category | Technologies |
|----------|--------------|
| Agents | Google ADK |
| LLM | OpenRouter (Nemotron, Qwen) |
| Knowledge Graph | Neo4j |
| Vector Database | Milvus |
| Memory | Neo4j Agent Memory Service (NAMS) |
| Protocol | MCP (Model Context Protocol) |
| Observability | Langfuse |
| Backend | FastAPI |
| Language | Python 3.12+ |

---

## Project Structure

```
agents/
graph/
rag/
mcp_sdk/
nams_memory/
orchestration/
observability/
evaluation/
config/
app/
deployment/
tests/
```

---

## Current Status

🚧 Active Development

Current focus includes:

- Context Engineering
- Google ADK Integration
- GraphRAG Pipeline
- Hybrid Retrieval
- Multi-Agent Orchestration
- NAMS Memory Integration
- Enterprise Observability

---

## Roadmap

- [ ] Complete GraphRAG Pipeline
- [ ] Neo4j Agent Memory Integration
- [ ] Context Compression
- [ ] Dynamic Worker Agents
- [ ] Loop Engineering
- [ ] Evaluation Framework
- [ ] Docker Deployment

---

## License

This project is currently under development and further iteration, it is intended for research and production build purposes. System is currently versioned as V1.0.0
