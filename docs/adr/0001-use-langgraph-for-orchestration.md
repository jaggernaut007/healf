# 1. Use LangGraph for Agentic Orchestration

## Status
Accepted

## Context
The health-intelligence engine requires complex state management, cyclical agentic workflows (e.g., plan -> implement -> review -> revise), and fault tolerance for external API calls (Firecrawl, Neo4j, LLM endpoints). Standard sequential chains are insufficient for building resilient, autonomous AI agents capable of correcting their own errors or managing a shared memory space across multiple tools.

## Decision
We will use LangGraph to orchestrate our AI workflows. LangGraph provides a robust, stateful framework built on top of LangChain, allowing us to define our agents as nodes in a graph with explicit state channels (using `TypedDict`). It supports cyclical reasoning patterns, human-in-the-loop capabilities, and straightforward state persistence.

## Consequences
- **Positive:** Robust state management across complex, multi-step subagent workflows.
- **Positive:** Easier debugging of agent decisions through inspectable graph state.
- **Negative:** Steeper learning curve compared to simple chains.
- **Negative:** Tighter coupling to the LangChain ecosystem.