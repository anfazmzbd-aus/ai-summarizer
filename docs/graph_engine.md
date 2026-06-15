#GRAPH ENGINE

##Dependency Resolution

Algorithm:

DFS-based resolution
visited set prevents cycles
recursive dependency expansion

##Parallel Group Builder
Input: execution_order + registry
Output: layered execution groups

Rules:

agents with satisfied dependencies go into same layer
unresolved dependencies block execution
empty group → circular dependency error

##Validation Layer

Checks:

unknown agents
missing dependencies
circular dependencies
registry mismatch

##Execution Flow
execution_order
    ↓
parallel_groups
    ↓
parallel_executor

















