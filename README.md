
# python-mini-db
Python-mini-db is a lightweight in-memory database engine with a query builder, query optimizer, and support for hash, range, and composite indexes.



## Features

- Standard table operations (insert, update, delete, get)
- Immutable query builder with chainable API
- Query planner with index scan optimization
- Hash, range and composite indexes
- Index intersection for multiple filters
- Supports filter, order_by, limit, offset, select, join (inner join)

## Installation

Clone repository
```bash
git clone https://github.com/Hlib-Oliinyk/python-mini-db.git
```
Install dependencies
```bash
pip install -r requirements.txt
```
Run examples
```bash
python examples/basic_usage.py
```
## Usage

See [examples](examples/) folder for detailed usage examples:

- [Basic operations](examples/basic_usage.py) - insert, get, update, delete
- [Query builder](examples/query_examples.py) - filter, order_by, limit, join
- [Indexes](examples/indexes.py) - hash, range, composite indexes


## Architecture

**Database** — manages tables, creates and drops them

**Table** — stores rows and indexes, handles insert, update, delete

**Query** — immutable query builder, each method returns a new Query object. See [Query Builder](docs/query_builder.md)

**QueryState** — snapshot of query parameters passed to planner and executor

**QueryPlanner** — builds execution plan based on available indexes. See [Query Planner](docs/query_planner.md)

**QueryExecutor** — executes the plan step by step. See [Query Executor](docs/query_executor.md)

**Indexes** — hash, range and composite. See [Indexes](docs/indexes.md)

## Limitations

- No data persistence — all data is lost when the program stops
- Only inner join is supported
- Filtering on joined table fields is not supported
- No transactions
- No aggregations (group_by, sum, count by field)
- This project is for educational purposes only
## Running tests
```bash
pytest
```
For more information
```bash
pytest -s -v
```
## Future plans

- group_by with aggregations (min, max, sum, count)
- Transactions support
- JSON persistence
- Publish as PyPI package
## Contributing

Feel free to fork this project and improve it. Any contributions are welcome