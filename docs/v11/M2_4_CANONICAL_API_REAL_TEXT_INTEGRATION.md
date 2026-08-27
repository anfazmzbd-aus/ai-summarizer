SHORT TEXT
HTTP → canonical application → DIRECT → service → HTTP response

MEDIUM TEXT
HTTP → canonical application → MAP_REDUCE → repeated service calls
     → aggregated usage → HTTP response

LONG TEXT
HTTP → canonical application → HIERARCHICAL → repeated service calls
     → aggregated usage → HTTP response

deterministic service only;
no live-provider calls;
no frontend integration yet;
no V10 intelligence yet;
compatibility /summarize remains unchanged;
strategy metadata remains application-internal until explicitly surfaced later.