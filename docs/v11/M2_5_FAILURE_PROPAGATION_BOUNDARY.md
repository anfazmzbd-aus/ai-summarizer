pipeline/provider failures propagate through the application boundary;
M2 does not reinterpret failures into retry/fallback decisions;
M2 does not introduce resilience policy;
generic API 500 behavior is accepted temporarily;
product-ready error mapping is deferred;
existing V9 resilience architecture remains untouched.