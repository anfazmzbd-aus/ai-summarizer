# AI-Summarizer

An enterprise-grade, **Agentic AI Document Processing and Summarization Platform** built on top of FastAPI and designed as a deterministic, contract-driven, and parallel-safe DAG execution runtime. 

AI-Summarizer has evolved from a simple monolithic script into a highly sophisticated **Agentic AI Workflow Engine** capable of dynamic routing, robust error isolation, event-driven observability, and advanced summarization strategies (such as hierarchical map-reduce and context preservation).

---

## 🚀 Current Version: V9.2.0 (Milestone 4 Frozen)

The platform is currently at **V9.2.0**, with **695 passing tests** and full compliance with `black`, `ruff`, and `pre-commit` quality gates.
* **Non-Live Test Suite:** 672 passed, 9 deselected.
* **Live Integration Suite:** 9 passed, skipped when credentials are absent.
* **Milestone 4 (Map-Reduce Summarization Strategy):** Complete and frozen.
* **Milestone 5 (Context-Preserving Aggregation):** In progress.

---

## 📋 Overview

AI-Summarizer is not just a text summarization tool; it is a general-purpose, reusable **AI Orchestration Platform** that executes specialized analytical agents through a Directed Acyclic Graph (DAG). By strictly separating the **Application/Service**, **Runtime**, and **Execution** layers, the platform allows developers to plug in new agents, prompts, or LLM providers without altering the underlying deterministic kernel.

### The Problem it Solves
Standard agentic systems often fail in production because of unconstrained state mutations, circular dependency deadlocks, or tight coupling to a single LLM vendor. AI-Summarizer solves these systemic challenges by enforcing:
1. **Clean Layer Separation:** Preprocessing and planning occur strictly outside the execution graph.
2. **Node Isolation:** Every agent executes inside a read-only, deep-copied snapshot of the state.
3. **Immutable State Merger:** A centralized merger aggregates results on a single thread to prevent parallel-safe state mutations.
4. **Provider Abstraction:** A vendor-neutral adapter layer separates agent logic from OpenAI, Azure, Ollama, or OpenRouter SDKs.

---

## 🏛️ System Architecture

AI-Summarizer implements a robust, layered Clean Architecture:

```
                  ┌──────────────────────────────────┐
                  │        CLIENT / UI LAYER         │
                  │   Web UI • API • Playground API   │
                  └────────────────┬─────────────────┘
                                   │
                                   ▼
                  ┌──────────────────────────────────┐
                  │       REQUEST ENTRY LAYER        │
                  │       routes/summarize.py        │
                  └────────────────┬─────────────────┘
                                   │
                                   ▼
   ═════════════════════ PREPROCESSING (NON-DAG) ═════════════════════
                  ┌──────────────────────────────────┐
                  │    Token-Aware Text Chunking     │
                  │  (DeterministicTokenCounter)     │
                  └────────────────┬─────────────────┘
                                   │
                                   ▼
                  ┌──────────────────────────────────┐
                  │        SUMMARY GENERATION        │
                  │       summary_agent (Sync)       │
                  └────────────────┬─────────────────┘
                                   │
                                   ▼
                  ┌──────────────────────────────────┐
                  │        PLANNING / ROUTING        │
                  │  Intent Classifier • Router      │
                  └────────────────┬─────────────────┘
                                   │
                                   ▼
   ═════════════════════════ DAG ENGINE ═════════════════════════
                  ┌──────────────────────────────────┐
                  │       DEPENDENCY RESOLVER        │
                  │    resolve_execution_order()     │
                  └────────────────┬─────────────────┘
                                   │
                                   ▼
                  ┌──────────────────────────────────┐
                  │        GRAPH VALIDATOR           │
                  │   validate_execution_graph()     │
                  └────────────────┬─────────────────┘
                                   │
                                   ▼
                  ┌──────────────────────────────────┐
                  │        PARALLEL SCHEDULER        │
                  │    scheduler.py (Kahn-based)     │
                  └────────────────┬─────────────────┘
                                   │
                                   ▼
                  ┌──────────────────────────────────┐
                  │         LAYER EXECUTOR           │
                  │  ThreadPoolExecutor Concurrency  │
                  └────────────────┬─────────────────┘
                                   │
                                   ▼
                  ┌──────────────────────────────────┐
                  │          NODE EXECUTOR           │
                  │  Isolated Snapshot Execution     │
                  └────────────────┬─────────────────┘
                                   │
                                   ▼
                  ┌──────────────────────────────────┐
                  │          STATE MERGER            │
                  │     Centralized Commit (V7.7)    │
                  └────────────────┬─────────────────┘
                                   │
                                   ▼
   ══════════════════════ STORAGE & PERSISTENCE ══════════════════════
                  ┌──────────────────────────────────┐
                  │   DB Persistence / History /     │
                  │   Telemetry / Checkpoint Engine  │
                  └──────────────────────────────────┘
```

### The Two-Phase Pipeline
1. **Phase A (Pre-DAG Preprocessing - Non-DAG):** Performs token-aware text chunking, normalization, summary pre-computation, and semantic planning/routing. These are deterministic transformers, completely separated from the DAG scheduling core to avoid graph contamination.
2. **Phase B (DAG Engine - Graph Core):** Constructs a pure dependency graph containing only analytical nodes (e.g., `insights`, `trends`, `risks`, `recommendations`). This graph is validated for cycles and executed layer-by-layer concurrently.

---

## ✨ Key Features

AI-Summarizer contains several enterprise-ready subsystems designed for reliability, scalability, and observability:

### 1. Multi-Agent Ecosystem
A centralized decorated registry (`@register_agent`) allows dynamic discovery of specialized agents. Current analytical agents include:
* **Summary Agent:** Generates text summaries (utilizing the model or a sentence preservation fallback).
* **Actions Agent:** Extracts concrete tasks and follow-up items using regex rule-based structures.
* **Insights Agent:** Captures high-level business insights and CSAT/NPS shifts.
* **Trend & Sentiment Agents:** Classifies trend indicators and text sentiment.
* **Risk & Forecast Agents:** Identifies threat vectors and projects potential future trends.
* **Recommendation & Root Cause Agents:** Suggests actions and performs evidential diagnosis.

### 2. Advanced Summarization (V9.2)
* **Token-Aware Chunking:** Paragraph and sentence boundaries are preserved while dividing large documents using a deterministic `TokenCounter` and configurable maximum sizes/overlaps.
* **Hierarchical Summarization:** Constructs a dependency hierarchy tree of document segments (`SummaryNode`), retaining deep character-source offset provenance back to the raw chunk inputs.
* **Map-Reduce Strategy:** Executes parallel MAP summarization across segments and merges them using an intelligent REDUCE aggregator without model-context leakage.

### 3. State & Execution Isolation
* **ExecutionSession:** The single container that wraps the graph, execution context, and intelligence decision, representing one unified workflow execution.
* **Node Isolation:** Avoids race conditions by running each node on deep-copied snapshots. Outputs are committed back to the session only after a successful execution.
* **Contract Enforcement:** Integrates a strict `StateContract` validation step. An agent cannot execute unless its required input schemas are validated, and its output must be validated before it is committed to the shared state.

### 4. Pluggable Infrastructure Abstractions
* **PromptOS:** Treats prompt templates (`PromptDefinition`) as first-class versioned assets stored in markdown with YAML front matter, isolated from Python code.
* **AI Provider Abstraction:** A vendor-neutral SDK client interface (`BaseProvider`) that isolates the runtime from concrete APIs. Supports a fully offline/deterministic `MockProvider`, alongside live integrations for **OpenAI**, **Azure OpenAI**, **Google Gemini**, and local **Ollama** backends.
* **OpenRouter Compatibility:** Supports routing requests to any OpenAI-compatible API endpoint (such as OpenRouter, LiteLLM, or LM Studio) using configuration variables.

### 5. Production Reliability & Resiliency
* **Event-Driven Observability:** Decouples core execution from logging, metrics, and tracing. Emits detailed lifecycle events (e.g., `ExecutionStarted`, `NodeFailed`, `RetryStarted`) to an `EventBus` consumed by independent subscribers.
* **Retry Executor:** Implements configurable backoff retry loops at the individual node level, rather than re-running the entire graph.
* **Circuit Breakers:** Uses a state-machine circuit breaker (`Closed`, `Open`, `Half-Open`) to isolate flaky external LLM endpoints and prevent cascading failures.
* **Timeout & Graceful Cancellation:** Implements cooperative cancellation tokens and execution timeout enforcement across nodes.
* **Execution Cache:** Caches execution results to prevent redundant calls to expensive LLMs for duplicate content.
* **Checkpoint & Recovery:** Automatically persists states at layer-level checkpoints, allowing failed or interrupted executions to resume exactly where they failed.

---

## 📁 Project Structure

The project has a highly modular Clean Architecture layout:

```
ai-summarizer/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── execution_playground.py   # Debugging & E2E execution surface
│   │       ├── runtime_endpoint.py       # Metrics & trace health API
│   │       └── summarize_endpoint.py     # Live /summarize REST endpoint
│   ├── core/
│   │   ├── exceptions.py                 # Central exception hierarchy
│   │   └── config.py                     # Global app configuration
│   ├── prompts/
│   │   ├── templates/                    # Versioned prompt definitions (Markdown/YAML)
│   │   ├── manager.py                    # Resolves and orchestrates prompts
│   │   ├── renderer.py                   # Dynamic Jinja template rendering
│   │   ├── registry.py                   # Runtime-facing prompt discovery
│   │   └── repository.py                 # Persistence layer for templates
│   ├── providers/
│   │   ├── openai/
│   │   │   ├── adapter.py                # Adapts OpenAI payload to LLMResponse
│   │   │   ├── client.py                 # Thin OpenAI SDK client wrapper
│   │   │   ├── config.py                 # Credentials and endpoint configurations
│   │   │   └── transport.py              # HTTP client/SDK initialization
│   │   ├── base.py                       # Provider abstraction (BaseProvider)
│   │   ├── config.py                     # Generic provider configuration (ProviderConfig)
│   │   ├── factory.py                    # Instantiates configured LLM providers
│   │   ├── mock_provider.py              # Deterministic offline provider for CI tests
│   │   └── runtime.py                    # Provider-to-runtime composition boundary
│   ├── runtime/
│   │   ├── events/
│   │   │   ├── event_bus.py              # Decoupled synchronous publisher
│   │   │   ├── event_dispatcher.py       # Dispatches execution events
│   │   │   ├── event_types.py            # Typed dataclass definitions
│   │   │   └── runtime_event_publisher.py# Unified helper to publish events
│   │   ├── observer/
│   │   │   ├── logging_subscriber.py     # Converts events to structured logs
│   │   │   ├── metrics_subscriber.py     # Monitors timings, counts, and retries
│   │   │   └── trace_subscriber.py       # Constructs execution tracing timelines
│   │   ├── middleware/                   # Request preprocessing hooks
│   │   ├── hooks/                        # Execution hook registry
│   │   ├── policy/                       # Pluggable admission controls
│   │   ├── cache/                        # Node execution caching
│   │   ├── persistence/                  # Persists execution metadata and results
│   │   ├── checkpoint/                   # Node-level checkpointing and recovery
│   │   ├── runtime_manager.py            # Orchestrates execution context & lifecycle
│   │   ├── runtime_session.py            # Aggregate session data container
│   │   └── runtime_context.py            # State metadata during lifecycle
│   ├── orchestration/
│   │   ├── agents/
│   │   │   ├── summary.py                # summary_agent (V8 legacy / V9 AI-mode)
│   │   │   ├── insights.py               # insights_agent
│   │   │   └── actions.py                # actions_agent
│   │   ├── contracts/
│   │   │   ├── execution_response.py     # Output response Pydantic models
│   │   │   └── response_builder.py       # Converts session state to response
│   │   ├── execution/
│   │   │   ├── execution_engine.py       # Executes DAG layers
│   │   │   ├── layer_executor.py         # Concurrent thread layer executor
│   │   │   └── node_executor.py          # State-contract validation & retry runner
│   │   ├── graph/
│   │   │   ├── graph_builder.py          # Constructs ExecutionGraph from intents
│   │   │   ├── graph_schema.py           # Immutable DAG schemas & types
│   │   │   └── graph_validator.py        # Dependency closure & cycle detector
│   │   ├── registry/
│   │   │   ├── agent_registry.py         # Maps agent names to implementations
│   │   │   └── contract_manager.py       # Enforces StateContracts
│   │   ├── scheduler/
│   │   │   └── scheduler.py              # Purely declarative parallel scheduler
│   │   └── state/
│   │       ├── state_model.py            # Shared State dataclass container
│   │       ├── state_builder.py          # Builds execution State
│   │       └── state_merger.py           # Thread-safe state mutation merger
│   └── services/
│       ├── llm_service.py                # Runtime-facing LLM execution wrapper
│       └── summarize_service.py          # Application-level service entrypoint
├── app/tests/                            # Standard V8/V9 pytest testing suite
│   ├── architecture/                     # Verifies import rules and layering
│   ├── distributed/                      # Queues, workers, and distributed tests
│   ├── execution/                        # Executor and engine tests
│   ├── integration/                      # End-to-end and live provider tests
│   ├── prompts/                          # Prompt lifecycle & rendering tests
│   └── runtime/                          # Context, metadata, and resilience tests
└── main.py                               # FastAPI application bootstrapper
```

---

## 🏃 Running the Application

AI-Summarizer is fully compatible with Windows 11, macOS, and Linux.

### 1. Environment Setup

It is highly recommended to use Python 3.11. 

**Windows (PowerShell):**
```powershell
# Create a virtual environment
python -m venv venv311

# Activate the virtual environment
.\venv311\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt
```

**macOS/Linux (Bash):**
```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 2. Environment Variables (`.env`)

Create a `.env` file in the project root:

```ini
# Core Configuration
DEBUG=True
PORT=8000

# Provider Selection (mock | openai | openrouter)
AI_PROVIDER=mock
AI_MODEL=mock-model

# OpenAI Credentials (Required if AI_PROVIDER=openai)
OPENAI_API_KEY=your_openai_api_key

# OpenRouter Credentials (Required if AI_PROVIDER=openrouter)
OPENAI_API_KEY=your_openrouter_api_key
OPENAI_BASE_URL=https://openrouter.ai/api/v1
AI_MODEL=openai/gpt-4o-mini
```

### 3. Starting the Server

Launch the FastAPI application with Uvicorn:

```bash
uvicorn app.main:app --reload
```
Once started:
* **Swagger UI Documentation:** http://127.0.0.1:8000/docs
* **Playground Home API:** http://127.0.0.1:8000/playground/

### 4. Running the Tests

To ensure the integrity of the runtime, you can execute the extensive test suite.

**Run All Standard (Offline) Tests:**
```bash
pytest -m "not live" -q
```
*Expected Output:* ~672 passed, 9 deselected (0.00s network calls).

**Run Live Integration Tests (API Key Required):**
Set up your `.env` credentials, then run:
```bash
pytest -m live --run-live -v
```

**Quality Gates Verification (Ruff + Black):**
```bash
pre-commit run --all-files
```

---

## 🗺️ Long-Term Roadmap

The platform follows a clear progression roadmap:

* **V7.7:** Deterministic DAG Execution Kernel ✅
* **V7.8:** Production Runtime Abstraction (Context, Sessions, EventBus, Observability) ✅
* **V9.0:** AI Integration Framework (PromptOS, LLM Abstraction, Mock/OpenAI providers) ✅
* **V9.1:** Provider Configuration & Live Validation (OpenRouter API integration, exception classifications) ✅
* **V9.2 (Current):** Advanced Summarization (Token-aware Chunking, Hierarchical Summary Trees, Map-Reduce workflows) 🚧
* **V9.3:** Prompt Intelligence (Prompt evaluations, token optimizers, versioning diagnostics)
* **V9.4:** Production Retrieval Augmented Generation (Document embeddings, Vector DB backends, citation generation, source verification)
* **V9.5:** Multi-Agent Intelligence (Planner, Researcher, Fact-checker, Critic, Synthesizer agents)
* **V9.6:** Autonomous Agentic Runtime (Autonomous planning, tool call execution, long-term memory-aware execution, reflection loops)
* **V10.0:** Distributed Enterprise Platform (Worker pooling, queues, multi-tenant horizontal scaling, gRPC remote adapters, human-in-the-loop review)

---

## 🤝 Contributing

Contributions are highly encouraged! Please ensure all pull requests strictly follow the project's core guidelines:
1. **Clean Imports:** Avoid circular dependencies. Walk imports down, never up.
2. **Deterministic Pipeline:** The execution engine must remain pure. All adaptive changes are made in the runtime or intelligence layers.
3. **No Uncoded Abstractions:** If you introduce an interface, implement a complete mocked representation alongside it.
4. **Test-First Cadence:** No new feature is considered merged until its unit tests pass with 100% reliability.

---

## 📄 License

This project is licensed under the Apache 2.0 License - see the LICENSE file for details.
