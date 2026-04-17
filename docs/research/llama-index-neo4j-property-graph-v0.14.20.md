# Research: LlamaIndex Neo4j Property Graph Store

**Library version:** llama-index 0.14.20, llama-index-graph-stores-neo4j 0.7.0
**Status:** Current
**Date:** 2026-04-15

## Sources Consulted

| Source | URL | Date accessed |
|--------|-----|---------------|
| Official docs | https://docs.llamaindex.ai/ | 2026-04-15 |
| Neo4j integration docs | https://docs.llamaindex.ai/en/stable/module_guides/indexing/lpg_index_guide/ | 2026-04-15 |

## The Correct Approach

Use `Neo4jPropertyGraphStore` with explicit `username`, `password`, and `url`. The installed package exposes a `client` object that can be used to open a Neo4j session. Keep writes parameterized and use `MERGE` for idempotency.

```python
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore

graph_store = Neo4jPropertyGraphStore(
    username="neo4j",
    password="password",
    url="bolt://localhost:7687",
    database="neo4j",
    refresh_schema=False,
    create_indexes=False,
)

with graph_store.client.session(database="neo4j") as session:
    session.run(
        "MERGE (p:Product {sku: $sku}) SET p.name = $name",
        sku="SKU-1",
        name="Magnesium Glycinate",
    )
```

## Files This Affects

- `src/graph_builder.py` — graph store construction and ingestion path
- `tests/test_graph_builder.py` — MERGE and failure-path coverage

## What We Ruled Out (and Why)

| Approach | Why Rejected |
|----------|--------------|
| Direct CREATE writes | Breaks idempotency and duplicates nodes on re-ingestion |
| Separate vector DB | Splits semantic search from traversal and adds sync risk |

## Security Assessment

- [ ] CVE check (Snyk, npm audit, pip-audit)
- [ ] Maintenance health (last release, open issues, bus factor)
- [ ] License compatibility
- [ ] Dependency tree risk (transitive deps count, known vulnerabilities)
- [ ] Download stats / popularity
- [ ] Single-maintainer risk assessment

## Known Gotchas / Edge Cases

- AuraDB credentials must be present before connecting.
- `MERGE` must stay parameterized to prevent duplicate nodes and injection risk.

## Integration Notes

`src/graph_builder.py` keeps the public entrypoint narrow: load enriched products, derive triples from research corpus text, then write idempotently into Neo4j.