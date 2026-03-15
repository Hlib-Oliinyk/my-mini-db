# Query Executor

QueryExecutor receives a QueryState and an execution plan from QueryPlanner and executes each step sequentially.

## How it works

Each step in the plan corresponds to a method in QueryExecutor. Steps are executed one by one, passing results from one step to the next.

## Steps

**finder** — gets candidate row ids using available indexes, then filters rows by conditions

**index_scan** — used instead of finder when RangeIndex is available on order_by field. Reads rows directly from sorted index keys with early stopping when limit is reached

**join** — performs inner join with another table by matching fields

**order_by** — sorts results in memory by specified field

**offset** — skips first N rows

**limit** — takes first N rows

**select** — returns only specified fields from each row

## Candidate ids optimization

Before doing a full scan, QueryExecutor tries to narrow down candidate rows using indexes:

1. If composite index matches all filter fields — use it directly
2. If single field indexes match — intersect their results
3. If no indexes match — fall back to full table scan

This reduces the number of rows that need to be checked against filter conditions.