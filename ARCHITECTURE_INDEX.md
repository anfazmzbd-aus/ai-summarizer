Architecture Audit #1 (V9.1.0 Package 3)
Services
app/services/

✔ llm_service.py
✔ summarize_service.py

Providers
app/providers/

✔ base.py
✔ config.py
✔ factory.py
✔ registry.py
✔ models.py
✔ capabilities.py
✔ health.py
✔ request_builder.py
✔ response_parser.py

✔ openai/

Prompts
app/prompts/

✔ manager.py
✔ service.py
✔ renderer.py
✔ repository.py
✔ registry.py
✔ loader.py
✔ validator.py
✔ rendered_prompt.py
✔ metadata.py
✔ models.py
✔ value_objects.py



FastAPI
    │
    ▼
SummarizeService          (existing)
    │
    ▼
PromptManager             (existing)
    │
    ▼
PromptRenderer            (existing)
    │
    ▼
LLMRequestBuilder         (existing)
    │
    ▼
LLMService                (existing)
    │
    ▼
ProviderFactory           (existing)
    │
    ▼
OpenAIProvider            (implemented)
    │
    ▼
OpenAIAdapter
    │
    ▼
OpenAITransport
    │
    ▼
OpenAI Responses API



Providers
---------
Canonical:
    app/providers/

Legacy:
    app/ai/providers/  (remove before V9 release)

Services
--------
Canonical:
    app/services/

Do not create:
    app/services/llm/

Prompts
-------
Canonical:
    app/prompts/

Runtime
-------
Canonical:
    app/orchestration/

V9 Intelligence Integration Boundary
    RuntimeManager

            |
            ▼

    State object

            |
            ▼

    NodeExecutor

            |
            ▼

    Agent.run(state)

            |
            ▼

Agent uses global_context

            |
            ▼

    LLMService

            |
            ▼

ProviderFactory

            |
            ▼

    OpenAIProvider

V9.1.0 Package 3A
=================

Agent Dependency Injection Foundation

ProviderFactory
        |
        ▼
LLMService
        |
        ▼
AgentRegistry
        |
        ▼
SummaryAgent

Files:
- AgentRegistry update
- Agent construction update
- SummaryAgent upgrade
- Tests

State
├── global_context
│   └── text
│
├── artifacts
│
├── node_outputs
│
└── services
    ├── llm_service       ← V9
    ├── prompt_manager    ← V9
    └── future services

Package 3A
State capability channel
        ↓
Package 3B
Service construction/configuration
        ↓
Package 3C
Agent consumes LLMService
        ↓
Package 3D
Real OpenAI end-to-end execution



V9.1.0 Package 3B
=================
Application LLM Wiring

app/services/
    llm_service.py              existing, unchanged
    llm_service_factory.py      NEW

app/services/
    summarize_service.py        minimal integration

app/tests/services/
    test_llm_service_factory.py
    test_summarize_service.py

SummarizeService
       │
       ▼
LLMServiceFactory
       │
       ├── ProviderConfig
       │
       ▼
ProviderFactory
       │
       ▼
Provider
       │
       ▼
State.services["llm_service"]

application
    ↓
LLMServiceFactory
    ↓
LLMService
    ↓
ProviderFactory

V9.1.0 checkpoint
Package 3A
State capability channel
9 tests
        ↓
Package 3B
Application LLM wiring
9 service tests
        ↓
Full regression
536 passed

V9.1.0 Package 3C — Intelligent Summary Agent
SummaryAgent
    │
    ├── text from State
    │
    ▼
PromptManager
    │
    ▼
Rendered Prompt
    │
    ▼
LLMRequest
    │
    ▼
LLMService
    │
    ▼
Provider
    │
    ▼
LLMResponse
    │
    ▼
{"summary": "..."}

Runtime flow
State
 │
 ├── global_context["text"]
 │
 └── services["llm_service"]
          │
          ▼
    PromptManager
          │
          ▼
    RenderedPrompt
          │
          ▼
      LLMRequest
          │
          ▼
      LLMService
          │
          ▼
     LLMResponse
          │
          ▼
    {"summary": "..."}

Architectural checkpoint
After Package 3C:
V8 Production Runtime
        │
        ▼
ExecutionEngine
        │
        ▼
NodeExecutor
        │
        ▼
SummaryAgent
        │
        ├──────── PromptManager
        │              │
        │              ▼
        │        Versioned Prompt
        │
        └──────── LLMService
                       │
                       ▼
                 ProviderFactory
                       │
              ┌────────┼────────┐
              ▼        ▼        ▼
           OpenAI    Azure    Ollama

** Correct architecture **
                    V8 Runtime
                        │
                 AgentRegistry
                        │
          ┌─────────────┴─────────────┐
          │                           │
   default/legacy agents       injected SummaryAgent
                                      │
                              PromptManager
                                      │
                                  LLMService
                                      │
                              ProviderFactory
                                      │
                         OpenAI / Azure / Ollama


** V9.1.0 Provider Runtime **
app/providers/ = V9 provider abstraction and provider implementations
app/services/ = application/service orchestration
app/prompts/ = prompt lifecycle
app/orchestration/ = execution graph and agents
app/runtime/ = runtime lifecycle/intelligence
Existing V8 runtime/orchestration components remain authoritative unless a deliberate V9 integration point is introduced.
No duplicate provider/service architecture.

# ** V9.1.0 Package 2: Provider Runtime Integration. **
SummaryAgent
    ↓
PromptManager
    ↓
LLMService
    ↓
ProviderFactory
    ↓
BaseProvider
    ↓
Mock/OpenAI/Azure/Ollama


#** V9.1.0 status **
| Area                              | Status            |
| --------------------------------- | ----------------  |
| Provider contracts                | ✅                |
| Provider registry/factory         | ✅                |
| OpenAI adapter                    | ✅                |
| Provider runtime composition      | ✅                |
| Prompt integration                | ✅                |
| `SummaryAgent` provider injection | ✅                |
| V8 legacy SummaryAgent behavior   | ✅                |
| V8 orchestration compatibility    | ✅                |
| Full regression suite             | **✅ 547 passed** |

# ** V9.1.0 Package 3: End-to-End Provider Execution. **
API
 ↓
SummarizeService                 ← V8 lifecycle remains
 ↓
RuntimeManager                   ← V8/V7 runtime remains
 ↓
ExecutionEngine
 ↓
SummaryAgent                     ← V9 intelligence boundary
 ↓
PromptManager
 ↓
LLMService
 ↓
ProviderFactory
 ↓
Mock / OpenAI / Azure / Ollama

** Package 3 objective **

Establish this complete path:
/playground/execute
        ↓
SummarizeService
        ↓
RuntimeManager
        ↓
ExecutionEngine
        ↓
SummaryAgent
        ↓
PromptManager
        ↓
LLMService
        ↓
ProviderFactory
        ↓
MockProvider

Architectural boundary

V8 Architecture
────────────────────────────────────────
API
 ↓
Service
 ↓
RuntimeManager
 ↓
ExecutionEngine
 ↓
AgentRegistry
 ↓
Agents
 ↓
State


V9 Intelligence
────────────────────────────────────────
                    ┌── PromptManager
                    │
Agent ──────────────┼── LLMService
                    │
                    └── ProviderRuntime
                             ↓
                         Provider


Package 3B

                 APPLICATION COMPOSITION ROOT
                           │
             ┌─────────────┴─────────────┐
             │                           │
       PromptRepository            ProviderFactory
             │                           │
       PromptRegistry              ProviderConfig
             │                           │
       PromptManager                LLMService
             │                           │
             └──────────────┬────────────┘
                            │
                     AgentRegistry
                            │
                       SummaryAgent
                            │
                     RuntimeManager
                            │
                    ExecutionEngine

Package 3B implementation
ProviderRuntime
      │
      └── LLMService
             │
PromptManager ─┤
               ▼
        AgentRegistry
               │
               ▼
          SummaryAgent
               │
               ▼
        ExecutionEngine
               │
               ▼
          RuntimeManager

**  After Package 3C  **
V9.0
 ├─ Package 1  Provider foundation       ✅
 ├─ Package 2  Agent/runtime integration ✅
 ├─ Package 3B Runtime wiring            ✅ 559
 ├─ Package 3C Prompt bootstrap          ← NEXT
 ├─ Package 3D Deterministic E2E
 └─ V9.1 Live Provider Validation
       ├─ Mock endpoint
       ├─ OpenAI API
       ├─ Error handling
       ├─ token/usage validation
       └─ real /api/v1/summarize

** V9.x current baseline **
| Package         | Status                          |
| --------------- | ------------------------------- |
| Package 1       | ✅ Complete                      |
| Package 2       | ✅ Complete                      |
| Package 3A      | ✅ Complete                      |
| Package 3B      | ✅ Complete                      |
| Package 3C      | ✅ Complete                      |
| **Package 3D**  | 🟢 Current implementation green |
| Full regression | **566 passed**                  |



** V9 AI execution inside that envelope **
POST /playground/execute
          │
          ▼
   SummarizeService
          │
          ▼
    RuntimeManager
          │
          ▼
   ExecutionEngine
          │
          ▼
     SummaryAgent
          │
          ▼
    PromptManager
          │
          ▼
      LLMService
          │
          ▼
     MockProvider
          │
          ▼
   ExecutionResponse
          │
          ├── result.summary
          ├── node_outputs
          ├── trace
          ├── metrics
          └── metadata

Package 3D now establishes:
SummarizeService()
    │
    ├── PromptRepository
    ├── PromptRegistry
    ├── PromptManager
    │
    └── ProviderRuntime
            │
            ├── LLMService
            └── MockProvider

V9.0 Package 3D
Deterministic V9 E2E
        │
        ▼
V9.1
├── Mock endpoint validation
├── OpenAI API validation
├── Provider error handling
├── Token / usage validation
└── Real /api/v1/summarize

API
 ↓
SummarizeService
 ↓
RuntimeManager
 ↓
ExecutionEngine
 ↓
SummaryAgent
 ↓
PromptManager
 ↓
LLMService
 ↓
MockProvider
 ↓
ExecutionResponse

** Package 3D completion scope **

I would treat 3D as complete only when all of these are green:

1. Deterministic V9 service execution
   * SummarizeService() uses the V9 runtime.
   * Default provider is MockProvider.
   * No V8 summary fallback.
2. Prompt → Agent → LLMService path
    * Summary prompt is resolved and rendered.
    * SummaryAgent executes through LLMService.
    * Mock response reaches the final result.
3. Execution response contract
    * ExecutionResponse is returned consistently.
    * execution_id is populated.
    * status is correct.
    * result contains the summary.
    * node_outputs contains the agent output.
    * trace/metrics remain compatible with the existing runtime.
4. API boundary
    * /playground/execute returns the complete ExecutionResponse.
    * FastAPI response validation passes.
5. Regression protection
    * Add focused tests for the above contracts.
    * Preserve all existing V8/V9 tests.
    * No architectural redesign.
6. Final verification
    * pytest

Package 3D
Deterministic V9 End-to-End
MockProvider
        ↓
V9.1
Live Provider Validation
        ↓
OpenAI API
Error handling
Usage/token validation
Real /api/v1/summarize

** Package 3D completion target **
SummarizeService
      ↓
RuntimeManager
      ↓
ExecutionEngine
      ↓
SummaryAgent
      ↓
PromptManager
      ↓
LLMService
      ↓
MockProvider
      ↓
ExecutionResponse
      ↓
/playground/execute

** Correct 3D change **
HTTP request
    ↓
FastAPI
    ↓
SummarizeService
    ↓
RuntimeManager
    ↓
ExecutionEngine
    ↓
SummaryAgent
    ↓
PromptManager
    ↓
LLMService
    ↓
MockProvider
    ↓
State
    ↓
ResponseBuilder
    ↓
ExecutionResponse
    ↓
HTTP response

** Package 3D — COMPLETE ✅ **
HTTP
 ↓
FastAPI
 ↓
SummarizeService
 ↓
RuntimeManager
 ↓
ExecutionEngine
 ↓
SummaryAgent
 ↓
PromptManager
 ↓
LLMService
 ↓
MockProvider
 ↓
ExecutionResponse
 ↓
HTTP response

** V9.0 status **
Package	Status
Package 1	✅ Complete
Package 2	✅ Complete
Package 3A	✅ Complete
Package 3B	✅ Complete
Package 3C	✅ Complete
Package 3D	✅ Complete

** Next Phase **
V9.0
Package 3D
Deterministic E2E
        │
        ▼
V9.1 Live Provider Validation
        │
        ├── Mock endpoint
        ├── OpenAI API
        ├── Provider error handling
        ├── Token / usage validation
        └── Real /api/v1/summarize

**V9.1 Milestone 1: Provider validation boundary**
/api/v1/summarize
        ↓
SummarizeService
        ↓
V9 Runtime
        ↓
SummaryAgent
        ↓
LLMService
        ↓
ProviderFactory
        ↓
┌─────────────────────┐
│ MockProvider        │ ← deterministic CI path
│ OpenAIProvider      │ ← live validation path
└─────────────────────┘

**project state**
V9.0
│
├── Package 1   Provider foundation                 ✅
├── Package 2   Agent/runtime integration           ✅
│
├── Package 3A  State capability channel            ✅
├── Package 3B  Service construction/config         ✅
├── Package 3C  Agent consumes LLMService           ✅
└── Package 3D  Deterministic E2E                   ✅ FROZEN
                                                     │
                                                     ▼
V9.1
└── Live Provider Validation
    ├── Mock endpoint
    ├── OpenAI API
    ├── Provider error handling
    ├── Token / usage validation
    └── Real /api/v1/summarize

V9.1 should build on the exact architecture already established:
/api/v1/summarize
        ↓
SummarizeService
        ↓
RuntimeManager
        ↓
ExecutionEngine
        ↓
SummaryAgent
        ↓
PromptManager
        ↓
LLMService
        ↓
ProviderRuntime
        ↓
OpenAI Provider
        ↓
real OpenAI API

**V9.1 next package**
V9.1 Live Provider Validation
        │
        ├── 1. OpenAI adapter normalization      ✅
        ├── 2. Provider/runtime composition      ✅
        ├── 3. Real API integration test         ← NEXT
        ├── 4. Error handling validation
        ├── 5. Token/usage validation
        └── 6. Real /api/v1/summarize validation

V9.1 API-level live validation

We have validated:

Provider construction ✅
Real external LLM execution ✅
Real response normalization ✅
Real token usage ✅
Real latency ✅
Full regression ✅

actual application path
POST /api/v1/summarize
        │
        ▼
SummarizeService
        │
        ▼
V9 Runtime
        │
        ▼
SummaryAgent
        │
        ▼
LLMService
        │
        ▼
OpenAIProvider
        │
        ▼
OpenRouter
        │
        ▼
Real LLM response

**V9.1 frozen scope**

The freeze should preserve the following established contracts:
    * ProviderSettings
    * ProviderRuntime.from_settings()
    * ProviderRuntime.openai()
    * SummarizeService(provider_settings=...)
    * SummarizeService.from_environment()
    * SummarizeService.from_openrouter()
    * explicit LLMService injection
    * deterministic MockProvider default
    * OpenRouter through the OpenAI-compatible provider
    * ExecutionResponse as the application execution contract
    * live OpenRouter validation
    * provider usage and latency capture
    * OpenAI provider exception classification

pytest: 617 passed
pre-commit: passed
git diff --check: passed

## **V9.1 status**

## V9.1 — Live Provider Validation → COMPLETE / FROZEN

The following are now established:

    * Provider configuration and environment settings
    * Provider runtime composition
    * MockProvider deterministic runtime
    * OpenAI-compatible provider path
    * OpenRouter live execution
    * Provider error classification
    * Usage/token normalization
    * Latency capture
    * Application-level provider wiring
    * SummarizeService configuration injection
    * Environment-based service construction
    * OpenRouter service construction
    * Deterministic default behavior
    * Full ExecutionResponse contract
    * End-to-end live summarization validation
    * Regression coverage

617 tests passing is the locked V9.1 baseline.

**Next: V9.2**

The natural next milestone is V9.2 — Advanced Summarization Intelligence:

Long-document handling
Token-aware chunking
Hierarchical summarization
Map-reduce summarization
Context-preserving aggregation
Streaming response architecture
Advanced summarization strategies
Tests and regression hardening

**V9.2-M1 status**
V9.1 frozen baseline              617 passed
V9.2-M1 new tests                  28
-----------------------------------------
Current regression                645 passed

** V9.2-M2 — Hierarchical Summarization Core **
Document
   ↓
Chunks
   ↓
Chunk summaries
   ↓
Grouped summaries
   ↓
Final summary

** M2 objective **
                Document
                  │
                  ▼
            ┌───────────┐
            │  Chunker  │
            └─────┬─────┘
                  │
        ┌─────────┼─────────┐
        ▼         ▼         ▼
    Chunk 0   Chunk 1    Chunk N
        │         │         │
        ▼         ▼         ▼
    Summary 0  Summary 1  Summary N
        │         │         │
        └─────────┼─────────┘
                  ▼
            Group / Aggregate
                  │
                  ▼
            Higher-level
            summaries
                  │
                  ▼
            Final Summary

Hierarchical summarization
Level 0
Chunks
 │
 ▼
Level 1
Chunk summaries
 │
 ▼
Level 2
Grouped summaries
 │
 ▼
Level 3
Final summary

** Map-Reduce **
                 Document
                    │
                 Chunker
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
      MAP         MAP         MAP
        │           │           │
        ▼           ▼           ▼
     Summary     Summary     Summary
        │           │           │
        └───────────┼───────────┘
                    │
                 REDUCE
                    │
                    ▼
               Final Summary

## ** V9.2-M4 — Map-Reduce Summarization Strategy **
Current state:
V9.1                         617 passed
V9.2-M1 Chunking             645
V9.2-M2 Hierarchy            673
V9.2-M3 Test isolation       672 + 9 skipped

M4 objective

Introduce a provider-independent Map-Reduce strategy.

Chunks
  │
  ├── Chunk 0 ──→ MAP ──→ Summary 0
  ├── Chunk 1 ──→ MAP ──→ Summary 1
  ├── Chunk 2 ──→ MAP ──→ Summary 2
  └── Chunk N ──→ MAP ──→ Summary N
                         │
                         ▼
                       REDUCE
                         │
                         ▼
                   Final Summary

** Architecture after M4 **
                     Document
                        │
                        ▼
                   TextChunker
                        │
                        ▼
                      Chunk[]
                        │
             ┌──────────┴──────────┐
             │                     │
             ▼                     ▼
        Hierarchy              Map-Reduce
        Builder                 Strategy
             │                     │
             │                ┌────┴────┐
             │                │         │
             │               MAP      REDUCE
             │                │         │
             └────────────────┴─────────┘
                              │
                              ▼
                     Future LLMService

## **V9.2-M5 — Context-Preserving Aggregation**

**M5 architecture**

                    Chunk
                      │
                      ▼
              Context Extraction
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
       Content     Position     Provenance
          │           │           │
          └───────────┼───────────┘
                      ▼
               ContextEnvelope
                      │
                      ▼
                 MapResult
                      │
                      ▼
             Context Aggregator
                      │
                      ▼
              AggregatedContext
                      │
                      ▼
                  REDUCE

**M5 final validation**
Context tests       27 passed
Summarization       106 passed
Full regression     722 passed
Live tests           9 deselected
Black                Passed
Ruff                 Passed
Pytest               Passed
git diff --check     Passed

## ** V9.2-M6 — Streaming Response Architecture **
**Objective**
Summarization
     │
     ▼
Streaming Strategy
     │
     ├── Event: started
     ├── Event: chunk
     ├── Event: chunk
     ├── Event: ...
     └── Event: completed

## **Current V9.2 architecture**
Document
   │
   ▼
Token-aware Chunking                 ✓ M1
   │
   ├──────────────┐
   ▼              ▼
Hierarchy      Map-Reduce             ✓ M2/M4
   │              │
   └──────┬───────┘
          ▼
Context Aggregation                   ✓ M5
          │
          ▼
   Future summarization
          │
          ▼
   Streaming Architecture             ← M6
          │
          ▼
      Future API

**M6 validation**
Validation	Result
Streaming tests	36 passed
Summarization tests	142 passed
Full non-live regression	758 passed
Live tests	9 deselected
Pre-commit	Passed
git diff --check	Passed

## **V9.2-M7 — Advanced Summarization Strategies**
**M7 objective**
                    Document
                       │
                       ▼
                 Strategy Selector
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       Direct       Map-Reduce   Hierarchical
          │            │            │
          └────────────┼────────────┘
                       ▼
                Strategy Result

## **V9.2 architecture now**
Document
   │
   ▼
Token-aware Chunking                 ✓ M1
   │
   ├───────────────┐
   ▼               ▼
Hierarchy       Map-Reduce           ✓ M2/M4
   │               │
   └───────┬───────┘
           ▼
Context-Preserving Aggregation       ✓ M5
           │
           ▼
Streaming Architecture               ✓ M6
           │
           ▼
Advanced Strategy Selection          ← M7
           │
           ▼
Future LLM integration

V9.2
 ├── M1 Long-document foundation          ✓
 ├── M2 Hierarchical core                 ✓
 ├── M3 Context-preserving aggregation    ✓
 ├── M4 Map-reduce strategy               ✓
 ├── M5 Context strategy layer            ✓
 ├── M6 Streaming architecture            ✓
 ├── M7 Advanced strategy selection       ✓
 └── M8 Regression hardening              → next

## ** V9.2-M8 — Regression Hardening & Strategy Integration **
**M8 scope**
Document
   │
   ▼
Token-aware Chunker
   │
   ▼
Strategy Selector
   │
   ├── DIRECT
   ├── MAP_REDUCE
   └── HIERARCHICAL
   │
   ▼
Context / Aggregation
   │
   ▼
Streaming Architecture
   │
   ▼
Strategy Result

** M8 architecture **
                    Document
                       │
                       ▼
                Token-aware Chunker
                       │
                       ▼
                Strategy Selector
                       │
             ┌─────────┼─────────┐
             ▼         ▼         ▼
           DIRECT   MAP_REDUCE  HIERARCHICAL
             │         │         │
             └─────────┼─────────┘
                       ▼
                Strategy Executor
                       │
                       ▼
                Pipeline Result

## ** V9.2 — Feature Complete **

V9.2
│
├── M1  Long-document foundation              ✓
│    └── Token-aware chunking
│
├── M2  Hierarchical summarization core      ✓
│
├── M3  Context-preserving aggregation       ✓
│
├── M4  Map-reduce summarization             ✓
│
├── M5  Context strategy layer               ✓
│
├── M6  Streaming response architecture      ✓
│
├── M7  Advanced strategy selection           ✓
│
└── M8  Regression hardening / pipeline      ✓

The progression from the V9.1 frozen baseline is:
V9.1 frozen       617 passed
        │
        ▼
V9.2 development
        │
        ▼
812 passed
+ 9 explicitly excluded live tests
        │
        ▼
V9.2 feature complete

## **Final V9.2 state**
                    V9.2.0
                      │
       ┌──────────────┴──────────────┐
       │                             │
   Intelligence                  Reliability
       │                             │
   Chunking                       812 tests
   Hierarchy                      9 live isolated
   Map-Reduce                     pre-commit ✓
   Context                        diff-check ✓
   Streaming
   Strategy Selection
   Pipeline
       │
       ▼
     FROZEN

## ** Final V9.2 release state **
V9.2.0
│
├── Commit: fa0fe4e
├── Branch: main
├── Remote: origin/main
├── Tag: v9.2.0
├── Tag points to HEAD: ✓
├── Remote tag synchronized: ✓
├── Working tree: CLEAN
│
├── Regression: 812 passed
├── Live tests: 9 deselected
├── Pre-commit: PASS
└── git diff --check: PASS



V9.2.0
fa0fe4e
   │
   ▼
V9.3-M1
Intelligent Summarization Planner
   │
   ├── 828 non-live tests passed
   ├── 9 live tests excluded
   ├── Black ✓
   ├── Ruff ✓
   ├── Pre-commit ✓
   └── diff check ✓

**M1 integration**
Document
   │
   ▼
DocumentProfiler
   │
   ▼
DocumentProfile
   │
   ├─────────────────────┐
   ▼                     ▼
TextChunker       StrategySelector
   │                     │
   └──────────┬──────────┘
              ▼
      SummarizationPlan

## V9.3-M2 — Document Intelligence / Document Profile.

**M2 architectural boundary**
                    V9.3
                     │
                     ▼
          ┌─────────────────────┐
          │ DocumentProfiler    │
          │                     │
          │ DocumentProfile     │
          └──────────┬──────────┘
                     │
                     ▼
          ┌─────────────────────┐
          │ SummarizationPlanner│
          └──────────┬──────────┘
                     │
                     ▼
              V9.2 mechanisms
          ┌──────────┼──────────┐
          ▼          ▼          ▼
       Chunking   Strategy    Context
                  Selection
                     │
                     ▼
                  Execute

**V9.3 status**
V9.3 Intelligent Summarization Orchestration

M1  Intelligent Summarization Planner       ✅
M2  Document Intelligence / Profile        ✅
M3  Intent-Aware Summarization              ⏳
M4  Adaptive Strategy Planning               ⏳
M5  Cost / Token / Latency Optimization     ⏳
M6  Quality Evaluation Layer                 ⏳
M7  Quality-Aware Adaptive Execution         ⏳
M8  Resilience & Fallback Strategy           ⏳
M9  Intelligent Streaming Integration        ⏳
M10 Production Hardening & Evaluation        ⏳

**V9.3-M3 — Intent-Aware Summarization.**

The architectural progression
Document
   │
   ├── DocumentProfile
   │
   └── IntentClassification
             │
             ▼
    Intelligent Planner
             │
             ▼
    SummarizationPlan
             │
       ┌─────┼─────┐
       ▼     ▼     ▼
    Chunking Strategy Context
             │
             ▼
          Execute

**V9.3 milestone status**
M1  Intelligent Summarization Planner        ✅ FROZEN
M2  Document Intelligence / Profile         ✅ FROZEN
M3  Intent-Aware Summarization               ✅ GREEN
M4  Adaptive Strategy Planning               ⏳
M5  Cost / Token / Latency Optimization      ⏳
M6  Quality Evaluation Layer                 ⏳
M7  Quality-Aware Adaptive Execution         ⏳
M8  Resilience & Fallback Strategy           ⏳
M9  Intelligent Streaming Integration        ⏳
M10 Production Hardening & Evaluation        ⏳

**V9.3-M4 — Adaptive Strategy Planning.**
**M4 objective**
Move from:

Document Profile
       +
Intent
       ↓
Deterministic Plan

to:

Document Profile
       +
Intent
       +
Constraints
       ↓
Adaptive Strategy Plan
       ↓
Existing V9.2 Strategy Executor

**M4 expected architecture**
                    SummarizationPlanner
                            │
            ┌───────────────┼────────────────┐
            ▼               ▼                ▼
    DocumentProfile   IntentClassification  Constraints
            │               │                │
            └───────────────┼────────────────┘
                            ▼
                 AdaptiveStrategyPlanner
                            │
                            ▼
                  AdaptiveStrategyPlan
                            │
                            ▼
                 Existing StrategyExecutor

V9.3-M4 design
The architecture:
                 V9.2 selector
                      │
                      ▼
              StrategySelection
                      │
                      │ baseline
                      ▼
        ┌──────────────────────────┐
        │ AdaptiveStrategyPlanner  │
        │                          │
        │ DocumentProfile          │
        │ IntentClassification     │
        │ Baseline Strategy        │
        └────────────┬─────────────┘
                     │
                     ▼
             AdaptiveStrategyPlan
                     │
                     ▼
             Existing Executor
The key principle is:

**M4 changes planning, not strategy implementation.**

**V9.3-M4 — Adaptive Strategy Planning**
The new architecture is:
DocumentProfile
       +
IntentClassification
       +
V9.2 StrategySelection
       │
       ▼
AdaptiveStrategyPlanner
       │
       ▼
AdaptiveStrategyDecision
       │
       ▼
Final SummarizationPlan
       │
       ▼
Existing StrategyExecutor

progression is now:
V9.2.0       812 passed
V9.3-M1      828 passed
V9.3-M2      842 passed
V9.3-M3      858 passed
V9.3-M4      876 passed

**V9.3 architecture after M4**
                         Document
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
      DocumentProfiler              IntentClassifier
              │                           │
              ▼                           ▼
      DocumentProfile             IntentClassification
              │                           │
              └─────────────┬─────────────┘
                            ▼
                  V9.2 StrategySelector
                            │
                            ▼
                   StrategySelection
                            │
                            ▼
                 AdaptiveStrategyPlanner
                            │
                            ▼
                 AdaptiveStrategyDecision
                            │
                            ▼
                   SummarizationPlan
                            │
                            ▼
                 Existing V9.2 Executor

The regression progression
V9.2.0       812 passed
V9.3-M1      828 passed
V9.3-M2      842 passed
V9.3-M3      858 passed
V9.3-M4      876 passed
V9.3-M5      893 passed

**V9.3 architecture now**
Document
   │
   ├── Document Profile
   │
   └── Intent Classification
             │
             ▼
      V9.2 Strategy Selector
             │
             ▼
      Adaptive Strategy Planner
             │
             ▼
      Adaptive Strategy Decision
             │
             ▼
      Resource Optimizer
       ├── Token estimate
       ├── Latency estimate
       └── Cost estimate
             │
             ▼
      Optimization Decision
             │
             ▼
      Summarization Execution

