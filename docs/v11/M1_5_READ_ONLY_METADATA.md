Document these rules:
- metadata is descriptive, never authoritative;
- no V9/V10/runtime/provider object may cross the application boundary;
- metadata values are strings/primitives only;
- M2 may populate strategy/chunk metadata;
- M3 may populate bounded-intelligence/explainability metadata;
- frontend exposure remains deferred to M4;
- metadata must never influence execution after the fact.