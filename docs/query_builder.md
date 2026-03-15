# Query Builder

Query builder provides a chainable API for building and executing queries.

## Immutable API

Each method returns a new Query object instead of modifying the current one. This means you can safely reuse queries.
```python
base_query = users.query().filter(age__gt=18)

query1 = base_query.limit(10)
query2 = base_query.order_by("age")

# base_query is not affected
```

## Available methods

**filter** — filter rows by field value, supports operators `eq`, `gt`, `lt`, `contains`
```python
users.query().filter(age=18)
users.query().filter(age__gt=18)
users.query().filter(age__lt=18)
users.query().filter(username__contains="lib")
```

**order_by** — sort results by field
```python
users.query().order_by("age")
users.query().order_by("age", "desc")
```

**limit** — take first N rows
```python
users.query().limit(10)
```

**offset** — skip first N rows
```python
users.query().offset(5)
```

**select** — return only specified fields
```python
users.query().select("username", "age")
```

**join** — inner join with another table
```python
users.query().join(posts, on=("row_id", "author_id"))
```

## Execution methods

**all** — returns list of all matching rows
**first** — returns first matching row or None
**count** — returns number of matching rows
**exists** — returns True if any matching rows exist
**get** — returns single row, raises exception if not found or multiple found
**update** — updates matching rows
**explain** — returns execution plan without running the query