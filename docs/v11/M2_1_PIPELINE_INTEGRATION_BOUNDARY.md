# V11 M2.1 — V9 Summarization Pipeline Integration Boundary

## Objective

Provide an asynchronous application integration boundary around the existing
synchronous, provider-independent V9 SummarizationPipeline.

## Constraint

The existing V9 pipeline accepts:

Callable[[str], str]

The canonical V11 application/provider path is asynchronous.

V11 must not redesign or duplicate the V9 pipeline solely to resolve this
execution-model mismatch.

## Solution

AsyncSummarizationPipelineAdapter runs the existing pipeline in a worker thread
and marshals summarization callbacks to the application's active event loop.

## Authority

The adapter owns execution-model translation only.

It does not own:

- chunking policy
- strategy selection
- map-reduce
- hierarchical summarization
- provider selection
- provider execution
- V10 intelligence
- runtime authority

## Milestone boundary

M2.1 introduces and validates the adapter.

M2.2 will compose this adapter behind SummarizationApplication.

M3 remains responsible for V10 bounded-intelligence integration.