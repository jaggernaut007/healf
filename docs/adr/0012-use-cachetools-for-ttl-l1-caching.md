# ADR-0012: Use Cachetools for TTL L1 Caching

## Status
Accepted

## Context
The Healf health intelligence engine interacts with external APIs (like the NIH Dietary Supplement Label Database) that have rate limits and introduce network latency. Repeated requests for the same product safety data or research summaries should be optimized to improve performance and reliability, especially as the system scales towards production (Phase 5: Industrial Hardening).

## Decision
We will use the `cachetools` library (v7.0.5) to implement in-memory Time-To-Live (TTL) Least Recently Used (LRU) caching. Specifically, we use the `@cached` decorator with `TTLCache` in the `EnrichmentClient` to cache safety and grounding data.

## Consequences
- **Easier**: Reduced latency for repeated queries, protection against external API rate limits, and zero-configuration L1 caching for local development.
- **Harder**: In-memory cache is not shared across processes or restarts (unlike Redis), and thread-safety must be explicitly managed with locks if the application moves to a multi-threaded web server (though currently it uses an async-first boundary where this is less of a concern for local IO-bound tasks).
