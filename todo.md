# Project Todos

## ✅ Phase 0: Research & Architecture (COMPLETE)
- [x] Research LangChain OpenAI integration
- [x] Research LangGraph orchestration
- [x] Research FastAPI framework
- [x] Research SlowAPI rate limiting
- [x] Research Uvicorn ASGI server
- [x] Research Pydantic v2
- [x] Research Instructor library
- [x] Research Requests HTTP client
- [x] Research DeepEval framework
- [x] Research Arize Phoenix observability
- [x] Research OpenInference instrumentation
- [x] Research pytest framework
- [x] Research Hypothesis property testing
- [x] Update INDEX with all research files
- [x] Create 6 ADRs for architectural decisions
- [x] Expand ADR set to cover GraphRAG/API/Safety/Observability/Evals/Structured outputs (0003-0008)

## ✅ Phase 1: Data Enrichment (COMPLETE)
- [x] Implement EnrichmentClient (Firecrawl, Instructor, NIH RxTerms)
- [x] Create enrichment pipeline orchestrator
- [x] Define EnrichedProduct Pydantic model
- [x] Add enrichment tests

## ✅ Phase 2: Knowledge Graph (COMPLETE)
- [x] Implement GraphBuilder with Neo4j integration
- [x] Create inference rules engine
- [x] Add preflight validation
- [x] Add comprehensive graph builder tests

## ✅ Phase 3: Agentic Orchestration (COMPLETE)
- [x] Create specs for all phases
- [x] Research LangGraph + NeMo orchestration patterns
- [x] Implement LangGraph orchestration workflow
- [x] Add NeMo Guardrails safety gateway integration
- [x] Add Phoenix observability instrumentation
- [x] Add DeepEval quality gates for LLM outputs
- [x] Add orchestration integration tests (happy path and failure routing)
- [x] Add prompt rewrite preprocessing node with typed output contract
- [x] Implement Intake Router agent for domain and risk routing
- [x] Implement Domain Specialist agent for graph query planning
- [x] Implement read-only graph query validator/executor boundary
- [x] Implement Graph Retriever integration with Neo4j evidence normalization
- [x] Implement Pharmacovigilance Critic with bounded retry loop
- [x] Implement conversational Payload Generator with strict evidence grounding
- [x] Add full 5-agent integration tests (pass/fail/retry paths)
- [x] Add configured-environment integration tests for DeepEval and Phoenix paths

## ✅ Governance: Copilot Spec Enforcement (COMPLETE)
- [x] Create canonical `SPEC.md` as repository source of truth
- [x] Add mandatory spec-grounding rules to `AGENTS.md` and `.github/copilot-instructions.md`
- [x] Add/strengthen `.github/instructions/*` with block-on-out-of-spec rules
- [x] Add spec grounding to all `.github/agents/*` and `.claude/agents/*`
- [x] Add spec gates to all `.agents/workflows/*`
- [x] Add spec conformance gates to `.claude/skills/*/SKILL.md`

## ✅ Phase 4: CLI & UX (COMPLETE)
- [x] Research Rich CLI patterns
- [x] Research Typer CLI framework
- [x] Research Invoke task runner
- [x] Document CLI/task-runner architecture decision in ADR
- [x] Create rich CLI interface with rich formatting
- [x] Add task runner implementation (`tasks.py`)
- [x] Add CLI integration tests and task runner tests
- [x] Run end-to-end smoke verification

## ✅ Legacy Todo Sync
- [x] Previous research checklist fully completed and reconciled into active plan
- [x] Previous plan items merged into Phase 3 and Phase 4 sections

## ✅ Phase 5: Compliance and Industrial Hardening (COMPLETE)
- [x] Research Industrial MCP Stack (nexus-mcp, memstate-ai, context7, playwright)
- [x] Implement MCP configuration and routing matrix
- [x] Implement `pre-flight-check` Industrial Meta-Tool skill
- [x] Perform Triple Agent Audit of Phase 4 CLI/UX (Evidence in `docs/audits/`)
- [x] Scaffold `evals/` suite with orchestration datasets
- [x] Implement TTL L1 Caching in enrichment pipeline
- [x] Perform Triple Agent Audit of Phase 5 (Evidence in `docs/audits/phase-5-audit.md`)

## My Notes (DO NOT EDIT THIS SECTION)
- evaluations
- tracing/observability
- better testing framweworks for LLM/softwre engineering
- Gronding audits and guardrails