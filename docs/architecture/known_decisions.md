Record decisions so future versions do not regress:

Summary is preprocessing, not DAG.
Scheduler filtering is safety only.
Validator owns DAG enforcement.
State merge immutable by default.
Retry always snapshot-based.
Empty DAG execution is valid.
Fallback intent preferred over business default.

After these docs updates, I would consider V7.6 officially closed and archived and then start V7.7 on a clean baseline.