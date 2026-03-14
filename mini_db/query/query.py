from dataclasses import dataclass
from copy import deepcopy

from mini_db.matcher import Matcher
from mini_db.exceptions import RowNotExists, MultipleObjectReturn
from mini_db.utils import timer
from .query_executor import QueryExecutor
from .query_planner import build_execution_plan


@dataclass
class QueryState:
    table_indexes: dict
    table_rows: dict
    filters: list
    limit: int
    order_by: tuple
    offset: int
    selected_fields: list
    join: dict


class Query:
    def __init__(self, table):
        self._table = table
        self._filters: list[dict] = []
        self._limit: int | None = None
        self._order_by: (str | None, str | None) = None
        self._offset: int | None = None
        self._selected_fields: list[tuple] = []
        self._join: dict = {}

    @staticmethod
    def _clone_row(row_id: int, row_value: dict) -> dict:
        new_row = {}

        new_row["id"] = row_id
        for key, value in row_value.items():
            new_row[key] = value

        return new_row

    def _clone_query(self):
        query = Query(self._table)

        query._filters = deepcopy(self._filters)
        query._limit = deepcopy(self._limit)
        query._order_by = deepcopy(self._order_by)
        query._offset = deepcopy(self._offset)
        query._selected_fields = deepcopy(self._selected_fields)
        query._join = deepcopy(self._join)

        return query

    def filter(self, **kwargs):
        new_query = self._clone_query()

        for key, value in kwargs.items():
            new_filter = {key:value}
            new_query._filters.append(new_filter)

        return new_query

    def limit(self, limit_num: int):
        new_query = self._clone_query()

        if limit_num < 0:
            limit_num = -limit_num

        new_query._limit = limit_num
        return new_query

    def order_by(self, order_field: str, order_type: str | None = None):
        new_query = self._clone_query()
        new_query._order_by = (order_field, order_type)
        return new_query

    def offset(self, offset_num: int):
        new_query = self._clone_query()

        if offset_num < 0:
            offset_num = -offset_num

        new_query._offset = offset_num
        return new_query

    def select(self, *args):
        new_query = self._clone_query()
        for arg in args:
            new_query._selected_fields.append(arg)
        return new_query

    def join(self, other_table, on: tuple):
        new_query = self._clone_query()
        new_query._join[other_table] = on
        return new_query

    def _create_query_state(self):
        query_state = QueryState(
            table_indexes = self._table._indexes,
            table_rows = self._table._rows,
            filters = self._filters,
            limit = self._limit,
            order_by = self._order_by,
            offset = self._offset,
            selected_fields = self._selected_fields,
            join = self._join
        )
        return query_state

    def _build_plan(self) -> list:
        query_state = self._create_query_state()
        plan = build_execution_plan(query_state)
        return plan

    @timer
    def _execute(self) -> list:
        plan = self._build_plan()
        query_state = self._create_query_state()
        result = QueryExecutor(query_state).run_plan(plan)
        return result

    def all(self) -> list:
        return self._execute()

    def first(self) -> dict | None:
        result = self._execute()
        return result[0] if result else None

    def explain(self) -> list:
        build_plan = self._build_plan()
        return build_plan

    def count(self) -> int:
        query_state = self._create_query_state()
        return len(QueryExecutor(query_state).finder())

    def exists(self) -> bool:
        query_state = self._create_query_state()
        if QueryExecutor(query_state).finder():
            return True
        return False

    def get(self, **kwargs) -> dict | None:
        new_query = self._clone_query()
        new_query._filters.append(kwargs)
        new_query_state = new_query._create_query_state()

        result = QueryExecutor(new_query_state).finder()

        if len(result) == 0:
            raise RowNotExists()
        if len(result) > 1:
            raise MultipleObjectReturn()

        return result[0]

    def update(self, filters: dict, values: dict) -> int:
        query_state = self._create_query_state()

        matching_ids = []
        candidate_ids = QueryExecutor(query_state).get_candidate_ids([filters])

        for row_id in candidate_ids:
            row = self._table._rows[row_id]
            if Matcher.matches(row, [filters]):
                matching_ids.append(row_id)

        for row_id in matching_ids:
            self._table.update(row_id, values)

        return len(matching_ids)