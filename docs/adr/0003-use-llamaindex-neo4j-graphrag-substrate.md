# 3. Use LlamaIndex + Neo4j Property Graph as the GraphRAG Substrate

## Status
Accepted

## Context
The platform needs a single retrieval substrate that supports both graph traversal and semantic retrieval over product and mechanism knowledge. We need idempotent writes, provenance-aware relationships, and a direct path to AuraDB.

Research evidence was captured through official docs and package validation for `llama-index` and `llama-index-graph-stores-neo4j`, with existing implementation guidance in `docs/research/llama-index-neo4j-property-graph-v0.14.20.md`.

## Decision
Adopt `LlamaIndex` with `Neo4jPropertyGraphStore` on AuraDB as the default GraphRAG foundation.

- Graph writes must use parameterized `MERGE` semantics.
- Ingestion remains deterministic and data-driven from repository artifacts.
- Vectorized retrieval is co-located with graph entities where supported by the property graph workflow.

## Consequences
- Positive: Unified graph + semantic retrieval model with clear ingestion path.
- Positive: Reduced architecture sprawl versus running separate graph and vector stores.
- Negative: Strong coupling to LlamaIndex integration behavior and version cadence.
- Negative: Requires tighter version pinning and periodic validation for upstream changes.
