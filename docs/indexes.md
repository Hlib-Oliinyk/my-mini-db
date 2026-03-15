# Indexes

MiniDB supports three types of indexes to optimize query performance.

## HashIndex

Uses a hash map for storage. Best for equality lookups.

**Supported operators:** `eq`
**Time complexity:** O(1) lookup

**When to use:** when you filter by exact value, for example `filter(name="Hlib")`

## RangeIndex

Uses a sorted list of keys via Python `bisect` module. Supports range queries and is used by QueryPlanner for index scan optimization.

**Supported operators:** `eq`, `gt`, `lt`
**Time complexity:** O(log n) lookup

**When to use:** when you filter by range or order by field, for example `filter(age__gt=18)` or `order_by("age")`

## CompositeIndex

Uses a tuple of fields as a key. Best for equality lookups on multiple fields simultaneously.

**Supported operators:** `eq`
**Time complexity:** O(1) lookup

**When to use:** when you filter by multiple fields together, for example `filter(name="Hlib", age=18)`

## Index intersection

When multiple indexes are available, python-mini-db automatically intersects results to narrow down candidates before filtering.

## Example
```python
users.create_index("name", "hash")
users.create_index("age", "range")
users.create_index(("name", "age"), "composite")
```