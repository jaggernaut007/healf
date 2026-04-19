# Agent Observability

Healf uses **Arize Phoenix** for comprehensive agent tracing and observability.

## Tracing Coverage

- **LangChain/LangGraph**: Full execution graph, including node transitions and state updates.
- **OpenAI / Instructor**: All structured extractions and direct LLM completions.
- **Tools**: Evidence retrieval and external API calls.

## Configuration

Observability is controlled via environment variables in your `.env` file:

- `HEALF_ENABLE_OBSERVABILITY`: Set to `true` to enable tracing. Defaults to `false`.
- `PHOENIX_COLLECTOR_ENDPOINT`: The URL of your Phoenix server (default: `http://localhost:6006`).

## Usage

### 1. Start the Phoenix Server
For persistent traces, run the server in a separate terminal:
```bash
uv run python -m phoenix.server.main serve
```

### 2. View Traces
Run the agent (with `HEALF_ENABLE_OBSERVABILITY=true`) and visit [http://localhost:6006](http://localhost:6006) to inspect:
- **Trace Spans**: Detailed timing and input/output for every LLM call.
- **Evaluation Spans**: Quality gate scores and findings.
- **Response Schemas**: Exact Pydantic models used by Instructor.
