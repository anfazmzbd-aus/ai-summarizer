# Revised V7.8 Architecture (RFC-002)
## Design Principles
    From this point onward, every class belongs to exactly one architectural layer.

                    API Layer
                    │
                    ▼
           SummarizeService
                    │
                    ▼
        Runtime Layer (V7.8)
        ─────────────────────
           RuntimeManager
                │
                ▼
          RuntimeSession
                │
      ┌─────────┴─────────┐
      ▼                   ▼
 RuntimeContext     ExecutionContext
 (Lifecycle)         (Telemetry)
      │
      ▼
 ExecutionResult
      │
      ▼
     Response
                │
                ▼
      Execution Layer (V7.7)
      ─────────────────────
         Scheduler
             │
             ▼
      ExecutionEngine
             │
             ▼
        LayerExecutor
             │
             ▼
        NodeExecutor
             │
             ▼
           Agents

        Notice something important.

        The Execution Layer is now completely frozen.

        That becomes your deterministic kernel.

## Responsibility Matrix

| Component        | Responsibility                | Changes after V7.8? |
| ---------------- | ----------------------------- | ------------------- |
| ExecutionEngine  | Execute graph                 | Rarely              |
| LayerExecutor    | Execute one layer             | Rarely              |
| NodeExecutor     | Execute one node              | Rarely              |
| Scheduler        | Build execution graph         | Minor               |
| RuntimeManager   | Runtime orchestration         | Frequently          |
| RuntimeSession   | Execution-scoped runtime data | Frequently          |
| RuntimeContext   | Lifecycle                     | Frequently          |
| ExecutionContext | Telemetry                     | Frequently          |

This is a much healthier architecture.