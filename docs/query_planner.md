# Query Planner

QueryPlanner analyzes the query state and builds an optimal execution plan before running the query.

## How it works

When you call `.all()`, `.first()` or other execution methods, QueryPlanner receives a QueryState object and returns a list of steps for QueryExecutor to execute.

## Execution plan steps

- `finder` — full table scan with filter
- `index_scan` — scan using sorted RangeIndex keys, replaces finder when order_by field has RangeIndex
- `join` — inner join with another table
- `order_by` — sort results in memory
- `offset` — skip N rows
- `limit` — take N rows
- `select` — return only specified fields

## Example

Query without index:
users.query().filter(age__gt=17).order_by("age").limit(10).all()
Plan: ["finder", "order_by", "limit"]

Query with RangeIndex on "age":
users.query().filter(age__gt=17).order_by("age").limit(10).all()
Plan: ["index_scan", "limit"]

## Why index_scan is faster

finder does a full table scan and then sorts all results in memory.
index_scan reads rows directly from sorted RangeIndex keys — no full scan, no separate sorting step.