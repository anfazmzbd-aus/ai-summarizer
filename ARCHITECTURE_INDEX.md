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